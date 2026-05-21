from frappe.model.document import Document

from school_health.school_health.utils import get_student_name


class StudentHealthProfile(Document):
    def validate(self):
        self.student_name = get_student_name(self.student) if self.student else ""
