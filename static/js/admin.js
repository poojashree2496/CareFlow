import { get, post, patch } from "./api.js";
import { h, card, table, chip, fmt, toast, guarded, field } from "./ui.js";
import { createPatientLogin, addUser } from "./actions.js";
import { del } from "./api.js";

export async function renderAdmin(setMain) {
  const root = h("div", { class: "grid" }, h("h2", null, "Users & audit"));
  const usersBox = h("div"), auditBox = h("div"), verifyBox = h("div");
  const pick = h("select", { "aria-label": "Patient" });
  const portalBox = h("div", { class: "row" }, pick, h("button", { class: "btn primary", onclick: () => { const o = pick.selectedOptions[0]; if (o && o.value) createPatientLogin(JSON.parse(o.dataset.p), loadUsers); } }, "Create portal login"));
  get("/api/patients?per_page=100").then((d) => pick.append(h("option", { value: "" }, "Choose a patient…"), ...d.items.map((p) => h("option", { value: p.id, "data-p": JSON.stringify({ id: p.id, name: p.name, email: p.email || "" }) }, `${p.name} · ${p.patient_code}`)))).catch(() => {});
  root.append(card("Patient portal logins", h("div", null, h("p", { class: "muted small" }, "Give a patient a read-only dashboard for their own records, reports and the assistant."), portalBox)), card("Users", usersBox, h("button", { class: "btn primary sm", onclick: () => addUser(loadUsers) }, "+ Add account")), card("Audit trail", auditBox, h("div", { class: "row", style: "margin-top:.6rem" }, h("button", { class: "btn sm", onclick: () => guarded(verifyChain) }, "Verify integrity")), verifyBox));
  setMain(root);

  async function loadUsers() {
    const d = await get("/api/admin/users");
    usersBox.replaceChildren(table([
      { label: "Name", render: (u) => u.name },
      { label: "E-mail", key: "email" }, { label: "Role", key: "role_label" },
      { label: "State", render: (u) => u.locked ? chip("locked", "crit") : u.is_active ? chip("active", "ok") : chip("disabled", "warn") },
      { label: "Last sign-in", render: (u) => fmt(u.last_login_at) },
      { label: "Actions", render: (u) => h("div", { class: "row" },
        u.locked ? h("button", { class: "btn sm", onclick: () => guarded(async () => { await post(`/api/admin/users/${u.id}/unlock`); toast("Unlocked"); loadUsers(); }) }, "Unlock") : null,
        h("button", { class: "btn sm", onclick: () => guarded(async () => { await patch(`/api/admin/users/${u.id}`, { is_active: !u.is_active }); loadUsers(); }) }, u.is_active ? "Disable" : "Enable"),
        h("button", { class: "btn sm", onclick: () => guarded(async () => { await post(`/api/admin/users/${u.id}/revoke-sessions`); toast("Sessions revoked"); }) }, "Revoke sessions"),
        h("button", { class: "btn sm danger", onclick: () => { if (window.confirm(`Delete ${u.name}? Accounts already used in records can't be erased and will be disabled instead.`)) guarded(async () => { const r = await del(`/api/admin/users/${u.id}`); toast(r.message); loadUsers(); }); } }, "Delete")) },
    ], d.items));
  }
  async function loadAudit() {
    const d = await get("/api/admin/audit?per_page=25");
    auditBox.replaceChildren(table([
      { label: "When", render: (r) => fmt(r.at) }, { label: "User", render: (r) => r.user || "—" }, { label: "Action", key: "action" },
      { label: "Outcome", render: (r) => chip(r.outcome, r.outcome === "success" ? "ok" : "crit") }, { label: "IP", key: "ip" },
    ], d.items, "No audit entries."));
  }
  async function verifyChain() {
    verifyBox.replaceChildren(h("p", { class: "muted small" }, "Checking every entry…"));
    const d = await get("/api/admin/audit/verify");
    const head = h("p", { class: "muted small" }, `Entries checked: ${d.checked}. Latest entry hash (note it down to detect later removal of recent entries): `, h("code", null, d.head_hash.slice(0, 16) + "…"));
    verifyBox.replaceChildren(
      h("p", null, d.chain_ok ? chip("Audit trail intact", "ok") : chip(`${d.issue_count} problem(s) found`, "crit")),
      head,
      d.chain_ok ? null : table([{ label: "Entry id", key: "id" }, { label: "Problem", key: "problem" }], d.issues, ""),
      d.unprotected_before_chain ? h("p", { class: "muted small" }, `${d.unprotected_before_chain} older entries pre-date the hash chain.`) : null);
  }
  await Promise.all([loadUsers(), loadAudit()]);
}
