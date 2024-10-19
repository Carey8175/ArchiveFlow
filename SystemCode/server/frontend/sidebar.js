import {deleteKnowledgebase, manageKnowledgebase} from './baseManage.js';
import {goToChatInterface} from './chatInterface.js';

const backendHost = "http://47.108.135.173";
const backendPort = "8777";
const knowledgebaseUrl = `${backendHost}:${backendPort}/api/orag/select/knowledge_base`; // Knowledgebase API base URL
const addKnowledgebaseUrl = `${backendHost}:${backendPort}/api/orag/add/knowledge_base`; // Knowledgebase API base URL
const knowledgebaseList = document.getElementById("knowledgebase-list");
const addKnowledgebaseButton = document.getElementById("add-knowledgebase");
const newKnowledgebaseInput = document.getElementById("new-knowledgebase");
const sidebarMenu = document.getElementById("sidebar-context-menu");
const chatInterface = document.getElementById("chat-interface");

export let selectedKnowledgebase = null;

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
            const li = document.createElement('li');
            li.setAttribute('kb_id', kb[0]);
            li.setAttribute('kb_name', kb[1]);
            li.textContent = kb[1];
            knowledgebaseList.appendChild(li);
        });
    })
    .catch(error => {
        console.error("Error loading knowledge bases:", error);
    });
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

// Left click event listener for entering chat interface
knowledgebaseList.addEventListener("click", function (event) {
    event.preventDefault(); // Prevent default click behavior

    const selectedItem = event.target.closest('li');
    if (!selectedItem) return;

    const kb_id = selectedItem.getAttribute('kb_id');
    const kb_name = selectedItem.getAttribute('kb_name');

    if (!kb_id || !kb_name) return;

    selectedKnowledgebase = { kb_id, kb_name };

    // Enter chat interface for selected knowledgebase
    goToChatInterface(selectedKnowledgebase);
});

// Listen for right-click event on the knowledgebase list
knowledgebaseList.addEventListener("contextmenu", function (event) {
    event.preventDefault(); // Prevent default context menu

    const selectedItem = event.target.closest('li');
    if (!selectedItem) return;

    const kb_id = selectedItem.getAttribute('kb_id');
    const kb_name = selectedItem.getAttribute('kb_name');

    if (!kb_id || !kb_name) return;

    selectedKnowledgebase = { kb_id, kb_name };

    // Show the custom context menu
    sidebarMenu.style.display = "block";
    sidebarMenu.style.left = `${event.pageX}px`;
    sidebarMenu.style.top = `${event.pageY}px`;

    // Handle context menu item clicks
    document.getElementById("manage-knowledgebase").onclick = function() {
        chatInterface.style.display = "none";
        manageKnowledgebase()
        sidebarMenu.style.display = "none"; // Hide the menu
    };

    document.getElementById("delete-knowledgebase").onclick = function() {
        const confirmDelete = confirm(`Are you sure you want to delete the knowledge base "${selectedKnowledgebase.kb_name}"?`);
        if (confirmDelete) {
            deleteKnowledgebase();
        }
        sidebarMenu.style.display = "none"; // Hide the menu
    };

    // Hide menu when clicking outside
    document.addEventListener("click", function () {
        if (sidebarMenu&& !sidebarMenu.contains(event.target)) {
            sidebarMenu.style.display = "none";
        }
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
