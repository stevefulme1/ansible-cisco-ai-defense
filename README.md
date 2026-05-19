# Cisco AI Defense Ansible Collection

[![CI](https://github.com/stevefulme1/ansible-cisco-ai-defense/actions/workflows/ci.yml/badge.svg)](https://github.com/stevefulme1/ansible-cisco-ai-defense/actions/workflows/ci.yml)
[![Ansible Galaxy](https://img.shields.io/badge/galaxy-stevefulme1.cisco__ai__defense-blue.svg)](https://galaxy.ansible.com/ui/repo/published/stevefulme1/cisco_ai_defense/)

Ansible Collection for the Cisco AI Defense platform. Provides
35 modules, 6 roles, 4 filter plugins, 1 lookup plugin, and 2 EDA
plugins for comprehensive AI security lifecycle management -- from
guardrail enforcement and threat detection to model supply chain
validation, red-team testing, and compliance reporting via the Cisco
AI Defense REST API.

## Requirements

| Dependency | Version |
|---|---|
| Python | >= 3.9 |
| ansible-core | >= 2.16.0 |
| `requests` | latest |

## Installation

```bash
ansible-galaxy collection install stevefulme1.cisco_ai_defense
```

Install the Python dependency:

```bash
pip install requests
```

## Authentication

All modules require two parameters for API access:

| Parameter | Description |
|---|---|
| `api_url` | Base URL of your Cisco AI Defense instance |
| `api_key` | API key for authentication (use `no_log`) |

### Using Ansible Vault (recommended)

```yaml
# group_vars/all/vault.yml (encrypt with ansible-vault)
vault_ai_defense_api_key: "your-api-key-here"

# group_vars/all/vars.yml
ai_defense_api_url: "https://aidefense.example.com"
ai_defense_api_key: "{{ vault_ai_defense_api_key }}"
```

### Environment variables

```yaml
- name: Use env vars
  stevefulme1.cisco_ai_defense.policy_info:
    api_url: "{{ lookup('env', 'AI_DEFENSE_URL') }}"
    api_key: "{{ lookup('env', 'AI_DEFENSE_API_KEY') }}"
```

## Content

### Modules (35)

#### Policy Management

| Module | Description |
|---|---|
| `policy` | Manage policies in Cisco AI Defense |
| `policy_info` | Retrieve policy information from Cisco AI Defense |
| `policy_assignment` | Assign policies to endpoints, models, or applications |
| `policy_export` | Export policies as structured data |
| `policy_import` | Import policies from definitions |
| `topic_policy` | Configure allowed and blocked topic policies |
| `pii_policy` | Configure PII detection and masking policies |

#### Guardrails

| Module | Description |
|---|---|
| `guardrail` | Manage guardrails in Cisco AI Defense |
| `guardrail_info` | Retrieve guardrail information |
| `guardrail_rule` | Manage individual guardrail rules |

#### Threat Detection

| Module | Description |
|---|---|
| `threat_detection` | Manage threat detection rules |
| `threat_detection_info` | Retrieve threat detection information |
| `threat_feed` | Manage threat feed configurations |

#### Model Security

| Module | Description |
|---|---|
| `model_scan` | Manage model scanning configurations |
| `model_scan_info` | Retrieve model scan information |
| `model_provenance` | Validate AI model provenance |
| `container_scan` | Scan AI workload containers |

#### API Protection

| Module | Description |
|---|---|
| `api_protection` | Manage API protection rules |
| `api_protection_info` | Retrieve API protection information |
| `rate_limit` | Configure rate limiting |

#### Compliance and Reporting

| Module | Description |
|---|---|
| `compliance_report` | Manage compliance reports |
| `compliance_report_info` | Retrieve compliance report information |
| `supply_chain_report` | Generate AI supply chain risk reports |
| `supply_chain_report_info` | Retrieve supply chain reports |
| `audit_log_info` | Retrieve audit log information |
| `metrics_info` | Retrieve protection metrics |

#### Discovery and Inventory

| Module | Description |
|---|---|
| `discovery` | Trigger AI workload discovery scans |
| `inventory_info` | Query discovered AI asset inventory |
| `shadow_ai` | Detect unauthorized shadow AI workloads |

#### Validation (Red Team)

| Module | Description |
|---|---|
| `validation_run` | Execute automated red-team validation |
| `validation_config` | Configure validation parameters |
| `validation_schedule` | Schedule recurring AI model validations |
| `validation_categories_info` | List available validation categories |
| `validation_report_info` | Retrieve validation run results |

#### Integrations

| Module | Description |
|---|---|
| `splunk_integration` | Configure Splunk telemetry export |

### Roles (6)

| Role | Description |
|---|---|
| `ai_defense_deploy` | Deploy and configure the Cisco AI Defense platform |
| `baseline_policy` | Apply baseline guardrail policies for common AI use cases |
| `guardrail_config` | Configure guardrails for Cisco AI Defense |
| `monitoring` | Configure monitoring and alerting for Cisco AI Defense |
| `red_team` | Automated red-team validation workflow |
| `supply_chain` | Supply chain scanning pipeline for AI models in CI/CD |

### Filter Plugins (4)

| Filter | Description |
|---|---|
| `ai_defense_risk_score` | Calculate aggregate risk score from findings |
| `ai_defense_critical_findings` | Extract critical findings from scan results |
| `ai_defense_format_compliance` | Format compliance report for a given framework |
| `ai_defense_pii_summary` | Summarize PII detection results |

### Lookup Plugin (1)

| Plugin | Description |
|---|---|
| `ai_defense_policy` | Retrieve policy details from the Cisco AI Defense API |

### EDA Plugins (2)

| Plugin | Type | Description |
|---|---|---|
| `threat_events` | Event source | Poll Cisco AI Defense for alert events |
| `severity_filter` | Event filter | Filter threat events by severity level |

## Quick Start

### Retrieve all policies

```yaml
- name: List all policies
  stevefulme1.cisco_ai_defense.policy_info:
    api_url: "{{ ai_defense_api_url }}"
    api_key: "{{ ai_defense_api_key }}"
  register: policies

- name: Show policies
  ansible.builtin.debug:
    var: policies.policies
```

### Create a guardrail

```yaml
- name: Create a prompt injection guardrail
  stevefulme1.cisco_ai_defense.guardrail:
    api_url: "{{ ai_defense_api_url }}"
    api_key: "{{ ai_defense_api_key }}"
    name: "block-prompt-injection"
    description: "Block prompt injection attempts"
    guardrail_type: "input"
    action: "block"
    state: present
```

### Run a model supply chain scan

```yaml
- name: Scan model for supply chain risks
  stevefulme1.cisco_ai_defense.supply_chain_report:
    api_url: "{{ ai_defense_api_url }}"
    api_key: "{{ ai_defense_api_key }}"
    model_name: "llama-3-8b"
    model_source: "huggingface"
    state: present
  register: scan_result

- name: Calculate risk score
  ansible.builtin.debug:
    msg: "Risk score: {{ scan_result.findings | stevefulme1.cisco_ai_defense.ai_defense_risk_score }}"
```

### Deploy baseline policies with a role

```yaml
- name: Deploy AI Defense baseline
  hosts: localhost
  roles:
    - role: stevefulme1.cisco_ai_defense.baseline_policy
      vars:
        ai_defense_api_url: "https://aidefense.example.com"
        ai_defense_api_key: "{{ vault_ai_defense_api_key }}"
```

### Event-Driven Ansible (EDA)

```yaml
# rulebook.yml
- name: Respond to AI Defense threats
  hosts: all
  sources:
    - stevefulme1.cisco_ai_defense.threat_events:
        api_url: "{{ ai_defense_api_url }}"
        api_key: "{{ ai_defense_api_key }}"
        interval: 30
  rules:
    - name: Alert on critical threats
      condition: event.severity == "critical"
      action:
        run_playbook:
          name: respond_to_threat.yml
```

## Testing

```bash
# Install test dependencies
pip install ansible-core>=2.16 ansible-lint yamllint flake8 pytest pytest-cov

# Lint
yamllint -c .yamllint .
flake8 plugins/ --max-line-length=160 --ignore=E402,W503
ansible-lint --strict

# Unit tests
pytest tests/unit/ -v --tb=short --cov=plugins

# Sanity tests (must be at ansible_collections/stevefulme1/cisco_ai_defense/)
ansible-test sanity --docker default -v
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development setup, coding
standards, and pull request requirements.

## License

GNU General Public License v3.0 or later.

See [COPYING](COPYING) for the full license text.
