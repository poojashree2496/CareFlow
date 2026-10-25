import { api, setCsrf } from "./api.js";
import { h } from "./ui.js";

const form = document.getElementById("login-form");
const err = document.getElementById("login-error");
form.addEventListener("submit", async (ev) => {
  ev.preventDefault();
  err.hidden = true;
  const btn = form.querySelector("button");
  btn.disabled = true;
  try {
    const d = await api("POST", "/api/auth/login", { email: form.email.value.trim(), password: form.password.value }, { quiet401: true });
    setCsrf(d.csrf);
    window.location.href = "/";
  } catch (e) {
    err.textContent = e.message;
    err.hidden = false;
    form.password.value = "";
    btn.disabled = false;
  }
});

const box = document.getElementById("demo-accounts");
if (box) {
  api("GET", "/api/auth/demo-accounts", undefined, { quiet401: true }).then((d) => {
    if (!d.demo) { box.parentElement.hidden = true; return; }
    d.accounts.forEach((a) => box.append(h("button", {
      type: "button", class: "btn sm", title: a.email,
      onclick: () => { form.email.value = a.email; form.password.value = d.password || ""; form.password.focus(); },
    }, a.role_label + " — " + a.name.replace(" (demo)", ""))));
  }).catch(() => { box.parentElement.hidden = true; });
}
