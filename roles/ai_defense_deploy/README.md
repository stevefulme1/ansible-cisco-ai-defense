# ai_defense_deploy

Deploy and configure the Cisco AI Defense platform.

## Description

This role handles the initial deployment and configuration of Cisco AI Defense.
It validates API connectivity, registers your organization, configures API
credentials and permissions, sets up webhook endpoints for event notifications,
and verifies that the deployment is healthy.

## Requirements

- Ansible >= 2.16
- Network access to the Cisco AI Defense API endpoint
- Valid Cisco AI Defense API key with administrative permissions

## Role Variables

| Variable | Default | Required | Description |
|---|---|---|---|
| `ai_defense_deploy_api_url` | `https://aidefense.cisco.com/api/v1` | no | Base URL for the AI Defense API |
| `ai_defense_deploy_api_key` | `""` | **yes** | API key for authentication (no_log) |
| `ai_defense_deploy_verify_ssl` | `true` | no | Verify SSL certificates |
| `ai_defense_deploy_organization_id` | `""` | **yes** | Organization identifier |
| `ai_defense_deploy_organization_name` | `""` | no | Human-readable organization name |
| `ai_defense_deploy_webhook_url` | `""` | no | Webhook URL for event notifications |
| `ai_defense_deploy_webhook_secret` | `""` | no | Shared secret for webhook verification (no_log) |
| `ai_defense_deploy_webhook_events` | `[threat_detected, policy_violation, compliance_alert]` | no | Event types to subscribe to |
| `ai_defense_deploy_log_level` | `info` | no | Log level: debug, info, warning, error |
| `ai_defense_deploy_state` | `present` | no | Desired state: present or absent |
| `ai_defense_deploy_api_timeout` | `30` | no | API request timeout in seconds |
| `ai_defense_deploy_health_check_retries` | `5` | no | Health check retry count |
| `ai_defense_deploy_health_check_delay` | `10` | no | Delay between health check retries |

## Dependencies

None.

## Example Playbook

```yaml
- name: Deploy Cisco AI Defense
  hosts: localhost
  connection: local
  gather_facts: false
  roles:
    - role: stevefulme1.cisco_ai_defense.ai_defense_deploy
      ai_defense_deploy_api_key: "{{ vault_ai_defense_api_key }}"
      ai_defense_deploy_organization_id: "org-12345"
      ai_defense_deploy_organization_name: "My Organization"
      ai_defense_deploy_webhook_url: "https://hooks.example.com/ai-defense"
      ai_defense_deploy_webhook_secret: "{{ vault_webhook_secret }}"
```

## License

GPL-3.0-or-later

## Author

Steve Fulmer
