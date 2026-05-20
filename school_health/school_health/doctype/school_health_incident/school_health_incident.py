import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import getdate, now_datetime


class SchoolHealthIncident(Document):
    def validate(self):
        self.set_defaults()
        self.validate_scores()

    def set_defaults(self):
        if not self.incident_datetime:
            self.incident_datetime = now_datetime()
        if self.incident_datetime:
            self.incident_date = getdate(self.incident_datetime)
        if not self.status:
            self.status = "Open"
        if self.follow_up_required and self.status == "Open":
            self.status = "Follow Up"
        if self.resolved_on:
            self.status = "Resolved"

    def validate_scores(self):
        if self.pain_score is not None and self.pain_score != "":
            pain_score = int(self.pain_score)
            if pain_score < 0 or pain_score > 10:
                frappe.throw(_("Pain Score must be between 0 and 10."))
