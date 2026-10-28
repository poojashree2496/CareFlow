import { get, post, patch, api } from "./api.js";
import { h, clear, card, table, chip, sevChip, srcChip, fmt, ago, toast, guarded } from "./ui.js";
import { mountAssistant } from "./assistant.js";
import { put, state } from "./app.js";
import { can, addNote } from "./actions.js";
import { addAllergy, addProblem, setProblemStatus, orderLab, orderRadiology, prescribe, admitPatient, moveBed, planDischarge, authorizeDischarge, completeDischarge, bookAppointment } from "./clinical_forms.js";

const drawer = () => document.getElementById("drawer");

export async function openPatient(id) {
  const dr = drawer();
  clear(dr).append(h("p", { class: "muted" }, "Loading patient…"));
  dr.hidden = false;
  try {
    const j = await get(`/api/patients/${id}/journey`);
    render(dr, id, j);
  } catch (e) {
    clear(dr).append(h("div", { class: "row between" }, h("h2", null, "Patient"), h("button", { class: "btn sm", onclick: () => { dr.hidden = true; } }, "Close")), h("div", { class: "empty" }, e.message));
  }
}

function render(dr, id, j) {
  const p = j.patient, s = j.snapshot || {};
  const body = h("div");
  const tabsEl = h("div", { class: "tabs-sub" });
  const views = {
    Journey: () => journey(j),
    Vitals: () => vitals(id, s),
    Clinical: () => clinical(id, s),
    "Ask CareFlow AI": () => mountAssistant(id, p),
  };
  const perms = state.user;
  if (can(perms, "lab.read") || can(perms, "rad.read") || can(perms, "doc.read")) views["Results & reports"] = () => results(id, p);
  if (can(perms, "deliverable.manage")) views["Hand-over"] = () => handover(id);
  const show = (name) => {
    [...tabsEl.children].forEach((b) => b.setAttribute("aria-current", b.textContent === name ? "page" : "false"));
    clear(body).append(views[name]());
  };
  Object.keys(views).forEach((n) => tabsEl.append(h("button", { class: "tab", onclick: () => show(n) }, n)));
  put(dr,
    h("div", { class: "row between" }, h("div", null, h("h2", null, p.name), h("div", { class: "muted small" }, `${p.patient_code} · ${p.age ?? "?"} y · ${p.gender || ""} · ${p.blood_group || ""}`)),
      h("button", { class: "btn sm", onclick: () => { dr.hidden = true; } }, "Close")),
    (s.allergies || []).length ? h("p", null, chip("Allergies", "crit"), " ", s.allergies.map((a) => `${a.substance}${a.reaction ? " (" + a.reaction + ")" : ""}`).join("; ")) : h("p", { class: "muted small" }, "No structured allergies recorded."),
    (s.alerts || []).length ? card("Open alerts", h("ul", null, s.alerts.map((a) => h("li", null, sevChip(a.severity), " ", a.title || a.message || "",
      h("button", { class: "btn sm", onclick: () => guarded(async () => { await post(`/api/alerts/${a.id}/acknowledge`); toast("Acknowledged"); openPatient(id); }) }, "Acknowledge"))))) : null,
    s.stay ? h("p", { class: "small" }, chip("Admitted", "ok"), ` ${s.stay.ward || ""}${s.stay.bed ? " · bed " + s.stay.bed.code : " · no bed yet"}`, s.stay.discharge_status && s.stay.discharge_status !== "None" ? [" ", chip("Discharge " + s.stay.discharge_status.toLowerCase(), "warn")] : "") : null,
    actionBar(id, p, s, perms),
    tabsEl, body);
  show("Journey");
}

// Data entry: every button opens a dialog that calls an existing API route; the server decides what the role may actually do.
function actionBar(id, p, s, perms) {
  const reload = () => openPatient(id);
  const btn = (label, perm, fn) => can(perms, perm) ? h("button", { class: "btn sm", onclick: fn }, label) : null;
  const stay = s.stay, ds = stay?.discharge_status || "None";
  const items = [
    btn("Add note", "note.write", () => addNote(id, p.name, perms.role === "nurse" ? ["Nursing"] : ["Progress", "Consult", "Procedure", "Discharge", "Admission"], reload)),
    btn("Add allergy", "allergy.write", () => addAllergy(id, p.name, reload)),
    btn("Add problem", "problem.write", () => addProblem(id, p.name, reload)),
    btn("Order lab test", "lab.order", () => orderLab(id, p.name, reload)),
    btn("Order imaging", "rad.order", () => orderRadiology(id, p.name, reload)),
    btn("Prescribe", "rx.prescribe", () => prescribe(id, p.name, reload)),
    btn("Book appointment", "appointment.manage", () => bookAppointment({ patient_id: id, patient_name: p.name }, perms, reload)),
    !stay ? btn("Admit", "admission.manage", () => admitPatient(id, p.name, perms, reload)) : null,
    stay ? btn(stay.bed ? "Transfer bed" : "Assign bed", "bed.operate", () => moveBed(stay, p.name, reload)) : null,
    stay && ds !== "Authorized" ? btn("Plan discharge", "admission.manage", () => planDischarge(stay, p.name, reload)) : null,
    stay && ds !== "Authorized" ? btn("Authorize discharge", "discharge.authorize", () => authorizeDischarge(stay, p.name, reload)) : null,
    stay && ds === "Authorized" ? btn("Complete discharge", "admission.manage", () => completeDischarge(stay, p.name, reload)) : null,
  ].filter(Boolean);
  return items.length ? h("div", { class: "row wrap" }, items) : null;
}

function journey(j) {
  const t = j.timeline || [];
  if (!t.length) return h("div", { class: "empty" }, "No events recorded yet for this patient.");
  return h("ol", { class: "journey" }, t.map((e) => h("li", { class: "k-" + e.kind },
    h("div", { class: "when" }, fmt(e.at), " · ", e.source || e.kind, e.by_name ? ` · ${e.by_name}` : ""),
    h("div", { class: "what" }, e.title, e.status ? [" ", chip(e.status)] : ""),
    e.detail ? h("div", { class: "detail" }, e.detail) : null)));
}

function vitals(id, s) {
  const f = s.freshness || {};
  const wrap = h("div");
  wrap.append(h("p", { class: f.state === "fresh" ? "muted small" : "small" },
    f.last_at ? `Last observation ${ago(f.age_min)} (${f.state}). Expected every ${f.expected_interval_min} min.` : "No observations recorded.",
    f.state && f.state !== "fresh" ? [" ", chip(f.state, "warn")] : ""));
  const entries = Object.values(s.vitals || {});
  wrap.append(entries.length ? h("div", { class: "vitals" }, entries.map((v) => h("div", { class: "vital" + (f.state !== "fresh" ? " stale" : "") },
    h("small", null, v.label), h("b", null, v.value), " ", h("span", null, v.unit),
    h("small", null, fmt(v.observed_at)), srcChip(v.source), " ", chip(v.validation_status))))
    : h("div", { class: "empty" }, "No vital signs recorded."));
  wrap.append(h("p", { class: "muted small" }, "Readings labelled “simulated” are simulated and must never be used for care decisions. Alerts require clinical review."));
  return wrap;
}

function clinical(id, s) {
  const canEdit = can(state.user, "problem.write");
  return h("div", { class: "grid" },
    card("Active problems", table([{ label: "Problem", key: "description" }, { label: "Since", key: "onset_on" }, { label: "Status", key: "status" },
      { label: "", render: (r) => canEdit ? h("button", { class: "btn sm", onclick: () => guarded(() => setProblemStatus(r.id, "Resolved", () => openPatient(id))) }, "Mark resolved") : "" }], s.problems || [], "None recorded.")),
    card("Medications", table([{ label: "Medicine", key: "medicine" }, { label: "Dose", key: "dosage" }, { label: "Frequency", key: "frequency" }, { label: "Status", render: (r) => chip(r.status) }], s.medications || [], "None active.")),
    card("Open tasks", table([{ label: "Due", render: (r) => fmt(r.due_at) }, { label: "Task", key: "title" }, { label: "", render: (r) => r.overdue ? chip("overdue", "crit") : "" }], s.tasks || [], "None.")),
    card("Care team", table([{ label: "Name", key: "name" }, { label: "Role", key: "role" }, { label: "Relation", key: "relation" }], s.team || [], "No assignments.")));
}

const sizeKb = (n) => `${Math.max(1, Math.round((n || 0) / 1024))} KB`;

// Lab / scan reports and files for this patient. Staff see them according to role; sharing with the patient is a deliberate toggle.
function results(id, p) {
  const box = h("div", { class: "grid" });
  const u = state.user;
  const load = async () => {
    const [labs, rads, docs] = await Promise.all([
      can(u, "lab.read") ? get(`/api/labs?patient_id=${id}`).catch(() => ({ items: [] })) : { items: [] },
      can(u, "rad.read") ? get(`/api/radiology?patient_id=${id}`).catch(() => ({ items: [] })) : { items: [] },
      can(u, "doc.read") ? get(`/api/patients/${id}/documents`).catch(() => ({ items: [] })) : { items: [] }]);
    const canShare = can(u, "doc.upload");
    const dl = (d) => h("a", { class: "btn sm", href: `/api/documents/${d.id}/download` }, "Download");
    clear(box).append(
      card("Laboratory orders", table([{ label: "Test", render: (r) => r.test_name || r.test }, { label: "Status", render: (r) => chip(r.status) }, { label: "Ordered", render: (r) => fmt(r.ordered_at) }, { label: "Released", render: (r) => fmt(r.released_at) }], labs.items, "No lab orders you can see.")),
      card("Imaging", table([{ label: "Study", render: (r) => r.modality || r.study_description }, { label: "Status", render: (r) => chip(r.order_status || r.report_status || "") }, { label: "Impression", render: (r) => r.impression || "—" }], rads.items, "No imaging you can see.")),
      card("Files (reports, scans, documents)", h("div", null, table([{ label: "Title", key: "title" }, { label: "Type", key: "doc_type" }, { label: "Added", render: (r) => fmt(r.uploaded_at) }, { label: "Size", render: (r) => sizeKb(r.size_bytes) },
        { label: "Patient can see", render: (r) => canShare ? h("label", { class: "inline" }, h("input", { type: "checkbox", checked: r.patient_visible, onchange: (ev) => guarded(async () => { await post(`/api/documents/${r.id}/visibility`, { patient_visible: ev.target.checked }); toast(ev.target.checked ? "Shared with the patient" : "No longer shared"); }) }), " shared") : (r.patient_visible ? chip("shared", "ok") : chip("staff only")) },
        { label: "", render: dl }], docs.items, "No files."),
      can(u, "doc.upload") ? upForm(id, load) : null)));
  };
  load();
  return box;
}

function upForm(id, reload) {
  const file = h("input", { type: "file", accept: ".pdf,.png,.jpg,.jpeg,.txt" });
  const type = h("select", null, ["Laboratory report", "Radiology report", "Clinical letter", "Other"].map((t) => h("option", null, t)));
  const share = h("input", { type: "checkbox" });
  return h("div", { class: "row" }, file, type, h("label", { class: "inline" }, share, " share with patient"),
    h("button", { class: "btn primary", type: "button", onclick: () => guarded(async () => {
      if (!file.files[0]) return toast("Choose a file first", true);
      const fd = new FormData(); fd.append("file", file.files[0]); fd.append("doc_type", type.value); fd.append("patient_visible", share.checked ? "1" : "0");
      await api("POST", `/api/patients/${id}/documents`, fd); toast("File stored"); reload();
    }) }, "Upload"));
}

// Hand-over of physical copies: record what has been printed, is ready, and who collected it.
function handover(id) {
  const box = h("div", { class: "grid" });
  const load = async () => {
    const d = await get(`/api/patients/${id}/deliverables`);
    const status = (r) => h("select", { "aria-label": "Printed copy status", onchange: (ev) => guarded(async () => {
      const body = { physical_status: ev.target.value };
      if (ev.target.value === "Handed over") { const who = window.prompt("Who received the printed copy? (name of the patient or their representative)"); if (!who) { load(); return; } body.received_by_name = who; }
      await patch(`/api/deliverables/${r.id}`, body); toast("Updated"); load();
    }) }, d.statuses.map((s) => h("option", { value: s, selected: s === r.physical_status }, s)));
    clear(box).append(card("Digital & physical copies given to the patient", h("div", null,
      table([{ label: "Item", key: "title" }, { label: "Kind", key: "kind" }, { label: "Digital", render: (r) => r.digital_available ? chip("available", "ok") : "—" },
        { label: "Print with QR", render: (r) => r.print_url ? h("a", { class: "btn sm", href: r.print_url, target: "_blank", rel: "noopener" }, "Print") : "—" },
        { label: "Printed copy", render: (r) => r.physical_status === "Handed over" ? h("span", null, chip("Handed over", "ok"), " ", h("span", { class: "small muted" }, `${r.received_by_name || ""} · ${fmt(r.handed_over_at)}`)) : status(r) }], d.items, "Nothing tracked yet. Released reports appear here automatically."),
      h("p", { class: "muted small" }, "Use “Print” to open a copy with a QR code that anyone can scan to confirm it is genuine, then record here when it is ready or collected."))));
  };
  load();
  return box;
}
