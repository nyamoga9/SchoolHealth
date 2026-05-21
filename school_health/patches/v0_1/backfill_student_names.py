import frappe


def execute():
    for doctype in ("School Health Incident", "Student Health Profile"):
        if not frappe.db.table_exists(doctype):
            continue

        frappe.db.sql(
            f"""
            update `tab{doctype}` r
            left join `tabStudent` s on s.name = r.student
            set r.student_name = coalesce(
                nullif(trim(s.student_name), ''),
                nullif(
                    trim(
                        concat_ws(
                            ' ',
                            nullif(trim(s.first_name), ''),
                            nullif(trim(s.middle_name), ''),
                            nullif(trim(s.last_name), '')
                        )
                    ),
                    ''
                ),
                r.student
            )
            where ifnull(r.student, '') != ''
                and ifnull(r.student_name, '') = ''
            """
        )
