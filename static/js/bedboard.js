import { get } from "./api.js";
import { h, card, chip, fmt } from "./ui.js";
import { openPatientDrawer } from "./app.js";

export async function renderBedboard(setMain) {
  const d = await get("/api/bedboard");
  const root = h("div", { class: "grid" }, h("div", { class: "row between" }, h("h2", null, "Live bedboard"), h("span", { class: "muted small" }, "Updated " + fmt(d.generated_at))));
  root.append(h("div", { class: "grid g3" }, d.wards.map((w) => h("div", { class: "card stat" },
    h("b", null, `${w.occupied}/${w.total}`), h("span", null, `${w.ward} — ${w.occupancy_pct}% occupied`),
    h("span", { class: "small" }, `${w.available} available · ${w.cleaning} cleaning · ${w.reserved} reserved · ${w.maintenance} maintenance`)))));
  if (d.awaiting_bed.length) root.append(card("Admitted, awaiting a bed", h("ul", null, d.awaiting_bed.map((a) =>
    h("li", null, h("button", { class: "btn sm ghost", onclick: () => openPatientDrawer(a.patient_id) }, a.patient || `Admission ${a.admission_id}`), " ", chip(a.ward || "no ward", "warn"))))));
  const byWard = {};
  d.beds.forEach((b) => (byWard[b.ward] ||= []).push(b));
  Object.entries(byWard).forEach(([ward, beds]) => root.append(card(ward, h("div", { class: "beds" }, beds.map((b) => h("div", { class: "bed " + b.status },
    h("strong", null, `${b.room} · ${b.label}`), h("div", null, b.status),
    b.patient ? h("button", { onclick: () => openPatientDrawer(b.patient.id) }, b.patient.name) : null,
    b.status_note ? h("div", { class: "muted small" }, b.status_note) : null))))));
  setMain(root);
}
