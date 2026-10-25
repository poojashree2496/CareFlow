// Patient dashboard: read-only view of the patient's own released record, plus the assistant. No editing controls by design.
import { get } from "./api.js";
import { h, clear, card, table, chip, fmt } from "./ui.js";
import { mountAssistant } from "./assistant.js";

const money = (n) => (n ?? 0).toFixed(2);
const fileLinks = (files) => (files || []).length ? h("span", null, files.map((f) => h("a", { class: "btn sm", href: f.download_url, download: "", rel: "noopener" }, `Download ${f.title || "file"}`), " ")) : null;
const view = (f) => ["image/png", "image/jpeg", "application/pdf"].includes(f.mime_type) ? h("a", { class: "btn sm", href: f.download_url + "?inline=1", target: "_blank", rel: "noopener" }, "View") : null;

export async function renderPortal(setMain, user) {
  const d = await get("/api/portal/overview");
  const p = d.patient;
  const body = h("div");
  const tabsEl = h("div", { class: "tabs-sub", role: "tablist" });
  const pages = {
    Summary: () => summary(d),
    "My stay": () => stay(d),
    "Medicines": () => meds(d),
    "Results & scans": () => results(d),
    "Documents": () => documents(d),
    "Bills": () => bills(d),
    "Copies & hand-over": () => handover(d),
    "Ask CareFlow AI": () => h("div", null, h("p", { class: "muted" }, "The assistant explains your own record in plain language. It cannot change anything and never gives a diagnosis or prescription."), mountAssistant(user.patient_id, { name: p.name })),
  };
  const show = (n) => { [...tabsEl.children].forEach((b) => b.setAttribute("aria-current", b.textContent === n ? "page" : "false")); clear(body).append(pages[n]()); };
  Object.keys(pages).forEach((n) => tabsEl.append(h("button", { class: "tab", role: "tab", onclick: () => show(n) }, n)));
  setMain(h("div", { class: "grid" },
    h("div", null, h("h2", null, `Welcome, ${p.name}`), h("p", { class: "muted small" }, `${p.patient_code} · ${p.age ?? "?"} y · ${p.gender || ""} · ${p.blood_group || ""}`)),
    tabsEl, body));
  show("Summary");
}

function summary(d) {
  const s = d.stay;
  return h("div", { class: "grid g2" },
    card("Right now", s ? h("dl", { class: "kv" }, ...Object.entries({ "Ward / bed": `${s.ward || ""} ${s.bed || ""}`, "Admitted": s.admitted_on, "Doctor": s.doctor || s.responsible_doctor || "—", "Reason": s.reason || "—" }).flatMap(([k, v]) => [h("dt", null, k), h("dd", null, String(v ?? "—"))])) : h("div", { class: "empty" }, "You are not currently admitted.")),
    card("Care team", table([{ label: "Name", key: "name" }, { label: "Role", key: "role" }, { label: "Relation", key: "relation" }], d.care_team, "Your care team will appear here.")),
    card("Allergies", d.allergies.length ? h("ul", null, d.allergies.map((a) => h("li", null, `${a.substance}${a.reaction ? " — " + a.reaction : ""}`, " ", chip(a.severity || "", "warn")))) : h("div", { class: "empty" }, "None recorded.")),
    card("Conditions", table([{ label: "Condition", key: "description" }, { label: "Since", key: "onset_on" }], d.problems, "None recorded.")),
    card("Latest vital signs", d.vitals.items.length ? h("div", { class: "vitals" }, d.vitals.items.map((v) => h("div", { class: "vital" }, h("small", null, v.label), h("b", null, v.value), " ", h("span", null, v.unit), h("small", null, fmt(v.observed_at)), v.source === "simulated" ? chip("simulated", "sim") : null))) : h("div", { class: "empty" }, "No readings yet.")),
    card("Appointments & follow-up", h("div", null, table([{ label: "Date", key: "date" }, { label: "Time", key: "time" }, { label: "Doctor", key: "doctor" }, { label: "Status", render: (r) => chip(r.status) }], d.appointments, "No appointments."),
      d.follow_ups.length ? h("ul", null, d.follow_ups.map((f) => h("li", null, `${f.due_on}: ${f.instructions}`))) : null)));
}

function stay(d) {
  return h("div", { class: "grid" },
    card("Admissions", table([{ label: "Ward / bed", render: (r) => `${r.ward || ""} ${r.bed || ""}` }, { label: "Admitted", key: "admitted_on" }, { label: "Discharged", key: "discharged_on" }, { label: "Doctor", key: "doctor" }, { label: "Status", render: (r) => chip(r.status) }, { label: "Reason", key: "reason" }], d.admissions, "No admissions.")),
    ...d.admissions.filter((a) => a.discharge_summary || a.discharge_plan).map((a) => card(`Discharge information — ${a.admitted_on}`, h("div", null, a.discharge_summary ? h("p", { class: "pre" }, a.discharge_summary) : null, a.discharge_plan ? h("p", { class: "pre" }, a.discharge_plan) : null))),
    card("My details", h("dl", { class: "kv" }, ...Object.entries({ "Phone": d.patient.phone, "E-mail": d.patient.email, "Address": d.patient.address, "Emergency contact": [d.patient.emergency_contact, d.patient.emergency_contact_phone].filter(Boolean).join(" · "), "Insurance": [d.patient.insurance_provider, d.patient.insurance_policy_no].filter(Boolean).join(" · ") }).flatMap(([k, v]) => [h("dt", null, k), h("dd", null, v || "—")])),
      h("p", { class: "muted small" }, "To correct any detail, please speak to the front desk.")));
}

function meds(d) {
  return card("Medicines", table([{ label: "Medicine", key: "medicine" }, { label: "Dose", key: "dosage" }, { label: "How often", key: "frequency" }, { label: "Route", key: "route" },
    { label: "Prescribed by", key: "prescribed_by" }, { label: "Pharmacy", render: (r) => r.dispensed_quantity ? chip(`${r.dispensed_quantity} dispensed`, "ok") : chip(r.status) },
    { label: "Last dose", render: (r) => r.last_dose ? `${r.last_dose.status} · ${fmt(r.last_dose.at)}` : "—" }, { label: "Instructions", key: "instructions" }], d.medications, "No medicines recorded."));
}

function results(d) {
  return h("div", { class: "grid" },
    h("p", { class: "muted small" }, "Only results your care team has finished and released appear here. If you are expecting one that is missing, it is still being prepared."),
    card("Laboratory reports", d.labs.length ? h("div", { class: "grid" }, d.labs.map((l) => h("div", { class: "sub-card" },
      h("div", { class: "row between" }, h("strong", null, l.test_name), h("span", { class: "muted small" }, `Released ${fmt(l.released_at)}`)),
      l.results.length ? table([{ label: "Test", key: "analyte" }, { label: "Result", render: (r) => `${r.value ?? "—"} ${r.unit || ""}` }, { label: "Reference", key: "reference" }, { label: "Flag", render: (r) => r.flag ? chip(r.flag, "warn") : "" }], l.results) : (l.summary ? h("p", { class: "pre" }, l.summary) : null),
      h("div", { class: "row" }, (l.files || []).map((f) => h("span", null, view(f), " ", h("a", { class: "btn sm", href: f.download_url, download: "" }, `Download ${f.title}`))))))) : h("div", { class: "empty" }, "No released lab reports yet.")),
    card("Scans & imaging reports", d.radiology.length ? h("div", { class: "grid" }, d.radiology.map((r) => h("div", { class: "sub-card" },
      h("div", { class: "row between" }, h("strong", null, `${r.modality} — ${r.description || ""}`), h("span", { class: "muted small" }, fmt(r.reported_at))),
      r.findings ? h("p", { class: "pre" }, h("b", null, "Findings: "), r.findings) : null, r.impression ? h("p", { class: "pre" }, h("b", null, "Impression: "), r.impression) : null,
      r.recommendations ? h("p", { class: "pre" }, h("b", null, "Recommendations: "), r.recommendations) : null,
      h("div", { class: "row" }, (r.files || []).map((f) => h("span", null, view(f), " ", h("a", { class: "btn sm", href: f.download_url, download: "" }, `Download ${f.title}`))))))) : h("div", { class: "empty" }, "No final imaging reports yet.")));
}

function documents(d) {
  return card("Documents shared with you", table([{ label: "Title", key: "title" }, { label: "Type", key: "doc_type" }, { label: "Added", render: (r) => fmt(r.uploaded_at) },
    { label: "", render: (r) => h("span", null, view(r), " ", h("a", { class: "btn sm", href: r.download_url, download: "" }, "Download")) }], d.documents, "Nothing has been shared with you yet."));
}

function bills(d) {
  return h("div", { class: "grid" }, d.bills.length ? d.bills.map((b) => card(b.description || `Bill #${b.id}`, h("div", null,
    h("dl", { class: "kv" }, h("dt", null, "Total"), h("dd", null, money(b.total)), h("dt", null, "Paid"), h("dd", null, money(b.paid)), h("dt", null, "Balance"), h("dd", null, h("b", null, money(b.balance))),
      h("dt", null, "Insurance"), h("dd", null, `${b.insurance_provider || "—"} · ${b.insurance_status || "—"}`)),
    b.payments.length ? table([{ label: "Payment", key: "kind" }, { label: "Amount", render: (x) => money(x.amount) }, { label: "Method", key: "method" }, { label: "Date", render: (x) => fmt(x.at) }], b.payments) : null))) : [h("div", { class: "empty" }, "No bills.")]);
}

function handover(d) {
  return card("Everything the hospital provides — download or print your copies", h("div", null,
    h("p", { class: "muted small" }, "Tap “Download / print” to get your own copy now (you can print it or save it as a PDF). You can also collect an official printed copy from the hospital — the last two columns show its status."),
    table([{ label: "Item", key: "title" }, { label: "Kind", key: "kind" },
      { label: "Download / print", render: (r) => (r.digital_available || r.document) ? h("a", { class: "btn sm primary", href: r.copy_url, target: "_blank", rel: "noopener" }, "Download / print") : chip("not ready yet", "") },
      { label: "Official printed copy", render: (r) => chip(r.physical_status, r.physical_status === "Handed over" ? "ok" : r.physical_status === "Ready for collection" ? "warn" : "") },
      { label: "Received by", render: (r) => r.physical_status === "Handed over" ? `${r.received_by_name || ""} · ${fmt(r.handed_over_at)}` : "—" }], d.deliverables, "Nothing recorded yet.")));
}
