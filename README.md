# Cisco AI Defense Ansible Collection

Ansible Collection for Cisco AI Defense platform. Provides modules for managing policies, guardrails, threat detection, model scanning, API protection, compliance reports, audit logs, and threat feeds via the Cisco AI Defense REST API.

## Requirements

- Ansible >= 2.16
- Python >= 3.9
- `requests` Python library

## Installation

```bash
ansible-galaxy collection install stevefulme1.cisco_ai_defense
```

## Modules

- `stevefulme1.cisco_ai_defense.policy` - Manage policies in Cisco AI Defense
- `stevefulme1.cisco_ai_defense.policy_info` - Retrieve policy information from Cisco AI Defense
- `stevefulme1.cisco_ai_defense.guardrail` - Manage guardrails in Cisco AI Defense
- `stevefulme1.cisco_ai_defense.guardrail_info` - Retrieve guardrail information from Cisco AI Defense
- `stevefulme1.cisco_ai_defense.threat_detection` - Manage threat detection rules in Cisco AI Defense
- `stevefulme1.cisco_ai_defense.threat_detection_info` - Retrieve threat detection information from Cisco AI Defense
- `stevefulme1.cisco_ai_defense.model_scan` - Manage model scanning configurations in Cisco AI Defense
- `stevefulme1.cisco_ai_defense.model_scan_info` - Retrieve model scan information from Cisco AI Defense
- `stevefulme1.cisco_ai_defense.api_protection` - Manage API protection rules in Cisco AI Defense
- `stevefulme1.cisco_ai_defense.api_protection_info` - Retrieve API protection information from Cisco AI Defense
- `stevefulme1.cisco_ai_defense.compliance_report` - Manage compliance reports in Cisco AI Defense
- `stevefulme1.cisco_ai_defense.compliance_report_info` - Retrieve compliance report information from Cisco AI Defense
- `stevefulme1.cisco_ai_defense.audit_log_info` - Retrieve audit log information from Cisco AI Defense
- `stevefulme1.cisco_ai_defense.threat_feed` - Manage threat feed configurations in Cisco AI Defense

## Roles

- `ai_defense_deploy` - Deploy Cisco AI Defense agents and policies
- `guardrail_config` - Configure guardrails for Cisco AI Defense

## Event-Driven Ansible

- `threat_events` - Cisco AI Defense Threat Events event source plugin

## License

GPL-3.0-or-later

## Author

Steve Fulmer ([@stevefulme1](https://github.com/stevefulme1))
