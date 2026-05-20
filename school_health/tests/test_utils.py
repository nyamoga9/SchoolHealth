import unittest
from datetime import date, timedelta

from school_health.school_health.utils import (
    normalize_severity,
    status_for_legacy_incident,
    symptom_name_from_legacy,
)


class TestSchoolHealthUtils(unittest.TestCase):
    def test_normalize_severity_defaults_safely(self):
        self.assertEqual(normalize_severity("critical"), "Emergency")
        self.assertEqual(normalize_severity(""), "Mild")
        self.assertEqual(normalize_severity("Moderate"), "Moderate")

    def test_legacy_status_uses_follow_up_and_escalation(self):
        self.assertEqual(status_for_legacy_incident(1, date.today() + timedelta(days=1)), "Follow Up")
        self.assertEqual(status_for_legacy_incident(1, date.today() - timedelta(days=1)), "Resolved")
        self.assertEqual(status_for_legacy_incident(0, None, "Hospitalized"), "Escalated")

    def test_symptom_name_from_legacy(self):
        self.assertEqual(symptom_name_from_legacy("Fever - General Symptoms"), "Fever")
        self.assertEqual(symptom_name_from_legacy("Nose bleed"), "Nose bleed")


if __name__ == "__main__":
    unittest.main()
