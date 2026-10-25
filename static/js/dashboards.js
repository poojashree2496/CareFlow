import { get, patch } from "./api.js";
import { h, card, table, chip, sevChip, fmt, toast, guarded } from "./ui.js";
import { openPatientDrawer, state } from "./app.js";
import { can, submitLab, submitRadiology, pharmacyAct, takePayment, recordVitals } from "./actions.js";

const stat = (n, label, kind) => h("div", { class: "card stat" }, h("b", null, n ?? 0), h("span", null, label), kind ? chip(kind, "warn") : null);
const openBtn = (id, label = "Open") => h("button", { class: "btn sm", onclick: () => openPatientDrawer(id) }, label);
const patientCell = (r) => h("span", null, h("button", { class: "btn sm ghost", onclick: () => openPatientDrawer(r.patient_id || r.id) }, r.patient || r.name), " ", h("span", { class: "muted small" }, r.patient_code || ""));

const REFRESH = { current: () => {} };

export async function renderDashboard(id, setMain) {
  const load = async () => {
    const d = await get("/api/workspaces/" + id);
    const root = h("div", { class: "grid" });
    (RENDER[id] || fallback)(root, d);
    setMain(root);
  };
  REFRESH.current = load;
  await load();
}
const reload = () => REFRESH.current();
const U = () => state.user;

const RENDER = {
  doctor(root, d) {
    const s = d.summary;
    root.append(h("h2", null, "Clinical Command Center"), h("div", { class: "grid g3" }, stat(s.patients, "My patients"), stat(s.admitted, "Currently admitted"), stat(s.needing_attention, "Needing attention"),
        stat(s.critical_results_pending, "Critical results awaiting acknowledgment"), stat(s.appointments_today, "Appointments today")),
      h("p", { class: "muted small" }, d.note || ""),
      card("Needs attention first", table([
        { label: "Patient", render: patientCell },
        { label: "Where", render: (r) => r.admitted ? `${r.ward || ""} ${r.bed || ""}` : "Outpatient" },
        { label: "Why", render: (r) => h("ul", { class: "small" }, (r.reasons || []).map((x) => h("li", null, typeof x === "string" ? x : (x.text || x.reason || JSON.stringify(x))))) },
      ], d.attention, "Nothing currently flagged by recorded alerts, overdue tasks or unacknowledged critical results.")),
      card("Appointments today", table([
        { label: "Time", key: "time" }, { label: "Patient", render: patientCell }, { label: "Status", key: "status" },
      ], d.appointments_today || [], "No appointments today.")),
      card("Quiet — no flags", table([{ label: "Patient", render: patientCell }, { label: "Where", render: (r) => r.admitted ? `${r.ward || ""} ${r.bed || ""}` : "Outpatient" }], d.quiet || [], "—")));
  },
  nurse(root, d) {
    root.append(h("h2", null, "Nursing workbench"), card("My ward patients", table([
        { label: "Patient", render: patientCell }, { label: "Bed", render: (r) => `${r.ward || ""} ${r.bed || ""}` },
        { label: "Observations", render: (r) => r.freshness ? h("span", null, chip(r.freshness.state, r.freshness.state === "fresh" ? "ok" : "warn")) : "—" },
        { label: "Alerts", render: (r) => (r.alerts || []).length ? chip(`${r.alerts.length} open`, "crit") : "—" },
        { label: "", render: (r) => can(U(), "obs.record") ? h("button", { class: "btn sm", onclick: () => recordVitals(r.id, r.name, reload) }, "Record vitals") : null },
      ], d.patients, "No admitted patients on your ward.")),
      card("Tasks", table([
        { label: "Due", render: (r) => h("span", null, fmt(r.due_at), r.overdue ? [" ", chip("overdue", "crit")] : "") },
        { label: "Task", key: "title" }, { label: "Patient", render: patientCell }, { label: "Priority", render: (r) => sevChip(r.priority) },
        { label: "", render: (r) => h("button", { class: "btn sm", onclick: (ev) => guarded(async () => { await patch(`/api/tasks/${r.id}`, { status: "Done" }); ev.target.closest("tr").remove(); toast("Task marked done"); }) }, "Done") },
      ], d.tasks, "No open tasks.")),
      card("Medications due", table([{ label: "Medicine", key: "medicine" }, { label: "Patient", render: patientCell }], d.medications_due || [], "None due.")));
  },
  lab(root, d) {
    root.append(h("h2", null, "Laboratory"), h("div", { class: "grid g3" }, Object.entries(d.counts || {}).map(([k, v]) => stat(v, k))),
      card("Critical results awaiting acknowledgment", table([
        { label: "Since", render: (r) => fmt(r.since) }, { label: "Result", key: "summary" }, { label: "", render: (r) => openBtn(r.patient_id) },
      ], d.critical_unacknowledged, "No unacknowledged critical results.")),
      card("Work queue", table([
        { label: "Accession", key: "accession_no" }, { label: "Test", key: "test" }, { label: "Patient", render: patientCell },
        { label: "Priority", render: (r) => sevChip(r.priority) }, { label: "Status", render: (r) => chip(r.status) },
        { label: "", render: (r) => can(U(), "lab.verify") && !["Released", "Rejected", "Cancelled"].includes(r.status) ? h("button", { class: "btn sm primary", onclick: () => submitLab(r, reload) }, "Attach report & complete") : (r.status === "Released" ? chip("completed", "ok") : "") },
      ], d.queue, "Queue is empty.")));
  },
  pharmacy(root, d) {
    root.append(h("h2", null, "Pharmacy"), card("Dispensing queue", table([
        { label: "Medicine", key: "medicine" }, { label: "Dose", key: "dosage" }, { label: "Patient", render: patientCell },
        { label: "Qty", render: (r) => `${r.dispensed_quantity}/${r.quantity ?? "—"}` }, { label: "Status", render: (r) => chip(r.status) },
        { label: "Warnings", render: (r) => (r.warnings || []).length ? chip(`${r.warnings.length} to review`, "crit") : "—" },
        { label: "", render: (r) => r.status === "Ordered" && can(U(), "rx.verify") ? h("button", { class: "btn sm", onclick: () => pharmacyAct(r, reload) }, "Verify")
          : ["Verified", "Partially Dispensed"].includes(r.status) && can(U(), "rx.dispense") ? h("button", { class: "btn sm primary", onclick: () => pharmacyAct(r, reload) }, "Dispense") : "" },
      ], d.queue, "No orders waiting.")),
      card("Low stock", table([{ label: "Medicine", key: "name" }, { label: "Stock", key: "stock" }, { label: "Reorder at", key: "reorder_level" }], d.low_stock || [], "Stock levels are fine.")),
      card("Expiring soon", table([{ label: "Medicine", key: "name" }, { label: "Expires", key: "expiry_date" }], d.expiring || [], "Nothing expiring soon.")));
  },
  radiology(root, d) {
    root.append(h("h2", null, "Radiology"), h("div", { class: "grid g3" }, Object.entries(d.counts || {}).map(([k, v]) => stat(v, k))),
      card("Work queue", table([{ label: "Study", key: "modality" }, { label: "Patient", render: patientCell }, { label: "Status", render: (r) => chip(r.status || r.order_status || "") },
        { label: "", render: (r) => can(U(), "rad.authorize") && !["Final", "Cancelled"].includes(r.status || r.order_status) ? h("button", { class: "btn sm primary", onclick: () => submitRadiology(r, reload) }, "Report & complete") : ((r.status || r.order_status) === "Final" ? chip("completed", "ok") : "") }], d.queue, "No studies waiting.")));
  },
  billing(root, d) {
    const s = d.summary;
    root.append(h("h2", null, "Billing & insurance"), h("div", { class: "grid g3" }, stat(s.bills, "Bills"), stat(s.unpaid, "Unpaid"), stat(s.unpaid_total?.toFixed?.(2), "Outstanding total")),
      card("Unpaid bills", table([{ label: "Patient", render: patientCell }, { label: "Description", key: "description" }, { label: "Total", render: (r) => r.total.toFixed(2) }, { label: "Insurance", key: "insurance_status" },
        { label: "", render: (r) => can(U(), "billing.write") ? h("button", { class: "btn sm primary", onclick: () => takePayment(r, reload) }, "Record payment") : null }], d.unpaid, "No unpaid bills.")));
  },
  admin(root, d) {
    root.append(h("h2", null, "Operations overview"), h("div", { class: "grid g3" }, stat(d.open_alerts, "Open clinical alerts"), stat(d.security_events_24h?.total, "Security events (24 h)"), stat(d.security_events_24h?.denied, "Denied requests (24 h)")),
      card("System", h("dl", { class: "kv" }, ...Object.entries({
        "Database": `${d.system.database_backend} (${d.system.database_kind})`, "Environment": d.system.environment,
        "Schema": d.system.schema.state,
        "Document storage": d.system.storage_backend, "AI": d.system.ai.configured ? "configured" : d.system.ai.message,
      }).flatMap(([k, v]) => [h("dt", null, k), h("dd", null, String(v))]))),
      card("Users by role", h("div", { class: "row" }, Object.entries(d.users_by_role).map(([k, v]) => chip(`${k.replace(/_/g, " ")}: ${v}`)))));
  },
};

function fallback(root, d) { root.append(h("div", { class: "empty" }, "No view for this workspace.")); }
