// Thin fetch wrapper: JSON, CSRF header, uniform error objects. No secrets are ever stored in the browser.
let csrf = document.querySelector('meta[name="csrf-token"]')?.content || "";
export const setCsrf = (t) => { if (t) csrf = t; };

export class ApiError extends Error {
  constructor(message, status, body) { super(message); this.status = status; this.body = body || {}; }
}

export async function api(method, url, body, opts = {}) {
  const headers = { Accept: "application/json", "X-CSRF-Token": csrf };
  let payload;
  if (body instanceof FormData) payload = body;
  else if (body !== undefined) { headers["Content-Type"] = "application/json"; payload = JSON.stringify(body); }
  let res;
  try {
    res = await fetch(url, { method, headers, body: payload, credentials: "same-origin" });
  } catch (e) {
    throw new ApiError("Cannot reach the CareFlow server. Check your connection.", 0);
  }
  let data = {};
  try { data = await res.json(); } catch (e) { /* non-JSON */ }
  if (data.csrf) setCsrf(data.csrf);
  if (res.status === 401 && !opts.quiet401) { window.location.href = "/login"; throw new ApiError("Session expired", 401, data); }
  if (res.status === 403 && /CSRF/i.test(data.error || "") && !opts.noReload) {
    // Another tab signed in or out (all tabs share one browser session). Reload so this tab shows whoever is signed in now.
    setTimeout(() => window.location.reload(), 1200);
    throw new ApiError("Your session changed in another tab (a different account signed in). Reloading this page…", 403, data);
  }
  if (!res.ok) throw new ApiError(data.error || `Request failed (${res.status})`, res.status, data);
  return data;
}
export const get = (u) => api("GET", u);
export const post = (u, b = {}) => api("POST", u, b);
export const patch = (u, b = {}) => api("PATCH", u, b);
export const put = (u, b = {}) => api("PUT", u, b);
export const del = (u) => api("DELETE", u);
