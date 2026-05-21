from __future__ import annotations

from datetime import date, datetime


SYMPTOM_CATEGORIES = (
    "General Symptoms",
    "Respiratory Symptoms",
    "Gastrointestinal Symptoms",
    "Neurological Symptoms",
    "Skin & Allergic Reactions",
    "Eye Symptoms",
    "Ear Symptoms",
    "Throat & Mouth Symptoms",
    "Musculoskeletal Symptoms",
    "Psychological & Behavioral Symptoms",
    "Urinary & Genital Symptoms",
    "Injuries & Trauma",
    "Infectious Disease Symptoms",
)


def normalize_severity(value: str | None) -> str:
    severity = (value or "").strip().title()
    if severity in {"Mild", "Moderate", "Severe", "Emergency"}:
        return severity
    if severity in {"Critical", "Urgent"}:
        return "Emergency"
    return "Mild"


def status_for_legacy_incident(follow_up_required, follow_up_date=None, action_taken: str | None = None) -> str:
    action = (action_taken or "").strip()
    if action in {"Hospitalized", "Emergency Services"}:
        return "Escalated"

    parsed_follow_up = parse_date(follow_up_date)
    if int(follow_up_required or 0) and parsed_follow_up and parsed_follow_up >= date.today():
        return "Follow Up"

    return "Resolved"


def parse_date(value) -> date | None:
    if not value:
        return None
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    return date.fromisoformat(str(value)[:10])


def symptom_name_from_legacy(value: str | None) -> str:
    symptom = (value or "").strip()
    if " - " in symptom:
        return symptom.rsplit(" - ", 1)[0].strip()
    return symptom


def full_name_from_parts(*parts: str | None) -> str:
    return " ".join(part.strip() for part in parts if part and part.strip())


def get_student_names(students: list[str] | tuple[str, ...] | set[str]) -> dict[str, str]:
    student_ids = sorted({student for student in students if student})
    if not student_ids:
        return {}

    import frappe

    rows = frappe.get_all(
        "Student",
        filters={"name": ("in", student_ids)},
        fields=["name", "student_name", "first_name", "middle_name", "last_name"],
    )
    names = {}
    for row in rows:
        student_name = (row.student_name or "").strip()
        names[row.name] = student_name or full_name_from_parts(row.first_name, row.middle_name, row.last_name)
    return names


def get_student_name(student: str | None) -> str:
    if not student:
        return ""
    return get_student_names([student]).get(student, "")
