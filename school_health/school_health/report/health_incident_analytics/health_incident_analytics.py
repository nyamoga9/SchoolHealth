import frappe
from frappe import _
from frappe.utils import add_months, getdate, nowdate


def execute(filters=None):
    filters = frappe._dict(filters or {})
    conditions = {}

    from_date = filters.get("from_date") or add_months(nowdate(), -12)
    to_date = filters.get("to_date") or nowdate()
    conditions["incident_date"] = ["between", [getdate(from_date), getdate(to_date)]]

    for fieldname in ("student", "severity", "status", "category"):
        if filters.get(fieldname):
            conditions[fieldname] = filters[fieldname]

    data = frappe.get_all(
        "School Health Incident",
        filters=conditions,
        fields=[
            "name",
            "incident_datetime",
            "student",
            "student_name",
            "severity",
            "category",
            "location",
            "action_taken",
            "guardian_notified",
            "follow_up_required",
            "status",
        ],
        order_by="incident_datetime desc",
    )

    columns = [
        {"fieldname": "name", "label": _("Incident"), "fieldtype": "Link", "options": "School Health Incident", "width": 160},
        {"fieldname": "incident_datetime", "label": _("When"), "fieldtype": "Datetime", "width": 150},
        {"fieldname": "student", "label": _("Student"), "fieldtype": "Link", "options": "Student", "width": 130},
        {"fieldname": "student_name", "label": _("Student Name"), "fieldtype": "Data", "width": 180},
        {"fieldname": "severity", "label": _("Severity"), "fieldtype": "Data", "width": 100},
        {"fieldname": "category", "label": _("Category"), "fieldtype": "Data", "width": 130},
        {"fieldname": "location", "label": _("Location"), "fieldtype": "Data", "width": 160},
        {"fieldname": "action_taken", "label": _("Action Taken"), "fieldtype": "Data", "width": 140},
        {"fieldname": "guardian_notified", "label": _("Guardian Notified"), "fieldtype": "Check", "width": 120},
        {"fieldname": "follow_up_required", "label": _("Follow-up"), "fieldtype": "Check", "width": 90},
        {"fieldname": "status", "label": _("Status"), "fieldtype": "Data", "width": 110},
    ]

    summary = [
        {"value": len(data), "label": _("Incidents"), "datatype": "Int"},
        {"value": sum(1 for row in data if row.severity in ("Severe", "Emergency")), "label": _("High Severity"), "datatype": "Int"},
        {"value": sum(1 for row in data if row.follow_up_required), "label": _("Follow-ups"), "datatype": "Int"},
        {"value": sum(1 for row in data if row.guardian_notified), "label": _("Guardians Notified"), "datatype": "Int"},
    ]

    chart = {
        "data": {
            "labels": [_("Mild"), _("Moderate"), _("Severe"), _("Emergency")],
            "datasets": [
                {
                    "name": _("Incidents"),
                    "values": [
                        sum(1 for row in data if row.severity == "Mild"),
                        sum(1 for row in data if row.severity == "Moderate"),
                        sum(1 for row in data if row.severity == "Severe"),
                        sum(1 for row in data if row.severity == "Emergency"),
                    ],
                }
            ],
        },
        "type": "donut",
    }

    return columns, data, None, chart, summary
