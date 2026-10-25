"""Private document storage, validation and text extraction (embedded text + OCR)."""
from __future__ import annotations

import hashlib
import io
import os
import re
import uuid
from dataclasses import dataclass, field
from pathlib import Path

import requests
from flask import current_app

from ..utils import ApiError

MAGIC = (
    (b"%PDF-", "application/pdf", (".pdf",)),
    (b"\x89PNG\r\n\x1a\n", "image/png", (".png",)),
    (b"\xff\xd8\xff", "image/jpeg", (".jpg", ".jpeg")),
)
MAX_IMAGE_PIXELS = 60_000_000
OCR_PAGE_TIMEOUT = 60


# --------------------------------------------------------------------------- #
# Validation
# --------------------------------------------------------------------------- #
def sniff_and_validate(data: bytes, filename: str) -> tuple[str, str]:
    """Return (mime, extension) from the content itself; reject anything unexpected."""
    if not data:
        raise ApiError("The uploaded file is empty")
    ext = Path(filename or "").suffix.lower()
    mime = None
    head = data[:1024]
    for magic, m, exts in MAGIC:
        if (m == "application/pdf" and magic in head) or head.startswith(magic):
            mime = m
            if ext not in exts:
                raise ApiError(f"The file extension '{ext or '(none)'}' does not match its content ({m})")
            break
    if mime is None:
        if ext not in (".txt", ".text"):
            raise ApiError("Unsupported file type. Allowed: PDF, PNG, JPEG, plain text (.txt)")
        if b"\x00" in data[:8192]:
            raise ApiError("This does not look like a plain-text file")
        try:
            data.decode("utf-8")
        except UnicodeDecodeError:
            raise ApiError("Text files must be UTF-8 encoded")
        mime = "text/plain"
    if mime == "application/pdf":
        import pypdfium2 as pdfium
        try:
            pdf = pdfium.PdfDocument(data)
            n = len(pdf)
            pdf.close()
        except Exception as exc:
            msg = "password" if "password" in str(exc).lower() else "invalid"
            raise ApiError("The PDF is password-protected and cannot be processed" if msg == "password" else "The PDF is damaged or invalid")
        if n == 0 or n > current_app.config["UPLOAD_MAX_PDF_PAGES"]:
            raise ApiError(f"PDF must have between 1 and {current_app.config['UPLOAD_MAX_PDF_PAGES']} pages")
    elif mime in ("image/png", "image/jpeg"):
        from PIL import Image
        Image.MAX_IMAGE_PIXELS = MAX_IMAGE_PIXELS
        try:
            with Image.open(io.BytesIO(data)) as im:
                im.verify()
            with Image.open(io.BytesIO(data)) as im:
                if im.width * im.height > MAX_IMAGE_PIXELS:
                    raise ApiError("Image dimensions are too large")
        except ApiError:
            raise
        except Exception:
            raise ApiError("The image is damaged or invalid")
    return mime, (ext if ext else ".bin")


def safe_display_name(name: str) -> str:
    name = os.path.basename(name or "document").replace("\\", "/").split("/")[-1]
    name = re.sub(r"[^A-Za-z0-9._ \-()]", "_", name).strip(" .") or "document"
    return name[:150]


# --------------------------------------------------------------------------- #
# Storage backends (always private; access only through authorised API routes)
# --------------------------------------------------------------------------- #
class LocalStorage:
    name = "local"

    def __init__(self, base: str):
        self.base = Path(base).resolve()
        self.base.mkdir(parents=True, exist_ok=True)
        try:
            os.chmod(self.base, 0o700)
        except OSError:
            pass

    def _path(self, key: str) -> Path:
        p = (self.base / key).resolve()
        if self.base not in p.parents:
            raise ApiError("Invalid storage key", 400)
        return p

    def put(self, key: str, data: bytes, mime: str):
        p = self._path(key)
        p.parent.mkdir(parents=True, exist_ok=True)
        with open(p, "xb") as f:
            f.write(data)

    def get(self, key: str) -> bytes:
        p = self._path(key)
        if not p.is_file():
            raise ApiError("Stored file is missing", 404)
        return p.read_bytes()

    def signed_url(self, key: str, seconds: int):
        return None  # served through the authorised download route


class SupabaseStorage:
    """Private Supabase Storage bucket, server-side service-role key only."""
    name = "supabase"

    def __init__(self, url: str, key: str, bucket: str):
        if not url or not key:
            raise ApiError("Supabase storage is selected but SUPABASE_URL / SUPABASE_SERVICE_ROLE_KEY are not set", 503)
        self.url, self.bucket = url.rstrip("/"), bucket
        self.h = {"Authorization": f"Bearer {key}", "apikey": key}

    def put(self, key, data, mime):
        r = requests.post(f"{self.url}/storage/v1/object/{self.bucket}/{key}", headers={**self.h, "Content-Type": mime, "x-upsert": "false"}, data=data, timeout=30)
        if r.status_code >= 300:
            raise ApiError(f"Document storage rejected the upload (HTTP {r.status_code})", 502)

    def get(self, key) -> bytes:
        r = requests.get(f"{self.url}/storage/v1/object/{self.bucket}/{key}", headers=self.h, timeout=30)
        if r.status_code >= 300:
            raise ApiError(f"Document storage could not return the file (HTTP {r.status_code})", 502)
        return r.content

    def signed_url(self, key, seconds):
        r = requests.post(f"{self.url}/storage/v1/object/sign/{self.bucket}/{key}", headers=self.h, json={"expiresIn": seconds}, timeout=15)
        if r.status_code >= 300:
            raise ApiError("Could not create a signed URL", 502)
        return f"{self.url}/storage/v1{r.json()['signedURL']}"


def get_storage(backend: str | None = None):
    backend = backend or current_app.config["STORAGE_BACKEND"]
    if backend == "supabase":
        c = current_app.config
        return SupabaseStorage(c["SUPABASE_URL"], c["SUPABASE_SERVICE_ROLE_KEY"], c["SUPABASE_BUCKET"])
    return LocalStorage(current_app.config["UPLOAD_DIR"])


def new_storage_key(patient_id: int, ext: str) -> str:
    ext = ext if re.fullmatch(r"\.[a-z0-9]{1,5}", ext or "") else ".bin"
    return f"patients/{int(patient_id)}/{uuid.uuid4()}{ext}"


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


# --------------------------------------------------------------------------- #
# Extraction
# --------------------------------------------------------------------------- #
@dataclass
class PageResult:
    page_no: int
    text: str
    method: str  # embedded-text | ocr | plain-text | none
    confidence: float | None
    note: str = ""


@dataclass
class Extraction:
    pages: list[PageResult] = field(default_factory=list)
    status: str = "Failed"
    method: str = "none"
    quality: float | None = None
    note: str = ""


def ocr_available() -> bool:
    if not current_app.config["OCR_ENABLED"]:
        return False
    try:
        import pytesseract
        if current_app.config["TESSERACT_CMD"]:
            pytesseract.pytesseract.tesseract_cmd = current_app.config["TESSERACT_CMD"]
        pytesseract.get_tesseract_version()
        return True
    except Exception:
        return False


def _ocr_image(img) -> tuple[str, float | None]:
    import pytesseract
    from pytesseract import Output
    lang = current_app.config["OCR_LANGUAGES"]
    d = pytesseract.image_to_data(img, lang=lang, output_type=Output.DICT, timeout=OCR_PAGE_TIMEOUT)
    words, confs, lines = [], [], {}
    for i, w in enumerate(d["text"]):
        w = (w or "").strip()
        try:
            c = float(d["conf"][i])
        except (TypeError, ValueError):
            c = -1
        if not w or c < 0:
            continue
        key = (d["block_num"][i], d["par_num"][i], d["line_num"][i])
        lines.setdefault(key, []).append(w)
        confs.append(c)
    text = "\n".join(" ".join(ws) for _, ws in sorted(lines.items()))
    return text, (sum(confs) / len(confs) / 100.0 if confs else None)


def _text_quality(text: str) -> float:
    t = text.strip()
    if not t:
        return 0.0
    good = sum(ch.isalnum() or ch.isspace() or ch in ".,:;()/%-+<>=#&'\"[]*" for ch in t)
    return round(good / len(t), 3)


def extract(data: bytes, mime: str) -> Extraction:
    """Embedded text first; OCR only where a page has no usable text. Never invents text."""
    ex = Extraction()
    if mime == "text/plain":
        txt = data.decode("utf-8", errors="replace")
        ex.pages = [PageResult(1, txt, "plain-text", 1.0)]
        ex.method, ex.quality = "plain-text", 1.0
        ex.status = "Complete" if txt.strip() else "Failed"
        ex.note = "" if txt.strip() else "File contains no text"
        return ex

    can_ocr = ocr_available()
    needs_ocr_but_unavailable = 0
    if mime == "application/pdf":
        import pypdfium2 as pdfium
        pdf = pdfium.PdfDocument(data)
        try:
            for i in range(len(pdf)):
                page = pdf[i]
                emb = ""
                try:
                    tp = page.get_textpage()
                    emb = (tp.get_text_bounded() or "").strip()
                    tp.close()
                except Exception:
                    emb = ""
                if len(emb) >= 25 and _text_quality(emb) >= 0.6:
                    ex.pages.append(PageResult(i + 1, emb, "embedded-text", _text_quality(emb)))
                elif can_ocr:
                    try:
                        img = page.render(scale=300 / 72).to_pil()
                        text, conf = _ocr_image(img)
                        ex.pages.append(PageResult(i + 1, text, "ocr" if text.strip() else "none", conf, "" if text.strip() else "OCR found no readable text"))
                    except Exception as exc:
                        ex.pages.append(PageResult(i + 1, "", "none", None, f"OCR failed: {exc.__class__.__name__}"))
                else:
                    needs_ocr_but_unavailable += 1
                    ex.pages.append(PageResult(i + 1, emb, "embedded-text" if emb else "none", _text_quality(emb) if emb else None, "Scanned page: OCR engine unavailable"))
                page.close()
        finally:
            pdf.close()
    else:  # images
        from PIL import Image
        Image.MAX_IMAGE_PIXELS = MAX_IMAGE_PIXELS
        if not can_ocr:
            ex.pages = [PageResult(1, "", "none", None, "OCR engine unavailable")]
            needs_ocr_but_unavailable = 1
        else:
            try:
                with Image.open(io.BytesIO(data)) as im:
                    im = im.convert("RGB")
                    text, conf = _ocr_image(im)
                ex.pages = [PageResult(1, text, "ocr" if text.strip() else "none", conf, "" if text.strip() else "No readable text found (picture-only image?)")]
            except Exception as exc:
                ex.pages = [PageResult(1, "", "none", None, f"OCR failed: {exc.__class__.__name__}")]

    methods = {p.method for p in ex.pages if p.method != "none"}
    ex.method = "mixed" if len(methods) > 1 else (next(iter(methods)) if methods else "none")
    scored = [p.confidence for p in ex.pages if p.confidence is not None and p.text.strip()]
    ex.quality = round(sum(scored) / len(scored), 3) if scored else 0.0
    with_text = sum(1 for p in ex.pages if p.text.strip())
    if with_text == 0:
        ex.status = "OCR unavailable" if needs_ocr_but_unavailable else "Failed"
        ex.note = "The OCR engine (Tesseract) is not installed or disabled; the original file is stored but unreadable by the assistant." if needs_ocr_but_unavailable else "No text could be extracted."
    elif with_text < len(ex.pages) or ex.quality < 0.80 or needs_ocr_but_unavailable:
        ex.status = "Partial"
        bits = []
        if with_text < len(ex.pages):
            bits.append(f"{len(ex.pages) - with_text} of {len(ex.pages)} page(s) produced no text")
        if ex.quality < 0.80:
            bits.append(f"low extraction confidence ({ex.quality:.0%})")
        if needs_ocr_but_unavailable:
            bits.append("OCR unavailable for scanned pages")
        ex.note = "; ".join(bits)
    else:
        ex.status = "Complete"
    return ex
