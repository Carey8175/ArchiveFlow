import { selectedKnowledgebase } from "./sidebar.js";

const backendHost = "http://47.108.135.173";
const backendPort = "8777";

const chatStreamUrl = `${backendHost}:${backendPort}/api/orag/chat_stream`; // Knowledgebase API base URL
const modelSelect = document.getElementById('model-select');
const multiTurnBtn = document.getElementById('multi-turn-button');
const modelSettingsButton = document.getElementById('model-settings-button');
const modal = document.getElementById('model-settings-modal');
const closeButton = document.querySelector('.close-button');
const confirmButton = document.getElementById('confirm-button');
const tokenLimit = document.getElementById('token-limit');
const tokenValue = document.getElementById('token-value');

const modelOptions = [
    "gpt-3.5-turbo", "gpt-3.5-turbo-1106", "gpt-3.5-turbo-0125", "gpt-3.5-turbo-16k",
    "gpt-3.5-turbo-instruct", "gpt-4", "gpt-4o", "gpt-4o-2024-05-13", "gpt-4o-2024-08-06",
    "chatgpt-4o-latest", "gpt-4o-mini", "gpt-4-0613", "gpt-4-turbo-preview", "gpt-4-0125-preview",
    "gpt-4-1106-preview", "gpt-4-vision-preview", "gpt-4-turbo", "gpt-4-turbo-2024-04-09",
    "claude-3-5-sonnet-20240620"
];

let chatHistory = [];
let selectedModel = null;
let isMultiTurnEnabled = false;

modelSettingsButton.addEventListener('click', () => {
    modal.style.display = 'block';
});

closeButton.addEventListener('click', () => {
    modal.style.display = 'none';
});

confirmButton.addEventListener('click', () => {
    const apiKey = document.getElementById('api-key').value;
    const baseUrl = document.getElementById('base-url').value;
    const selectedModel = document.getElementById('model-select').value;

    if (!apiKey || !baseUrl){
        alert("Please enter your api key and base url")
    }

    console.log("User ID:", getCookie('user_name'), "API Key:", apiKey, "Base URL:", baseUrl, "Selected Model:", selectedModel);
    // document.getElementById("model-settings-modal").style.display = "none"; // Hide management interface

});

modelSelect.addEventListener('change', () => {
    const selectedModel = modelSelect.value;
    console.log("Selected Model:", selectedModel);
});

tokenLimit.addEventListener('input', () => {
    tokenValue.textContent = tokenLimit.value;
});

document.addEventListener('DOMContentLoaded', function() {

    // Check if model is selected
    if (!selectedModel) {
        alert("Please select a model before starting the chat.");
    }

    modelSelect.addEventListener('change', function() {
        selectedModel = this.value;
    });

    multiTurnBtn.addEventListener('click', toggleMultiTurn);
    modelChoices();

})

document.getElementById("send-button").addEventListener("click", sendMessage);

function toggleMultiTurn() {
    console.log("multi-turned!")
    isMultiTurnEnabled = !isMultiTurnEnabled;
    multiTurnBtn.title = isMultiTurnEnabled ? "Multi-turn conversation is enabled" : "Multi-turn conversation is disabled";
    multiTurnBtn.classList.toggle('active', isMultiTurnEnabled);
}

// Function to handle sending messages
function sendMessage() {
    const userId = getCookie('user_name')
    const currentMessage = document.getElementById("message-input").value.trim(); // Get the message

    if (!selectedModel) {
        alert("Please select a model.");
        return;
    }

    if (!currentMessage) {
        alert("Enter a message.");
        return;
    }

    // In multi-turn mode, add the message to the queue
    if (isMultiTurnEnabled) {
        chatHistory.push({ role: 'user', message: messageInput }); // Add message to queue
        addMessageToChat('user', currentMessage);
        console.log("Message added to queue:", currentMessage);
        sendToBackend(userId, selectedModel, chatHistory);
    } else {
        // Single-turn mode: Send only the current message immediately
        addMessageToChat('user', currentMessage);
        sendToBackend(userId, selectedModel, [{ role: 'user', message: currentMessage }]);
    }
    document.getElementById("message-input").value = '';
}

// Function to connect to chatStream mode
function sendToBackend(userId, model, messageList) {
    // Send a request to chatStreamUrl
    fetch(chatStreamUrl, {
        method: "POST",
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            user_id: userId,
            model: model,
            message: messageList,
        })
    })
    .then(response => response.json())
    .then(data => {
        console.log("Message sent to backend:", data);
        const assistantMessage = data.message;  // Get assistant's response from backend
        addMessageToChat('assistant', assistantMessage);  // Display assistant's response

        if (isMultiTurnEnabled) {
            chatHistory.push({ role: 'assistant', message: assistantMessage });  // Add assistant's response to chat history
        }
    })
    .catch(error => {
        console.error("Error sending message:", error);
        alert("Error sending message.");
    });
}

// Function to display messages in the chat box
function addMessageToChat(role, message) {
    const chatBox = document.getElementById("chat-box");
    const newMessage = document.createElement("div");
    newMessage.classList.add(role);  // Add class based on role (e.g., 'user' or 'assistant')
    newMessage.textContent = message;
    chatBox.appendChild(newMessage);  // Append the new message to chat display
}

function modelChoices() {
    modelSelect.innerHTML = '';
    modelOptions.forEach(model => {
        const option = document.createElement('option');
        option.value = model;
        option.textContent = model;
        modelSelect.appendChild(option);
    });
}

document.getElementById("message-input").addEventListener("keydown", function(e) {
    if (e.key === "Enter") {
        sendMessage();
    }
});

document.getElementById("new-chat-button").addEventListener("click", function() {
    chatHistory = [];  // Reset chat history
    document.getElementById("chat-box").innerHTML = '';  // Clear the chat display
    document.getElementById("message-input").value = '';  // Clear the input field
    alert("New conversation started!");  // Optional alert to notify the user
});

export function goToChatInterface(knowledgebase) {
    document.getElementById("chat-interface").style.display = "block"; // Show chat interface
    document.getElementById("database-management").style.display = "none"; // Hide management interface
    console.log(`Switched to chat for knowledgebase: ${knowledgebase.kb_name}`);
}

// Get cookie value by name
function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
    return null;
}