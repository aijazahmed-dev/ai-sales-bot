let sessionToken = sessionStorage.getItem("chat_session");

async function askBot(text) {
  const first = !sessionToken;
  const res = await fetch(API_BASE + (first ? "/chat/" : "/chat/message"), {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(first ? { content: text }
                               : { session_token: sessionToken, content: text }),
  });

  if (res.status === 429) return "You're sending messages too fast. Please wait a moment.";
  if (res.status === 404) {                      // chat expired or invalid: start a new one
    sessionStorage.removeItem("chat_session");
    sessionToken = null;
    return askBot(text);
  }
  if (!res.ok) return "Sorry, something went wrong. Please try again.";

  const data = await res.json();
  if (data.session_token) {                      // only the first response has it
    sessionToken = data.session_token;
    sessionStorage.setItem("chat_session", sessionToken);
  }
  return data.reply;
}