frappe.ui.form.on("School Health Incident", {
    setup(frm) {
        frm.set_query("student", () => ({
            filters: {
                enabled: 1,
            },
        }));

        frm.set_query("reported_by", () => ({
            filters: {
                status: "Active",
            },
        }));
    },

    refresh(frm) {
        if (frm.is_new()) {
            return;
        }

        if (frm.doc.follow_up_required && frm.doc.status !== "Resolved") {
            frm.dashboard.add_indicator(__("Follow-up Needed"), "orange");
        }
        if (["Severe", "Emergency"].includes(frm.doc.severity)) {
            frm.dashboard.add_indicator(__("High Severity"), "red");
        }
    },

    incident_datetime(frm) {
        if (frm.doc.incident_datetime) {
            frm.set_value("incident_date", frappe.datetime.str_to_obj(frm.doc.incident_datetime));
        }
    },

    follow_up_required(frm) {
        if (frm.doc.follow_up_required && frm.doc.status === "Open") {
            frm.set_value("status", "Follow Up");
        }
    },

    resolved_on(frm) {
        if (frm.doc.resolved_on) {
            frm.set_value("status", "Resolved");
        }
    },
});
