const backendHost = "http://47.108.135.173";
const backendPort = "18777";
const loginUrl = `${backendHost}:${backendPort}/api/orag/search/login`;
const createUserUrl = `${backendHost}:${backendPort}/api/orag/add/user`;

// Function to display messages
function displayMessage(message, type) {
    const messageContainer = document.getElementById("errorMessage");
    messageContainer.textContent = message;
    messageContainer.className = type; // Apply class based on message type (error/success)
    messageContainer.style.display = "block"; // Ensure the message container is visible
}

document.getElementById("login-form").addEventListener("submit", function (event) {
    event.preventDefault(); // Prevent the default form submission
    const user_name = document.getElementById("user_name").value;

    if (user_name) {
        fetch(loginUrl, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ user_name: user_name })
        })
        .then(response => response.json())
        .then(data => {
            if (data.status) {
                // Login successful, store userid and redirect to database page
                // localStorage.setItem("user_id", data.user_id); // Store userid
                setCookie('user_id', data.user_id, 7)
                localStorage.setItem('user_name', user_name)
                localStorage.setItem('api-key', data.api_key);
                localStorage.setItem('base-url', data.base_url);
                // localStorage.setItem('model-select', data.model);
                window.location.href = "chat"; // Redirect to database page
            } else {
                // Login failed, ask if user wants to create a new username
                const createUser = confirm("Invalid username! Would you like to create a new username?");
                if (createUser) {
                        // Call API to create a new user
                        fetch(createUserUrl, {
                            method: "POST",
                            headers: {
                                "Content-Type": "application/json"
                            },
                            body: JSON.stringify({ user_name: user_name })
                        })
                        .then(response => response.json())
                        .then(createResponse => {
                            if (createResponse.code===200) {
                                // New user created successfully, redirect to database page
                                setCookie('user_id', createResponse.user_id, 7); // Store userid
                                window.location.href = "chat"; // Redirect to database page
                            } else {}
                        })
                        .catch(error => {
                            console.error('Error during user creation:', error);
                            displayMessage("An error occurred while creating the user. Please try again.", "error");
                        });
                } else {
                        // User chose not to create a new username
                        displayMessage("Please re-enter your username.", "error");
                }
            }
        })
        .catch(error => {
            console.error('Error during login:', error);
            displayMessage("An error occurred during login. Please try again.", "error");
        });
    } else {
        displayMessage("Username cannot be empty.", "error");
    }
});

function setCookie(name, value, days) {
    const date = new Date();
    date.setTime(date.getTime() + (days * 24 * 60 * 60 * 1000)); // `days` specifies how long the cookie should be valid
    const expires = "expires=" + date.toUTCString();
    document.cookie = name + "=" + value + ";" + expires + ";path=/"; // Set cookie for the whole site
}

