# supply_chain

Supply chain scanning pipeline for AI models in CI/CD.

## Description

This role provides a supply chain scanning pipeline for AI models. It scans
model files for known vulnerabilities, scans associated container images,
verifies model provenance and lineage, generates SBOM reports in SPDX format,
and evaluates overall risk against a configurable threshold.

## Requirements

- Ansible >= 2.16
- Network access to the Cisco AI Defense API endpoint
- Valid Cisco AI Defense API key with supply chain scanning permissions
- Model reference must be accessible from AI Defense

## Role Variables

| Variable | Default | Required | Description |
|---|---|---|---|
| `ai_defense_supply_chain_api_url` | `https://aidefense.cisco.com/api/v1` | no | Base URL for the AI Defense API |
| `ai_defense_supply_chain_api_key` | `""` | **yes** | API key for authentication (no_log) |
| `ai_defense_supply_chain_verify_ssl` | `true` | no | Verify SSL certificates |
| `ai_defense_supply_chain_organization_id` | `""` | **yes** | Organization identifier |
| `ai_defense_supply_chain_model_reference` | `""` | **yes** | Model reference to scan |
| `ai_defense_supply_chain_scan_containers` | `true` | no | Scan container images |
| `ai_defense_supply_chain_container_images` | `[]` | no | Container image references to scan |
| `ai_defense_supply_chain_verify_provenance` | `true` | no | Verify model provenance |
| `ai_defense_supply_chain_generate_sbom` | `true` | no | Generate SBOM report |
| `ai_defense_supply_chain_risk_threshold` | `medium` | no | Max risk level: critical, high, medium, low |
| `ai_defense_supply_chain_fail_on_risk` | `true` | no | Fail play if risk exceeds threshold |
| `ai_defense_supply_chain_poll_interval` | `15` | no | Seconds between status polls |
| `ai_defense_supply_chain_poll_timeout` | `300` | no | Max seconds to wait |

## Dependencies

None.

## Example Playbook

```yaml
- name: Run supply chain scan in CI/CD pipeline
  hosts: localhost
  connection: local
  gather_facts: false
  roles:
    - role: stevefulme1.cisco_ai_defense.supply_chain
      ai_defense_supply_chain_api_key: "{{ vault_ai_defense_api_key }}"
      ai_defense_supply_chain_organization_id: "org-12345"
      ai_defense_supply_chain_model_reference: "models/gpt-custom-v2"
      ai_defense_supply_chain_container_images:
        - registry.example.com/ml-model:v2.1
      ai_defense_supply_chain_risk_threshold: high
```

## License

GPL-3.0-or-later

## Author

Steve Fulmer
