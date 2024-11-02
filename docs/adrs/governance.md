# Decentralized Governance

## Status

Draft

## Context

Enable two way relay from decentralized to and from centralized.

- References
  - [publicdomainrelay/patterns: Towards Transparent Representation](https://github.com/publicdomainrelay/patterns)

## Requirements

- [ ] POC use auto branch governance to relay changes from non-GitHub through entity GitHub account via fork and pull-request to entity account forks of org repos
  - This is a simple "roll up"

## Examples

### Maintainers

```yaml
name: 'branch_name Maintainers'
branch: 'branch_name'
deny:
- name: 'Deny owners modifications without sign off from current owners'
  action: 'mod_owners'
allow:
- 'branch_name'
- 'branch_name_mod_policy_.*"
pending_changes:
- action: mod_owners
  inputs:
    new_key_public: '...'
    new_key_revocation: '...'
    new_owner: 'Eve'
    signer_keys: '$this.data.public_keys'
data:
  public_keys:
  - owner: 'Bob'
    keys:
    - '...'
    revocation:
    - '...'
  - owner: 'Alice'
    keys:
    - '...'
    revocation:
    - '...'
actions:
- name: mod_owners
  runs-on: slsa-l4-reproducable-wasm
  steps:
  # TODO Figure out where reproducable-wasm source is, more policy to okay?
  # - uses: actions/checkout@v4
```

Expanded form of action `add_owner`

```yaml
- name: add_owner
  request:
    context:
      config:
        env:
          KEY: "value"
      secrets:
        MY_SECRET: "test-secret"
    workflow: |
      on:
        push:
          branches:
          - '$this.branch'

      jobs:
        single:
          steps: '... as above ...'
```

### Elect

```yaml
name: 'branch_name Elect'
branch: 'branch_name'
deny:
- name: 'Deny changes to elect without representation'
  action: 'mod_elect'
- name: 'Deny changes to policy without representation'
  action: 'mod_policy'
allow:
- 'branch_name'
- 'branch_name_mod_elect_.*"
- 'branch_name_mod_policy_.*"
pending_changes:
- action: elect_mod
  inputs:
    new_representative: 'Alice'
    key_public: '...'
    key_revocation: '...'
    signer_servers: '$this.data.public_key_servers'
data:
  representative:
    - name: 'Alice'
      keys:
      - public: '...'
        revocation: '...'
  public_key_servers:
  - '...'
actions:
- name: elect
  runs-on: slsa-l4-attested-risc-v
  steps:
  - uses: zkrollup
    with:
      public_key_servers: ${{ inputs.signer_servers }}
```
