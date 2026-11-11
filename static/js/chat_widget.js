// Inject the chat widget into the page
(function() {
  const body = document.body;

  body.insertAdjacentHTML("beforeend", `
    <div id="ai-chat-widget" class="fixed bottom-4 right-4 w-80 max-w-full bg-white shadow-lg rounded-lg border hidden z-50 font-sans">
      <div class="bg-indigo-600 text-white px-4 py-2 rounded-t-lg flex justify-between items-center cursor-pointer" id="chat-widget-header">
        <h3 class="font-semibold text-sm">AI Chat Bot</h3>
        <button id="chat-widget-close" class="text-white font-bold">&times;</button>
      </div>
      <div id="chat-widget-messages" class="p-4 h-64 overflow-y-auto flex flex-col gap-2 bg-gray-50"></div>
      <div class="px-4 py-2 border-t flex gap-2">
        <input type="text" id="chat-widget-input" placeholder="Type a message..." class="flex-1 border rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500"/>
        <button id="chat-widget-send" class="bg-indigo-600 text-white px-3 py-2 rounded-lg hover:bg-indigo-700">Send</button>
      </div>
    </div>
  `);

  const widget = document.getElementById("ai-chat-widget");
  const header = document.getElementById("chat-widget-header");
  const closeBtn = document.getElementById("chat-widget-close");
  const messages = document.getElementById("chat-widget-messages");
  const input = document.getElementById("chat-widget-input");
  const sendBtn = document.getElementById("chat-widget-send");

  // Open / Close toggle
  header.addEventListener("click", () => {
    widget.classList.toggle("hidden");
  });
  closeBtn.addEventListener("click", (e) => {
    e.stopPropagation();
    widget.classList.add("hidden");
  });

  // Helper to append messages
  function addMessage(text, sender = "bot") {
    const msg = document.createElement("div");
    msg.className = sender === "bot" ? "bg-gray-200 text-gray-800 px-3 py-2 rounded-lg self-start" : "bg-indigo-600 text-white px-3 py-2 rounded-lg self-end";
    msg.textContent = text;
    messages.appendChild(msg);
    messages.scrollTop = messages.scrollHeight;
  }

  // Send message
  async function sendMessage() {
    const text = input.value.trim();
    if (!text) return;

    addMessage(text, "user");
    input.value = "";

    try {
      // Call your FastAPI backend
      const response = await fetch("/chat/send", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({ message: text })
      });

      const data = await response.json();
      addMessage(data.reply || "Sorry, no response from bot.", "bot");

      // Optional: handle lead collection if backend sends collect_lead flag
      if (data.collect_lead) {
        addMessage("Please enter your email to continue...", "bot");
      }

    } catch (err) {
      addMessage("Error: Could not reach server.", "bot");
    }
  }

  sendBtn.addEventListener("click", sendMessage);
  input.addEventListener("keydown", (e) => {
    if (e.key === "Enter") sendMessage();
  });

  // Optional: function to open widget programmatically
  window.openChatWidget = function() {
    widget.classList.remove("hidden");
  };

})();
