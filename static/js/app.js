import { get, post, api } from "./api.js";
import { h, clear, toast, fmt } from "./ui.js";
import { renderDashboard } from "./dashboards.js";
import { renderBedboard } from "./bedboard.js";
import { openPatient } from "./patient.js";
import { renderAdmin } from "./admin.js";
import { renderPatients, renderAppointments, renderAi } from "./views.js";
import { renderPortal } from "./portal.js";

export const state = { user: null, workspaces: [], current: null, meta: {} };
const main = document.getElementById("main");
const tabs = document.getElementById("workspace-tabs");

export function setMain(node) { clear(main); main.append(node); main.focus({ preventScroll: true }); }
export const put = (node, ...kids) => { clear(node); kids.flat().forEach((k) => { if (k !== null && k !== undefined && k !== false) node.append(k); }); return node; };
export const openPatientDrawer = (id) => openPatient(id);

const EXTRA = { bedboard: { label: "Bedboard", render: renderBedboard }, patients: { render: renderPatients }, appointments: { render: renderAppointments }, ai: { render: renderAi }, users: { label: "Users & audit", render: renderAdmin } };
const hasPerm = (p) => state.user.permissions.includes(p);

async function showWorkspace(id) {
  state.current = id;
  [...tabs.children].forEach((b) => b.setAttribute("aria-current", b.dataset.id === id ? "page" : "false"));
  location.hash = id;
  setMain(h("p", { class: "muted pad" }, "Loading…"));
  try {
    if (EXTRA[id]) await EXTRA[id].render(setMain);
    else await renderDashboard(id, setMain);
  } catch (e) {
    setMain(h("div", { class: "empty" }, e.message || "Could not load this workspace."));
  }
}

function buildTabs() {
  clear(tabs);
  const items = state.workspaces.map((w) => ({ id: w.id, label: w.label }));
  if (["super_admin", "hospital_admin"].includes(state.user.role)) items.push({ id: "users", label: "Users & audit" });
  items.forEach((w) => tabs.append(h("button", { class: "tab", "data-id": w.id, onclick: () => showWorkspace(w.id) }, w.label)));
  return items;
}

async function notifications() {
  try {
    const d = await get("/api/auth/notifications");
    const c = document.getElementById("notify-count");
    c.textContent = d.unread; c.hidden = !d.unread;
    return d;
  } catch (e) { return { items: [] }; }
}

document.getElementById("btn-notify").addEventListener("click", async () => {
  const d = await notifications();
  const dr = document.getElementById("drawer");
  put(dr,
    h("div", { class: "row between" }, h("h2", null, "Notifications"), h("button", { class: "btn sm", onclick: () => { dr.hidden = true; } }, "Close")),
    d.items.length ? h("ul", { class: "journey" }, d.items.map((n) => h("li", { class: n.severity === "Critical" ? "k-critical" : "" },
      h("div", { class: "when" }, fmt(n.created_at), n.read ? "" : " · new"),
      h("div", { class: "what" }, n.title), h("div", { class: "detail" }, n.body),
      n.patient_id ? h("button", { class: "btn sm", onclick: () => openPatient(n.patient_id) }, "Open patient") : null)))
      : h("div", { class: "empty" }, "No notifications."),
    d.unread ? h("button", { class: "btn", onclick: async () => { await post("/api/auth/notifications/read", {}); dr.hidden = true; notifications(); } }, "Mark all read") : null);
  dr.hidden = false;
});

document.getElementById("btn-logout").addEventListener("click", async () => {
  try { await api("POST", "/api/auth/logout", {}, { quiet401: true }); } finally { window.location.href = "/login"; }
});

async function boot() {
  const me = await get("/api/auth/me");
  state.user = me.user; state.meta = me; window.__user = me.user;
  document.getElementById("who").textContent = `${me.user.name} · ${me.user.role_label}`;
  const env = document.getElementById("env-badge");
  env.textContent = me.environment === "production" ? "" : me.environment;
  const banner = document.getElementById("banner");
  const notes = [];
  if (me.user.must_change_password) notes.push("You must change your password before continuing.");
  banner.textContent = notes.join("  ");
  banner.hidden = !notes.length;
  if (me.user.must_change_password) return forcePasswordChange();
  if (me.user.role === "patient") {   // patients get one read-only dashboard; no workspace tabs
    clear(tabs);
    await renderPortal(setMain, me.user);
    return;
  }
  const ws = (await get("/api/workspaces"));
  state.workspaces = ws.items;
  const items = buildTabs();
  const want = location.hash.slice(1);
  await showWorkspace(items.some((i) => i.id === want) ? want : (ws.default || items[0]?.id));
  notifications();
  setInterval(notifications, 60000);
}

function forcePasswordChange() {
  const f = h("form", { class: "card", onsubmit: async (ev) => {
    ev.preventDefault();
    try {
      await post("/api/auth/password", { current: f.cur.value, new: f.nw.value });
      toast("Password changed"); location.reload();
    } catch (e) { toast(e.message, true); }
  } },
  h("h2", null, "Choose a new password"),
  h("p", { class: "muted" }, "At least 12 characters; avoid common words and patterns."),
  h("label", null, "Current password", h("input", { name: "cur", type: "password", autocomplete: "current-password", required: true })),
  h("label", null, "New password", h("input", { name: "nw", type: "password", autocomplete: "new-password", minlength: 12, required: true })),
  h("button", { class: "btn primary", type: "submit" }, "Change password"));
  setMain(f);
}

document.addEventListener("keydown", (e) => { if (e.key === "Escape") document.getElementById("drawer").hidden = true; });
boot().catch((e) => setMain(h("div", { class: "empty" }, e.message)));
