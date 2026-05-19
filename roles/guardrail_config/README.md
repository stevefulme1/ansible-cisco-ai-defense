# guardrail_config

Configure guardrails for Cisco AI Defense.

## Description

This role configures guardrail policies for the Cisco AI Defense platform
including PII detection rules, topic boundaries, content filters, and
rate limiting policies.

## Requirements

- Ansible >= 2.16
- Network access to the Cisco AI Defense API endpoint
- Valid Cisco AI Defense API key with guardrail management permissions
- Organization must be registered (see `ai_defense_deploy` role)

## Role Variables

| Variable | Default | Required | Description |
|---|---|---|---|
| `guardrail_config_api_url` | `https://aidefense.cisco.com/api/v1` | no | Base URL for the AI Defense API |
| `guardrail_config_api_key` | `""` | **yes** | API key for authentication (no_log) |
| `guardrail_config_verify_ssl` | `true` | no | Verify SSL certificates |
| `guardrail_config_organization_id` | `""` | **yes** | Organization identifier |
| `guardrail_config_policies` | `[]` | no | List of guardrail policy definitions |
| `guardrail_config_pii_detection_enabled` | `true` | no | Enable PII detection |
| `guardrail_config_pii_entity_types` | `[email, phone_number, credit_card, ssn, ip_address]` | no | PII entity types to detect |
| `guardrail_config_pii_action` | `redact` | no | Action on PII detection: redact, block, log |
| `guardrail_config_topic_boundaries_enabled` | `true` | no | Enable topic boundaries |
| `guardrail_config_allowed_topics` | `[]` | no | Allowed conversation topics |
| `guardrail_config_blocked_topics` | `[]` | no | Blocked conversation topics |
| `guardrail_config_content_filters_enabled` | `true` | no | Enable content filters |
| `guardrail_config_content_filter_categories` | *(see defaults)* | no | Content filter category definitions |
| `guardrail_config_rate_limiting_enabled` | `true` | no | Enable rate limiting |
| `guardrail_config_rate_limit_requests_per_minute` | `60` | no | Max requests per minute |
| `guardrail_config_rate_limit_tokens_per_minute` | `100000` | no | Max tokens per minute |
| `guardrail_config_state` | `present` | no | Desired state |

## Dependencies

None.

## Example Playbook

```yaml
- name: Configure AI Defense guardrails
  hosts: localhost
  connection: local
  gather_facts: false
  roles:
    - role: stevefulme1.cisco_ai_defense.guardrail_config
      guardrail_config_api_key: "{{ vault_ai_defense_api_key }}"
      guardrail_config_organization_id: "org-12345"
      guardrail_config_policies:
        - name: input-safety
          type: input
          enabled: true
          actions:
            - block
            - log
      guardrail_config_pii_entity_types:
        - email
        - credit_card
        - ssn
      guardrail_config_blocked_topics:
        - competitor_products
        - internal_financials
```

## License

GPL-3.0-or-later

## Author

Steve Fulmer
