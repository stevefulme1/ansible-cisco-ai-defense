# Changelog

All notable changes to the `stevefulme1.cisco_ai_defense` Ansible collection
will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0] - 2026-05-19

### Added

#### New Modules (21)

Day 2 operations, supply chain, validation, discovery, and integration modules:

- `container_scan` -- Scan AI workload containers
- `discovery` -- Trigger AI workload discovery scans
- `guardrail_rule` -- Manage individual guardrail rules
- `inventory_info` -- Query discovered AI asset inventory
- `metrics_info` -- Retrieve protection metrics
- `model_provenance` -- Validate AI model provenance
- `pii_policy` -- Configure PII detection and masking policies
- `policy_assignment` -- Assign policies to endpoints, models, or applications
- `policy_export` -- Export policies as structured data
- `policy_import` -- Import policies from definitions
- `rate_limit` -- Configure rate limiting
- `shadow_ai` -- Detect unauthorized shadow AI workloads
- `splunk_integration` -- Configure Splunk telemetry export
- `supply_chain_report` -- Generate AI supply chain risk reports
- `supply_chain_report_info` -- Retrieve supply chain reports
- `topic_policy` -- Configure allowed and blocked topic policies
- `validation_categories_info` -- List available validation categories
- `validation_config` -- Configure validation parameters
- `validation_report_info` -- Retrieve validation run results
- `validation_run` -- Execute automated red-team validation
- `validation_schedule` -- Schedule recurring AI model validations

#### New Roles (4)

- `baseline_policy` -- Apply baseline guardrail policies for common AI use cases
- `monitoring` -- Configure monitoring and alerting for Cisco AI Defense
- `red_team` -- Automated red-team validation workflow
- `supply_chain` -- Supply chain scanning pipeline for AI models in CI/CD

#### New Plugins

- **Filter plugins** (4): `ai_defense_risk_score`, `ai_defense_critical_findings`,
  `ai_defense_format_compliance`, `ai_defense_pii_summary`
- **Lookup plugin**: `ai_defense_policy` -- Retrieve policy details from the API
- **EDA event source**: `threat_events` -- Poll for alert events
- **EDA event filter**: `severity_filter` -- Filter threat events by severity

### Improved

- Shared `module_utils/ai_defense.py` base class for consistent API interaction,
  error handling, and authentication across all modules
- Enhanced CI pipeline with lint, sanity (ansible-core 2.16/2.17/2.18), unit
  test (pytest with coverage), and integration test jobs
- Comprehensive `.pre-commit-config.yaml` with trailing-whitespace, yamllint,
  flake8, and ansible-lint hooks
- Full content inventory in README with quick start examples

## [1.0.1] - 2026-05-18

### Security

- Added `no_log: true` to `ai_defense_deploy_api_key` in role argument specs
- Created `argument_specs.yml` for roles with sensitive variables

## [1.0.0] - 2026-05-18

### Added

- Initial release with 14 modules covering policy, guardrail, threat detection,
  model scanning, API protection, compliance, audit log, and threat feed
  management
- 2 roles: `ai_defense_deploy`, `guardrail_config`
- EDA event source plugin: `threat_events`
