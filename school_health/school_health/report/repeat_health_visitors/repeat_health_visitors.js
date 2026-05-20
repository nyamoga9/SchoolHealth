frappe.query_reports["Repeat Health Visitors"] = {
    filters: [
        { fieldname: "from_date", label: __("From Date"), fieldtype: "Date", default: frappe.datetime.add_months(frappe.datetime.get_today(), -12) },
        { fieldname: "to_date", label: __("To Date"), fieldtype: "Date", default: frappe.datetime.get_today() },
        { fieldname: "min_visits", label: __("Minimum Visits"), fieldtype: "Int", default: 2 },
    ],
};
