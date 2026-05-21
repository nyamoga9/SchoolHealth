import frappe
from frappe import _
from frappe.utils import add_months, getdate, nowdate

from school_health.school_health.utils import get_student_names


def execute(filters=None):
    filters = frappe._dict(filters or {})
    from_date = getdate(filters.get("from_date") or add_months(nowdate(), -12))
    to_date = getdate(filters.get("to_date") or nowdate())
    min_visits = int(filters.get("min_visits") or 2)

    data = frappe.db.sql(
        """
        select
            student,
            max(student_name) as student_name,
            count(*) as incident_count,
            sum(case when severity in ('Severe', 'Emergency') then 1 else 0 end) as high_severity_count,
            sum(case when follow_up_required = 1 then 1 else 0 end) as follow_up_count,
            max(incident_date) as last_incident_date
        from `tabSchool Health Incident`
        where incident_date between %s and %s
            and ifnull(student, '') != ''
        group by student
        having count(*) >= %s
        order by incident_count desc, last_incident_date desc
        """,
        (from_date, to_date, min_visits),
        as_dict=True,
    )
    student_names = get_student_names([row.student for row in data])
    for row in data:
        row.student_name = (row.student_name or "").strip() or student_names.get(row.student) or row.student

    columns = [
        {"fieldname": "student", "label": _("Student"), "fieldtype": "Link", "options": "Student", "width": 130},
        {"fieldname": "student_name", "label": _("Student Name"), "fieldtype": "Data", "width": 220},
        {"fieldname": "incident_count", "label": _("Incidents"), "fieldtype": "Int", "width": 100},
        {"fieldname": "high_severity_count", "label": _("High Severity"), "fieldtype": "Int", "width": 120},
        {"fieldname": "follow_up_count", "label": _("Follow-ups"), "fieldtype": "Int", "width": 110},
        {"fieldname": "last_incident_date", "label": _("Last Incident"), "fieldtype": "Date", "width": 120},
    ]
    return columns, data
