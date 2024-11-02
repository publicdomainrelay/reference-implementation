# Decentralized Governance

## Status

Draft

## Context

Enable two way relay from decentralized to and from centralized.

- References
  - [SLSA: BuildEnv L3: Hardware-attested build environment](https://github.com/slsa-framework/slsa/blob/c9ea020c963df7941a29fdd21ea6303406ae7b34/docs/spec/draft/attested-build-env-levels.md)
  - [slsa-framework/slsa#977: Workstream: SLSA Build L4](https://github.com/slsa-framework/slsa/issues/977)
    - [slsa-framework/slsa#873: Semantic equivalency, reproducible builds, and a new "verifiable build" track](https://github.com/slsa-framework/slsa/issues/873)
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
- 'branch_name_mod_policy_.*'
pending_changes:
- nonce: '... UUID for pending change ...'
  action: mod_owners
  inputs:
    new_key_public: '...'
    new_key_revocation: '...'
    new_owner: 'Eve'
    signer_keys: '$this.data.public_keys'
data:
  pending_changes:
  # TODO Document process and how Alice signs next then they remove once Eve is
  # added. Then document secret sharing and further abstract privilege levels in
  # further ADRs, eventually get to dynamic based on more policy
  - nonce: '... UUID for pending change ...'
    cnonce: '... UUID ...'
    owner: 'Bob'
  secrets:
  - name: 'Apple'
    expected:
      alg: 'sha384'
      digest: '...'
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
  runs-on: slsa-l4
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
- 'branch_name_mod_elect_.*'
- 'branch_name_mod_policy_.*'
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
- name: mod_elect
  runs-on: slsa-l3
  steps:
  - uses: zkrollup
    with:
      public_key_servers: ${{ inputs.signer_servers }}
- name: mod_policy
  uses: '.github/workflows/mod_policy.yml'
```
