import { get } from "./api.js";
import { h, card, table, chip, field } from "./ui.js";
import { openPatientDrawer } from "./app.js";
import { mountAssistant } from "./assistant.js";
import { can, registerPatient } from "./actions.js";
import { state } from "./app.js";

export async function renderPatients(setMain) {
  const list = h("div");
  const q = h("input", { type: "search", placeholder: "Search by name or patient code", "aria-label": "Search patients" });
  const load = async () => {
    const d = await get("/api/patients?per_page=50&q=" + encodeURIComponent(q.value.trim()));
    list.replaceChildren(table([
      { label: "Patient", render: (p) => h("button", { class: "btn sm ghost", onclick: () => openPatientDrawer(p.id) }, p.name) },
      { label: "Code", key: "patient_code" }, { label: "Age", key: "age" }, { label: "Sex", key: "gender" },
      { label: "", render: (p) => p.data_origin !== "real" ? chip(p.data_origin, "sim") : "" },
    ], d.items, "No patients you are authorised to see match this search."),
    h("p", { class: "muted small" }, `${d.total} patient(s) visible to you. You only see patients you have a care relationship with.`));
  };
  let t; q.addEventListener("input", () => { clearTimeout(t); t = setTimeout(load, 250); });
  setMain(h("div", { class: "grid" }, h("div", { class: "row between" }, h("h2", null, "Patients"), can(state.user, "patient.register") ? h("button", { class: "btn primary", onclick: () => registerPatient((r) => { load(); if (r?.id) openPatientDrawer(r.id); }) }, "+ Register patient") : null), q, list));
  await load();
}

export async function renderAppointments(setMain) {
  const d = await get("/api/appointments");
  setMain(h("div", { class: "grid" }, h("h2", null, "Appointments"), card("Schedule", table([
    { label: "Date", key: "date" }, { label: "Time", key: "time" },
    { label: "Patient", render: (a) => a.patient_id ? h("button", { class: "btn sm ghost", onclick: () => openPatientDrawer(a.patient_id) }, a.patient_name) : h("span", { class: "muted" }, "Restricted") },
    { label: "Doctor", render: (a) => a.doctor_name || "—" }, { label: "Status", render: (a) => chip(a.status) },
  ], d.items, "No appointments."))));
}

export async function renderAi(setMain) {
  const box = h("div"), pick = h("select", { "aria-label": "Patient" });
  const d = await get("/api/patients?per_page=100");
  pick.append(h("option", { value: "" }, "Choose a patient…"), ...d.items.map((p) => h("option", { value: p.id }, `${p.name} · ${p.patient_code}`)));
  pick.addEventListener("change", () => {
    const p = d.items.find((x) => String(x.id) === pick.value);
    box.replaceChildren(p ? mountAssistant(p.id, p) : "");
  });
  setMain(h("div", { class: "grid" }, h("h2", null, "CareFlow AI"),
    h("p", { class: "muted" }, "Answers are built only from records you are authorised to see for the selected patient, cite their sources, and are never a diagnosis or prescription."),
    field("Patient", pick), box));
}
