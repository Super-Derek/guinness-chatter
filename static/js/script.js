document.addEventListener('DOMContentLoaded', () => {
    const themeToggleBtn = document.getElementById('theme-toggle');
    const themeIcon = document.getElementById('theme-icon');
    const currentTheme = localStorage.getItem('theme') || 'light';
    document.body.classList.toggle('dark', currentTheme === 'dark');
    themeIcon.src = currentTheme === 'dark' ? 'static/images/moon-icon.png' : 'static/images/sun-icon.png';

    themeToggleBtn.addEventListener('click', () => {
        document.body.classList.toggle('dark');
        const newTheme = document.body.classList.contains('dark') ? 'dark' : 'light';
        localStorage.setItem('theme', newTheme);
        themeIcon.src = newTheme === 'dark' ? 'static/images/moon-icon.png' : 'static/images/sun-icon.png';
    });

    appendMessage('bot', "Welcome! I'm here to help you understand Project 2025, its implications, and its connections to The Heritage Foundation and Donald Trump. Ask me anything!");
});

document.getElementById('send-btn').addEventListener('click', async () => {
    const userInput = document.getElementById('user-input').value;
    if (userInput.trim() === '') return;

    appendMessage('user', userInput);
    document.getElementById('user-input').value = '';

    // Show the spinner
    document.getElementById('spinner').style.display = 'block';

    try {
        const response = await fetch('/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ message: userInput })
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        console.log("Bot response:", data);
        appendMessage('bot', data.reply);
    } catch (error) {
        console.error("Error:", error);
        appendMessage('bot', "Sorry, there was an error processing your request.");
    } finally {
        // Hide the spinner
        document.getElementById('spinner').style.display = 'none';
    }
});

function appendMessage(sender, message) {
    const chatBox = document.getElementById('chat-box');
    const messageElement = document.createElement('div');
    messageElement.classList.add('message', sender);
    messageElement.innerHTML = message;
    chatBox.appendChild(messageElement);
    // Scroll to the end of the user's message
    if (sender === 'bot') {
        const userMessages = chatBox.getElementsByClassName('user');
        const lastUserMessage = userMessages[userMessages.length - 1];
        if (lastUserMessage) {
            const offset = 150; // Adjust this value for more or less scrolling
            chatBox.scrollTop = lastUserMessage.offsetTop - offset;
        }
    }
}
