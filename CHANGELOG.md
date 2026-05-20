# Changelog

All notable changes to the `stevefulme1.cisco_ai_defense` Ansible collection
will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [3.0.0] - 2026-05-20

### Removed

- **All 35 modules deleted** -- every module used fabricated REST API endpoints
  (`/api/v1/guardrails`, `/api/v1/policies`, `/api/v1/threat_detection`, etc.)
  that do not exist in the real Cisco AI Defense API. The actual API is an
  Inspection API at `POST /api/v1/inspect/chat`.
- **All 6 roles deleted** -- roles called fabricated endpoints via
  `ansible.builtin.uri` (`/organizations/{id}/policies/baseline`, etc.).
- **Lookup plugin deleted** (`ai_defense_policy`) -- used fabricated
  `/policies/{id}` endpoint.
- **EDA plugins deleted** (`threat_events`, `severity_filter`) -- used
  fabricated `/api/v1/alerts` endpoint.
- **module_utils/ai_defense.py** deleted.

### Retained

- 4 filter plugins (data transformation only, no API calls).

## [2.0.0] - 2026-05-19

### Added

- 21 new modules (now deleted), 4 roles (now deleted), filter/lookup/EDA plugins

## [1.0.0] - 2026-05-18

### Added

- Initial release with 14 modules (now deleted), 2 roles (now deleted)
