class GriloChat {
    constructor() {
        this.conversations = [];
        this.currentConversationKey = null;
        this.isStreaming = false;
        this.eventSource = null;

        this.initElements();
        this.bindEvents();
        this.loadConversations();
    }

    initElements() {
        this.conversationList = document.getElementById('conversationList');
        this.messagesContainer = document.getElementById('messagesContainer');
        this.messageInput = document.getElementById('messageInput');
        this.sendBtn = document.getElementById('sendBtn');
        this.newChatBtn = document.getElementById('newChatBtn');
        this.chatHeader = document.getElementById('chatHeader');
        this.epistemicBar = document.getElementById('epistemicBar');
        this.claimsCount = document.getElementById('claimsCount');
        this.gapsCount = document.getElementById('gapsCount');
        this.newChatModal = document.getElementById('newChatModal');
        this.cancelNewChat = document.getElementById('cancelNewChat');
        this.confirmNewChat = document.getElementById('confirmNewChat');
        this.conversationTitle = document.getElementById('conversationTitle');
    }

    bindEvents() {
        this.sendBtn.addEventListener('click', () => this.sendMessage());
        this.messageInput.addEventListener('keydown', (e) => this.handleKeyDown(e));
        this.messageInput.addEventListener('input', () => this.autoResize());
        this.newChatBtn.addEventListener('click', () => this.showNewChatModal());
        this.cancelNewChat.addEventListener('click', () => this.hideNewChatModal());
        this.confirmNewChat.addEventListener('click', () => this.createNewConversation());
    }

    async loadConversations() {
        try {
            const response = await fetch('/api/v1/chat/conversations');
            const data = await response.json();
            this.conversations = data.conversations || [];
            this.renderConversationList();
        } catch (error) {
            console.error('Failed to load conversations:', error);
            this.conversationList.innerHTML = '<div class="error">Failed to load conversations</div>';
        }
    }

    renderConversationList() {
        if (this.conversations.length === 0) {
            this.conversationList.innerHTML = '<div class="empty-state">No conversations yet</div>';
            return;
        }

        const html = this.conversations.map(conv => `
            <div class="conversation-item ${conv.conversation_key === this.currentConversationKey ? 'active' : ''}"
                 data-key="${conv.conversation_key}">
                <div class="conversation-title">${this.escapeHtml(conv.title)}</div>
                <div class="conversation-meta">
                    <span>${conv.message_count || 0} messages</span>
                    <span>${this.formatDate(conv.last_message_at)}</span>
                </div>
                <div class="conversation-stats">
                    <span class="stat-claims">⚠️ ${conv.claims_count || 0}</span>
                    <span class="stat-gaps">❓ ${conv.gaps_count || 0}</span>
                </div>
            </div>
        `).join('');

        this.conversationList.innerHTML = html;

        this.conversationList.querySelectorAll('.conversation-item').forEach(item => {
            item.addEventListener('click', () => {
                const key = item.dataset.key;
                this.loadConversation(key);
            });
        });
    }

    async loadConversation(conversationKey) {
        try {
            const response = await fetch(`/api/v1/chat/conversations/${conversationKey}`);
            const data = await response.json();

            this.currentConversationKey = conversationKey;
            this.renderMessages(data.messages);

            const conv = data.conversation;
            this.chatHeader.querySelector('.chat-title').textContent = conv.title;
            this.chatHeader.querySelector('.chat-model').textContent = `Model: ${conv.model_used || 'default'}`;

            this.updateEpistemicStats(conv.claims_count || 0, conv.gaps_count || 0);
            this.renderConversationList();
        } catch (error) {
            console.error('Failed to load conversation:', error);
            this.showError('Failed to load conversation');
        }
    }

    renderMessages(messages) {
        if (messages.length === 0) {
            this.messagesContainer.innerHTML = `
                <div class="welcome-message">
                    <div class="welcome-icon">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                            <path stroke-linecap="round" stroke-linejoin="round" d="M8.625 12a.375.375 0 11-.75 0 .375.375 0 01.75 0zm0 0H8.25m4.125 0a.375.375 0 11-.75 0 .375.375 0 01.75 0zm0 0H12m4.125 0a.375.375 0 11-.75 0 .375.375 0 01.75 0zm0 0h-.375M21 12c0 4.556-4.03 8.25-9 8.25a9.764 9.764 0 01-2.555-.337A5.972 5.972 0 015.41 20.97a5.969 5.969 0 01-.474-.065 4.48 4.48 0 00.978-2.025c.09-.457-.133-.901-.467-1.226C3.93 16.178 3 14.189 3 12c0-4.556 4.03-8.25 9-8.25s9 3.694 9 8.25z" />
                        </svg>
                    </div>
                    <h2>Start a conversation</h2>
                    <p>Send a message to begin chatting with epistemic governance.</p>
                </div>
            `;
            return;
        }

        let html = '';
        for (const msg of messages) {
            html += this.renderMessage(msg);
        }
        this.messagesContainer.innerHTML = html;
        this.scrollToBottom();
    }

    renderMessage(msg) {
        const isUser = msg.role === 'user';
        const claims = msg.claims_detected || [];
        const gaps = msg.gaps_identified || [];

        let epistemicHtml = '';
        if (claims.length > 0 || gaps.length > 0) {
            epistemicHtml = `
                <div class="message-epistemic">
                    ${claims.length > 0 ? `<span class="epistemic-badge claim-badge" title="${claims.length} claims detected">🔵 UNVERIFIED (${claims.length})</span>` : ''}
                    ${gaps.length > 0 ? `<span class="epistemic-badge gap-badge" title="${gaps.length} gaps identified">❓ Gap (${gaps.length})</span>` : ''}
                </div>
            `;
        }

        return `
            <div class="message ${isUser ? 'user-message' : 'assistant-message'}">
                <div class="message-avatar">
                    ${isUser ? '👤' : '🤖'}
                </div>
                <div class="message-content">
                    <div class="message-bubble">
                        ${this.escapeHtml(msg.content)}
                    </div>
                    ${epistemicHtml}
                    <div class="message-meta">
                        ${msg.model ? `<span class="model-name">${msg.model}</span>` : ''}
                        ${msg.inference_time_ms ? `<span class="inference-time">${msg.inference_time_ms}ms</span>` : ''}
                    </div>
                </div>
            </div>
        `;
    }

    async sendMessage() {
        if (this.isStreaming) return;

        const content = this.messageInput.value.trim();
        if (!content) return;

        let conversationKey = this.currentConversationKey;

        if (!conversationKey) {
            const conv = await this.createConversation('New Conversation');
            conversationKey = conv.conversation_key;
        }

        this.appendUserMessage(content);
        this.messageInput.value = '';
        this.autoResize();

        await this.streamResponse(conversationKey, content);
    }

    async streamResponse(conversationKey, content) {
        this.isStreaming = true;
        this.updateSendButton();

        const assistantMsgEl = this.createAssistantMessage();
        let responseContent = '';
        let detectedClaims = [];
        let detectedGaps = [];

        try {
            const response = await fetch('/api/v1/chat/message', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    conversation_key: conversationKey,
                    message: content,
                }),
            });

            const reader = response.body.getReader();
            const decoder = new TextDecoder();

            while (true) {
                const { done, value } = await reader.read();
                if (done) break;

                const chunk = decoder.decode(value);
                const lines = chunk.split('\n');

                for (const line of lines) {
                    if (line.startsWith('event: ')) {
                        const eventType = line.slice(7).trim();
                        continue;
                    }
                    if (line.startsWith('data: ')) {
                        const data = line.slice(6);
                        try {
                            const eventData = JSON.parse(data);
                            await this.handleStreamEvent(eventType || 'chunk', eventData, assistantMsgEl);
                        } catch (e) {
                            // ignore parse errors
                        }
                    }
                }
            }
        } catch (error) {
            console.error('Stream error:', error);
            assistantMsgEl.querySelector('.message-bubble').textContent = 'Error: Failed to get response';
        }

        this.isStreaming = false;
        this.updateSendButton();
        this.loadConversations();
    }

    async handleStreamEvent(type, data, assistantMsgEl) {
        const bubble = assistantMsgEl.querySelector('.message-bubble');

        if (type === 'chunk' && data.content) {
            bubble.textContent += data.content;
            this.scrollToBottom();
        } else if (type === 'claim') {
            this.incrementClaims();
        } else if (type === 'gap') {
            this.incrementGaps();
        } else if (type === 'done') {
            this.updateConversationStats(data);
        }
    }

    createAssistantMessage() {
        const html = `
            <div class="message assistant-message streaming">
                <div class="message-avatar">🤖</div>
                <div class="message-content">
                    <div class="message-bubble"></div>
                    <div class="message-meta">
                        <span class="streaming-indicator">Thinking...</span>
                    </div>
                </div>
            </div>
        `;

        this.messagesContainer.insertAdjacentHTML('beforeend', html);
        this.scrollToBottom();

        return this.messagesContainer.lastElementChild;
    }

    appendUserMessage(content) {
        const html = `
            <div class="message user-message">
                <div class="message-avatar">👤</div>
                <div class="message-content">
                    <div class="message-bubble">${this.escapeHtml(content)}</div>
                </div>
            </div>
        `;
        this.messagesContainer.insertAdjacentHTML('beforeend', html);
        this.scrollToBottom();
    }

    async createConversation(title = 'New Conversation') {
        try {
            const response = await fetch('/api/v1/chat/conversations', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ title }),
            });
            const conv = await response.json();
            this.currentConversationKey = conv.conversation_key;
            this.chatHeader.querySelector('.chat-title').textContent = conv.title;
            await this.loadConversations();
            return conv;
        } catch (error) {
            console.error('Failed to create conversation:', error);
            throw error;
        }
    }

    showNewChatModal() {
        this.newChatModal.classList.add('active');
        this.conversationTitle.value = '';
        this.conversationTitle.focus();
    }

    hideNewChatModal() {
        this.newChatModal.classList.remove('active');
    }

    async createNewConversation() {
        const title = this.conversationTitle.value.trim() || 'New Conversation';
        this.hideNewChatModal();

        const conv = await this.createConversation(title);
        this.messagesContainer.innerHTML = `
            <div class="welcome-message">
                <div class="welcome-icon">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                        <path stroke-linecap="round" stroke-linejoin="round" d="M8.625 12a.375.375 0 11-.75 0 .375.375 0 01.75 0zm0 0H8.25m4.125 0a.375.375 0 11-.75 0 .375.375 0 01.75 0zm0 0H12m4.125 0a.375.375 0 11-.75 0 .375.375 0 01.75 0zm0 0h-.375M21 12c0 4.556-4.03 8.25-9 8.25a9.764 9.764 0 01-2.555-.337A5.972 5.972 0 015.41 20.97a5.969 5.969 0 01-.474-.065 4.48 4.48 0 00.978-2.025c.09-.457-.133-.901-.467-1.226C3.93 16.178 3 14.189 3 12c0-4.556 4.03-8.25 9-8.25s9 3.694 9 8.25z" />
                    </svg>
                </div>
                <h2>Start a conversation</h2>
                <p>Send a message to begin chatting with epistemic governance.</p>
            </div>
        `;
    }

    handleKeyDown(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            this.sendMessage();
        }
    }

    autoResize() {
        this.messageInput.style.height = 'auto';
        this.messageInput.style.height = Math.min(this.messageInput.scrollHeight, 200) + 'px';
    }

    updateSendButton() {
        if (this.isStreaming) {
            this.sendBtn.classList.add('streaming');
            this.sendBtn.innerHTML = '<span class="spinner"></span>';
        } else {
            this.sendBtn.classList.remove('streaming');
            this.sendBtn.innerHTML = `
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M22 2L11 13M22 2l-7 20-4-9-9-4 20-7z"/>
                </svg>
            `;
        }
    }

    incrementClaims() {
        const current = parseInt(this.claimsCount.textContent) || 0;
        this.claimsCount.textContent = current + 1;
    }

    incrementGaps() {
        const current = parseInt(this.gapsCount.textContent) || 0;
        this.gapsCount.textContent = current + 1;
    }

    updateEpistemicStats(claims, gaps) {
        this.claimsCount.textContent = claims;
        this.gapsCount.textContent = gaps;
    }

    updateConversationStats(data) {
        if (data.claims_count) {
            this.claimsCount.textContent = parseInt(this.claimsCount.textContent) + data.claims_count;
        }
        if (data.gaps_count) {
            this.gapsCount.textContent = parseInt(this.gapsCount.textContent) + data.gaps_count;
        }
    }

    scrollToBottom() {
        this.messagesContainer.scrollTop = this.messagesContainer.scrollHeight;
    }

    showError(message) {
        const html = `<div class="error-message">${this.escapeHtml(message)}</div>`;
        this.messagesContainer.insertAdjacentHTML('beforeend', html);
        this.scrollToBottom();
    }

    formatDate(dateStr) {
        if (!dateStr) return '';
        const date = new Date(dateStr);
        const now = new Date();
        const diff = now - date;

        if (diff < 60000) return 'Just now';
        if (diff < 3600000) return `${Math.floor(diff / 60000)}m ago`;
        if (diff < 86400000) return `${Math.floor(diff / 3600000)}h ago`;

        return date.toLocaleDateString();
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

document.addEventListener('DOMContentLoaded', () => {
    window.griloChat = new GriloChat();
});