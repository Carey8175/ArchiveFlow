import { selectedKnowledgebase } from './baseManage.js';

const backendHost = "http://47.108.135.173";
const backendPort = "8777";
const knowledgebaseUrl = `${backendHost}:${backendPort}/api/orag/select/knowledge_base`; // Knowledgebase API base URL
const addKnowledgebaseUrl = `${backendHost}:${backendPort}/api/orag/add/knowledge_base`; // Knowledgebase API base URL

const knowledgebaseList = document.getElementById("knowledgebase-list");
const addKnowledgebaseButton = document.getElementById("add-knowledgebase");
const newKnowledgebaseInput = document.getElementById("new-knowledgebase");

// Fetch knowledgebase list and display it
export function loadKnowledgebases() {
    const userId = getCookie('user_id');
    if (!userId) {
        console.error("User ID not found in cookies.");
        return;
    }

    fetch(knowledgebaseUrl, {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ user_id: userId })
    })
    .then(response => response.json())
    .then(data => {
        knowledgebaseList.innerHTML = ""; // Clear current list
        data.data.forEach(kb => {
            const [kb_id, kb_name] = kb;
            const listItem = document.createElement("li");
            listItem.textContent = kb_name || "Unnamed Knowledgebase";

            // Add event listener for when a knowledgebase is clicked
            listItem.addEventListener("click", () => {
                selectKnowledgebase(kb_id, kb_name);
            });

            knowledgebaseList.appendChild(listItem);
        });
    })
    .catch(error => {
        console.error("Error fetching knowledgebases:", error);
    });
}

// Select a knowledgebase and show its files
function selectKnowledgebase(kb_id, kb_name) {
    const knowledgebase = { kb_id, kb_name };
    const event = new CustomEvent('knowledgebaseSelected', { detail: knowledgebase });
    document.dispatchEvent(event);
}

// Add new knowledgebase
addKnowledgebaseButton.addEventListener("click", function () {
    const knowledgebaseName = newKnowledgebaseInput.value.trim(); // Trim whitespace

    if (knowledgebaseName) {
        fetch(addKnowledgebaseUrl, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ kb_name: knowledgebaseName, user_id: getCookie('user_id') })
        })
        .then(response => response.json())
        .then(data => {
            if (data.code === 200) {
                newKnowledgebaseInput.value = ""; // Clear input
                loadKnowledgebases(); // Reload list
            } else {
                alert(data.message || "Failed to add knowledgebase.");
            }
        })
        .catch(error => {
            console.error("Error adding knowledgebase:", error);
        });
    } else {
        alert("Knowledgebase name cannot be empty.");
    }
});

document.addEventListener('contextmenu', function (e) {
    e.preventDefault();

    // Show the context menu for managing the knowledgebase
    const contextMenu = document.getElementById("context-menu");
    contextMenu.style.display = "block";
    contextMenu.style.left = `${e.pageX}px`;
    contextMenu.style.top = `${e.pageY}px`;

    // Create a "Manage Knowledgebase" option in the context menu
    const manageKnowledgebaseOption = document.createElement("li");
    manageKnowledgebaseOption.textContent = "Manage Knowledgebase";
    contextMenu.appendChild(manageKnowledgebaseOption);

    // Handle click on the "Manage Knowledgebase" option
    manageKnowledgebaseOption.addEventListener('click', function () {
        document.getElementById('database-management').style.display = 'block';
        // Trigger the load of knowledgebase details
        const editKnowledgebaseInput = document.getElementById("edit-knowledgebase-name");
        editKnowledgebaseInput.value = selectedKnowledgebase.kb_name; // Set current knowledgebase name in input
        contextMenu.style.display = 'none'; // Hide the context menu
    });

    // Hide the context menu when clicking elsewhere
    document.addEventListener('click', () => {
        contextMenu.style.display = 'none';
    });
});

// Get cookie value by name
function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
    return null;
}

document.addEventListener("DOMContentLoaded", loadKnowledgebases);