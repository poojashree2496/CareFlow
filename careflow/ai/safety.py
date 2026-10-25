"""Deterministic safety checks around the AI assistant (independent of the model)."""
from __future__ import annotations

import re

INJECTION_PATTERNS = [
    r"ignore (all |any |the )?(previous|prior|above|earlier) (instructions|rules|prompts?)",
    r"disregard (all |any |the )?(previous|prior|above|earlier)",
    r"(reveal|show|print|repeat|output) (me )?(your |the )?(system prompt|instructions|api[ _-]?key|secret|password|token)",
    r"you are now\b", r"act as (an? )?(admin|administrator|system|developer)",
    r"override (the )?(access|permission|security|rules?)", r"new instructions?\s*:", r"\bsystem\s*:\s", r"</?(system|assistant|instructions?)>",
    r"(for|about) (all|every|other) patients?", r"list (all|every) patients?", r"pretend (that )?",
    r"do not (cite|mention|tell)", r"base64", r"\bjailbreak\b",
]
_INJ = re.compile("|".join(INJECTION_PATTERNS), re.I)
EMERGENCY = re.compile(r"chest pain|can'?t breathe|cannot breathe|difficulty breathing|shortness of breath|suicid|overdose|unconscious|unresponsive|stroke|severe bleeding|seizure|anaphyla", re.I)
DECISION = re.compile(r"\b(should (i|we|the patient) (take|stop|start|increase|decrease)|what dose|how much (should|to) (take|give)|prescribe|diagnose|do (i|they|he|she) have|is (it|this) safe to|can (i|they) stop)\b", re.I)
SECRET_PATTERNS = re.compile(r"sk-[A-Za-z0-9]{16,}|api[_-]?key\s*[:=]|BEGIN (RSA |EC )?PRIVATE KEY|service[_-]?role|SECRET_KEY|DATABASE_URL|postgres(ql)?://", re.I)
PATIENT_CODE = re.compile(r"\bP-\d{6}-[0-9A-F]{4}\b")
CITATION = re.compile(r"\[E(\d+)\]")


def sanitize_untrusted(text: str) -> tuple[str, int]:
    """Neutralise instruction-like lines inside uploaded-document text before it reaches a model."""
    flagged = 0
    out = []
    for line in (text or "").splitlines():
        if _INJ.search(line):
            flagged += 1
            out.append("[line removed: instruction-like text found in a document]")
        else:
            out.append(line)
    return "\n".join(out), flagged


def is_emergency(question: str) -> bool:
    return bool(EMERGENCY.search(question or ""))


def is_decision_request(question: str) -> bool:
    return bool(DECISION.search(question or ""))


# ---- numeric grounding ------------------------------------------------------
_NUM = re.compile(r"(?<![\w.])-?\d+(?:\.\d+)?")
_DATEISH = re.compile(r"\b\d{4}-\d{2}-\d{2}(?:[T ]\d{2}:\d{2}(?::\d{2})?(?:Z|[+-]\d{2}:?\d{2})?)?\b|\b\d{1,2}:\d{2}\b|\b\d{1,2}/\d{1,2}/\d{2,4}\b")
_UNIT_AFTER = re.compile(r"^\s*(mg|g|mcg|µg|ug|ml|l|dl|mmol|mmhg|bpm|%|°c|°f|kg|cm|mm|iu|u/l|/min|breaths|cells|x10|10\^|fl|pg|mEq)", re.I)


def _norm_num(tok: str) -> str:
    try:
        f = float(tok)
        return str(int(f)) if f == int(f) else repr(round(f, 6)).rstrip("0").rstrip(".")
    except ValueError:
        return tok


def numbers_in(text: str) -> set[str]:
    text = CITATION.sub(" ", text or "")
    text = _DATEISH.sub(" ", text)
    return {_norm_num(m.group()) for m in _NUM.finditer(text)}


def ungrounded_numbers(answer: str, evidence_text: str) -> list[str]:
    """Numbers that matter (decimals, values with units, anything above 20) must appear in the evidence."""
    ev = numbers_in(evidence_text)
    # also accept numbers present in dates of the evidence (e.g. "2026" in a date text)
    ev |= {_norm_num(x) for x in re.findall(r"\d+(?:\.\d+)?", evidence_text or "")}
    cleaned = _DATEISH.sub(" ", CITATION.sub(" ", answer or ""))
    cleaned = re.sub(r"(?m)^\s*\d+[.)]\s", " ", cleaned)  # list numbering
    bad = []
    for m in _NUM.finditer(cleaned):
        tok = m.group()
        n = _norm_num(tok)
        tail = cleaned[m.end(): m.end() + 14]
        significant = ("." in tok) or abs(float(tok)) > 20 or bool(_UNIT_AFTER.match(tail))
        if significant and n not in ev:
            bad.append(tok)
    return sorted(set(bad))


def validate_answer(answer: str, evidence_ids: set[str], evidence_text: str, own_patient_code: str, system_prompt: str) -> tuple[str, list[dict]]:
    """Return (possibly cleaned answer, issues). Issues with block=True mean the answer must be withheld."""
    issues: list[dict] = []
    if not answer.strip():
        issues.append({"code": "empty", "block": True, "detail": "The model returned no text."})
        return answer, issues
    if SECRET_PATTERNS.search(answer):
        issues.append({"code": "secret_like_content", "block": True, "detail": "The answer contained credential-like text."})
    marker = system_prompt[:60].strip()
    if marker and marker in answer:
        issues.append({"code": "prompt_leak", "block": True, "detail": "The answer repeated internal instructions."})
    for code in set(PATIENT_CODE.findall(answer)):
        if code != own_patient_code:
            issues.append({"code": "foreign_patient_reference", "block": True, "detail": "The answer referenced another patient identifier."})
    cited = {f"E{m}" for m in CITATION.findall(answer)}
    unknown = sorted(cited - evidence_ids)
    if unknown:
        answer = CITATION.sub(lambda m: m.group(0) if f"E{m.group(1)}" in evidence_ids else "", answer)
        issues.append({"code": "unknown_citation", "block": False, "detail": f"Removed citation(s) to records that were not retrieved: {', '.join(unknown)}"})
    bad = ungrounded_numbers(answer, evidence_text)
    if bad:
        issues.append({"code": "ungrounded_numbers", "block": True, "detail": "Values not found in the retrieved records: " + ", ".join(bad[:8])})
    return answer, issues
