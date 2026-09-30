// State
let sessionId = generateSessionId();
let isProcessing = false;

// DOM Elements
const els = {};

document.addEventListener('DOMContentLoaded', init);

function init() {
    // Cache elements
    els.sidebar = document.getElementById('sidebar');
    els.sidebarToggle = document.getElementById('sidebarToggle');
    els.sidebarClose = document.getElementById('sidebarClose');
    
    els.uploadDropzone = document.getElementById('uploadDropzone');
    els.fileInput = document.getElementById('fileInput');
    els.uploadProgress = document.getElementById('uploadProgress');
    els.progressFill = document.getElementById('progressFill');
    els.progressText = document.getElementById('progressText');
    
    els.documentsList = document.getElementById('documentsList');
    els.newChatBtn = document.getElementById('newChatBtn');
    
    els.chatMessages = document.getElementById('chatMessages');
    els.welcomeMessage = document.getElementById('welcomeMessage');
    els.chatInput = document.getElementById('chatInput');
    els.sendBtn = document.getElementById('sendBtn');
    
    els.statusIndicator = document.getElementById('statusIndicator');
    els.statusText = els.statusIndicator.querySelector('.status-text');
    
    // Event Listeners
    setupSidebar();
    setupUpload();
    setupChat();
    
    // Initial loads
    loadDocuments();
}

function setupSidebar() {
    els.sidebarToggle.addEventListener('click', () => {
        els.sidebar.classList.add('open');
    });
    els.sidebarClose.addEventListener('click', () => {
        els.sidebar.classList.remove('open');
    });
}

// === Upload Functions ===
function setupUpload() {
    els.uploadDropzone.addEventListener('click', () => els.fileInput.click());
    
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        els.uploadDropzone.addEventListener(eventName, preventDefaults, false);
    });
    
    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }
    
    ['dragenter', 'dragover'].forEach(eventName => {
        els.uploadDropzone.addEventListener(eventName, () => {
            els.uploadDropzone.classList.add('drag-over');
        });
    });
    
    ['dragleave', 'drop'].forEach(eventName => {
        els.uploadDropzone.addEventListener(eventName, () => {
            els.uploadDropzone.classList.remove('drag-over');
        });
    });
    
    els.uploadDropzone.addEventListener('drop', (e) => {
        const dt = e.dataTransfer;
        const files = dt.files;
        if (files.length > 0) handleFile(files[0]);
    });
    
    els.fileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) handleFile(e.target.files[0]);
    });
}

function handleFile(file) {
    if (file.type !== 'application/pdf') {
        showToast('Please upload a valid PDF file.', 'error');
        return;
    }
    uploadFile(file);
}

async function uploadFile(file) {
    els.uploadDropzone.style.display = 'none';
    els.uploadProgress.style.display = 'block';
    els.progressFill.style.width = '30%';
    els.progressText.textContent = `Uploading ${file.name}...`;
    
    const formData = new FormData();
    formData.append('file', file);
    
    try {
        const res = await fetch('/upload', {
            method: 'POST',
            body: formData
        });
        
        els.progressFill.style.width = '70%';
        els.progressText.textContent = 'Processing PDF...';
        
        const data = await res.json();
        
        if (res.ok) {
            els.progressFill.style.width = '100%';
            showToast(`Successfully uploaded ${data.filename}`, 'success');
            setTimeout(() => {
                resetUploadUI();
                loadDocuments();
            }, 1000);
        } else {
            throw new Error(data.detail || 'Upload failed');
        }
    } catch (err) {
        showToast(err.message, 'error');
        resetUploadUI();
    }
}

function resetUploadUI() {
    els.uploadDropzone.style.display = 'block';
    els.uploadProgress.style.display = 'none';
    els.progressFill.style.width = '0%';
    els.fileInput.value = '';
}

// === Document Management ===
async function loadDocuments() {
    try {
        const res = await fetch('/documents');
        const docs = await res.json();
        renderDocumentList(docs);
    } catch (err) {
        console.error('Failed to load documents', err);
    }
}

function renderDocumentList(docs) {
    els.documentsList.innerHTML = '';
    
    if (docs.length === 0) {
        els.documentsList.innerHTML = '<p class="no-docs">No documents uploaded yet</p>';
        return;
    }
    
    docs.forEach(doc => {
        const div = document.createElement('div');
        div.className = 'doc-item';
        div.innerHTML = `
            <div class="doc-info">
                <span class="doc-name" title="${doc.filename}">${doc.filename}</span>
                <span class="doc-meta">${doc.total_pages} pages</span>
            </div>
            <button class="doc-delete" data-id="${doc.id}" title="Delete document">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <polyline points="3 6 5 6 21 6"></polyline>
                    <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
                </svg>
            </button>
        `;
        
        div.querySelector('.doc-delete').addEventListener('click', () => deleteDocument(doc.id, doc.filename));
        els.documentsList.appendChild(div);
    });
}

async function deleteDocument(docId, docName) {
    if (!confirm(`Are you sure you want to delete ${docName}?`)) return;
    
    try {
        const res = await fetch(`/documents/${docId}`, { method: 'DELETE' });
        if (res.ok) {
            showToast('Document deleted', 'success');
            loadDocuments();
        } else {
            const data = await res.json();
            throw new Error(data.detail || 'Delete failed');
        }
    } catch (err) {
        showToast(err.message, 'error');
    }
}

// === Chat Functions ===
function setupChat() {
    els.chatInput.addEventListener('input', function() {
        this.style.height = 'auto';
        this.style.height = (this.scrollHeight) + 'px';
        if (this.value.trim() === '') {
            this.style.height = 'auto';
        }
    });
    
    els.chatInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });
    
    els.sendBtn.addEventListener('click', sendMessage);
    els.newChatBtn.addEventListener('click', newConversation);
    
    // Suggestion clicks
    document.querySelectorAll('.suggestion').forEach(btn => {
        btn.addEventListener('click', () => {
            els.chatInput.value = btn.textContent;
            sendMessage();
        });
    });
}

async function sendMessage() {
    if (isProcessing) return;
    
    const text = els.chatInput.value.trim();
    if (!text) return;
    
    els.chatInput.value = '';
    els.chatInput.style.height = 'auto';
    
    if (els.welcomeMessage) els.welcomeMessage.style.display = 'none';
    
    addUserMessage(text);
    showTypingIndicator();
    isProcessing = true;
    updateStatus('Processing', true);
    
    try {
        const res = await fetch('/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ session_id: sessionId, message: text })
        });
        
        removeTypingIndicator();
        const data = await res.json();
        
        if (res.ok) {
            addAssistantMessage(data.answer, data.sources);
        } else {
            throw new Error(data.detail || 'Chat error');
        }
    } catch (err) {
        removeTypingIndicator();
        showToast(err.message, 'error');
    } finally {
        isProcessing = false;
        updateStatus('Ready', false);
    }
}

function updateStatus(text, processing) {
    els.statusText.textContent = text;
    if (processing) {
        els.statusIndicator.classList.add('processing');
        els.sendBtn.disabled = true;
    } else {
        els.statusIndicator.classList.remove('processing');
        els.sendBtn.disabled = false;
    }
}

function addUserMessage(text) {
    const div = document.createElement('div');
    div.className = 'message user';
    div.innerHTML = `<div class="message-content">${escapeHTML(text)}</div>`;
    els.chatMessages.appendChild(div);
    scrollToBottom();
}

function addAssistantMessage(answer, sources) {
    const div = document.createElement('div');
    div.className = 'message assistant';
    
    let html = `<div class="message-content">${formatMarkdown(answer)}</div>`;
    
    if (sources && sources.length > 0) {
        html += renderSources(sources);
    }
    
    div.innerHTML = html;
    els.chatMessages.appendChild(div);
    
    // Attach source toggle listeners
    if (sources && sources.length > 0) {
        const toggle = div.querySelector('.sources-toggle');
        const list = div.querySelector('.sources-list');
        toggle.addEventListener('click', () => {
            toggle.classList.toggle('open');
            list.classList.toggle('open');
        });
        
        div.querySelectorAll('.source-text').forEach(el => {
            el.addEventListener('click', function() {
                this.classList.toggle('expanded');
            });
        });
    }
    
    scrollToBottom();
}

function renderSources(sources) {
    let listHtml = sources.map((s, i) => `
        <div class="source-item">
            <div class="source-meta">
                <span class="source-badge">${escapeHTML(s.filename)}</span>
                <span class="source-badge">Pg ${s.page_number}</span>
            </div>
            <div class="source-text" title="Click to expand/collapse">${escapeHTML(s.text)}</div>
        </div>
    `).join('');
    
    return `
        <div class="sources-container">
            <div class="sources-toggle">
                <span>Sources (${sources.length})</span>
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <polyline points="6 9 12 15 18 9"></polyline>
                </svg>
            </div>
            <div class="sources-list">${listHtml}</div>
        </div>
    `;
}

function showTypingIndicator() {
    const div = document.createElement('div');
    div.className = 'typing-indicator';
    div.id = 'typingIndicator';
    div.innerHTML = `
        <div class="typing-dot"></div>
        <div class="typing-dot"></div>
        <div class="typing-dot"></div>
    `;
    els.chatMessages.appendChild(div);
    scrollToBottom();
}

function removeTypingIndicator() {
    const el = document.getElementById('typingIndicator');
    if (el) el.remove();
}

async function newConversation() {
    try {
        await fetch(`/chat/clear?session_id=${sessionId}`, { method: 'POST' });
    } catch (e) {
        // ignore
    }
    
    sessionId = generateSessionId();
    els.chatMessages.innerHTML = '';
    els.chatMessages.appendChild(els.welcomeMessage);
    els.welcomeMessage.style.display = 'flex';
    showToast('Started new conversation', 'info');
}

// === Utility ===
function generateSessionId() {
    return 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
}

function showToast(message, type = 'success') {
    const container = document.getElementById('toastContainer');
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.textContent = message;
    
    container.appendChild(toast);
    
    setTimeout(() => {
        toast.classList.add('fade-out');
        setTimeout(() => toast.remove(), 300);
    }, 4000);
}

function scrollToBottom() {
    els.chatMessages.scrollTo({
        top: els.chatMessages.scrollHeight,
        behavior: 'smooth'
    });
}

function escapeHTML(str) {
    return str.replace(/[&<>'"]/g, tag => ({
        '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#39;', '"': '&quot;'
    }[tag] || tag));
}

function formatMarkdown(text) {
    if (!text) return '';
    let html = escapeHTML(text);
    
    // Bold
    html = html.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    // Italic
    html = html.replace(/\*(.*?)\*/g, '<em>$1</em>');
    // Code blocks
    html = html.replace(/```([\s\S]*?)```/g, '<pre><code>$1</code></pre>');
    // Inline code
    html = html.replace(/`([^`]+)`/g, '<code>$1</code>');
    // Paragraphs (simplified)
    html = html.split(/\n\n+/).map(p => `<p>${p.replace(/\n/g, '<br>')}</p>`).join('');
    
    return html;
}
