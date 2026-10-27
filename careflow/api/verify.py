"""Public check page for printed/downloaded report copies. No sign-in; shows no clinical content and no patient name."""
from __future__ import annotations

from flask import Blueprint, current_app, make_response, render_template_string, request

from ..audit import audit
from ..extensions import db
from ..security import limiter
from ..services import verify as vsvc

bp = Blueprint("verify", __name__)

_PAGE = """<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex"><title>Check a report copy · CareFlow</title><style>
body{font:16px/1.5 system-ui,Segoe UI,Arial,sans-serif;max-width:560px;margin:1.5rem auto;padding:0 1rem;color:#111;background:#f6f8f8}
h1{font-size:1.35rem;margin:.2rem 0 1rem}form{display:flex;gap:.5rem;flex-wrap:wrap;margin:1rem 0}
input{font:inherit;padding:.55rem .7rem;flex:1;min-width:220px;border:1px solid #888;border-radius:6px;text-transform:uppercase;letter-spacing:.04em}
button{font:inherit;padding:.55rem 1.1rem;border:0;border-radius:6px;background:#0b6e6e;color:#fff;cursor:pointer}
.card{border-radius:10px;padding:1rem 1.2rem;margin-top:1rem;border:2px solid}.ok{background:#e7f6ee;border-color:#1c8f55}.bad{background:#fdecec;border-color:#c0392b}
.big{font-size:1.2rem;font-weight:700;margin:0 0 .4rem}dl{display:grid;grid-template-columns:max-content 1fr;gap:.25rem 1rem;margin:.6rem 0 0}dt{color:#444}dd{margin:0;font-weight:600}
.small{color:#555;font-size:.88rem;margin-top:1rem}</style></head><body>
<h1>Check a report copy</h1>
<p>Enter the verification code printed under the QR code on the report, or scan the QR code.</p>
<form method="get" action="/verify"><input name="code" value="{{ code }}" placeholder="e.g. L12-3FA9 C1D2 E4B7 A8F0 1234" autocomplete="off" maxlength="40"><button>Check</button></form>
{% if state == 'ok' %}<div class="card ok"><p class="big">✔ Genuine: this matches the hospital's record</p>
<dl><dt>Document</dt><dd>{{ r.type }}</dd><dt>Released</dt><dd>{{ released }}</dd><dt>Issued by</dt><dd>{{ r.issuer }} department</dd>
<dt>Patient</dt><dd>{{ r.patient_initials }} (ref {{ r.patient_ref }})</dd><dt>Code</dt><dd>{{ r.code }}</dd></dl>
<p class="small">Compare the patient initials, document type and date above with the paper copy. If they differ, the copy is not genuine. This page does not show any medical details.</p></div>
{% elif state == 'bad' %}<div class="card bad"><p class="big">✖ This code does not match any released record</p>
<p>Possible reasons: the code was typed wrongly, the copy was altered, or the report was corrected after this copy was printed. Do not rely on this copy; ask the hospital for a fresh one.</p></div>
{% elif state == 'limited' %}<div class="card bad"><p class="big">Too many checks</p><p>Please wait a minute and try again.</p></div>{% endif %}
<p class="small">CareFlow report verification. Codes are tied to the exact content that was released.</p></body></html>"""


@bp.get("/verify")
@bp.get("/verify/<path:code>")
def verify_page(code=""):
    code = (code or request.args.get("code", "")).strip()[:40]
    state, r, released = "", None, ""
    if code:
        ip = request.remote_addr or "-"
        if current_app.config["RATE_LIMIT_ENABLED"] and not limiter.hit(f"verify:{ip}", 30):
            state = "limited"
        else:
            r = vsvc.check(code)
            state = "ok" if r else "bad"
            if r and r["released_at"]:
                released = r["released_at"].strftime("%d %b %Y")
            audit("verify.public_check", category="access", outcome="success" if r else "denied", details=f"code check from public page ({'match' if r else 'no match'})", commit=True)
    resp = make_response(render_template_string(_PAGE, code=code, state=state, r=r, released=released), 429 if state == "limited" else 200)
    resp.headers["Content-Security-Policy"] = "default-src 'none'; style-src 'unsafe-inline'; form-action 'self'; base-uri 'none'; frame-ancestors 'none'"
    resp.headers["Cache-Control"] = "no-store"
    resp.headers["X-Content-Type-Options"] = "nosniff"
    return resp
