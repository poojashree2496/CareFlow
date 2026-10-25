"""Shared vocabularies and state machines for CareFlow."""

SUPER_ADMIN = "super_admin"
HOSPITAL_ADMIN = "hospital_admin"
DOCTOR = "doctor"
NURSE = "nurse"
LAB_STAFF = "lab_staff"
PHARMACIST = "pharmacist"
RADIOLOGY_STAFF = "radiology_staff"
BILLING_STAFF = "billing_staff"
PATIENT = "patient"

ROLES = (SUPER_ADMIN, HOSPITAL_ADMIN, DOCTOR, NURSE, LAB_STAFF, PHARMACIST, RADIOLOGY_STAFF, BILLING_STAFF, PATIENT)
ROLE_LABELS = {
    SUPER_ADMIN: "Super Administrator",
    HOSPITAL_ADMIN: "Hospital Administrator",
    DOCTOR: "Doctor",
    NURSE: "Nurse",
    LAB_STAFF: "Laboratory Staff",
    PHARMACIST: "Pharmacist",
    RADIOLOGY_STAFF: "Radiology Staff",
    BILLING_STAFF: "Billing & Insurance",
    PATIENT: "Patient",
}

BED_STATUSES = ("Available", "Occupied", "Cleaning", "Reserved", "Maintenance")
# Manual (non-admission) bed transitions. Occupied is only entered through admission/transfer.
BED_MANUAL_TRANSITIONS = {
    "Available": {"Reserved", "Maintenance"},
    "Reserved": {"Available", "Maintenance"},
    "Cleaning": {"Available", "Maintenance"},
    "Maintenance": {"Available", "Cleaning"},
    "Occupied": set(),
}

APPOINTMENT_STATUSES = ("Scheduled", "Checked-in", "Completed", "Cancelled", "No-show")
APPOINTMENT_TRANSITIONS = {
    "Scheduled": {"Checked-in", "Completed", "Cancelled", "No-show"},
    "Checked-in": {"Completed", "Cancelled", "No-show"},
    "Completed": set(),
    "Cancelled": set(),
    "No-show": set(),
}
ACTIVE_APPOINTMENT = ("Scheduled", "Checked-in")

LAB_STATUSES = ("Ordered", "Collected", "Received", "Resulted", "Verified", "Released", "Rejected", "Cancelled")
LAB_TRANSITIONS = {
    "Ordered": {"Collected", "Cancelled", "Rejected"},
    "Collected": {"Received", "Rejected", "Cancelled"},
    "Received": {"Resulted", "Rejected"},
    "Resulted": {"Verified", "Rejected"},
    "Verified": {"Released"},
    "Released": set(),
    "Rejected": {"Ordered"},  # recollection re-opens the order
    "Cancelled": set(),
}
LAB_FLAGS = ("Normal", "High", "Low", "Critical High", "Critical Low", "Abnormal", "Not assessed")

RAD_ORDER_STATUSES = ("Ordered", "Scheduled", "Performed", "Reported", "Final", "Cancelled")
RAD_TRANSITIONS = {
    "Ordered": {"Scheduled", "Performed", "Cancelled"},
    "Scheduled": {"Performed", "Cancelled"},
    "Performed": {"Reported"},
    "Reported": {"Final", "Reported"},
    "Final": set(),  # amendments create a new report version, status stays Final
    "Cancelled": set(),
}

RX_STATUSES = ("Ordered", "Verified", "Dispensed", "Partially Dispensed", "Cancelled", "Discontinued")
MAR_STATUSES = ("Scheduled", "Given", "Held", "Refused", "Missed")

ALERT_SEVERITIES = ("Info", "Warning", "Critical")
ALERT_STATUSES = ("Open", "Acknowledged", "Escalated", "Resolved")
OBS_SOURCES = ("manual", "device", "simulated")

DISCHARGE_STATUSES = ("None", "Planned", "Authorized", "Completed")

CLAIM_STATUSES = ("Draft", "Submitted", "Approved", "Partially approved", "Rejected", "Paid")
# Legacy bill.insurance_status vocabulary kept for backward compatibility.
LEGACY_INSURANCE_STATUS = {
    "Draft": "Not submitted", "Submitted": "Submitted", "Approved": "Approved",
    "Partially approved": "Approved", "Rejected": "Rejected", "Paid": "Approved",
}

DOC_TYPES = ("Laboratory report", "Radiology report", "Discharge summary", "Prescription", "Clinical letter", "Consent", "Insurance", "Other")
# Physical hand-over lifecycle for items that exist in both digital and printed form.
PHYSICAL_STATUSES = ("Not requested", "Requested", "Ready for collection", "Handed over")
DELIVERABLE_KINDS = ("Laboratory report", "Radiology report", "Radiology images (film/CD)", "Prescription / medicine label", "Discharge summary",
                     "Invoice / receipt", "Insurance document", "Consent form", "Identity wristband", "Other")
DOC_MAX_BYTES_DEFAULT = 15 * 1024 * 1024

# Reference observation types: code, label, unit, plausible_min, plausible_max, decimals.
# plausible_* are data-entry sanity bounds (typo guards) only. They are NOT clinical thresholds.
OBSERVATION_TYPES = (
    ("heart_rate", "Heart rate", "bpm", 10, 300, 0),
    ("bp_systolic", "Systolic blood pressure", "mmHg", 30, 300, 0),
    ("bp_diastolic", "Diastolic blood pressure", "mmHg", 10, 200, 0),
    ("resp_rate", "Respiratory rate", "breaths/min", 2, 80, 0),
    ("spo2", "Oxygen saturation (SpO2)", "%", 30, 100, 0),
    ("temperature", "Body temperature", "°C", 25, 45, 1),
    ("pain_score", "Pain score (0-10)", "/10", 0, 10, 0),
    ("glucose", "Blood glucose", "mg/dL", 10, 1500, 0),
)

CARE_TASK_CATEGORIES = ("Observation", "Medication", "Wound care", "Mobility", "Intake/Output", "Assessment", "Discharge", "Other")
