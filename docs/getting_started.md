# Getting Started with stevefulme1.cisco_ai_defense

This guide walks you through installing the collection, authenticating with
the Cisco AI Defense API, and running common Day 1 and Day 2 operations.

## Installation

```bash
ansible-galaxy collection install stevefulme1.cisco_ai_defense
pip install requests
```

## Requirements

| Dependency | Version |
|---|---|
| Python | >= 3.9 |
| ansible-core | >= 2.16.0 |
| `requests` | latest |

## Authentication

All modules require `api_url` and `api_key` parameters. Store credentials
securely with Ansible Vault:

```bash
ansible-vault encrypt_string 'your-api-key-here' --name 'vault_ai_defense_api_key'
```

Create a variables file:

```yaml
# group_vars/all/vars.yml
ai_defense_api_url: "https://aidefense.example.com"
ai_defense_api_key: "{{ vault_ai_defense_api_key }}"
```

## Collection Contents

| Type | Count | Description |
|---|---|---|
| Modules | 35 | Policy, guardrail, threat, model, API, compliance, validation |
| Roles | 6 | Deploy, baseline, guardrail config, monitoring, red team, supply chain |
| Filter plugins | 4 | Risk scoring, critical findings, compliance formatting, PII summary |
| Lookup plugin | 1 | Query policy details from the API |
| EDA plugins | 2 | Threat event source and severity filter |

## Day 1: Initial Deployment

### Deploy the platform with default settings

```yaml
---
- name: Deploy Cisco AI Defense
  hosts: localhost
  connection: local
  gather_facts: false
  roles:
    - role: stevefulme1.cisco_ai_defense.ai_defense_deploy
      vars:
        ai_defense_api_url: "{{ ai_defense_api_url }}"
        ai_defense_api_key: "{{ ai_defense_api_key }}"
```

### Apply baseline policies

```yaml
---
- name: Apply baseline guardrail policies
  hosts: localhost
  connection: local
  gather_facts: false
  roles:
    - role: stevefulme1.cisco_ai_defense.baseline_policy
      vars:
        ai_defense_api_url: "{{ ai_defense_api_url }}"
        ai_defense_api_key: "{{ ai_defense_api_key }}"
```

### Configure guardrails

```yaml
---
- name: Configure AI guardrails
  hosts: localhost
  connection: local
  gather_facts: false
  tasks:
    - name: Create prompt injection guardrail
      stevefulme1.cisco_ai_defense.guardrail:
        api_url: "{{ ai_defense_api_url }}"
        api_key: "{{ ai_defense_api_key }}"
        name: "block-prompt-injection"
        description: "Block prompt injection attempts"
        guardrail_type: "input"
        action: "block"
        state: present

    - name: Create PII detection policy
      stevefulme1.cisco_ai_defense.pii_policy:
        api_url: "{{ ai_defense_api_url }}"
        api_key: "{{ ai_defense_api_key }}"
        name: "mask-pii-output"
        detection_mode: "mask"
        pii_types:
          - email
          - phone
          - ssn
        state: present

    - name: Set topic restrictions
      stevefulme1.cisco_ai_defense.topic_policy:
        api_url: "{{ ai_defense_api_url }}"
        api_key: "{{ ai_defense_api_key }}"
        name: "block-harmful-topics"
        blocked_topics:
          - violence
          - illegal_activities
        state: present
```

## Day 2: Ongoing Operations

### Discover shadow AI workloads

```yaml
---
- name: Shadow AI discovery
  hosts: localhost
  connection: local
  gather_facts: false
  tasks:
    - name: Trigger discovery scan
      stevefulme1.cisco_ai_defense.discovery:
        api_url: "{{ ai_defense_api_url }}"
        api_key: "{{ ai_defense_api_key }}"
        scan_type: "full"
      register: scan

    - name: Check for shadow AI
      stevefulme1.cisco_ai_defense.shadow_ai:
        api_url: "{{ ai_defense_api_url }}"
        api_key: "{{ ai_defense_api_key }}"
      register: shadow

    - name: Report unauthorized workloads
      ansible.builtin.debug:
        msg: "Found {{ shadow.workloads | length }} unauthorized AI workloads"
      when: shadow.workloads | length > 0
```

### Model supply chain validation

```yaml
---
- name: Supply chain scan pipeline
  hosts: localhost
  connection: local
  gather_facts: false
  tasks:
    - name: Scan model for supply chain risks
      stevefulme1.cisco_ai_defense.supply_chain_report:
        api_url: "{{ ai_defense_api_url }}"
        api_key: "{{ ai_defense_api_key }}"
        model_name: "llama-3-8b"
        model_source: "huggingface"
        state: present
      register: scan

    - name: Calculate risk score
      ansible.builtin.set_fact:
        risk_score: "{{ scan.findings | stevefulme1.cisco_ai_defense.ai_defense_risk_score }}"

    - name: Fail on high risk
      ansible.builtin.fail:
        msg: "Model risk score {{ risk_score }} exceeds threshold"
      when: risk_score | float > 7.0
```

### Red-team validation

```yaml
---
- name: Run automated red-team validation
  hosts: localhost
  connection: local
  gather_facts: false
  roles:
    - role: stevefulme1.cisco_ai_defense.red_team
      vars:
        ai_defense_api_url: "{{ ai_defense_api_url }}"
        ai_defense_api_key: "{{ ai_defense_api_key }}"
```

Or use the modules directly:

```yaml
    - name: Execute red-team validation
      stevefulme1.cisco_ai_defense.validation_run:
        api_url: "{{ ai_defense_api_url }}"
        api_key: "{{ ai_defense_api_key }}"
        target_model: "my-chatbot"
        categories:
          - prompt_injection
          - jailbreak
          - data_exfiltration
      register: validation

    - name: Get results
      stevefulme1.cisco_ai_defense.validation_report_info:
        api_url: "{{ ai_defense_api_url }}"
        api_key: "{{ ai_defense_api_key }}"
        run_id: "{{ validation.run_id }}"
      register: report
```

### Compliance reporting

```yaml
---
- name: Generate compliance report
  hosts: localhost
  connection: local
  gather_facts: false
  tasks:
    - name: Generate EU AI Act compliance report
      stevefulme1.cisco_ai_defense.compliance_report:
        api_url: "{{ ai_defense_api_url }}"
        api_key: "{{ ai_defense_api_key }}"
        framework: "eu_ai_act"
        state: present
      register: report

    - name: Format report
      ansible.builtin.debug:
        msg: "{{ report.report | stevefulme1.cisco_ai_defense.ai_defense_format_compliance('eu_ai_act') }}"
```

### Event-Driven Ansible (EDA)

```yaml
# rulebook.yml -- respond to threats in real time
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

    - name: Log high severity events
      condition: event.severity == "high"
      action:
        run_playbook:
          name: log_threat.yml
```

### Using the lookup plugin

```yaml
- name: Fetch policy by name
  ansible.builtin.debug:
    msg: >-
      {{ lookup('stevefulme1.cisco_ai_defense.ai_defense_policy',
                'block-prompt-injection',
                api_url=ai_defense_api_url,
                api_key=ai_defense_api_key) }}
```

## Next Steps

- Browse module documentation: `ansible-doc stevefulme1.cisco_ai_defense.<module_name>`
- Check the [README](../README.md) for the full module and role list
- Review [CONTRIBUTING.md](../CONTRIBUTING.md) to contribute
