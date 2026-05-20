# -*- coding: utf-8 -*-
# Copyright: (c) 2025, Steve Fulmer <sfulmer@redhat.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


class ModuleDocFragment(object):
    """Doc fragment for Cisco AI Defense modules."""

    DOCUMENTATION = r"""
options:
  api_key:
    description:
      - Cisco AI Defense API key for authentication.
      - For the Inspection API this is the connection API key.
      - For the Management API this is the tenant API key.
    type: str
    required: true
  region:
    description:
      - API region for the Cisco AI Defense service.
      - Determines the base URL used for API requests.
    type: str
    default: us
    choices:
      - us
      - eu
      - apjc
  validate_certs:
    description:
      - Whether to validate SSL certificates.
    type: bool
    default: true
  timeout:
    description:
      - Timeout in seconds for API requests.
    type: int
    default: 30
"""
