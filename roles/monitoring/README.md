# monitoring

Configure monitoring and alerting for Cisco AI Defense.

## Description

This role configures monitoring and alerting for the Cisco AI Defense platform.
It sets up Splunk integration for log forwarding, configures alerting rules
with severity-based thresholds, enables compliance monitoring for regulatory
frameworks (EU AI Act, NIST AI RMF, ISO 42001), and manages the monitoring
dashboard.

## Requirements

- Ansible >= 2.16
- Network access to the Cisco AI Defense API endpoint
- Valid Cisco AI Defense API key with monitoring permissions
- Splunk HEC endpoint (if configuring Splunk integration)

## Role Variables

| Variable | Default | Required | Description |
|---|---|---|---|
| `ai_defense_monitoring_api_url` | `https://aidefense.cisco.com/api/v1` | no | Base URL for the AI Defense API |
| `ai_defense_monitoring_api_key` | `""` | **yes** | API key for authentication (no_log) |
| `ai_defense_monitoring_verify_ssl` | `true` | no | Verify SSL certificates |
| `ai_defense_monitoring_organization_id` | `""` | **yes** | Organization identifier |
| `ai_defense_monitoring_splunk_url` | `""` | no | Splunk HEC URL |
| `ai_defense_monitoring_splunk_token` | `""` | no | Splunk HEC token (no_log) |
| `ai_defense_monitoring_splunk_index` | `ai_defense` | no | Splunk index name |
| `ai_defense_monitoring_splunk_source_type` | `cisco:ai_defense` | no | Splunk source type |
| `ai_defense_monitoring_alert_severity_threshold` | `high` | no | Min severity for alerts: critical, high, medium, low |
| `ai_defense_monitoring_alert_channels` | `[email]` | no | Alert notification channels |
| `ai_defense_monitoring_alert_email_recipients` | `[]` | no | Email recipients for alerts |
| `ai_defense_monitoring_dashboard_enabled` | `true` | no | Enable monitoring dashboard |
| `ai_defense_monitoring_compliance_frameworks` | `[eu_ai_act, nist_ai_rmf]` | no | Compliance frameworks to monitor |
| `ai_defense_monitoring_state` | `present` | no | Desired state |

## Dependencies

None.

## Example Playbook

```yaml
- name: Configure AI Defense monitoring
  hosts: localhost
  connection: local
  gather_facts: false
  roles:
    - role: stevefulme1.cisco_ai_defense.monitoring
      ai_defense_monitoring_api_key: "{{ vault_ai_defense_api_key }}"
      ai_defense_monitoring_organization_id: "org-12345"
      ai_defense_monitoring_splunk_url: "https://splunk.example.com:8088"
      ai_defense_monitoring_splunk_token: "{{ vault_splunk_token }}"
      ai_defense_monitoring_alert_email_recipients:
        - security@example.com
      ai_defense_monitoring_compliance_frameworks:
        - eu_ai_act
        - nist_ai_rmf
        - iso_42001
```

## License

GPL-3.0-or-later

## Author

Steve Fulmer
