import {loadKnowledgebases} from "./sidebar.js";
import {setupHeader} from "./header.js";

const backendHost = "http://47.108.135.173";
const backendPort = "8777";
const fileListUrl = `${backendHost}:${backendPort}/api/orag/select/files`; // Knowledgebase API base URL
const deleteFileUrl = `${backendHost}:${backendPort}/api/orag/delete/file`; // Knowledgebase API base URL
const uploadFileUrl = `${backendHost}:${backendPort}/api/orag/add/document`; // Knowledgebase API base URL
const addUrlUrl = `${backendHost}:${backendPort}/api/orag/add/url`; // Knowledgebase API base URL
const editKnowledgebaseUrl = `${backendHost}:${backendPort}/api/orag/update/kb_name`; // Knowledgebase API base URL
const deleteKnowledgebaseUrl = `${backendHost}:${backendPort}/api/orag/delete/knowledge_base`; // Knowledgebase API base URL

const knowledgebaseActions = document.getElementById("knowledgebase-actions");
const editKnowledgebaseInput = document.getElementById("edit-knowledgebase-name");
const editKnowledgebaseButton = document.getElementById("edit-knowledgebase");
const deleteKnowledgebaseButton = document.getElementById("delete-knowledgebase");

const fileUploadContainer = document.querySelector(".file-upload-container");
const fileList = document.getElementById("file-list");
const uploadButton = document.getElementById("upload-button");
const fileInput = document.getElementById("file");
const allowedExtensions = ['.txt', '.pdf', '.docx', '.md', '.jpg', '.jpeg', '.png'];
const urlInput = document.getElementById('url-input');
const addUrlButton = document.getElementById('add-url-button');
const uploadProgress = document.getElementById('upload-progress');

let selectedKnowledgebase = null;

// Edit selected knowledgebase
editKnowledgebaseButton.addEventListener("click", function () {
    const newKbName = editKnowledgebaseInput.value;

    if (selectedKnowledgebase && newKbName) {
        fetch(editKnowledgebaseUrl, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ kb_id: selectedKnowledgebase.kb_id, user_id: getCookie('user_id'), new_kb_name: newKbName }) // Send the ID of the knowledgebase to delete
        })
            .then(response => response.json())
            .then(data => {
                if (data.code===200) {
                    loadKnowledgebases(); // Reload list
                    knowledgebaseActions.style.display = "none"; // Hide actions
                } else {
                    alert(data.message || "Failed to edit knowledgebase.");
                }
            })
            .catch(error => {
                console.error("Error editing knowledgebase:", error);
            });
        } else {
            alert("Please select a knowledgebase and enter a valid name.");
        }
});

// Delete selected knowledgebase
deleteKnowledgebaseButton.addEventListener("click", function () {
    if (selectedKnowledgebase) {
        fetch(deleteKnowledgebaseUrl, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ kb_id: selectedKnowledgebase.kb_id, user_id: getCookie('user_id') }) // Send the ID of the knowledgebase to delete
        })
            .then(response => response.json())
            .then(data => {
                if (data.code===200) {
                    loadKnowledgebases(); // Reload list
                    knowledgebaseActions.style.display = "none"; // Hide actions
                } else {
                    alert(data.message || "Failed to delete knowledgebase.");
                }
            })
            .catch(error => {
                console.error("Error deleting knowledgebase:", error);
            });
        } else {
            alert("Please select a knowledgebase to delete.");
        }
});


// Listen for knowledgebase selection event
document.addEventListener("knowledgebaseSelected", function (event) {
    selectedKnowledgebase = event.detail;
    const knowledgebaseActions = document.getElementById("knowledgebase-actions");
    knowledgebaseActions.style.display = "block";

    // Hide file upload and file list sections
    fileUploadContainer.style.display = "none";
    fileList.style.display = "none";
});

// Fetch file list based on selected knowledgebase
function loadFileList() {
    if (!selectedKnowledgebase || !selectedKnowledgebase.kb_id) {
        console.error("Knowledgebase ID not found.");
        return;
    }

    fetch(fileListUrl, {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ kb_id: selectedKnowledgebase.kb_id, user_id: getCookie('user_id') }) // Send selected knowledgebase ID
    })
        .then(response => response.json())
        .then((data) => {
            // Clear current file list
            fileList.innerHTML = "";

            // Iterate over returned files and append to the list
            data.data.forEach(file => {
                const [file_id, kb_id, file_name, file_path, status, timestamp, deleted, file_size, chunk_size] = file;
                const fileDate = new Date(
                    timestamp.substring(0, 4),
                    timestamp.substring(4, 6) - 1,
                    timestamp.substring(6, 8),
                    timestamp.substring(8, 10),
                    timestamp.substring(10, 12)
                );
                const formattedDate = fileDate.toISOString().replace("T", " ").substring(0, 16);

                let formattedFileSize;
                if (file_size < 1024) {
                    formattedFileSize = `${file_size} B`; // 小于 1 KB 时显示字节
                } else if (file_size < 1024 * 1024) {
                    formattedFileSize = `${(file_size / 1024).toFixed(2)} KB`; // KB 显示
                } else {
                    formattedFileSize = `${(file_size / (1024 * 1024)).toFixed(2)} MB`; // MB 显示
                }

                let currentFileId = null;
                const listItem = document.createElement("li");
                const contextMenu = document.getElementById("context-menu");
                listItem.textContent = `${file_name}, ${formattedDate}, ${formattedFileSize}`;

                listItem.addEventListener("contextmenu", function (e) {
                    e.preventDefault();
                    currentFileId = file_id;

                    contextMenu.style.display = "block";
                    contextMenu.style.left = `${e.pageX}px`;
                    contextMenu.style.top = `${e.pageY}px`;

                    const deleteButton = document.getElementById('delete-file');
                    deleteButton.style.display = "block";

                    deleteButton.onclick = () => {
                        deleteFile(currentFileId);
                        contextMenu.style.display = 'none';
                        deleteButton.style.display = 'none';
                    };
                });

                document.addEventListener('click', () => {
                    contextMenu.style.display = 'none';
                    const deleteButton = document.getElementById('delete-file');
                    deleteButton.style.display = 'none';
                });

                // Append file details to the list item
                fileList.appendChild(listItem);
            });
        })
        .catch(error => {
            console.error("Error fetching file list:", error);
        });
}

// Delete a file
function deleteFile(file_id) {
    fetch(deleteFileUrl, {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ user_id: getCookie('user_id'), kb_id: selectedKnowledgebase.kb_id, file_id: file_id })
    })
        .then(response => response.json())
        .then(data => {
            if (data.code === 200) {
                loadFileList(); // Reload the file list after deletion
            } else {
                alert(data.msg || "Failed to delete file.");
            }
        })
        .catch(error => {
            console.error("Error deleting file:", error);
        });
}



    uploadButton.addEventListener("click", () => {
        const file = fileInput.files[0];
        if (!file) {
            alert("Please select a file to upload.");
            return;
        }

        const fileExtension = '.' + file.name.split('.').pop().toLowerCase();
        if (!allowedExtensions.includes(fileExtension)) {
            alert(`Invalid file type. Allowed types: ${allowedExtensions.join(', ')}`);
            return;
        }

        const reader = new FileReader();
        const formData = new FormData();
        formData.append('kb_id', selectedKnowledgebase.kb_id);
        formData.append('user_id', getCookie('user_id'));
        formData.append('files', file);
        formData.append('mode', 'soft');

        uploadProgress.style.display = 'block';
        uploadProgress.value = 0;

        const xhr = new XMLHttpRequest();

        xhr.upload.addEventListener("progress", (event) => {
            if (event.lengthComputable) {
                uploadProgress.value = (event.loaded / event.total) * 100;
            }
        });

        xhr.open("POST", uploadFileUrl, true);

        xhr.onload = () => {
            if (xhr.status === 200) {
                const data = JSON.parse(xhr.responseText);
                if (data.code === 200) {
                    alert("File uploaded successfully!");
                    loadFileList();
                } else {
                    alert(data.msg || "Failed to upload file.");
                }
            } else {
                alert("Error uploading file.");
            }

            uploadProgress.style.display = 'none';
        };

        xhr.onerror = () => {
            alert("Error uploading file.");
            uploadProgress.style.display = 'none';
        };

        xhr.send(formData);
    });

    addUrlButton.addEventListener("click", () => {
        const url = urlInput.value.trim();

        if (!url) {
            alert("Please enter a URL.");
            return;
        }

        const formData = new FormData();
        formData.append('kb_id', selectedKnowledgebase.kb_id);
        formData.append('user_id', getCookie('user_id'));
        formData.append('url', url);

        fetch(addUrlUrl, {
            method: "POST",
            body: formData,
        })
        .then(response => response.json())
        .then(data => {
            if (data.code === 200) {
                alert("uploaded successfully!");
                loadFileList();
            } else {
                uploadStatus.textContent = data.msg || "Failed to upload URL.";
            }
        })
        .catch(error => {
            console.error("Error uploading URL:", error);
            alert("Error uploading URL.");
        });
    });

function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
    return null;
}

export { selectedKnowledgebase };


