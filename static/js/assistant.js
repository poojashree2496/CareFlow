import { get, post } from "./api.js";
import { h, chip, guarded } from "./ui.js";

// Patient-aware assistant. All authorization, evidence selection and safety checks happen on the server.
export function mountAssistant(patientId, patient) {
  const root = h("div");
  const chat = h("div", { class: "chat", "aria-live": "polite" });
  const status = h("p", { class: "muted small" }, "Checking assistant status…");
  const mode = h("select", { "aria-label": "Answer style" }, h("option", { value: "simple" }, "Plain language"), h("option", { value: "clinical" }, "Clinical"));
  const q = h("textarea", { rows: 2, placeholder: `Ask about ${patient.name.split(" (")[0]}'s record…`, maxlength: 1500 });
  const send = h("button", { class: "btn primary", type: "button" }, "Ask");
  let cid = null;

  const bubble = (role, text, extra) => {
    const m = h("div", { class: "msg " + role }, text);
    if (extra?.notice) m.append(h("span", { class: "notice" }, extra.notice));
    if (extra?.sources?.length) m.append(h("div", { class: "cites" }, "Sources: ", extra.sources.map((s) => `[${s.id || s.ref || "?"}] ${s.title || ""}`).join(" · ")));
    if (extra?.limitations?.length) m.append(h("div", { class: "cites" }, extra.limitations.join(" ")));
    chat.append(m); chat.scrollTop = chat.scrollHeight;
    return m;
  };

  get("/api/ai/status").then((s) => {
    status.textContent = "";
    status.append(s.configured
      ? chip(`${s.provider}${s.external ? " · external" : " · local"}`, "ok")
      : chip("configuration required", "warn"), " ",
    s.configured ? (s.image_analysis ? "" : "Answers use report text only; images are not analysed.") : (s.message || ""));
  }).catch(() => { status.textContent = "Assistant status unavailable."; });

  send.addEventListener("click", () => guarded(async () => {
    const question = q.value.trim();
    if (question.length < 2) return;
    send.disabled = true; q.value = "";
    bubble("user", question);
    const wait = bubble("assistant", "Looking through the record…");
    try {
      if (!cid) cid = (await post("/api/ai/conversations", { patient_id: patientId })).conversation_id;
      const r = await post(`/api/ai/conversations/${cid}/ask`, { question, mode: mode.value });
      wait.remove();
      const m = r.message;
      const withheld = r.status !== "ok";
      bubble("assistant", m.content || "(no content)", { sources: m.sources, limitations: m.limitations,
        notice: withheld ? `Status: ${r.status.replace(/_/g, " ")}. This is not an AI-generated answer.` : "AI-generated from the cited records. Verify before acting; this is not a diagnosis or prescription." });
    } catch (e) { wait.remove(); bubble("assistant", e.message); }
    finally { send.disabled = false; }
  }));
  q.addEventListener("keydown", (e) => { if (e.key === "Enter" && (e.ctrlKey || e.metaKey)) send.click(); });
  root.append(status, chat, h("div", { class: "row" }, mode), q, h("div", { class: "row between" }, h("span", { class: "muted small" }, "Ctrl+Enter to send · uses only records you are authorised to see"), send));
  return root;
}
