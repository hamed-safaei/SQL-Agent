// ==================== Sidebar ====================


function toggleSidebar() {
    const sidebar = document.getElementById('sidebar');
    const topButtons = document.getElementById('top-buttons');
    const menuToggle = document.getElementsByClassName('menu-toggle')[0];

    sidebar.classList.toggle('open');
    document.body.classList.toggle('sidebar-open');

    if (sidebar.classList.contains('open')) {
        menuToggle.hidden = true;
        topButtons.classList.add('sidebar-open');
    } else {
        menuToggle.hidden = false;
        topButtons.classList.remove('sidebar-open');
    }
}

function closesidebar() {
    const sidebar = document.getElementById('sidebar');
    const topButtons = document.getElementById('top-buttons');

    sidebar.classList.remove('open');
    document.body.classList.remove('sidebar-open');
    document.getElementsByClassName('menu-toggle')[0].hidden = false;
    topButtons.classList.remove('sidebar-open');
}

// ==================== Connection Panel ====================

function toggleConnectionPanel() {
    const panel = document.getElementById('connection-panel');
    panel.classList.toggle('open');

    const savedServer = localStorage.getItem('db_server');
    const savedDatabase = localStorage.getItem('db_database');

    if (savedServer) document.getElementById('db-server').value = savedServer;
    if (savedDatabase) document.getElementById('db-name').value = savedDatabase;
}

function closeConnectionPanel() {
    const panel = document.getElementById('connection-panel');
    panel.classList.remove('open');
    hideStatusMessage();
}

function showStatusMessage(message, type) {
    const statusMsg = document.getElementById('status-message');
    statusMsg.textContent = message;
    statusMsg.className = `status-message ${type}`;
    statusMsg.style.display = 'block';
}

function hideStatusMessage() {
    const statusMsg = document.getElementById('status-message');
    statusMsg.style.display = 'none';
}

async function connectDatabase() {
    const server = document.getElementById('db-server').value.trim();
    const dbName = document.getElementById('db-name').value.trim();

    if (!server || !dbName) {
        showStatusMessage('لطفا تمام فیلدها را پر کنید', 'error');
        return;
    }

    const connectBtn = document.getElementById('connect-btn');
    connectBtn.disabled = true;
    connectBtn.textContent = 'در حال تست اتصال...';
    hideStatusMessage();

    try {
        const response = await fetch('/test-connection', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ server, database: dbName })
        });

        const data = await response.json();

        if (data.success) {
            showStatusMessage(data.message, 'success');
            document.getElementById('status-dot').style.backgroundColor = 'limegreen';
            document.getElementById('status-text').textContent = "Data Base : " + dbName;
            localStorage.setItem('db_server', server);
            localStorage.setItem('db_database', dbName);
        } else {
            showStatusMessage(data.message, 'error');
            document.getElementById('status-dot').style.backgroundColor = 'red';
            document.getElementById('status-text').textContent = "! Connection Failed";
        }

    } catch (error) {
        showStatusMessage('خطا در برقراری ارتباط با سرور', 'error');
        document.getElementById('status-dot').style.backgroundColor = 'red';
        document.getElementById('status-text').textContent = "! Connection Failed";
    } finally {
        connectBtn.disabled = false;
        connectBtn.textContent = 'اتصال';
    }
}

// ==================== Chat UI Helpers ====================

function scrollChatToBottom() {
    const chat = document.getElementById("chat-area");
    chat.scrollTop = chat.scrollHeight;
}

function addUserMessage(text) {
    const chat = document.getElementById("chat-area");
    const msg = document.createElement("div");
    msg.className = "chat-message user-message";
    msg.innerText = text;
    chat.appendChild(msg);
    scrollChatToBottom();
}

/**
 * یک حباب bot خالی می‌سازد که tokenها داخلش اضافه می‌شوند.
 * @returns {HTMLElement} رفرنس به المان حباب
 */
function createStreamingBubble() {
    const chat = document.getElementById("chat-area");
    const msg = document.createElement("div");
    msg.className = "chat-message bot-message chat-only";
    msg.textContent = "";  // تغییر از innerText به textContent
    chat.appendChild(msg);
    scrollChatToBottom();
    return msg;
}


/** یک پیام متنی کامل (بدون streaming) اضافه می‌کند */
function addChatMessage(text) {
    const chat = document.getElementById("chat-area");
    const msg = document.createElement("div");
    msg.className = "chat-message bot-message chat-only";
    msg.innerText = text;
    chat.appendChild(msg);
    scrollChatToBottom();
}

function addSQLBox(query) {
    const chat = document.getElementById("chat-area");
    const msg = document.createElement("div");
    msg.className = "chat-message bot-message";

    msg.innerHTML = `
    <div class="query-title">
        <button class="copy-query-btn" onclick="copyQuery(this)">Copy</button>
        <span>SQL Query</span>
    </div>
    <div class="query-box">
        <pre class="sql-box">${escapeHtml(query)}</pre>
    </div>
    `;

    chat.appendChild(msg);
    scrollChatToBottom();
}

function addResultTable(columns, data) {
    const chat = document.getElementById("chat-area");
    const msg = document.createElement("div");
    msg.className = "chat-message bot-message";

    if (data && data.length) {
        let table = "<table class='result-table'><thead><tr>";
        columns.forEach(col => { table += `<th>${escapeHtml(String(col))}</th>`; });
        table += "</tr></thead><tbody>";
        data.forEach(row => {
            table += "<tr>";
            columns.forEach(col => {
                const val = row[col] !== null && row[col] !== undefined ? row[col] : "";
                table += `<td>${escapeHtml(String(val))}</td>`;
            });
            table += "</tr>";
        });
        table += "</tbody></table>";
        msg.innerHTML = `<div class="table-scroll-wrapper">${table}</div>`;
    } else {
        msg.innerHTML = "<p>نتیجه‌ای یافت نشد</p>";
    }

    chat.appendChild(msg);
    scrollChatToBottom();
}

function escapeHtml(str) {
    return str
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;");
}

function copyQuery(btn) {
    const query = btn.parentElement.nextElementSibling.querySelector(".sql-box").innerText;
    navigator.clipboard.writeText(query).then(() => {
        btn.innerText = "Copied";
        setTimeout(() => { btn.innerText = "Copy"; }, 1500);
    });
}

function showTypingLoader() {
    const chat = document.getElementById("chat-area");
    const loader = document.createElement("div");
    loader.id = "typing-loader";
    loader.innerHTML = `
        <div class="typing-loader">
            <span></span>
            <span></span>
            <span></span>
        </div>
    `;
    chat.appendChild(loader);
    scrollChatToBottom();
}

function removeTypingLoader() {
    const loader = document.getElementById("typing-loader");
    if (loader) loader.remove();
}

// ==================== Send Question (Streaming) ====================

async function sendQuestion() {
    const inputField = document.getElementById("user-input");
    const question = inputField.value.trim();
    if (!question) return;

    // UI setup
    document.getElementById("prompt-text").style.display = "none";
    document.getElementById('header-section').style.display = 'none';
    document.querySelector(".main-container").classList.add("chat-mode");
    sendBtn.classList.remove('active');

    addUserMessage(question);
    showTypingLoader();
    inputField.value = "";

    // متغیرهای وضعیت
    let loaderVisible = true;
    let currentBubble = null;

    // تعریف تابع در سطح تابع اصلی تا همه جا در دسترس باشد
    const ensureLoaderRemoved = () => {
        if (loaderVisible) {
            removeTypingLoader();
            loaderVisible = false;
        }
    };

    try {
        const response = await fetch('/ask-stream', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ question })
        });

        if (!response.ok) {
            const err = await response.json();
            alert(err.detail || 'خطا در دریافت پاسخ');
            ensureLoaderRemoved(); // استفاده از تابع تعریف شده
            return;
        }

        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let buffer = "";

        function getOrCreateBubble() {
            if (!currentBubble) {
                currentBubble = createStreamingBubble();
            }
            return currentBubble;
        }

        while (true) {
            const { done, value } = await reader.read();
            if (done) break;

            buffer += decoder.decode(value, { stream: true });
            const parts = buffer.split("\n\n");
            buffer = parts.pop();

            for (const part of parts) {
                const line = part.trim();
                if (!line.startsWith("data: ")) continue;

                let parsed;
                try {
                    parsed = JSON.parse(line.slice(6));
                } catch { continue; }

                const event = parsed.event;

                if (event === "token") {
                    ensureLoaderRemoved();
                    const bubble = getOrCreateBubble();
                    bubble.textContent += parsed.text;
                    scrollChatToBottom();
                }
                else if (event === "new_bubble") {
                    currentBubble = null;
                }
                else if (event === "sql") {
                    ensureLoaderRemoved();
                    currentBubble = null;
                    addSQLBox(parsed.sql);
                    
                    showTypingLoader();
                    loaderVisible = true;
                }
                else if (event === "table") {
                    ensureLoaderRemoved();
                    currentBubble = null;
                    addResultTable(parsed.columns, parsed.data);
                    
                    showTypingLoader();
                    loaderVisible = true;
                }
                else if (event === "error") {
                    ensureLoaderRemoved();
                    currentBubble = null;
                    addChatMessage("❌ خطا: " + parsed.error);
                }
                else if (event === "done") {
                    ensureLoaderRemoved();
                    currentBubble = null;
                }
            }
        }
        ensureLoaderRemoved();
    } catch (error) {
        ensureLoaderRemoved(); // استفاده از تابع تعریف شده
        alert('خطا در ارتباط با سرور: ' + error.message);
    }
}

// ==================== Input Listeners ====================

const userInput = document.getElementById('user-input');
const sendBtn = document.querySelector('.send-btn');

userInput.addEventListener('input', function () {
    sendBtn.classList.toggle('active', this.value.trim().length > 0);
});

sendBtn.addEventListener('click', sendQuestion);

userInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') sendQuestion();
});

// ==================== Typewriter intro ====================

function typeWriter(text, elementId, speed = 200) {
    let i = 0;
    const element = document.getElementById(elementId);
    element.textContent = '';

    function type() {
        if (i < text.length) {
            element.textContent += text.charAt(i);
            i++;
            setTimeout(type, speed);
        }
    }

    type();
}

window.addEventListener('DOMContentLoaded', function () {
    typeWriter('چطور می‌توانم به شما کمک کنم ؟', 'prompt-text', 60);
});







// ==================== New Chat ====================

function newChat() {
    document.getElementById('chat-area').innerHTML = '';
    document.getElementById('user-input').value = '';
    document.getElementById('prompt-text').style.display = 'block';
    document.getElementById('header-section').style.display = 'block';
    document.querySelector('.main-container').classList.remove('chat-mode');
    sendBtn.classList.remove('active');
    typeWriter('چطور می‌توانم به شما کمک کنم ؟', 'prompt-text', 60);
}









