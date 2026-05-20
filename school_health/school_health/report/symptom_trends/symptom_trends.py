import frappe
from frappe import _
from frappe.utils import add_months, getdate, nowdate


def execute(filters=None):
    filters = frappe._dict(filters or {})
    from_date = getdate(filters.get("from_date") or add_months(nowdate(), -12))
    to_date = getdate(filters.get("to_date") or nowdate())

    data = frappe.db.sql(
        """
        select
            s.symptom,
            coalesce(s.category, hs.category) as category,
            count(*) as incident_count,
            max(i.incident_date) as last_seen
        from `tabHealth Incident Symptom` s
        inner join `tabSchool Health Incident` i on i.name = s.parent
        left join `tabHealth Symptom` hs on hs.name = s.symptom
        where s.parenttype = 'School Health Incident'
            and i.incident_date between %s and %s
        group by s.symptom, coalesce(s.category, hs.category)
        order by incident_count desc, last_seen desc
        """,
        (from_date, to_date),
        as_dict=True,
    )

    columns = [
        {"fieldname": "symptom", "label": _("Symptom"), "fieldtype": "Link", "options": "Health Symptom", "width": 240},
        {"fieldname": "category", "label": _("Category"), "fieldtype": "Data", "width": 180},
        {"fieldname": "incident_count", "label": _("Incidents"), "fieldtype": "Int", "width": 100},
        {"fieldname": "last_seen", "label": _("Last Seen"), "fieldtype": "Date", "width": 120},
    ]

    chart_rows = data[:10]
    chart = {
        "data": {
            "labels": [row.symptom for row in chart_rows],
            "datasets": [{"name": _("Incidents"), "values": [row.incident_count for row in chart_rows]}],
        },
        "type": "bar",
    }
    return columns, data, None, chart
