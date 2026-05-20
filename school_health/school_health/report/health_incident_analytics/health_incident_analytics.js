frappe.query_reports["Health Incident Analytics"] = {
    filters: [
        { fieldname: "from_date", label: __("From Date"), fieldtype: "Date", default: frappe.datetime.add_months(frappe.datetime.get_today(), -12) },
        { fieldname: "to_date", label: __("To Date"), fieldtype: "Date", default: frappe.datetime.get_today() },
        { fieldname: "student", label: __("Student"), fieldtype: "Link", options: "Student" },
        { fieldname: "severity", label: __("Severity"), fieldtype: "Select", options: "\nMild\nModerate\nSevere\nEmergency" },
        { fieldname: "status", label: __("Status"), fieldtype: "Select", options: "\nOpen\nFollow Up\nPending Pickup\nResolved\nEscalated" },
        { fieldname: "category", label: __("Category"), fieldtype: "Select", options: "\nIllness\nInjury\nMedication\nMental / Behavioral\nPreventive Care\nOther" },
    ],
};
