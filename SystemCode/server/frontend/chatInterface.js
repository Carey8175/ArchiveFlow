// chatInterface.js

// Get DOM elements
const chatInterface = document.getElementById("chat-interface");
const messageInput = document.getElementById("message-input");
const sendButton = document.getElementById("send-button");
const messageList = document.getElementById("message-list");

// Initialize chat
function initChat() {
    console.log("Chat interface initialized");
}

// Send message function
function sendMessage() {
    const message = messageInput.value.trim();
    if (message) {
        // Display sent message
        displayMessage("You", message);

        // Clear input
        messageInput.value = '';

        // Send message to server (replace with your logic)
        sendMessageToServer(message);
    } else {
        alert("Please enter a message.");
    }
}

// Display message function
function displayMessage(sender, message) {
    const li = document.createElement("li");
    li.textContent = `${sender}: ${message}`;
    messageList.appendChild(li);
}

// Send message to server function
function sendMessageToServer(message) {
    // Here you can implement the logic to send the message to your server
    console.log("Sending message to server:", message);

    // Example of a fetch request
    fetch('your-chat-server-endpoint', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message }),
    })
    .then(response => response.json())
    .then(data => {
        // Handle server response
        if (data.success) {
            console.log("Message sent successfully");
        } else {
            console.error("Failed to send message:", data.message);
        }
    })
    .catch(error => {
        console.error("Error sending message:", error);
    });
}

// Bind events
sendButton.addEventListener("click", sendMessage);
messageInput.addEventListener("keypress", function(event) {
    // Send message on Enter key press
    if (event.key === "Enter") {
        sendMessage();
    }
});

// Initialize chat interface
initChat();
