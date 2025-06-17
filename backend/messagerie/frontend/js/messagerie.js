// messaging.js
class MessagingApp {
    constructor() {
        this.currentConversationId = null;
        this.conversations = [];
        this.messages = [];
        this.currentPage = 1;
        this.hasMoreMessages = true;
        this.isLoadingMessages = false;
        
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.loadConversations();
        
        // Connexion Socket.IO avec le token JWT
        const token = localStorage.getItem('jwt_token');
        if (token) {
            window.socketClient.connect(token);
        }
    }

    setupEventListeners() {
        // Envoi de message
        document.getElementById('sendBtn').addEventListener('click', () => {
            this.sendMessage();
        });

        document.getElementById('messageInput').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.sendMessage();
            } else {
                this.handleTyping();
            }
        });

        // Nouvelle conversation
        document.getElementById('newConversationBtn').addEventListener('click', () => {
            this.showNewConversationModal();
        });

        // Scroll infini pour les messages
        document.getElementById('chatMessages').addEventListener('scroll', (e) => {
            if (e.target.scrollTop === 0 && !this.isLoadingMessages && this.hasMoreMessages) {
                this.loadMoreMessages();
            }
        });
    }

    async loadConversations() {
        try {
            const response = await fetch('/api/messaging/conversations', {
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('jwt_token')}`
                }
            });

            if (response.ok) {
                this.conversations = await response.json();
                this.renderConversations();
            }
        } catch (error) {
            console.error('Erreur lors du chargement des conversations:', error);
        }
    }

    renderConversations() {
        const conversationsList = document.getElementById('conversationsList');
        conversationsList.innerHTML = '';

        this.conversations.forEach(conversation => {
            const conversationElement = this.createConversationElement(conversation);
            conversationsList.appendChild(conversationElement);
        });
    }

    createConversationElement(conversation) {
        const div = document.createElement('div');
        div.className = 'conversation-item';
        div.dataset.conversationId = conversation.id;
        
        const lastMessage = conversation.last_message;
        const lastMessageText = lastMessage ? lastMessage.content : 'Aucun message';
        const lastMessageTime = lastMessage ? this.formatTime(lastMessage.created_at) : '';
        
        div.innerHTML = `
            <img src="/api/users/${conversation.other_user_id}/avatar" 
                 alt="Avatar" class="conversation-avatar" 
                 onerror="this.src='/assets/default-avatar.png'">
            <div class="conversation-info">
                <div class="conversation-name" id="userName_${conversation.other_user_id}">
                    Utilisateur ${conversation.other_user_id}
                </div>
                <div class="conversation-last-message">${lastMessageText}</div>
            </div>
            <div class="conversation-meta">
                <div class="conversation-time">${lastMessageTime}</div>
                ${conversation.unread_count > 0 ? 
                    `<div class="unread-badge">${conversation.unread_count}</div>` : ''}
            </div>
        `;

                div.addEventListener('click', () => {
                    this.selectConversation(conversation.id);
                });
        
                return div;
            }
        }
        