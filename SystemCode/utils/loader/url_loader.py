import os
import re
import requests
from typing import Optional, Set, List, Any
from urllib.parse import urljoin, urldefrag
from bs4 import BeautifulSoup
from SystemCode.configs.basic import SENTENCE_SIZE, MAX_URL_DEPTH
from unstructured.partition.text import partition_text
from langchain_community.document_loaders import UnstructuredFileLoader


class URLToTextConverter(UnstructuredFileLoader):
    def __init__(
        self,
        base_url: str,
        output_dir: str = "tmp_files",
        max_depth: int = 5,
        exclude_dirs: Optional[List[str]] = None,
        mode: str = "elements",
        **unstructured_kwargs: Any,
    ):
        super().__init__(file_path=base_url, mode=mode, **unstructured_kwargs)
        self.base_url = base_url
        self.output_dir = output_dir
        self.exclude_dirs = exclude_dirs or []
        self.unstructured_kwargs = unstructured_kwargs

        # Create the output directory if it doesn't exist
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def get_url_content(self, url: str) -> str:
        """ """
        try:
            # Fetch the content of the URL
            headers = {
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36'

            }

            response = requests.get(url, headers=headers)
            if response.status_code != 200:
                print(f"Failed to retrieve URL: {url} (Status code: {response.status_code})")
                return None

            # Parse the page content
            soup = BeautifulSoup(response.content, "html.parser")
            page_text = " ".join(soup.stripped_strings)
            clean_text = self._clean_text(page_text)
            segments = self._split_text_by_size(clean_text, SENTENCE_SIZE)  # Separate content to segments

            return segments

        except Exception as e:
            print(f"Error processing {url}: {e}")
            return None

    def url_to_txt(self, url: str, depth: int = 0, visited: Optional[Set[str]] = None) -> Optional[str]:
        combined_text = []
        visited = visited or set()

        # Exclude certain directories
        if any(url.startswith(exclude_dir) for exclude_dir in self.exclude_dirs):
            return None

        visited.add(url)

        try:
            response = requests.get(url)
            if response.status_code == 200:
                main_content = self.get_url_content(url)
                if main_content:  # Ensure main content is not None
                    combined_text += main_content

                soup = BeautifulSoup(response.text, "html.parser")
                child_links = self._get_child_links(soup, url)

                for link in child_links[:MAX_URL_DEPTH]:
                    print('parser url :', link)
                    combined_text += self.get_url_content(link)

        except Exception as e:
            print(f"Error fetching links for {url}: {e}")

        tmp_file_name = self._sanitize_filename(url)[:30] if len(self._sanitize_filename(url)) > 50 \
            else self._sanitize_filename(url)

        output_path = os.path.join(self.output_dir, tmp_file_name + ".txt")

        with open(output_path, "w", encoding="utf-8") as f:
            f.write('/n'.join(combined_text))

        print(f"Saved combined content from {url} to {output_path}")

        return output_path

    def _get_elements(self) -> List:
        """Main method to start the extraction process."""
        txt_file_path = self.url_to_txt(self.base_url) # Use self to call the url_to_txt

        if not os.path.exists(txt_file_path):
            print("No files were generated.")
            return []

        docs = partition_text(filename=txt_file_path, **self.unstructured_kwargs)

        # Delete each file after processing
        if os.path.exists(txt_file_path):
            os.remove(txt_file_path)

        return docs

    def _clean_text(self, text: str) -> str:
        """remove extra spaces"""
        text = re.sub(r'\s+', ' ', text)
        return text.strip()

    def _split_text_by_size(self, text: str, max_size: int) -> List[str]:
        """split page content by max_size"""
        return [text[i:i + max_size] for i in range(0, len(text), max_size)]

    def _get_child_links(self, soup: BeautifulSoup, base_url: str) -> List[str]:
        """Extract and return all valid child links on the page."""
        all_links = [urljoin(base_url, a.get('href')) for a in soup.find_all('a', href=True)]
        child_links = [urldefrag(link).url for link in all_links if link.startswith(base_url)]
        return list(set(child_links))  # Remove duplicates

    def _sanitize_filename(self, url: str) -> str:
        """Create a valid filename from a URL."""
        return url.replace("http://", "").replace("https://", "").replace("/", "_").replace("?", "_").replace(".", "_")