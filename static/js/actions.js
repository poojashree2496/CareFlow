// Role actions: small dialogs that call the server. The server re-checks every permission; the UI only hides what a role cannot do.
import { post, api } from "./api.js";
import { h, field, toast } from "./ui.js";

export const can = (user, perm) => (user?.permissions || []).includes(perm);

export function modal(title, body, { onSubmit, submitLabel = "Save" } = {}) {
  const back = h("div", { class: "modal-back", role: "dialog", "aria-modal": "true", "aria-label": title });
  const err = h("p", { class: "form-error", role: "alert" });
  const close = () => { back.remove(); document.removeEventListener("keydown", esc); };
  const esc = (e) => { if (e.key === "Escape") close(); };
  const btn = h("button", { class: "btn primary", type: "submit" }, submitLabel);
  const form = h("form", { class: "modal", onsubmit: async (ev) => {
    ev.preventDefault(); err.textContent = ""; btn.disabled = true;
    try { const r = await onSubmit(form); close(); return r; }
    catch (e) { err.textContent = e.message || "Could not save"; btn.disabled = false; }
  } }, h("h2", null, title), body, err,
  h("div", { class: "row between" }, h("button", { class: "btn", type: "button", onclick: close }, "Cancel"), btn));
  back.append(form);
  document.body.append(back);
  document.addEventListener("keydown", esc);
  form.querySelector("input,textarea,select")?.focus();
  return close;
}

const upload = (pid, file, fields) => {
  const fd = new FormData();
  fd.append("file", file);
  Object.entries(fields).forEach(([k, v]) => fd.append(k, v));
  return api("POST", `/api/patients/${pid}/documents`, fd);
};
const ACCEPT = ".pdf,.png,.jpg,.jpeg,.txt";

// Laboratory: attach the report file and submit -> the order is completed and released to doctors, admins and the patient.
export function submitLab(row, done) {
  const file = h("input", { type: "file", name: "file", accept: ACCEPT });
  modal(`Submit laboratory report — ${row.test}`, h("div", null,
    h("p", { class: "muted small" }, `Patient: ${row.patient}. Submitting marks the order complete and releases the report to the patient's doctors, administrators and the patient.`),
    field("Report file (PDF, image or text)", file)),
  { submitLabel: "Complete & submit", onSubmit: async () => {
    if (file.files[0]) await upload(row.patient_id, file.files[0], { doc_type: "Laboratory report", lab_report_id: row.id, title: `${row.test} report` });
    const r = await post(`/api/labs/${row.id}/submit`, {});
    toast(r.message || "Submitted"); done?.();
  } });
}

// Radiology: findings (required) + optional scan/report file.
export function submitRadiology(row, done) {
  const f = {
    file: h("input", { type: "file", accept: ".pdf,.png,.jpg,.jpeg" }),
    findings: h("textarea", { rows: 5, required: true, maxlength: 8000 }),
    impression: h("textarea", { rows: 2, maxlength: 3000 }),
    recommendations: h("textarea", { rows: 2, maxlength: 3000 }),
    urgent: h("input", { type: "checkbox" }),
  };
  modal(`Report & submit — ${row.modality || "study"}`, h("div", null,
    h("p", { class: "muted small" }, `Patient: ${row.patient}. Submitting finalises the report and releases it to doctors, administrators and the patient.`),
    field("Scan image or report file (optional)", f.file), field("Findings (required)", f.findings), field("Impression", f.impression),
    field("Recommendations", f.recommendations), h("label", null, f.urgent, " Urgent finding — start the acknowledgment workflow")),
  { submitLabel: "Complete & submit", onSubmit: async () => {
    if (f.file.files[0]) await upload(row.patient_id, f.file.files[0], { doc_type: "Radiology report", radiology_id: row.id, title: `${row.modality || "Imaging"} report` });
    const r = await post(`/api/radiology/${row.id}/submit`, { findings: f.findings.value, impression: f.impression.value, recommendations: f.recommendations.value, urgent_finding: f.urgent.checked });
    toast(r.message || "Submitted"); done?.();
  } });
}

export function pharmacyAct(row, done) {
  const qty = h("input", { type: "number", min: 1, value: row.quantity || 1 });
  const verify = row.status === "Ordered";
  modal(`${verify ? "Verify" : "Dispense"} — ${row.medicine}`, h("div", null,
    h("p", { class: "muted small" }, `Patient: ${row.patient}. ${(row.warnings || []).length ? "Review the warnings in the patient record before continuing." : ""}`),
    verify ? h("p", null, "Verify this order after checking dose, interactions and allergies.") : field("Quantity to dispense", qty)),
  { submitLabel: verify ? "Verify order" : "Dispense", onSubmit: async () => {
    const r = verify ? await post(`/api/prescriptions/${row.id}/verify`, {})
      : await post(`/api/prescriptions/${row.id}/dispense`, { quantity: Number(qty.value), acknowledged_warnings: row.warnings || [] });
    toast(r.message || "Saved"); done?.();
  } });
}

export function recordVitals(patientId, name, done) {
  const keys = [["heart_rate", "Heart rate (bpm)"], ["bp_systolic", "BP systolic"], ["bp_diastolic", "BP diastolic"], ["spo2", "SpO2 (%)"], ["temperature", "Temperature (°C)"], ["resp_rate", "Respiratory rate"]];
  const inputs = Object.fromEntries(keys.map(([k]) => [k, h("input", { type: "number", step: "any" })]));
  modal(`Record vital signs — ${name}`, h("div", { class: "grid g2" }, keys.map(([k, l]) => field(l, inputs[k]))),
    { submitLabel: "Record", onSubmit: async () => {
      const values = {};
      keys.forEach(([k]) => { if (inputs[k].value !== "") values[k] = Number(inputs[k].value); });
      if (!Object.keys(values).length) throw new Error("Enter at least one reading");
      const r = await post(`/api/patients/${patientId}/observations`, { values });
      toast(r.message || "Recorded"); done?.();
    } });
}

export function addNote(patientId, name, types, done) {
  const t = h("select", null, types.map((x) => h("option", { value: x }, x)));
  const body = h("textarea", { rows: 6, required: true, maxlength: 8000 });
  modal(`Add clinical note — ${name}`, h("div", null, field("Note type", t), field("Note", body),
    h("p", { class: "muted small" }, "Notes are append-only. Corrections are made as amendments.")),
  { submitLabel: "Save note", onSubmit: async () => { await post(`/api/patients/${patientId}/notes`, { note_type: t.value, body: body.value }); toast("Note saved"); done?.(); } });
}

export function takePayment(row, done) {
  const amt = h("input", { type: "number", step: "0.01", min: "0.01", value: row.total, required: true });
  const method = h("select", null, ["Cash", "Card", "UPI", "Bank transfer", "Insurance"].map((m) => h("option", null, m)));
  const ref = h("input", { maxlength: 80 });
  modal(`Record payment — ${row.patient}`, h("div", null, h("p", { class: "muted small" }, row.description), field("Amount", amt), field("Method", method), field("Reference", ref)),
    { submitLabel: "Record payment", onSubmit: async () => { await post(`/api/bills/${row.id}/payments`, { amount: Number(amt.value), method: method.value, reference: ref.value }); toast("Payment recorded"); done?.(); } });
}

export function createPatientLogin(patient, done) {
  const email = h("input", { type: "email", required: true, value: patient.email || "" });
  const pw = h("input", { type: "text", required: true, minlength: 12, autocomplete: "off" });
  modal(`Create portal login — ${patient.name}`, h("div", null,
    h("p", { class: "muted small" }, "The patient will see only their own released records and the assistant. They must change this temporary password at first sign-in. Hand it over in person or by phone — never by unencrypted message."),
    field("Patient's sign-in e-mail", email), field("Temporary password (12+ characters)", pw)),
  { submitLabel: "Create login", onSubmit: async () => {
    await post("/api/admin/users", { email: email.value, name: patient.name, role: "patient", patient_id: patient.id, password: pw.value });
    toast("Portal login created"); done?.();
  } });
}

// ---- Administrators: add any account (a super administrator may also add administrators); delete = erase if unused, otherwise disable.
export function addUser(done) {
  const privileged = can(window.__user, "user.manage_privileged");
  const f = { name: h("input", { required: true, maxlength: 120 }), email: h("input", { type: "email", required: true }), pw: h("input", { required: true, minlength: 12, autocomplete: "off" }),
    role: h("select", null), ward: h("select", null), doc: h("select", null), spec: h("input", { placeholder: "Specialty (for a new doctor profile)" }), patient: h("select", null) };
  const extra = h("div");
  const roles = [["doctor", "Doctor"], ["nurse", "Nurse"], ["lab_staff", "Laboratory staff"], ["pharmacist", "Pharmacist"], ["radiology_staff", "Radiology staff"], ["billing_staff", "Billing staff"], ["patient", "Patient (portal login)"]]
    .concat(privileged ? [["hospital_admin", "Hospital administrator"], ["super_admin", "Super administrator"]] : []);
  roles.forEach(([v, l]) => f.role.append(h("option", { value: v }, l)));
  const draw = () => {
    extra.replaceChildren();
    if (f.role.value === "doctor") extra.append(field("Doctor profile", f.doc), field("…or create a new profile", f.spec));
    if (f.role.value === "nurse") extra.append(field("Ward (optional)", f.ward));
    if (f.role.value === "patient") extra.append(field("Patient record", f.patient));
  };
  f.role.addEventListener("change", draw);
  Promise.all([api("GET", "/api/doctors"), api("GET", "/api/facilities"), api("GET", "/api/patients?per_page=100")]).then(([d, w, p]) => {
    f.doc.append(h("option", { value: "" }, "Choose…"), ...d.items.map((x) => h("option", { value: x.id }, `${x.name} · ${x.specialty}`)));
    f.ward.append(h("option", { value: "" }, "None"), ...w.wards.map((x) => h("option", { value: x.id }, x.name)));
    f.patient.append(h("option", { value: "" }, "Choose…"), ...p.items.map((x) => h("option", { value: x.id }, `${x.name} · ${x.patient_code}`)));
  }).catch(() => {});
  draw();
  modal("Add account", h("div", null, field("Role", f.role), field("Full name", f.name), field("E-mail (used to sign in)", f.email), field("Temporary password (12+ characters)", f.pw), extra,
    h("p", { class: "muted small" }, "The person must change this password at first sign-in. Share it in person or by phone, not in writing.")),
  { submitLabel: "Create account", onSubmit: async () => {
    const body = { name: f.name.value, email: f.email.value, password: f.pw.value, role: f.role.value };
    if (body.role === "doctor") {
      if (f.doc.value) body.doctor_id = Number(f.doc.value);
      else if (f.spec.value.trim()) body.doctor_id = (await post("/api/doctors", { name: f.name.value, specialty: f.spec.value })).id;
      else throw new Error("Choose a doctor profile or enter a specialty to create one");
    }
    if (body.role === "nurse" && f.ward.value) body.ward_id = Number(f.ward.value);
    if (body.role === "patient") { if (!f.patient.value) throw new Error("Choose the patient record"); body.patient_id = Number(f.patient.value); }
    await post("/api/admin/users", body); toast("Account created"); done?.();
  } });
}

// ---- Register a new patient (administrators, doctors, nurses).
export function registerPatient(done) {
  const f = { name: h("input", { required: true, maxlength: 120 }), dob: h("input", { type: "date" }), gender: h("select", null, ["Female", "Male", "Other", "Not specified"].map((x) => h("option", null, x))),
    blood: h("select", null, ["", "A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"].map((x) => h("option", { value: x }, x || "Unknown"))),
    phone: h("input", { type: "tel", maxlength: 30 }), email: h("input", { type: "email", maxlength: 120 }), address: h("textarea", { rows: 2, maxlength: 400 }),
    ec: h("input", { maxlength: 120 }), ecp: h("input", { type: "tel", maxlength: 30 }) };
  const submit = async (confirm) => {
    const body = { name: f.name.value, gender: f.gender.value, phone: f.phone.value, email: f.email.value, address: f.address.value, emergency_contact: f.ec.value, emergency_contact_phone: f.ecp.value };
    if (f.dob.value) body.dob = f.dob.value;
    if (f.blood.value) body.blood_group = f.blood.value;
    if (confirm) body.confirm_duplicate = true;
    try { const r = await post("/api/patients", body); toast(`Registered ${r.patient_code}`); done?.(r); }
    catch (e) { if (e.status === 409 && window.confirm(e.message)) return submit(true); throw e; }
  };
  modal("Register patient", h("div", { class: "grid g2" }, field("Full name", f.name), field("Date of birth", f.dob), field("Gender", f.gender), field("Blood group", f.blood), field("Phone", f.phone), field("E-mail", f.email),
    h("div", { style: "grid-column:1/-1" }, field("Address", f.address)), field("Emergency contact", f.ec), field("Emergency phone", f.ecp)),
  { submitLabel: "Register patient", onSubmit: () => submit(false) });
}
