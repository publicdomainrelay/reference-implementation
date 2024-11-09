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

```bash
export LOCAL_OPERATION_CACHE_SHA="$(head -n 1000 /dev/urandom | sha384sum - | awk '{print $1}')"
export LOCAL_OPERATION_CACHE_DIR="cache/operations/${LOCAL_OPERATION_CACHE_SHA}"
export DATA_PUBLIC_KEY_JSON_PATH="${LOCAL_OPERATION_CACHE_DIR}/data.public_keys.json"
export NEXT_DATA_PUBLIC_KEY_JSON_PATH="${LOCAL_OPERATION_CACHE_DIR}/next.data.public_keys.json"
mkdir -pv "${LOCAL_OPERATION_CACHE_DIR}"
echo '[{}]' > "${DATA_PUBLIC_KEY_JSON_PATH}"
jq --arg owner "$USER" '.[0].owner = $owner' "${DATA_PUBLIC_KEY_JSON_PATH}" | tee "${NEXT_DATA_PUBLIC_KEY_JSON_PATH}"
cat "${NEXT_DATA_PUBLIC_KEY_JSON_PATH}" | tee "${DATA_PUBLIC_KEY_JSON_PATH}" | jq
jq --arg public_key "$(gpg --export --armor $(git config user.email))" '.[0].public_key = $public_key' "${DATA_PUBLIC_KEY_JSON_PATH}" | tee "${NEXT_DATA_PUBLIC_KEY_JSON_PATH}"
cat "${NEXT_DATA_PUBLIC_KEY_JSON_PATH}" | tee "${DATA_PUBLIC_KEY_JSON_PATH}" | jq
python -m mistletoe docs/adrs/governance.md --renderer mistletoe.ast_renderer.AstRenderer | jq -r --arg searchString "branch_name Maintainers" --arg excludeString "mistletoe" '.. | strings | select(contains($searchString) and (contains($excludeString) | not))' | yq --indent 2 --prettyPrint '.data.public_keys = load(strenv(DATA_PUBLIC_KEY_JSON_PATH))'
```

```yaml
name: 'branch_name Maintainers'
deny:
- name: 'Deny owner additions without sign off from current owners'
  action: 'add_owner'
applies_to:
- 'branch_name'
- 'branch_name_mod_policy_.*'
pending_changes:
- nonce: '... UUID for pending change ...'
  action: add_owner
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
- name: add_owner
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
deny:
- name: 'Deny changes to elect without representation'
  action: 'mod_elect'
- name: 'Deny changes to policy without representation'
  action: 'mod_policy'
applies_to:
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
