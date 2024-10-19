const chatStreamUrl = `${backendHost}:${backendPort}/api/orag/chat_stream`; // Knowledgebase API base URL
const chatBotUrl = `${backendHost}:${backendPort}/api/orag/chat`; // Knowledgebase API base URL
const modelSelect = document.getElementById('model-select');
const multiTurnBtn = document.getElementById('multi-turn-button');


const modelOptions = [
    "gpt-3.5-turbo", "gpt-3.5-turbo-1106", "gpt-3.5-turbo-0125", "gpt-3.5-turbo-16k",
    "gpt-3.5-turbo-instruct", "gpt-4", "gpt-4o", "gpt-4o-2024-05-13", "gpt-4o-2024-08-06",
    "chatgpt-4o-latest", "gpt-4o-mini", "gpt-4-0613", "gpt-4-turbo-preview", "gpt-4-0125-preview",
    "gpt-4-1106-preview", "gpt-4-vision-preview", "gpt-4-turbo", "gpt-4-turbo-2024-04-09",
    "claude-3-5-sonnet-20240620"
];

let selectedModel = null;
let isMultiTurnEnabled = false;

document.addEventListener('DOMContentLoaded', function() {

    // Check if model is selected
    if (!selectedModel) {
        alert("Please select a model before starting the chat.");
    }

    modelSelect.addEventListener('change', function() {
        selectedModel = this.value;
    });

    multiTurnBtn.addEventListener('click', toggleMultiTurn);

})

function toggleMultiTurn() {
    console.log("multi-turned!")
    isMultiTurnEnabled = !isMultiTurnEnabled;

    multiTurnBtn.title = isMultiTurnEnabled ? "Multi-turn conversation is enabled" : "Multi-turn conversation is disabled";
    multiTurnBtn.classList.toggle('active', isMultiTurnEnabled);

    // Connect to charStreamUrl if multi-turn is enabled
    if (isMultiTurnEnabled) {
        connectToCharStream();  // Activate chatStream mode
    } else {
        activateChatBot();      // Switch to chatBot mode
    }

}

// Function to connect to chatStream mode
function connectToCharStream() {

    const model = document.getElementById("model-select").value;
    const message = document.getElementById("message-input").value.trim();

    // Send a request to chatStreamUrl
    fetch(chatStreamUrl, {
        method: "POST",
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            user_id: getCookie('user_name'),
            model: model,
            message: message,
            mode: 'chatStream',
        })
    })
    .then(response => {
        if (response.ok) {
            console.log("Connected to chatStreamUrl successfully!");
        } else {
            console.error("Failed to connect to chatStreamUrl");
        }
    })
    .catch(error => {
        console.error("Error connecting to charStreamUrl:", error);
    });
}

// Function to activate chatBot mode
function activateChatBot() {
    const model = document.getElementById("model-select").value; // Get selected model
    const message = document.getElementById("message-input").value.trim(); // Get the message

    // Send a POST request to chatBotUrl
    fetch(chatBotUrl, {
        method: "POST",
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            user_id: getCookie("user_name"),
            model: model,
            message: message,
            mode: 'chatBot' // Specify the mode
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            console.log("Switched to chatBot mode successfully!");
        } else {
            console.error("Failed to switch to chatBot mode");
        }
    })
    .catch(error => {
        console.error("Error switching to chatBot mode:", error);
    });
}

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