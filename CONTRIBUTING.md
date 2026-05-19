# Contributing to stevefulme1.cisco_ai_defense

Thank you for your interest in contributing to the Cisco AI Defense Ansible
collection. This document explains the process for contributing code,
reporting issues, and running tests.

## Getting Started

### Prerequisites

| Requirement | Version |
|---|---|
| Python | >= 3.9 |
| ansible-core | >= 2.16 |
| requests | latest |
| pytest | latest |

### Environment Setup

1. Fork the repository and clone your fork:

   ```bash
   mkdir -p ansible_collections/stevefulme1
   git clone https://github.com/<your-fork>/ansible-cisco-ai-defense.git \
     ansible_collections/stevefulme1/cisco_ai_defense
   cd ansible_collections/stevefulme1/cisco_ai_defense
   ```

2. Create a Python virtual environment:

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install ansible-core>=2.16 requests pytest pytest-cov yamllint flake8 ansible-lint
   ```

3. Install pre-commit hooks:

   ```bash
   pip install pre-commit
   pre-commit install
   ```

## Running Tests

### Linting

```bash
yamllint -c .yamllint .
flake8 plugins/ --max-line-length=160 --ignore=E402,W503
ansible-lint --strict
```

### Sanity Tests

The collection must be checked out at the path
`ansible_collections/stevefulme1/cisco_ai_defense/` for sanity tests:

```bash
ansible-test sanity --docker default -v
```

### Unit Tests

```bash
PYTHONPATH=$(pwd)/../../.. pytest tests/unit/ -v --tb=short --cov=plugins
```

## Module Development Guidelines

### Shared Module Utilities

All modules must use the shared base class in `plugins/module_utils/ai_defense.py`.
This provides:

- Consistent API authentication (`api_url`, `api_key`, `validate_certs`)
- Standard error handling and HTTP request methods
- Common argument spec via `AiDefenseBase.common_argument_spec()`

Example usage in a new module:

```python
from ansible_collections.stevefulme1.cisco_ai_defense.plugins.module_utils.ai_defense import (
    AiDefenseBase,
)

def main():
    module = AnsibleModule(
        argument_spec={
            **AiDefenseBase.common_argument_spec(),
            "name": {"type": "str", "required": True},
            "state": {"type": "str", "default": "present", "choices": ["present", "absent"]},
        },
        supports_check_mode=True,
    )
    client = AiDefenseBase(module)
    # ... module logic using client.get(), client.post(), etc.
```

### Module Structure

All modules must follow this pattern:

```python
# -*- coding: utf-8 -*-
# Copyright: (c) 2025, Steve Fulmer <sfulmer@redhat.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Ansible module for managing <Resource> in Cisco AI Defense."""

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r"""..."""
EXAMPLES = r"""..."""
RETURN = r"""..."""

# imports after DOCUMENTATION block
```

### Key Rules

- No shebangs (`#!/usr/bin/python`) in module files
- Imports must come after the `DOCUMENTATION`/`EXAMPLES`/`RETURN` blocks
- Use `no_log=True` in `argument_spec` for sensitive parameters (API keys,
  tokens), but **not** in the `DOCUMENTATION` block
- All modules must support `check_mode`
- All modules must be idempotent
- Use `extends_documentation_fragment: stevefulme1.cisco_ai_defense.ai_defense`
  when a doc fragment is available
- List-type parameters must include `elements:` in the DOCUMENTATION block

## Pull Request Process

1. **Fork** the repository and create a feature branch from `main`
2. **Write your changes** following the module patterns in `plugins/modules/`
3. **Use `module_utils/ai_defense.py`** for all API interaction
4. **Add tests** for new modules in `tests/unit/`
5. **Run all checks** (lint, sanity, unit tests) before submitting
6. **Submit a pull request** with a clear description of the changes
7. **Sign-off**: All commits must include a `Signed-off-by` line
   (use `git commit -s`)

### PR Requirements

- [ ] All sanity tests pass (`ansible-test sanity`)
- [ ] All unit tests pass (`pytest tests/unit/`)
- [ ] flake8 passes with `--max-line-length=160 --ignore=E402,W503`
- [ ] yamllint passes
- [ ] ansible-lint passes with `--strict`
- [ ] New modules include `DOCUMENTATION`, `EXAMPLES`, and `RETURN` blocks
- [ ] New modules use `plugins/module_utils/ai_defense.py` base class
- [ ] New modules set `version_added: "X.Y.0"` to the next release version
- [ ] CHANGELOG.md updated with changes

## Reporting Issues

Open a GitHub issue at
<https://github.com/stevefulme1/ansible-cisco-ai-defense/issues> with:

- A clear title and description
- Steps to reproduce (for bugs)
- Expected vs actual behavior
- Ansible version, Python version, and `requests` version
- Relevant playbook snippets or error output

## Code of Conduct

This project follows the
[Contributor Covenant Code of Conduct](https://www.contributor-covenant.org/version/2/1/code_of_conduct/).
See [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) for details.

## License

By contributing, you agree that your contributions will be licensed under the
GNU General Public License v3.0 or later. See [COPYING](COPYING).
