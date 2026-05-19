# -*- coding: utf-8 -*-
# Copyright: (c) 2025, Steve Fulmer <sfulmer@redhat.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""EDA event filter that filters threat events by severity level."""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
name: severity_filter
author: Steve Fulmer (@stevefulme1)
version_added: "1.0.0"
short_description: Filter AI Defense threat events by severity
description:
  - Filters incoming threat events from Cisco AI Defense based on
    a minimum severity threshold. Events below the threshold are
    dropped. Events at or above the threshold are passed through
    to the rulebook for processing.
options:
  minimum_severity:
    description: Minimum severity level to pass through.
    type: str
    default: high
    choices:
      - critical
      - high
      - medium
      - low
"""

# Severity levels ordered from lowest to highest
SEVERITY_LEVELS = {
    "low": 1,
    "medium": 2,
    "high": 3,
    "critical": 4,
}


def main(event, minimum_severity="high"):
    """Filter threat events by severity threshold.

    Events with severity at or above the minimum_severity threshold
    are passed through unchanged. Events below the threshold are
    dropped (return None).

    Args:
        event: The incoming event dict. Expected to contain a
               'severity' key with a string value.
        minimum_severity: Minimum severity to pass through.
                         One of: critical, high, medium, low.
                         Defaults to 'high'.

    Returns:
        dict or None: The event if it meets the threshold, None otherwise.
    """
    minimum_severity = minimum_severity.lower()
    if minimum_severity not in SEVERITY_LEVELS:
        # Invalid threshold, pass everything through for safety
        return event

    threshold = SEVERITY_LEVELS[minimum_severity]

    event_severity = event.get("severity", "").lower()
    if event_severity not in SEVERITY_LEVELS:
        # Unknown severity, pass through for manual review
        return event

    if SEVERITY_LEVELS[event_severity] >= threshold:
        return event

    return None
