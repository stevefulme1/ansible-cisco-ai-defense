> **EXPERIMENTAL** - This collection is a proof of concept and is not production ready.

# Cisco AI Defense Ansible Collection

Ansible Collection for the Cisco AI Defense platform.

**Status: Pre-release. Under active development.**

> **Note:** All 35 modules, 6 roles, 1 lookup plugin, and 2 EDA plugins were
> removed during an audit because they used fabricated REST API endpoints
> (`/api/v1/guardrails`, `/api/v1/policies`, `/organizations/{id}/...`, etc.)
> that do not exist in the real Cisco AI Defense API.  The actual Cisco AI
> Defense API is an Inspection API at
> `POST /api/v1/inspect/chat` using `X-Cisco-AI-Defense-API-Key` header
> authentication -- it evaluates prompts and responses, not CRUD management
> of guardrails/policies/scans.

## Remaining Content

### Filter Plugins (4)

Data-transformation filters (no API calls):

| Filter | Description |
|---|---|
| `ai_defense_risk_score` | Calculate aggregate risk score from findings |
| `ai_defense_critical_findings` | Extract critical findings from scan results |
| `ai_defense_format_compliance` | Format compliance report for a given framework |
| `ai_defense_pii_summary` | Summarize PII detection results |

## Requirements

| Dependency | Version |
|---|---|
| Python | >= 3.9 |
| ansible-core | >= 2.16.0 |

## Installation

```bash
ansible-galaxy collection install stevefulme1.cisco_ai_defense
```

## License

GNU General Public License v3.0 or later.
