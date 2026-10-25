// DOM helpers. Everything is built with textContent — server data is never injected as HTML.
export function h(tag, attrs, ...kids) {
  const n = document.createElement(tag);
  if (attrs) for (const [k, v] of Object.entries(attrs)) {
    if (v === undefined || v === null || v === false) continue;
    if (k === "class") n.className = v;
    else if (k.startsWith("on") && typeof v === "function") n.addEventListener(k.slice(2), v);
    else if (k === "text") n.textContent = v;
    else n.setAttribute(k, v === true ? "" : v);
  }
  for (const kid of kids.flat()) {
    if (kid === null || kid === undefined || kid === false) continue;
    n.append(kid.nodeType ? kid : document.createTextNode(String(kid)));
  }
  return n;
}
export const clear = (n) => { while (n.firstChild) n.removeChild(n.firstChild); return n; };
export const fmt = (iso) => {
  if (!iso) return "—";
  const d = new Date(iso);
  return isNaN(d) ? String(iso) : d.toLocaleString([], { dateStyle: "medium", timeStyle: "short" });
};
export const ago = (min) => min == null ? "no data" : min < 1 ? "just now" : min < 90 ? `${Math.round(min)} min ago` : `${(min / 60).toFixed(1)} h ago`;
export function toast(msg, isErr = false) {
  const t = document.getElementById("toast");
  t.textContent = msg; t.className = "toast" + (isErr ? " err" : ""); t.hidden = false;
  clearTimeout(toast._t); toast._t = setTimeout(() => { t.hidden = true; }, isErr ? 6000 : 3000);
}
export const chip = (text, kind = "") => h("span", { class: "chip " + kind }, text);
export const sevChip = (s) => chip(s, ["Critical", "Urgent", "High"].includes(s) ? "crit" : ["Warning", "Medium", "Moderate"].includes(s) ? "warn" : "");
export const srcChip = (src) => chip(src, src === "simulated" ? "sim" : src === "device" ? "ok" : "");
export function table(cols, rows, empty = "Nothing to show.") {
  if (!rows.length) return h("div", { class: "empty" }, empty);
  return h("div", { class: "table-wrap" }, h("table", null,
    h("thead", null, h("tr", null, cols.map((c) => h("th", null, c.label)))),
    h("tbody", null, rows.map((r) => h("tr", null, cols.map((c) => h("td", { "data-label": c.label || "" }, c.render ? c.render(r) : (r[c.key] ?? "—"))))))));
}
export function card(title, body, actions) {
  return h("section", { class: "card" }, h("header", null, h("h3", null, title), actions || null), body);
}
export function field(label, input) { return h("label", null, label, input); }
export async function guarded(fn) {
  try { return await fn(); } catch (e) { toast(e.message || "Something went wrong", true); return null; }
}
