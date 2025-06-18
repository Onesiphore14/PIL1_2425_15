let currentUserId = localStorage.getItem("user_id");
let selectedUserId = localStorage.getItem("receiver_id");
let selectedConversationId = null;

const conversationsList = document.getElementById("conversationsList");
const chatMessages = document.getElementById("chatMessages");
const chatUserName = document.getElementById("chatUserName");
const messageInput = document.getElementById("messageInput");
const sendBtn = document.getElementById("sendBtn");

if (selectedUserId) {
  openConversation(selectedUserId, null, "Conversation");
}

//  Charger les conversations
async function loadConversations() {
    const res = await fetch(http://localhost:5000/conversations/${currentUserId});
    const conversations = await res.json();
    conversationsList.innerHTML = "";
    conversations.forEach(conv => {
        const div = document.createElement("div");
        div.className = "conversation-item p-2 border-bottom";
        div.innerHTML = <strong>${conv.prenom} ${conv.nom}</strong>;
        div.onclick = () => openConversation(conv.user_id, conv.conversation_id, ${conv.prenom} ${conv.nom});
        conversationsList.appendChild(div);
    });
}

// Charger une conversation
async function openConversation(userId, conversationId, userName) {
    selectedUserId = userId;
    selectedConversationId = conversationId;
    chatUserName.textContent = userName;
    chatMessages.innerHTML = "";

    const res = await fetch(http://localhost:5000/messages/${currentUserId}/${userId});
    const messages = await res.json();
    messages.forEach(msg => {
        const msgDiv = document.createElement("div");
        msgDiv.className = "message mb-2";
        msgDiv.innerHTML = <strong>${msg.prenom} :</strong> ${msg.contenu};
        chatMessages.appendChild(msgDiv);
    });
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// ✉ Envoyer un message
sendBtn.addEventListener("click", async () => {
    const contenu = messageInput.value.trim();
    if (!contenu || !selectedUserId) return;

    const data = new URLSearchParams();
    data.append("sender_id", currentUserId);
    data.append("receiver_id", selectedUserId);
    data.append("contenu", contenu);

    await fetch("http://localhost:5000/messages/send", {
        method: "POST",
        headers: {
            "Content-Type": "application/x-www-form-urlencoded"
        },
        body: data
    });

    messageInput.value = "";
    openConversation(selectedUserId, selectedConversationId, chatUserName.textContent);
});

//  Rechercher un utilisateur (dans la modale)
document.getElementById("newConversationBtn").addEventListener("click", () => {
    const modal = new bootstrap.Modal(document.getElementById("newConversationModal"));
    modal.show();
});

document.getElementById("userSearch").addEventListener("input", async (e) => {
    const query = e.target.value;
    const res = await fetch(http://localhost:5000/users/search?query=${query});
    const users = await res.json();
    const resultsDiv = document.getElementById("userSearchResults");
    resultsDiv.innerHTML = "";

    users.forEach(user => {
        if (user.id == currentUserId) return;
        const div = document.createElement("div");
        div.className = "p-2 border-bottom user-result";
        div.textContent = ${user.prenom} ${user.nom} (${user.email});
        div.style.cursor = "pointer";
        div.onclick = () => {
            openConversation(user.id, null, ${user.prenom} ${user.nom});
            const modal = bootstrap.Modal.getInstance(document.getElementById("newConversationModal"));
            modal.hide();
        };
        resultsDiv.appendChild(div);
    });
});

//  Initialisation
loadConversations();
