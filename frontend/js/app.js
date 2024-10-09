// Base API URL for FastAPI backend
const API_BASE_URL = "http://localhost:8001";
const TOKEN_STORAGE_KEY = "auth_token";

// Utility Functions to Handle Authentication Token
function setAuthToken(token) {
    localStorage.setItem(TOKEN_STORAGE_KEY, token);
}

function getAuthToken() {
    return localStorage.getItem(TOKEN_STORAGE_KEY);
}

function removeAuthToken() {
    localStorage.removeItem(TOKEN_STORAGE_KEY);
}

// Generic function to make API requests with authentication
async function apiRequest(url, method = "GET", body = null, requiresAuth = false) {
    const headers = {
        "Content-Type": "application/json",
    };

    // Attach token if request requires authentication
    if (requiresAuth) {
        const token = getAuthToken();
        if (!token) {
            throw new Error("Authentication required");
        }
        headers["Authorization"] = `Bearer ${token}`;
    }

    const response = await fetch(`${API_BASE_URL}${url}`, {
        method,
        headers,
        body: body ? JSON.stringify(body) : null,
    });

    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || "API request failed");
    }

    return response.json();
}

// Handle user login
async function login(username, password) {
    try {
        const response = await apiRequest("/auth/login", "POST", {
            username,
            password,
        });

        setAuthToken(response.access_token); // Save JWT token
        alert("Login successful!");
        loadDashboard();
    } catch (error) {
        alert("Login failed: " + error.message);
    }
}

// Handle user logout
function logout() {
    removeAuthToken();
    alert("Logged out successfully!");
    loadLoginPage();
}

// Handle user signup
async function signup(username, password, role) {
    try {
        await apiRequest("/auth/signup", "POST", { username, password, role });
        alert("Signup successful! You can now login.");
        loadLoginPage();
    } catch (error) {
        alert("Signup failed: " + error.message);
    }
}

// Check if user is authenticated
function isAuthenticated() {
    return !!getAuthToken();
}

// Load dashboard for authenticated users
function loadDashboard() {
    if (isAuthenticated()) {
        document.getElementById("login-form").style.display = "none";
        document.getElementById("dashboard").style.display = "block";
        fetchBooks();
        fetchMembers();
    } else {
        loadLoginPage();
    }
}

// Load login page for unauthenticated users
function loadLoginPage() {
    document.getElementById("login-form").style.display = "block";
    document.getElementById("dashboard").style.display = "none";
}

// Initialize dashboard or login page on page load
window.onload = loadDashboard;

// CRUD Operations for Books
// Fetch all books and display them
async function fetchBooks() {
    try {
        const books = await apiRequest("/books", "GET", null, true);
        const booksContainer = document.getElementById("books-container");
        booksContainer.innerHTML = ""; // Clear existing books

        books.forEach((book) => {
            const bookElement = document.createElement("div");
            bookElement.className = "book-item";
            bookElement.innerHTML = `
                <p><strong>Title:</strong> ${book.title}</p>
                <p><strong>Author:</strong> ${book.author}</p>
                <p><strong>Status:</strong> ${book.status}</p>
                <button onclick="deleteBook(${book.id})">Delete</button>
                <button onclick="editBook(${book.id})">Edit</button>
            `;
            booksContainer.appendChild(bookElement);
        });
    } catch (error) {
        alert("Failed to load books: " + error.message);
    }
}

// Add a new book
async function addBook(title, author) {
    try {
        await apiRequest("/books", "POST", { title, author }, true);
        alert("Book added successfully!");
        fetchBooks();
    } catch (error) {
        alert("Failed to add book: " + error.message);
    }
}

// Edit an existing book
async function editBook(bookId) {
    const newTitle = prompt("Enter new title:");
    const newAuthor = prompt("Enter new author:");
    const newStatus = prompt("Enter new status (AVAILABLE or BORROWED):");

    try {
        await apiRequest(`/books/${bookId}`, "PUT", { title: newTitle, author: newAuthor, status: newStatus }, true);
        alert("Book updated successfully!");
        fetchBooks();
    } catch (error) {
        alert("Failed to update book: " + error.message);
    }
}

// Delete a book
async function deleteBook(bookId) {
    try {
        await apiRequest(`/books/${bookId}`, "DELETE", null, true);
        alert("Book deleted successfully!");
        fetchBooks();
    } catch (error) {
        alert("Failed to delete book: " + error.message);
    }
}

// CRUD Operations for Members (Librarians Only)
// Fetch all members
async function fetchMembers() {
    try {
        const members = await apiRequest("/members", "GET", null, true);
        const membersContainer = document.getElementById("members-container");
        membersContainer.innerHTML = ""; // Clear existing members

        members.forEach((member) => {
            const memberElement = document.createElement("div");
            memberElement.className = "member-item";
            memberElement.innerHTML = `
                <p><strong>Username:</strong> ${member.username}</p>
                <p><strong>Role:</strong> ${member.role}</p>
                <button onclick="deleteMember(${member.id})">Delete</button>
                <button onclick="editMember(${member.id})">Edit</button>
            `;
            membersContainer.appendChild(memberElement);
        });
    } catch (error) {
        alert("Failed to load members: " + error.message);
    }
}

// Add a new member (Librarian can do this)
async function addMember(username, password, role) {
    try {
        await apiRequest("/members", "POST", { username, password, role }, true);
        alert("Member added successfully!");
        fetchMembers();
    } catch (error) {
        alert("Failed to add member: " + error.message);
    }
}

// Edit an existing member (Librarian only)
async function editMember(memberId) {
    const newUsername = prompt("Enter new username:");
    const newPassword = prompt("Enter new password:");

    try {
        await apiRequest(`/members/${memberId}`, "PUT", { username: newUsername, password: newPassword }, true);
        alert("Member updated successfully!");
        fetchMembers();
    } catch (error) {
        alert("Failed to update member: " + error.message);
    }
}

// Delete a member (Librarian only)
async function deleteMember(memberId) {
    try {
        await apiRequest(`/members/${memberId}`, "DELETE", null, true);
        alert("Member deleted successfully!");
        fetchMembers();
    } catch (error) {
        alert("Failed to delete member: " + error.message);
    }
}
