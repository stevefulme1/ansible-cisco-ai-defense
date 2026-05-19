# baseline_policy

Apply baseline guardrail policies for common AI use cases.

## Description

This role applies preset guardrail policies tuned for specific AI use cases.
Each preset includes appropriate content filters, PII detection entity types,
and operational parameters. Available presets: chatbot, code_generation,
document_analysis, and customer_service.

## Requirements

- Ansible >= 2.16
- Network access to the Cisco AI Defense API endpoint
- Valid Cisco AI Defense API key
- Organization must be registered (see `ai_defense_deploy` role)

## Role Variables

| Variable | Default | Required | Description |
|---|---|---|---|
| `ai_defense_baseline_api_url` | `https://aidefense.cisco.com/api/v1` | no | Base URL for the AI Defense API |
| `ai_defense_baseline_api_key` | `""` | **yes** | API key for authentication (no_log) |
| `ai_defense_baseline_verify_ssl` | `true` | no | Verify SSL certificates |
| `ai_defense_baseline_organization_id` | `""` | **yes** | Organization identifier |
| `ai_defense_baseline_preset` | `chatbot` | no | Use case preset: chatbot, code_generation, document_analysis, customer_service |
| `ai_defense_baseline_pii_detection` | `true` | no | Enable PII detection |
| `ai_defense_baseline_prompt_injection_defense` | `true` | no | Enable prompt injection defense |
| `ai_defense_baseline_rate_limiting` | `true` | no | Enable rate limiting |
| `ai_defense_baseline_rate_limit_rpm` | `60` | no | Max requests per minute |
| `ai_defense_baseline_rate_limit_tpm` | `100000` | no | Max tokens per minute |
| `ai_defense_baseline_state` | `present` | no | Desired state |

## Dependencies

None.

## Example Playbook

```yaml
- name: Apply baseline policy for customer service chatbot
  hosts: localhost
  connection: local
  gather_facts: false
  roles:
    - role: stevefulme1.cisco_ai_defense.baseline_policy
      ai_defense_baseline_api_key: "{{ vault_ai_defense_api_key }}"
      ai_defense_baseline_organization_id: "org-12345"
      ai_defense_baseline_preset: customer_service
```

## License

GPL-3.0-or-later

## Author

Steve Fulmer
