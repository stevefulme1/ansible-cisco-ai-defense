# red_team

Automated red-team validation workflow for Cisco AI Defense.

## Description

This role configures and executes automated red-team validation against AI model
endpoints. It tests for common attack vectors including prompt injection,
jailbreak attempts, PII leakage, hallucination, toxicity, and bias. Results
are evaluated against a configurable pass threshold, enabling CI/CD gate checks.

## Requirements

- Ansible >= 2.16
- Network access to the Cisco AI Defense API endpoint
- Valid Cisco AI Defense API key with red-team permissions
- Target model endpoint must be accessible from AI Defense

## Role Variables

| Variable | Default | Required | Description |
|---|---|---|---|
| `ai_defense_redteam_api_url` | `https://aidefense.cisco.com/api/v1` | no | Base URL for the AI Defense API |
| `ai_defense_redteam_api_key` | `""` | **yes** | API key for authentication (no_log) |
| `ai_defense_redteam_verify_ssl` | `true` | no | Verify SSL certificates |
| `ai_defense_redteam_organization_id` | `""` | **yes** | Organization identifier |
| `ai_defense_redteam_model_endpoint` | `""` | **yes** | AI model endpoint URL to validate |
| `ai_defense_redteam_categories` | `[prompt_injection, jailbreak, pii_leakage, hallucination, toxicity, bias]` | no | Attack categories to test |
| `ai_defense_redteam_pass_threshold` | `0.8` | no | Minimum score to pass (0.0-1.0) |
| `ai_defense_redteam_fail_on_threshold` | `true` | no | Fail play if below threshold |
| `ai_defense_redteam_report_format` | `json` | no | Report format: json, html, csv |
| `ai_defense_redteam_poll_interval` | `30` | no | Seconds between status polls |
| `ai_defense_redteam_poll_timeout` | `600` | no | Max seconds to wait for completion |

## Dependencies

None.

## Example Playbook

```yaml
- name: Run red-team validation
  hosts: localhost
  connection: local
  gather_facts: false
  roles:
    - role: stevefulme1.cisco_ai_defense.red_team
      ai_defense_redteam_api_key: "{{ vault_ai_defense_api_key }}"
      ai_defense_redteam_organization_id: "org-12345"
      ai_defense_redteam_model_endpoint: "https://api.example.com/v1/chat"
      ai_defense_redteam_categories:
        - prompt_injection
        - jailbreak
        - pii_leakage
      ai_defense_redteam_pass_threshold: 0.9
```

## License

GPL-3.0-or-later

## Author

Steve Fulmer
