import {selectedKnowledgebase, loadKnowledgebases} from "./sidebar.js";

const backendHost = "http://47.108.135.173";
const backendPort = "18777";
const fileListUrl = `${backendHost}:${backendPort}/api/orag/select/files`; // Knowledgebase API base URL
const deleteFileUrl = `${backendHost}:${backendPort}/api/orag/delete/file`; // Knowledgebase API base URL
const uploadFileUrl = `${backendHost}:${backendPort}/api/orag/add/document`; // Knowledgebase API base URL
const addUrlUrl = `${backendHost}:${backendPort}/api/orag/add/url`; // Knowledgebase API base URL
const editKnowledgebaseUrl = `${backendHost}:${backendPort}/api/orag/update/kb_name`; // Knowledgebase API base URL
const deleteKnowledgebaseUrl = `${backendHost}:${backendPort}/api/orag/delete/knowledge_base`; // Knowledgebase API base URL

const databaseManagement = document.getElementById("database-management")
const knowledgebaseActions = document.getElementById("delete-knowledgebase");
const sidebarMenu = document.getElementById("sidebar-context-menu");

const fileList = document.getElementById("file-list");
const fileInput = document.getElementById("file");
const uploadButton = document.getElementById("upload-button");
const allowedExtensions = ['.txt', '.pdf', '.docx', '.md', '.jpg', '.jpeg', '.png'];
const urlInput = document.getElementById('url-input');
const addButton = document.getElementById("add-url-button");
const uploadProgress = document.getElementById('upload-progress');

export function manageKnowledgebase(selectedKnowledgebase) {
    databaseManagement.style.display = "block";

    document.getElementById("confirm-edit").onclick = function() {
        editKnowledgebase(selectedKnowledgebase);
    };

    uploadButton.disabled = false;
    document.getElementById("upload-button").onclick = function() {
        uploadButton.disabled = true;
        uploadFile(selectedKnowledgebase);
    };

    addButton.disabled = false;
    document.getElementById("add-url-button").onclick = function() {
        addButton.disabled = false;
        addUrl(selectedKnowledgebase)
    };

    loadFileList();
}

// Function to go back to the chat interface
document.getElementById("go-back-button").addEventListener("click", function() {
    // Hide the management interface
    document.getElementById("database-management").style.display = "none";
    // Show the chat interface
    document.getElementById("chat-interface").style.display = "flex"; // Make sure it's displayed properly
});

// Edit selected knowledgebase
function editKnowledgebase() {
    const newKbName = prompt("Enter new knowledgebase name:");

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
                    alert(data.message || "Rename Success.");
                } else {
                    alert(data.message || "Failed to edit knowledgebase.");
                }
            })
            .catch(error => {
                console.error("Error editing knowledgebase:", error);
            });
    } else {
        alert("Rename Canceled");
    }
}

// Delete selected knowledgebase
function deleteKnowledgebase() {
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
                    sidebarMenu.style.display = "none"; // Hide actions
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
}

// Fetch file list based on selected knowledgebase
function loadFileList(e) {
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
                const formattedDate = fileDate.toLocaleString().replace("T", " ").replace(",", " ").substring(0, 17);

                let formattedFileSize;
                if (file_size < 1024) {
                    formattedFileSize = `${file_size} B`;
                } else if (file_size < 1024 * 1024) {
                    formattedFileSize = `${(file_size / 1024).toFixed(2)} KB`;
                } else {
                    formattedFileSize = `${(file_size / (1024 * 1024)).toFixed(2)} MB`;
                }

                let currentFileId = null;

                const listItem = document.createElement("li");

                const fileNames = document.createElement("span");
                fileNames.classList.add("file-names");
                fileNames.textContent = file_name;

                const fileDates = document.createElement("span");
                fileDates.classList.add("file-dates");
                fileDates.textContent = formattedDate;

                const fileSizes = document.createElement("span");
                fileSizes.classList.add("file-details");
                fileSizes.textContent = formattedFileSize;

                const fileStatus = document.createElement("span");
                fileStatus.classList.add("file-status");

                switch (status.toLowerCase()) {
                    case "normal":
                        fileStatus.classList.add("normal");
                        break;
                    case "waiting":
                        fileStatus.classList.add("waiting");
                        break;
                    case "error":
                        fileStatus.classList.add("error");
                        break;
                    default:
                        fileStatus.style.color = "#000";
                        break;
                }

                fileStatus.textContent = status;

                const contextMenu = document.getElementById("context-menu");
                listItem.appendChild(fileNames);
                listItem.appendChild(fileDates);
                listItem.appendChild(fileSizes);
                listItem.appendChild(fileStatus);

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



function uploadFile() {
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
    document.querySelector('.file-upload-container').classList.add('show-progress');


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
                fileInput.value = '';
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
    uploadButton.disabled = false;
}

function addUrl() {
    const url = urlInput.value.trim();

    if (!url) {
        alert("Please enter a URL.");
        return;
    }

    const urlPattern = /^(http|https):\/\/[^\s$.?#].[^\s]*$/;
    if (!urlPattern.test(url)) {
        alert("Please enter a valid URL.");
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
                urlInput.value = '';
            } else {
                alert(data.msg);
            }
        })
        .catch(error => {
            console.error("Error uploading URL:", error);
            alert("Error uploading URL.");
        });
}

function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
    return null;
}

export { deleteKnowledgebase };


