"""Unit tests for stevefulme1.cisco_ai_defense filter plugins."""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import importlib
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'plugins', 'filter'))
FilterModule = importlib.import_module('ai_defense_filters').FilterModule


@pytest.fixture
def fm():
    """Return a FilterModule instance."""
    return FilterModule()


class TestFilterRegistration:
    """Verify filter names are registered."""

    def test_filters_returns_dict(self, fm):
        result = fm.filters()
        assert isinstance(result, dict)

    def test_expected_filters_present(self, fm):
        filters = fm.filters()
        expected = [
            "ai_defense_risk_score",
            "ai_defense_critical_findings",
            "ai_defense_format_compliance",
            "ai_defense_pii_summary",
        ]
        for name in expected:
            assert name in filters


# ------------------------------------------------------------------ #
# ai_defense_risk_score
# ------------------------------------------------------------------ #
class TestRiskScore:

    def test_empty_findings(self):
        assert FilterModule.ai_defense_risk_score([]) == 0.0

    def test_single_critical(self):
        assert FilterModule.ai_defense_risk_score([{"severity": "critical"}]) == 10.0

    def test_single_low(self):
        assert FilterModule.ai_defense_risk_score([{"severity": "low"}]) == 1.0

    def test_mixed_severities(self):
        findings = [
            {"severity": "critical"},
            {"severity": "low"},
        ]
        score = FilterModule.ai_defense_risk_score(findings)
        # (10 + 1) / 2 = 5.5
        assert score == 5.5

    def test_unknown_severity_defaults_to_low(self):
        findings = [{"severity": "unknown"}]
        assert FilterModule.ai_defense_risk_score(findings) == 1.0

    def test_missing_severity_defaults_to_low(self):
        findings = [{}]
        assert FilterModule.ai_defense_risk_score(findings) == 1.0

    @pytest.mark.parametrize("severity,expected", [
        ("critical", 10.0),
        ("high", 7.0),
        ("medium", 4.0),
        ("low", 1.0),
    ])
    def test_individual_weights(self, severity, expected):
        assert FilterModule.ai_defense_risk_score([{"severity": severity}]) == expected

    def test_case_insensitive(self):
        assert FilterModule.ai_defense_risk_score([{"severity": "HIGH"}]) == 7.0


# ------------------------------------------------------------------ #
# ai_defense_critical_findings
# ------------------------------------------------------------------ #
class TestCriticalFindings:

    def test_empty_list(self):
        assert FilterModule.ai_defense_critical_findings([]) == []

    def test_filters_critical_and_high(self):
        findings = [
            {"severity": "critical", "id": 1},
            {"severity": "high", "id": 2},
            {"severity": "medium", "id": 3},
            {"severity": "low", "id": 4},
        ]
        result = FilterModule.ai_defense_critical_findings(findings)
        assert len(result) == 2
        assert {f["id"] for f in result} == {1, 2}

    def test_all_low_returns_empty(self):
        findings = [{"severity": "low"}, {"severity": "medium"}]
        assert FilterModule.ai_defense_critical_findings(findings) == []

    def test_case_insensitive(self):
        findings = [{"severity": "CRITICAL"}]
        assert len(FilterModule.ai_defense_critical_findings(findings)) == 1


# ------------------------------------------------------------------ #
# ai_defense_format_compliance
# ------------------------------------------------------------------ #
class TestFormatCompliance:

    @pytest.fixture
    def sample_report(self):
        return {
            "score": 85,
            "timestamp": "2025-01-01T00:00:00Z",
            "findings": [
                {"section": "risk_classification", "severity": "critical"},
                {"section": "data_governance", "severity": "medium"},
                {"section": "govern", "severity": "high"},
            ],
        }

    def test_eu_ai_act_framework(self, sample_report):
        result = FilterModule.ai_defense_format_compliance(sample_report, "eu_ai_act")
        assert result["framework"] == "eu_ai_act"
        assert result["framework_label"] == "EU AI Act"
        assert result["overall_score"] == 85
        assert "risk_classification" in result["sections"]
        assert result["total_findings"] == 3
        assert result["critical_findings"] == 1

    def test_nist_framework(self, sample_report):
        result = FilterModule.ai_defense_format_compliance(sample_report, "nist_ai_rmf")
        assert result["framework_label"] == "NIST AI Risk Management Framework"
        assert "govern" in result["sections"]

    def test_iso_framework(self, sample_report):
        result = FilterModule.ai_defense_format_compliance(sample_report, "iso_42001")
        assert "ai_policy" in result["sections"]

    def test_unknown_framework(self, sample_report):
        result = FilterModule.ai_defense_format_compliance(sample_report, "custom_fw")
        assert result["framework_label"] == "custom_fw"
        assert result["sections"] == []

    def test_empty_report(self):
        result = FilterModule.ai_defense_format_compliance({}, "eu_ai_act")
        assert result["overall_score"] == 0
        assert result["total_findings"] == 0


# ------------------------------------------------------------------ #
# ai_defense_pii_summary
# ------------------------------------------------------------------ #
class TestPiiSummary:

    def test_empty_results(self):
        result = FilterModule.ai_defense_pii_summary([])
        assert result["total_detections"] == 0
        assert result["by_type"] == {}
        assert result["actions_taken"] == {}

    def test_single_detection(self):
        pii = [{"entity_type": "ssn", "count": 3, "action": "redacted"}]
        result = FilterModule.ai_defense_pii_summary(pii)
        assert result["total_detections"] == 3
        assert result["by_type"] == {"ssn": 3}
        assert result["actions_taken"] == {"redacted": 3}

    def test_multiple_types(self):
        pii = [
            {"entity_type": "ssn", "count": 2, "action": "redacted"},
            {"entity_type": "email", "count": 5, "action": "masked"},
            {"entity_type": "ssn", "count": 1, "action": "redacted"},
        ]
        result = FilterModule.ai_defense_pii_summary(pii)
        assert result["total_detections"] == 8
        assert result["by_type"]["ssn"] == 3
        assert result["by_type"]["email"] == 5
        assert result["actions_taken"]["redacted"] == 3
        assert result["actions_taken"]["masked"] == 5

    def test_missing_action_defaults(self):
        pii = [{"entity_type": "phone", "count": 1}]
        result = FilterModule.ai_defense_pii_summary(pii)
        assert result["actions_taken"]["detected"] == 1

    def test_missing_count_defaults_to_one(self):
        pii = [{"entity_type": "email"}]
        result = FilterModule.ai_defense_pii_summary(pii)
        assert result["total_detections"] == 1
