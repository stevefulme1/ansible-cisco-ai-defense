# -*- coding: utf-8 -*-
# Copyright: (c) 2025, Steve Fulmer <sfulmer@redhat.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Filter plugins for Cisco AI Defense collection."""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
name: ai_defense_filters
author: Steve Fulmer (@stevefulme1)
version_added: "1.0.0"
short_description: Filter plugins for Cisco AI Defense data
description:
  - Provides filters for processing Cisco AI Defense findings,
    compliance reports, and PII detection results.
"""


class FilterModule:
    """Cisco AI Defense filter plugins."""

    def filters(self):
        """Return a dict mapping filter names to callables."""
        return {
            "ai_defense_risk_score": self.ai_defense_risk_score,
            "ai_defense_critical_findings": self.ai_defense_critical_findings,
            "ai_defense_format_compliance": self.ai_defense_format_compliance,
            "ai_defense_pii_summary": self.ai_defense_pii_summary,
        }

    @staticmethod
    def ai_defense_risk_score(findings):
        """Calculate aggregate risk score from a list of findings.

        Each finding should have a 'severity' key with value:
        critical (10), high (7), medium (4), or low (1).
        Returns the weighted average score on a 0-10 scale.

        Args:
            findings: List of dicts, each with a 'severity' key.

        Returns:
            float: Weighted average risk score (0.0-10.0).
        """
        severity_weights = {
            "critical": 10,
            "high": 7,
            "medium": 4,
            "low": 1,
        }

        if not findings:
            return 0.0

        total_score = 0
        for finding in findings:
            severity = finding.get("severity", "low").lower()
            total_score += severity_weights.get(severity, 1)

        return round(total_score / len(findings), 2)

    @staticmethod
    def ai_defense_critical_findings(findings):
        """Filter to only critical and high severity findings.

        Args:
            findings: List of dicts, each with a 'severity' key.

        Returns:
            list: Findings with severity 'critical' or 'high'.
        """
        critical_severities = {"critical", "high"}
        return [
            f
            for f in findings
            if f.get("severity", "").lower() in critical_severities
        ]

    @staticmethod
    def ai_defense_format_compliance(report, framework="eu_ai_act"):
        """Format a compliance report for a specific regulatory framework.

        Supported frameworks: eu_ai_act, nist_ai_rmf, iso_42001.

        Args:
            report: Dict containing compliance report data with 'findings',
                    'score', and 'timestamp' keys.
            framework: Target framework identifier string.

        Returns:
            dict: Formatted compliance report with framework-specific fields.
        """
        framework_labels = {
            "eu_ai_act": "EU AI Act",
            "nist_ai_rmf": "NIST AI Risk Management Framework",
            "iso_42001": "ISO/IEC 42001",
        }

        framework_sections = {
            "eu_ai_act": [
                "risk_classification",
                "transparency_requirements",
                "data_governance",
                "human_oversight",
                "technical_robustness",
            ],
            "nist_ai_rmf": [
                "govern",
                "map",
                "measure",
                "manage",
            ],
            "iso_42001": [
                "ai_policy",
                "planning",
                "support",
                "operation",
                "performance_evaluation",
                "improvement",
            ],
        }

        label = framework_labels.get(framework, framework)
        sections = framework_sections.get(framework, [])

        findings = report.get("findings", [])
        section_findings = {}
        for section in sections:
            section_findings[section] = [
                f for f in findings if f.get("section", "") == section
            ]

        return {
            "framework": framework,
            "framework_label": label,
            "overall_score": report.get("score", 0),
            "timestamp": report.get("timestamp", ""),
            "sections": sections,
            "section_findings": section_findings,
            "total_findings": len(findings),
            "critical_findings": len(
                [f for f in findings if f.get("severity") == "critical"]
            ),
        }

    @staticmethod
    def ai_defense_pii_summary(pii_results):
        """Summarize PII detection results by entity type.

        Args:
            pii_results: List of PII detection result dicts, each with
                        'entity_type', 'count', and optionally 'action' keys.

        Returns:
            dict: Summary with total_detections, by_type breakdown,
                  and actions_taken counts.
        """
        if not pii_results:
            return {
                "total_detections": 0,
                "by_type": {},
                "actions_taken": {},
            }

        by_type = {}
        actions_taken = {}
        total = 0

        for result in pii_results:
            entity_type = result.get("entity_type", "unknown")
            count = result.get("count", 1)
            action = result.get("action", "detected")

            total += count
            by_type[entity_type] = by_type.get(entity_type, 0) + count
            actions_taken[action] = actions_taken.get(action, 0) + count

        return {
            "total_detections": total,
            "by_type": by_type,
            "actions_taken": actions_taken,
        }
