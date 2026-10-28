// Data-entry dialogs for clinicians: allergies, problems, lab / imaging / medication orders, admission, bed moves, discharge, appointments.
// Each dialog only calls an API route that already exists; the server re-checks every permission and every rule. The UI merely hides what a role cannot do.
import { get, post, patch } from "./api.js";
import { h, field, toast } from "./ui.js";
import { modal } from "./actions.js";

const today = () => new Date().toLocaleDateString("en-CA");   // YYYY-MM-DD in the browser's local time
const options = (items, pick) => items.map((x) => h("option", { value: pick(x)[0], selected: pick(x)[2] || false }, pick(x)[1]));
const val = (el) => (el.value || "").trim();
const when = (done, msg) => (r) => { toast(msg || r?.message || "Saved"); done?.(r); };

// ---- Allergy -----------------------------------------------------------------------------------------------------------------
export function addAllergy(pid, name, done) {
  const f = { substance: h("input", { required: true, maxlength: 120, placeholder: "e.g. Penicillin" }), reaction: h("input", { maxlength: 200, placeholder: "e.g. rash, anaphylaxis" }),
    severity: h("select", null, ["Unknown", "Mild", "Moderate", "Severe"].map((x) => h("option", null, x))) };
  modal(`Add allergy — ${name}`, h("div", null, field("Allergic to (substance or drug)", f.substance), field("Reaction", f.reaction), field("Severity", f.severity)),
    { submitLabel: "Save allergy", onSubmit: async () => when(done, "Allergy recorded")(await post(`/api/patients/${pid}/allergies`, { substance: val(f.substance), reaction: val(f.reaction), severity: f.severity.value })) });
}

// ---- Problem -----------------------------------------------------------------------------------------------------------------
export function addProblem(pid, name, done) {
  const f = { description: h("input", { required: true, maxlength: 300, placeholder: "e.g. Type 2 diabetes mellitus" }), code: h("input", { maxlength: 30, placeholder: "ICD code (optional)" }),
    onset: h("input", { type: "date", max: today() }) };
  modal(`Add problem — ${name}`, h("div", null, field("Problem / diagnosis (as recorded by the clinician)", f.description), field("Code", f.code), field("Since", f.onset)),
    { submitLabel: "Save problem", onSubmit: async () => {
      const body = { description: val(f.description), code: val(f.code) };
      if (f.onset.value) body.onset_on = f.onset.value;
      when(done, "Problem added")(await post(`/api/patients/${pid}/problems`, body));
    } });
}
export const setProblemStatus = (id, status, done) => patch(`/api/problems/${id}`, { status }).then(when(done, "Problem updated"));

// ---- Laboratory order --------------------------------------------------------------------------------------------------------
const COMMON_TESTS = ["Complete blood count", "Basic metabolic panel", "Liver function tests", "Renal function tests", "Lipid profile", "HbA1c", "Fasting blood glucose", "Thyroid profile (TSH)",
  "Urinalysis", "Coagulation profile (PT/INR)", "Troponin", "C-reactive protein", "Serum electrolytes", "Blood culture"];
export function orderLab(pid, name, done) {
  const list = h("datalist", { id: "lab-tests" }, COMMON_TESTS.map((t) => h("option", { value: t })));
  const f = { test: h("input", { required: true, maxlength: 120, list: "lab-tests", placeholder: "Choose or type a test" }),
    priority: h("select", null, ["Routine", "Urgent", "STAT"].map((x) => h("option", null, x))), specimen: h("input", { maxlength: 60, placeholder: "e.g. Blood, Urine" }),
    info: h("textarea", { rows: 2, maxlength: 300, placeholder: "Why is this test needed?" }), date: h("input", { type: "date", value: today() }) };
  modal(`Order laboratory test — ${name}`, h("div", null, list, field("Test", f.test), field("Priority", f.priority), field("Specimen", f.specimen), field("Clinical information", f.info), field("Sample date", f.date)),
    { submitLabel: "Place order", onSubmit: async () => when(done, "Lab test ordered")(await post("/api/labs", { patient_id: pid, test_name: val(f.test), priority: f.priority.value, specimen_type: val(f.specimen), clinical_info: val(f.info), sample_date: f.date.value })) });
}

// ---- Imaging order -----------------------------------------------------------------------------------------------------------
const MODALITIES = ["X-ray", "CT", "MRI", "Ultrasound", "Mammography", "Fluoroscopy", "Nuclear medicine", "Other"];
export function orderRadiology(pid, name, done) {
  const f = { modality: h("select", null, MODALITIES.map((x) => h("option", null, x))), study: h("input", { maxlength: 200, placeholder: "e.g. Chest, PA view" }),
    indication: h("textarea", { rows: 2, maxlength: 300, placeholder: "Clinical question / reason" }), priority: h("select", null, ["Routine", "Urgent", "STAT"].map((x) => h("option", null, x))),
    date: h("input", { type: "date", value: today() }) };
  modal(`Order imaging — ${name}`, h("div", null, field("Study type", f.modality), field("Body part / description", f.study), field("Indication", f.indication), field("Priority", f.priority), field("Study date", f.date)),
    { submitLabel: "Place order", onSubmit: async () => when(done, "Imaging study ordered")(await post("/api/radiology", { patient_id: pid, modality: f.modality.value, study_description: val(f.study), indication: val(f.indication), priority: f.priority.value, study_date: f.date.value })) });
}

// ---- Prescription (allergy / duplicate warnings must be acknowledged with a reason) ------------------------------------------
export function prescribe(pid, name, done) {
  const meds = h("select", null, h("option", { value: "" }, "Loading medicines…"));
  const f = { other: h("input", { maxlength: 120, placeholder: "Medicine name (if not in the list)" }), dose: h("input", { maxlength: 120, placeholder: "e.g. 500 mg" }),
    route: h("select", null, ["", "Oral", "IV", "IM", "SC", "Topical", "Inhaled", "Other"].map((x) => h("option", { value: x }, x || "—"))), freq: h("input", { maxlength: 60, placeholder: "e.g. twice daily" }),
    days: h("input", { type: "number", min: 1, max: 365 }), qty: h("input", { type: "number", min: 1 }), instr: h("textarea", { rows: 2, maxlength: 1000 }), prn: h("input", { type: "checkbox" }),
    override: h("input", { maxlength: 300, placeholder: "Reason for overriding the warning (at least 10 characters)" }) };
  const warn = h("div", { class: "form-error", role: "alert" });
  const overrideBox = h("div", { hidden: true }, field("Override reason", f.override));
  const byId = {};
  get("/api/medicines").then((d) => { d.items.forEach((m) => { byId[m.id] = m.name; }); meds.replaceChildren(h("option", { value: "" }, "Other (type the name below)"), ...d.items.filter((m) => m.is_active && !m.expired)
    .map((m) => h("option", { value: m.id }, `${m.name}${m.strength ? " " + m.strength : ""}${m.form ? " · " + m.form : ""}${m.in_stock ? "" : " (out of stock)"}`))); }).catch(() => meds.replaceChildren(h("option", { value: "" }, "Other (type the name below)")));
  modal(`Prescribe — ${name}`, h("div", null, field("Medicine", meds), field("…or other medicine", f.other), h("div", { class: "grid g2" }, field("Dose", f.dose), field("Route", f.route), field("Frequency", f.freq), field("Duration (days)", f.days), field("Quantity", f.qty),
    h("label", { class: "inline" }, f.prn, " as needed (PRN)")), field("Instructions", f.instr), warn, overrideBox,
  h("p", { class: "muted small" }, "The pharmacist verifies and dispenses the order. Recorded allergies and duplicate orders are checked automatically.")),
  { submitLabel: "Place order", onSubmit: async () => {
    const body = { patient_id: pid, dosage: val(f.dose), route: f.route.value, frequency: val(f.freq), instructions: val(f.instr), is_prn: f.prn.checked };
    if (meds.value) { body.medicine_id = Number(meds.value); body.medicine = byId[meds.value] || ""; } else body.medicine = val(f.other);
    if (!body.medicine_id && !body.medicine) throw new Error("Choose a medicine or type its name");
    if (f.days.value) body.duration_days = Number(f.days.value);
    if (f.qty.value) body.quantity = Number(f.qty.value);
    if (val(f.override)) body.override_reason = val(f.override);
    try { when(done, "Medication ordered")(await post("/api/prescriptions", body)); }
    catch (e) {
      if (e.status === 409 && (e.body.warnings || []).length) {
        warn.replaceChildren(...e.body.warnings.map((w) => h("div", null, "⚠ " + w.message)));
        overrideBox.hidden = false; f.override.focus();
        throw new Error("Review the warning above. To continue anyway, enter an override reason and press the button again.");
      }
      throw e;
    }
  } });
}

// ---- Admission / bed moves / discharge ---------------------------------------------------------------------------------------
const bedLabel = (w, b) => `${w.name} · ${b.code}`;
const freeBeds = (wards) => wards.flatMap((w) => w.beds.filter((b) => b.is_active && b.status === "Available").map((b) => ({ ward: w, bed: b })));

export function admitPatient(pid, name, user, done) {
  const patient = h("select", { required: true }, h("option", { value: "" }, "Choose a patient…"));
  const ward = h("select", null), bed = h("select", null), doctor = h("select", null);
  const f = { reason: h("textarea", { rows: 2, maxlength: 1000 }), exp: h("input", { type: "date", min: today() }), notes: h("textarea", { rows: 2, maxlength: 2000 }) };
  let wards = [];
  const drawBeds = () => { const w = wards.find((x) => String(x.id) === ward.value); bed.replaceChildren(h("option", { value: "" }, "No bed yet (assign later)"),
    ...(w ? w.beds.filter((b) => b.is_active && b.status === "Available").map((b) => h("option", { value: b.id }, `${b.code} (${b.status})`)) : [])); };
  ward.addEventListener("change", drawBeds);
  Promise.all([get("/api/facilities"), get("/api/doctors"), pid ? null : get("/api/patients?per_page=100")]).then(([fa, dr, pl]) => {
    wards = fa.wards.filter((w) => w.is_active);
    ward.replaceChildren(...wards.map((w) => h("option", { value: w.id }, `${w.name} — ${w.beds.filter((b) => b.is_active && b.status === "Available").length} bed(s) free`)));
    doctor.replaceChildren(h("option", { value: "" }, "—"), ...dr.items.map((d) => h("option", { value: d.id, selected: d.id === user?.doctor_id }, `${d.name} · ${d.specialty}`)));
    if (pl) patient.append(...pl.items.map((p) => h("option", { value: p.id }, `${p.name} · ${p.patient_code}`)));
    drawBeds();
  }).catch(() => {});
  modal(pid ? `Admit — ${name}` : "Admit patient", h("div", null, pid ? null : field("Patient", patient), field("Ward", ward), field("Bed", bed), field("Responsible doctor", doctor), field("Reason for admission", f.reason),
    field("Expected discharge", f.exp), field("Notes", f.notes)),
  { submitLabel: "Admit", onSubmit: async () => {
    const id = pid || Number(patient.value);
    if (!id) throw new Error("Choose a patient");
    const w = wards.find((x) => String(x.id) === ward.value);
    const body = { patient_id: id, reason: val(f.reason), notes: val(f.notes), ward: w?.name || "" };
    if (bed.value) body.bed_id = Number(bed.value);
    if (doctor.value) body.doctor_id = Number(doctor.value);
    if (f.exp.value) body.expected_discharge_on = f.exp.value;
    when(done, "Admission recorded")(await post("/api/admissions", body));
  } });
}

// assign a first bed, or transfer when the patient already has one
export function moveBed(stay, name, done) {
  const hasBed = !!stay.bed;
  const bed = h("select", { required: true }, h("option", { value: "" }, "Loading beds…")), note = h("input", { maxlength: 300 });
  get("/api/facilities").then((fa) => { bed.replaceChildren(h("option", { value: "" }, "Choose a free bed…"), ...freeBeds(fa.wards).map(({ ward, bed: b }) => h("option", { value: b.id }, bedLabel(ward, b)))); }).catch(() => {});
  modal(`${hasBed ? "Transfer" : "Assign bed"} — ${name}`, h("div", null, hasBed ? h("p", { class: "muted small" }, `Currently in ${stay.ward}, bed ${stay.bed.code}. The old bed goes to cleaning.`) : null,
    field("New bed", bed), field(hasBed ? "Reason for transfer" : "Note", note)),
  { submitLabel: hasBed ? "Transfer" : "Assign", onSubmit: async () => {
    if (!bed.value) throw new Error("Choose a bed");
    const r = await post(`/api/admissions/${stay.admission_id}/${hasBed ? "transfer" : "assign-bed"}`, hasBed ? { bed_id: Number(bed.value), reason: val(note) } : { bed_id: Number(bed.value), note: val(note) });
    when(done)(r);
  } });
}

export function planDischarge(stay, name, done) {
  const plan = h("textarea", { rows: 4, required: true, maxlength: 3000 }, stay.discharge_plan || ""), exp = h("input", { type: "date", value: stay.expected_discharge_on || "", min: today() });
  modal(`Plan discharge — ${name}`, h("div", null, field("Discharge plan (follow-up, medicines, instructions)", plan), field("Expected discharge date", exp)),
    { submitLabel: "Save plan", onSubmit: async () => when(done, "Discharge plan saved")(await post(`/api/admissions/${stay.admission_id}/discharge/plan`, { plan: val(plan), expected_discharge_on: exp.value })) });
}
export function authorizeDischarge(stay, name, done) {
  const sum = h("textarea", { rows: 6, required: true, maxlength: 8000 }, stay.discharge_summary || "");
  modal(`Authorize discharge — ${name}`, h("div", null, h("p", { class: "muted small" }, "Only the responsible clinician authorizes. The summary is given to the patient."), field("Discharge summary", sum)),
    { submitLabel: "Authorize", onSubmit: async () => when(done, "Discharge authorized")(await post(`/api/admissions/${stay.admission_id}/discharge/authorize`, { summary: val(sum) })) });
}
export function completeDischarge(stay, name, done) {
  modal(`Complete discharge — ${name}`, h("p", null, `Discharge ${name} now? The bed (${stay.bed?.code || "none"}) moves to cleaning, open care tasks are cancelled and open alerts are closed.`),
    { submitLabel: "Discharge patient", onSubmit: async () => when(done, "Patient discharged")(await post(`/api/admissions/${stay.admission_id}/discharge/complete`, {})) });
}

// ---- Appointment -------------------------------------------------------------------------------------------------------------
export function bookAppointment(preset, user, done) {
  const patient = h("select", { required: true }, h("option", { value: "" }, "Choose a patient…")), doctor = h("select", { required: true }), date = h("input", { type: "date", min: today(), value: today(), required: true });
  const time = h("input", { type: "time", required: true }), hint = h("p", { class: "muted small" }), reason = h("input", { maxlength: 300 });
  const type = h("select", null, ["Consultation", "Follow-up", "Check-up", "Procedure"].map((x) => h("option", null, x)));
  const slots = async () => {
    if (!doctor.value || !date.value) return;
    try { const s = await get(`/api/doctors/${doctor.value}/slots?date=${date.value}`); hint.textContent = `Hours ${s.day_start}–${s.day_end}. ${s.booked.length ? "Already booked: " + s.booked.join(", ") : "No bookings yet that day."}`; } catch { hint.textContent = ""; }
  };
  doctor.addEventListener("change", slots); date.addEventListener("change", slots);
  Promise.all([get("/api/doctors"), preset?.patient_id ? null : get("/api/patients?per_page=100")]).then(([dr, pl]) => {
    doctor.replaceChildren(...dr.items.filter((d) => d.available).map((d) => h("option", { value: d.id, selected: d.id === user?.doctor_id }, `${d.name} · ${d.specialty}`)));
    if (pl) patient.append(...pl.items.map((p) => h("option", { value: p.id }, `${p.name} · ${p.patient_code}`)));
    slots();
  }).catch(() => {});
  modal(preset?.patient_name ? `Book appointment — ${preset.patient_name}` : "Book appointment", h("div", null, preset?.patient_id ? null : field("Patient", patient), field("Doctor", doctor), h("div", { class: "grid g2" }, field("Date", date), field("Time", time)),
    hint, field("Visit type", type), field("Reason", reason)),
  { submitLabel: "Book", onSubmit: async () => {
    const id = preset?.patient_id || Number(patient.value);
    if (!id) throw new Error("Choose a patient");
    when(done, "Appointment booked")(await post("/api/appointments", { patient_id: id, doctor_id: Number(doctor.value), appointment_date: date.value, appointment_time: time.value, reason: val(reason), visit_type: type.value }));
  } });
}
export const appointmentAction = (id, what, done) => what === "cancel"
  ? (window.confirm("Cancel this appointment?") ? patch(`/api/appointments/${id}`, { status: "Cancelled", cancel_reason: window.prompt("Reason for cancelling:") || "Cancelled by staff" }).then(when(done, "Appointment cancelled")) : null)
  : post(`/api/appointments/${id}/${what}`, {}).then(when(done));
