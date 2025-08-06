# SemantoAssistant
You're focusing on keeping your existing Lovable design, which is a smart approach\! The prompt should guide Lovable to integrate its UI with your FastAPI backend's API, rather than redesigning the chat interface from scratch.

Here's a prompt designed for that purpose, with a strong emphasis on backend integration and instructions for how Lovable should handle the data flow, given your existing UI design:

-----

## Lovable Prompt: Integrate Chat UI with FastAPI Backend (Excluding Design)

````
# Context

You are a world-class Lovable AI coding assistant specializing in integrating web frontends with existing backend APIs. My goal is to connect an existing chat interface (whose design is already in place) to a new FastAPI backend.

# Task

Focus solely on the JavaScript and HTML/CSS structure needed to integrate the *existing* chat UI elements with the provided FastAPI backend API. Do NOT generate new design elements or styling; assume the visual design is handled externally.

# Existing UI Elements (Assume these HTML elements already exist and are styled)

- A main container for messages: `<div id="chat-messages"></div>`
- A text input field for user messages: `<input type="text" id="chat-input" placeholder="Type your message...">`
- A send button: `<button id="send-button">Send</button>`
- (Optional, if you have one): A header like `<h1 id="chat-header">Semanto's AI Assistant</h1>`

# Backend Integration (Crucial)

The frontend needs to make **POST** requests to an external FastAPI backend API.

- **API Endpoint (Deployed):** `https://semantoassistant.onrender.com/ask`
- **Request Body (JSON):**
    ```json
    {
        "session_id": "string", // A unique ID for the current chat session
        "question": "string"    // The user's message
    }
    ```
- **Response Body (JSON):**
    ```json
    {
        "answer": "string" // The assistant's generated answer
    }
    ```
- **JavaScript `fetch` API:** Use `fetch` for all API calls.
- **Session Management:**
    - Generate a `session_id` when the application *first loads* (e.g., using `localStorage` to persist it across browser refreshes for a user, or `Date.now()`).
    - Reuse this `session_id` for **all** subsequent requests within the same chat session.
- **Loading State:**
    - When a user sends a message, immediately add their message to the `chat-messages` container.
    - Immediately after, add a "Thinking..." message (or similar loading indicator text) for the assistant into the `chat-messages` container. Give this loading message a temporary ID (e.g., `loading-message`) so it can be updated.
    - Once the API response is received, replace the "Thinking..." message with the actual `answer` from the backend response.
- **Error Handling:** If the `fetch` call fails (network error, server error, etc.), replace the "Thinking..." message with a user-friendly error like: "Sorry, I'm having trouble connecting to the assistant. Please try again."

# Specific Frontend Actions:

1.  **On Load:**
    * Retrieve or generate a unique `session_id`.
    * Display an initial welcome message from the assistant in the `chat-messages` container: "Hi! I'm Semanto's AI Assistant. How can I help you today?"

2.  **On Send Button Click:**
    * Get text from `#chat-input`.
    * Clear the `#chat-input` field.
    * Append user's message to `#chat-messages`.
    * Append "Thinking..." message to `#chat-messages` (with a unique ID for later update).
    * Scroll `#chat-messages` to the bottom.
    * Call the backend API (`https://semantoassistant.onrender.com/ask`) with the `session_id` and user's `question`.
    * Process the backend `answer` and update the "Thinking..." message.
    * Scroll `#chat-messages` to the bottom again.

# Output Format

Provide the JavaScript code (and any minimal necessary HTML/CSS if essential for hooks) to implement this backend integration.

---
This video provides a practical example of connecting a Python backend to a JavaScript frontend, covering the core HTTP communication concepts relevant to your project: [Python + JavaScript - Full Stack App Tutorial](https://m.youtube.com/watch?v=PppslXOR7TA&pp=0gcJCfwAo7VqN5tD).
````
