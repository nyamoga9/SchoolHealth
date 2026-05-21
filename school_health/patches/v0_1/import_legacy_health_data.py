import frappe

from school_health.school_health.utils import (
    SYMPTOM_CATEGORIES,
    normalize_severity,
    get_student_name,
    status_for_legacy_incident,
    symptom_name_from_legacy,
)


COMMON_SYMPTOMS = (
    ("Fever", "General Symptoms"),
    ("Headache", "Neurological Symptoms"),
    ("Stomachache", "Gastrointestinal Symptoms"),
    ("Abdominal pain", "Gastrointestinal Symptoms"),
    ("Vomiting", "Gastrointestinal Symptoms"),
    ("Diarrhea", "Gastrointestinal Symptoms"),
    ("Cough (Dry)", "Respiratory Symptoms"),
    ("Cough (Productive)", "Respiratory Symptoms"),
    ("Sore throat", "Throat & Mouth Symptoms"),
    ("Nose bleed", "Respiratory Symptoms"),
    ("Dizziness", "Neurological Symptoms"),
    ("Fatigue", "General Symptoms"),
    ("Minor injury", "Injuries & Trauma"),
    ("Fall", "Injuries & Trauma"),
    ("Scratch / abrasion", "Injuries & Trauma"),
    ("Skin rash", "Skin & Allergic Reactions"),
    ("Allergic reaction", "Skin & Allergic Reactions"),
    ("Eye redness", "Eye Symptoms"),
    ("Ear pain", "Ear Symptoms"),
    ("Anxiety", "Psychological & Behavioral Symptoms"),
)


def execute():
    if not frappe.db.table_exists("Health Symptom"):
        return

    import_legacy_symptoms()
    seed_common_symptoms()
    import_legacy_incidents()


def import_legacy_symptoms():
    if not frappe.db.table_exists("Heath Symptoms"):
        return

    for legacy in frappe.get_all(
        "Heath Symptoms",
        fields=["name", "symptom", "symptomcategory"],
        order_by="creation asc",
    ):
        category = normalize_category(legacy.symptomcategory)
        symptom_name = symptom_name_from_legacy(legacy.symptom) or symptom_name_from_legacy(legacy.name)
        if not symptom_name:
            continue
        ensure_symptom(
            name=legacy.name,
            symptom_name=symptom_name,
            category=category,
            legacy_name=legacy.name,
        )


def seed_common_symptoms():
    if frappe.db.count("Health Symptom"):
        return
    for symptom_name, category in COMMON_SYMPTOMS:
        ensure_symptom(
            name=f"{symptom_name} - {category}",
            symptom_name=symptom_name,
            category=category,
        )


def ensure_symptom(name, symptom_name, category, legacy_name=None):
    if frappe.db.exists("Health Symptom", name):
        if legacy_name:
            frappe.db.set_value("Health Symptom", name, "legacy_heath_symptom", legacy_name, update_modified=False)
        return name

    doc = frappe.get_doc(
        {
            "doctype": "Health Symptom",
            "name": name,
            "symptom_name": symptom_name,
            "category": normalize_category(category),
            "active": 1,
            "legacy_heath_symptom": legacy_name,
        }
    )
    doc.flags.ignore_permissions = True
    doc.flags.name_set = True
    doc.insert(ignore_permissions=True, ignore_links=True)
    return doc.name


def import_legacy_incidents():
    if not frappe.db.table_exists("Health Incident"):
        return

    legacy_incidents = frappe.get_all(
        "Health Incident",
        fields=[
            "name",
            "docstatus",
            "studentname",
            "dateandtime",
            "incidencelocation",
            "reportedby",
            "severity",
            "incdescription",
            "action_taken",
            "medication_given",
            "follow_up_required",
            "follow_up_date",
            "guardian_notified",
            "notification_method",
            "guardian_response",
            "eye_witness",
        ],
        order_by="creation asc",
    )

    for legacy in legacy_incidents:
        if frappe.db.exists("School Health Incident", {"legacy_health_incident": legacy.name}):
            continue

        symptom_rows = get_legacy_symptom_rows(legacy.name)
        category = infer_incident_category(symptom_rows)
        status = status_for_legacy_incident(
            legacy.follow_up_required,
            legacy.follow_up_date,
            legacy.action_taken,
        )

        doc = frappe.get_doc(
            {
                "doctype": "School Health Incident",
                "naming_series": "SHI-.YYYY.-.#####",
                "legacy_health_incident": legacy.name,
                "student": legacy.studentname,
                "student_name": get_student_name(legacy.studentname),
                "incident_datetime": legacy.dateandtime,
                "location": clean_text(legacy.incidencelocation),
                "reported_by": legacy.reportedby,
                "witness": clean_text(legacy.eye_witness),
                "category": category,
                "severity": normalize_severity(legacy.severity),
                "description": legacy.incdescription,
                "action_taken": map_action_taken(legacy.action_taken),
                "disposition": disposition_for_action(legacy.action_taken),
                "medication_given": legacy.medication_given,
                "follow_up_required": int(legacy.follow_up_required or 0),
                "follow_up_date": legacy.follow_up_date,
                "guardian_notified": int(legacy.guardian_notified or 0),
                "notification_method": map_notification_method(legacy.notification_method),
                "guardian_response": legacy.guardian_response,
                "status": status,
                "resolved_on": legacy.follow_up_date if status == "Resolved" else None,
            }
        )

        for symptom in symptom_rows:
            doc.append("symptoms", {"symptom": symptom})

        doc.insert(ignore_permissions=True, ignore_links=True)
        if int(legacy.docstatus or 0):
            frappe.db.set_value(
                "School Health Incident",
                doc.name,
                "docstatus",
                int(legacy.docstatus),
                update_modified=False,
            )
            frappe.db.sql(
                """
                update `tabHealth Incident Symptom`
                set docstatus = %s
                where parent = %s
                """,
                (int(legacy.docstatus), doc.name),
            )

        ensure_student_profile(legacy.studentname)


def get_legacy_symptom_rows(parent):
    if not frappe.db.table_exists("Symptoms Selection"):
        return []

    rows = frappe.get_all(
        "Symptoms Selection",
        filters={"parent": parent, "parenttype": "Health Incident"},
        fields=["symptom1"],
        order_by="idx asc",
    )
    symptoms = []
    for row in rows:
        if not row.symptom1:
            continue
        if not frappe.db.exists("Health Symptom", row.symptom1):
            ensure_symptom(
                name=row.symptom1,
                symptom_name=symptom_name_from_legacy(row.symptom1),
                category=category_from_legacy_name(row.symptom1),
                legacy_name=row.symptom1,
            )
        symptoms.append(row.symptom1)
    return symptoms


def ensure_student_profile(student):
    if not student or frappe.db.exists("Student Health Profile", student):
        return
    doc = frappe.get_doc(
        {
            "doctype": "Student Health Profile",
            "student": student,
            "student_name": get_student_name(student),
            "status": "Active",
        }
    )
    doc.insert(ignore_permissions=True, ignore_links=True)


def normalize_category(value):
    category = (value or "").strip()
    return category if category in SYMPTOM_CATEGORIES else "General Symptoms"


def category_from_legacy_name(value):
    symptom = (value or "").strip()
    if " - " in symptom:
        return normalize_category(symptom.rsplit(" - ", 1)[1])
    return "General Symptoms"


def infer_incident_category(symptoms):
    categories = []
    if symptoms:
        categories = frappe.get_all(
            "Health Symptom",
            filters={"name": ("in", symptoms)},
            pluck="category",
        )
    if any(category == "Injuries & Trauma" for category in categories):
        return "Injury"
    if any(category == "Psychological & Behavioral Symptoms" for category in categories):
        return "Mental / Behavioral"
    return "Illness"


def map_action_taken(value):
    action = (value or "None").strip()
    mapping = {
        "None": "None",
        "First Aid": "First Aid",
        "Sent to Nurse": "Sent to Nurse",
        "Sent Home": "Sent Home",
        "Hospitalized": "Hospitalized",
    }
    return mapping.get(action, "Assessment Only")


def disposition_for_action(value):
    action = (value or "").strip()
    if action == "Hospitalized":
        return "Clinic / Hospital"
    if action == "Sent Home":
        return "Sent Home"
    if action == "Sent to Nurse":
        return "Observed in Health Office"
    if action in {"First Aid", "None"}:
        return "Returned to Class"
    return ""


def map_notification_method(value):
    method = (value or "N/A").strip()
    if method in {"N/A", "Phone", "Email", "In-person"}:
        return method
    return "SMS / Messaging"


def clean_text(value):
    return (value or "").strip()
