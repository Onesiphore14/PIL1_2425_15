class SocketClient {
    constructor() {
        this.socket = null;
        this.isConnected = false;
        this.currentConversationId = null;
        this.typingTimer = null;
        this.isTyping = false;
    }

    connect(token) {
        this.socket = io('http://localhost:5000', {
            auth: {
                token: token
            }
        });

        this.socket.on('connect', () => {
            this.isConnected = true;
            console.log('Connecté au serveur');
        });

        this.socket.on('disconnect', () => {
            this.isConnected = false;
            console.log('Déconnecté du serveur');
        });

        this.socket.on('new_message', (data) => {
            this.handleNewMessage(data);
        });

        this.socket.on('user_typing', (data) => {
            this.handleUserTyping(data);
        });

        this.socket.on('user_stop_typing', (data) => {
            this.handleUserStopTyping(data);
        });
    }

    joinConversation(conversationId) {
        if (this.currentConversationId) {
            this.leaveConversation(this.currentConversationId);
        }
        
        this.currentConversationId = conversationId;
        this.socket.emit('join_conversation', { conversation_id: conversationId });
    }

    leaveConversation(conversationId) {
        this.socket.emit('leave_conversation', { conversation_id: conversationId });
        this.currentConversationId = null;
    }

    startTyping() {
        if (!this.isTyping && this.currentConversationId) {
            this.isTyping = true;
            this.socket.emit('typing', { conversation_id: this.currentConversationId });
        }
    }

    stopTyping() {
        if (this.isTyping && this.currentConversationId) {
            this.isTyping = false;
            this.socket.emit('stop_typing', { conversation_id: this.currentConversationId });
        }
    }

    handleNewMessage(data) {
        if (window.messagingApp) {
            window.messagingApp.handleNewMessage(data);
        }
    }

    handleUserTyping(data) {
        if (window.messagingApp) {
            window.messagingApp.showTypingIndicator(data.user_id);
        }
    }

    handleUserStopTyping(data) {
        if (window.messagingApp) {
            window.messagingApp.hideTypingIndicator(data.user_id);
        }
    }
}

// Instance globale
window.socketClient = new SocketClient();
JavaScript - Ap