const backendHost = "http://47.108.135.173";
const backendPort = "18777";
const renameUserUrl = `${backendHost}:${backendPort}/api/orag/update/user_name`; // Rename user API endpoint

const renameButton = document.getElementById("rename-button");
const logoutButton = document.getElementById("logout-button");
const confirmRenameButton = document.getElementById("confirm-rename-button");
const cancelRenameButton = document.getElementById("cancel-rename-button");
const renameContainer = document.getElementById("rename-container");
const userNameDisplay = document.getElementById("user_name");
const newUserNameInput = document.getElementById("new_username");

const storedUsername = null;

export function setupHeader() {
    // Load stored username if exists
    let storedUsername = localStorage.getItem("user_name");
    if (storedUsername) {
        userNameDisplay.textContent = storedUsername;
    }

    // Show rename input
    renameButton.addEventListener("click", function () {
        renameContainer.style.display = "flex";
    })

    logoutButton.addEventListener("click", function () {
        if (confirm("Are you sure you want to log out?")) {
        window.location.href = "/";
        }
    });

    // Cancel rename action
    cancelRenameButton.addEventListener("click", function () {
        renameContainer.style.display = "none";
    });

    // Confirm rename action
    confirmRenameButton.addEventListener("click", function () {
        const newUsername = newUserNameInput.value.trim();

        if (newUsername) {
            fetch(renameUserUrl, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({ user_name: storedUsername, new_user_name: newUsername, user_id: getCookie('user_id') })
            })
            .then(response => response.json())
            .then(data => {
                if (data.code===200) {
                    localStorage.setItem("user_name", newUsername); // Update localStorage with new username
                    storedUsername = localStorage.getItem("user_name");
                    userNameDisplay.textContent = newUsername; // Update username display
                    renameContainer.style.display = "none";
                    alert("Username updated successfully!");
                } else {
                    alert(data.message || "Failed to update username. Try a different one.");
                }
            })
            .catch(error => {
                console.error("Error during renaming:", error);
                alert("An error occurred. Please try again.");
            });
        } else {
            alert("Username cannot be empty.");
        }
    });
}

// Get cookie value by name
function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
    return null;
}

document.addEventListener("DOMContentLoaded", () => {
    setupHeader();
});
