(function() {
    'use strict';

    // Widget configuration
    let config = {
        clientId: '',
        apiKey: '',
        apiUrl: window.location.origin, // Auto-detect API URL
        theme: 'light',
        position: 'bottom-right',
        title: 'Chat with us',
        placeholder: 'Type your message...',
        welcomeMessage: 'Hello! How can I help you today?',
        primaryColor: '#007bff',
        fontSize: '14px',
        zIndex: 9999
    };

    // Widget state
    let isOpen = false;
    let isMinimized = false;
    let messageHistory = [];

    // Create widget HTML
    function createWidgetHTML() {
        const widgetHTML = `
            <div id="chatbot-widget" style="
                position: fixed;
                ${config.position.includes('bottom') ? 'bottom: 20px;' : 'top: 20px;'}
                ${config.position.includes('right') ? 'right: 20px;' : 'left: 20px;'}
                z-index: ${config.zIndex};
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                font-size: ${config.fontSize};
            ">
                <!-- Chat Button -->
                <div id="chatbot-button" style="
                    width: 60px;
                    height: 60px;
                    border-radius: 50%;
                    background: ${config.primaryColor};
                    color: white;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    cursor: pointer;
                    box-shadow: 0 4px 12px rgba(0,0,0,0.15);
                    transition: all 0.3s ease;
                    font-size: 24px;
                " onmouseover="this.style.transform='scale(1.1)'" onmouseout="this.style.transform='scale(1)'">
                    💬
                </div>

                <!-- Chat Window -->
                <div id="chatbot-window" style="
                    position: absolute;
                    ${config.position.includes('bottom') ? 'bottom: 80px;' : 'top: 80px;'}
                    ${config.position.includes('right') ? 'right: 0;' : 'left: 0;'}
                    width: 350px;
                    height: 500px;
                    background: white;
                    border-radius: 12px;
                    box-shadow: 0 8px 32px rgba(0,0,0,0.12);
                    display: none;
                    flex-direction: column;
                    overflow: hidden;
                    border: 1px solid #e0e0e0;
                ">
                    <!-- Header -->
                    <div style="
                        background: ${config.primaryColor};
                        color: white;
                        padding: 16px;
                        display: flex;
                        justify-content: space-between;
                        align-items: center;
                        font-weight: 600;
                    ">
                        <span>${config.title}</span>
                        <div style="display: flex; gap: 8px;">
                            <button id="minimize-btn" style="
                                background: none;
                                border: none;
                                color: white;
                                cursor: pointer;
                                font-size: 16px;
                                padding: 4px;
                            ">−</button>
                            <button id="close-btn" style="
                                background: none;
                                border: none;
                                color: white;
                                cursor: pointer;
                                font-size: 16px;
                                padding: 4px;
                            ">×</button>
                        </div>
                    </div>

                    <!-- Messages Container -->
                    <div id="chatbot-messages" style="
                        flex: 1;
                        padding: 16px;
                        overflow-y: auto;
                        background: #f8f9fa;
                    "></div>

                    <!-- Input Area -->
                    <div style="
                        padding: 16px;
                        border-top: 1px solid #e0e0e0;
                        background: white;
                    ">
                        <div style="
                            display: flex;
                            gap: 8px;
                            align-items: flex-end;
                        ">
                            <div style="flex: 1;">
                                <textarea id="chatbot-input" placeholder="${config.placeholder}" style="
                                    width: 100%;
                                    padding: 12px;
                                    border: 1px solid #ddd;
                                    border-radius: 8px;
                                    resize: none;
                                    font-family: inherit;
                                    font-size: inherit;
                                    outline: none;
                                    min-height: 40px;
                                    max-height: 100px;
                                " rows="1"></textarea>
                            </div>
                            <button id="send-btn" style="
                                background: ${config.primaryColor};
                                color: white;
                                border: none;
                                border-radius: 8px;
                                padding: 12px 16px;
                                cursor: pointer;
                                font-size: 16px;
                                transition: background 0.3s ease;
                            " onmouseover="this.style.background='#0056b3'" onmouseout="this.style.background='${config.primaryColor}'">
                                ➤
                            </button>
                        </div>

                    </div>
                </div>
            </div>
        `;

        document.body.insertAdjacentHTML('beforeend', widgetHTML);
    }

    // Add message to chat
    function addMessage(content, isUser = false, isLoading = false) {
        const messagesContainer = document.getElementById('chatbot-messages');
        const messageDiv = document.createElement('div');
        const timestamp = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

        messageDiv.style.cssText = `
            margin-bottom: 12px;
            display: flex;
            ${isUser ? 'justify-content: flex-end;' : 'justify-content: flex-start;'}
        `;

        const messageBubble = document.createElement('div');
        messageBubble.style.cssText = `
            max-width: 80%;
            padding: 12px 16px;
            border-radius: 18px;
            word-wrap: break-word;
            ${isUser ? `
                background: ${config.primaryColor};
                color: white;
                border-bottom-right-radius: 4px;
            ` : `
                background: white;
                color: #333;
                border: 1px solid #e0e0e0;
                border-bottom-left-radius: 4px;
            `}
        `;

        if (isLoading) {
            messageBubble.innerHTML = `
                <div style="display: flex; align-items: center; gap: 4px;">
                    <div class="typing-indicator">
                        <span></span>
                        <span></span>
                        <span></span>
                    </div>
                    <span style="font-size: 12px; opacity: 0.7;">${timestamp}</span>
                </div>
            `;
        } else {
            messageBubble.innerHTML = `
                <div>${content}</div>
                <div style="font-size: 11px; opacity: 0.7; margin-top: 4px;">${timestamp}</div>
            `;
        }

        messageDiv.appendChild(messageBubble);
        messagesContainer.appendChild(messageDiv);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;

        return messageDiv;
    }

    // Show typing indicator
    function showTypingIndicator() {
        return addMessage('', false, true);
    }

    // Remove typing indicator
    function removeTypingIndicator(indicatorElement) {
        if (indicatorElement && indicatorElement.parentNode) {
            indicatorElement.parentNode.removeChild(indicatorElement);
        }
    }

    // Send message to API
    async function sendMessage(message) {
        try {
            const response = await fetch(`${config.apiUrl}/ask`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${config.apiKey}`
                },
                body: JSON.stringify({
                    client_id: config.clientId,
                    query: message
                })
            });

            if (!response.ok) {
                if (response.status === 403) {
                    // Client account is suspended
                    return '⚠️ Your account has been suspended. Please contact support for activation.';
                } else if (response.status === 401) {
                    // Invalid API key
                    return '⚠️ Authentication failed. Please check your API key.';
                } else {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
            }

            const data = await response.json();
            return data.answer;
        } catch (error) {
            console.error('Error sending message:', error);
            return 'Sorry, I encountered an error. Please try again later.';
        }
    }



    // Handle send button click
    async function handleSend() {
        const input = document.getElementById('chatbot-input');
        const message = input.value.trim();

        if (!message) return;

        // Add user message
        addMessage(message, true);
        input.value = '';
        input.style.height = 'auto';

        // Show typing indicator
        const typingIndicator = showTypingIndicator();

        // Send to API
        const response = await sendMessage(message);

        // Remove typing indicator and add bot response
        removeTypingIndicator(typingIndicator);
        addMessage(response, false);

        // Store in history
        messageHistory.push({ user: message, bot: response });
    }



    // Initialize event listeners
    function initializeEventListeners() {
        // Toggle chat window
        document.getElementById('chatbot-button').addEventListener('click', () => {
            const window = document.getElementById('chatbot-window');
            if (isOpen) {
                window.style.display = 'none';
                isOpen = false;
            } else {
                window.style.display = 'flex';
                isOpen = true;
                // Add welcome message if first time
                if (messageHistory.length === 0) {
                    addMessage(config.welcomeMessage, false);
                }
            }
        });

        // Close button
        document.getElementById('close-btn').addEventListener('click', () => {
            document.getElementById('chatbot-window').style.display = 'none';
            isOpen = false;
        });

        // Minimize button
        document.getElementById('minimize-btn').addEventListener('click', () => {
            const messagesContainer = document.getElementById('chatbot-messages');
            const inputArea = document.querySelector('#chatbot-window > div:last-child');
            
            if (isMinimized) {
                messagesContainer.style.display = 'block';
                inputArea.style.display = 'block';
                document.getElementById('minimize-btn').textContent = '−';
                isMinimized = false;
            } else {
                messagesContainer.style.display = 'none';
                inputArea.style.display = 'none';
                document.getElementById('minimize-btn').textContent = '+';
                isMinimized = true;
            }
        });

        // Send button
        document.getElementById('send-btn').addEventListener('click', handleSend);

        // Enter key to send
        document.getElementById('chatbot-input').addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                handleSend();
            }
        });

        // Auto-resize textarea
        document.getElementById('chatbot-input').addEventListener('input', (e) => {
            e.target.style.height = 'auto';
            e.target.style.height = Math.min(e.target.scrollHeight, 100) + 'px';
        });


    }

    // Add CSS for typing indicator
    function addStyles() {
        const style = document.createElement('style');
        style.textContent = `
            .typing-indicator {
                display: flex;
                gap: 4px;
                align-items: center;
            }
            
            .typing-indicator span {
                width: 8px;
                height: 8px;
                border-radius: 50%;
                background: #999;
                animation: typing 1.4s infinite ease-in-out;
            }
            
            .typing-indicator span:nth-child(1) { animation-delay: -0.32s; }
            .typing-indicator span:nth-child(2) { animation-delay: -0.16s; }
            
            @keyframes typing {
                0%, 80%, 100% { transform: scale(0); }
                40% { transform: scale(1); }
            }
            
            #chatbot-widget * {
                box-sizing: border-box;
            }
        `;
        document.head.appendChild(style);
    }

    // Check account status
    async function checkAccountStatus() {
        try {
            const response = await fetch(`${config.apiUrl}/ask`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${config.apiKey}`
                },
                body: JSON.stringify({
                    client_id: config.clientId,
                    query: 'test'
                })
            });

            if (response.status === 403) {
                // Account is suspended
                const button = document.getElementById('chatbot-button');
                if (button) {
                    button.style.background = '#dc3545';
                    button.title = 'Account Suspended - Contact Support';
                    button.innerHTML = '⚠️';
                }
                return false;
            }
            return true;
        } catch (error) {
            console.error('Error checking account status:', error);
            return true; // Assume active if we can't check
        }
    }

    // Public API
    window.ChatBotWidget = {
        init: async function(options) {
            // Merge options with defaults
            config = { ...config, ...options };
            
            // Validate required options
            if (!config.clientId) {
                console.error('ChatBotWidget: clientId is required');
                return;
            }
            if (!config.apiKey) {
                console.error('ChatBotWidget: apiKey is required');
                return;
            }

            // Create widget
            createWidgetHTML();
            addStyles();
            initializeEventListeners();

            // Check account status
            await checkAccountStatus();

            console.log('ChatBotWidget initialized successfully');
        },

        // Method to programmatically send message
        sendMessage: function(message) {
            if (isOpen) {
                document.getElementById('chatbot-input').value = message;
                handleSend();
            }
        },

        // Method to open/close chat
        toggle: function() {
            document.getElementById('chatbot-button').click();
        },

        // Method to update configuration
        updateConfig: function(newConfig) {
            config = { ...config, ...newConfig };
        }
    };

})();
