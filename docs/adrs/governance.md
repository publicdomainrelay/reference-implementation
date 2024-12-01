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
  - [Git Tools - Signing Your Work](https://git-scm.com/book/en/v2/Git-Tools-Signing-Your-Work)
  - [Alice Engineering Comms: 2023-10-25 Engineering Logs](https://github.com/dffml/dffml/blob/main/docs/discussions/alice_engineering_comms/0431/reply_0000.md)

## Requirements

- [ ] Ensure everything is kept in tree, keyservers MUST NOT be required
- [ ] POC use auto branch governance to relay changes from non-GitHub through entity GitHub account via fork and pull-request to entity account forks of org repos
  - This is a simple "roll up"

## Examples

### TODO

- Revocations for keys within `data`
- Policy which applies to all policies? Flows to check all other policies
- Document process and how Alice signs next then they remove once Eve is
  added.
  - Then document secret sharing and further abstract privilege levels in
    further ADRs
  - Eventually get to dynamic based on more policy
- Figure out where `runs-on: reproducable-wasm` source is, more policy to okay?
  - For instance, running some `uses: actions/checkout@v4` via IPVM
- Remove unneeded sections after initial generation

### Maintainers

- Apply policy to branches in `applies_to`
- Create branch per `mod_branch`
- Leverage `actions` as guidance for how to modify policy
- Changes to policy file require successful execution of all `mod_requires`

### Generation of Maintainers Upstream Policy

Shorthand

```bash
python -m mistletoe docs/adrs/governance.md --renderer mistletoe.ast_renderer.AstRenderer | jq -r --arg searchString "INIT_DATA_OWNERS_JSON_PATH" --arg excludeString "bash -xe" '.. | strings | select(contains($searchString) and (contains($excludeString) | not))' | bash -xe
```

Long form

```bash
export BRANCH_NAME="main"
export POLICY_YAML_PATH=".tools/open-architecture/governance/branches/${BRANCH_NAME}/policies/upstream.yml"
export LOCAL_OPERATION_CACHE_SHA="$(head -n 1000 /dev/urandom | sha384sum - | awk '{print $1}')"
export LOCAL_OPERATION_CACHE_DIR="cache/operations/${LOCAL_OPERATION_CACHE_SHA}"
export INIT_DATA_OWNERS_JSON_PATH="${LOCAL_OPERATION_CACHE_DIR}/data.owners.json"
export NEXT_DATA_OWNERS_JSON_PATH="${LOCAL_OPERATION_CACHE_DIR}/next.data.owners.json"
mkdir -pv "${LOCAL_OPERATION_CACHE_DIR}"
echo '[{}]' > "${INIT_DATA_OWNERS_JSON_PATH}"
jq --arg actor "$(git config user.actor)" '.[0].actors = [$actor]' "${INIT_DATA_OWNERS_JSON_PATH}" | tee "${NEXT_DATA_OWNERS_JSON_PATH}"
cat "${NEXT_DATA_OWNERS_JSON_PATH}" | tee "${INIT_DATA_OWNERS_JSON_PATH}" | jq
jq --arg email "$(git config user.email)" '.[0].emails = [$email]' "${INIT_DATA_OWNERS_JSON_PATH}" | tee "${NEXT_DATA_OWNERS_JSON_PATH}"
cat "${NEXT_DATA_OWNERS_JSON_PATH}" | tee "${INIT_DATA_OWNERS_JSON_PATH}" | jq
jq --arg public_key "$(gpg --export --armor $(git config user.signingkey))" '.[0].keys = [$public_key]' "${INIT_DATA_OWNERS_JSON_PATH}" | tee "${NEXT_DATA_OWNERS_JSON_PATH}"
cat "${NEXT_DATA_OWNERS_JSON_PATH}" | tee "${INIT_DATA_OWNERS_JSON_PATH}" | jq
mkdir -pv ".tools/open-architecture/governance/branches/${BRANCH_NAME}/policies"
python -m mistletoe docs/adrs/governance.md --renderer mistletoe.ast_renderer.AstRenderer | jq -r --arg searchString "Maintainers of branch_name branch" --arg excludeString "mistletoe" '.. | strings | select(contains($searchString) and (contains($excludeString) | not))' | yq --indent 2 --prettyPrint '.data.owners = load(strenv(INIT_DATA_OWNERS_JSON_PATH))' | tee "${POLICY_YAML_PATH}"
```

### Verification of Modifications

Ensure all existing owners sign off on all changes to policy

```bash
export BRANCH_NAME="main"
export LOCAL_OPERATION_CACHE_SHA="$(head -n 1000 /dev/urandom | sha384sum - | awk '{print $1}')"
export LOCAL_OPERATION_CACHE_DIR="cache/operations/${LOCAL_OPERATION_CACHE_SHA}"
cat .tools/open-architecture/governance/branches/${BRANCH_NAME}/policies/upstream.yml | yq '.data.owners[] | .keys[]' | gpg --import --homedir "${LOCAL_OPERATION_CACHE_DIR}"
# TODO Get patches (attacker controlled, attacker / potential contributor receives sign-offs via their federation pulling in new sign-off commits on their proposed branch from maintainers, this can be done via keys within hosted VCS or on device)
# cat patches | git am
# TODO Verify commits against owner keys in upstream
```

### Addition of Maintainer

Shorthand add PGP public

```bash
python -m mistletoe docs/adrs/governance.md --renderer mistletoe.ast_renderer.AstRenderer | jq -r --arg searchString "ADD_PGP_DATA_OWNERS_JSON_PATH" --arg excludeString "bash -xe" '.. | strings | select(contains($searchString) and (contains($excludeString) | not))' | bash -xe
```

Long form add PGP public

```bash
export BRANCH_NAME="main"
export POLICY_YAML_PATH=".tools/open-architecture/governance/branches/${BRANCH_NAME}/upstream.yml"
export LOCAL_OPERATION_CACHE_SHA="$(head -n 1000 /dev/urandom | sha384sum - | awk '{print $1}')"
export LOCAL_OPERATION_CACHE_DIR="cache/operations/${LOCAL_OPERATION_CACHE_SHA}"
export ADD_PGP_DATA_OWNERS_JSON_PATH="${LOCAL_OPERATION_CACHE_DIR}/data.owners.json"
export NEXT_DATA_OWNERS_JSON_PATH="${LOCAL_OPERATION_CACHE_DIR}/next.data.owners.json"
mkdir -pv "${LOCAL_OPERATION_CACHE_DIR}"
echo '[{}]' > "${ADD_PGP_DATA_OWNERS_JSON_PATH}"
jq --arg actor "$(git config user.actor)" '.[0].actors = [$actor]' "${ADD_PGP_DATA_OWNERS_JSON_PATH}" | tee "${NEXT_DATA_OWNERS_JSON_PATH}"
cat "${NEXT_DATA_OWNERS_JSON_PATH}" | tee "${ADD_PGP_DATA_OWNERS_JSON_PATH}" | jq
jq --arg email "$(git config user.email)" '.[0].emails = [$email]' "${ADD_PGP_DATA_OWNERS_JSON_PATH}" | tee "${NEXT_DATA_OWNERS_JSON_PATH}"
cat "${NEXT_DATA_OWNERS_JSON_PATH}" | tee "${ADD_PGP_DATA_OWNERS_JSON_PATH}" | jq
jq --arg public_key "$(gpg --export --armor $(git config user.signingkey))" '.[0].keys = [$public_key]' "${ADD_PGP_DATA_OWNERS_JSON_PATH}" | tee "${NEXT_DATA_OWNERS_JSON_PATH}"
cat "${NEXT_DATA_OWNERS_JSON_PATH}" | tee "${ADD_PGP_DATA_OWNERS_JSON_PATH}" | jq
python -m mistletoe docs/adrs/governance.md --renderer mistletoe.ast_renderer.AstRenderer | jq -r --arg searchString "Maintainers of branch_name branch" --arg excludeString "mistletoe" '.. | strings | select(contains($searchString) and (contains($excludeString) | not))' | yq -i --indent 2 --prettyPrint '.data.owners |= . + load(strenv(ADD_PGP_DATA_OWNERS_JSON_PATH))' "${POLICY_YAML_PATH}"
# TODO nonce, cnonce? branches, maintainer commits
```

### Template

```yaml
name: 'Maintainers of branch_name branch'
applies_to:
- 'branch_name'
mod_branch:
- '_mod_policy_'
mod_requires:
- 'verify_mod_owner'
data:
  pending_changes:
  - nonce: '... UUID for pending change ...'
    action: add_owner
    signers:
    - cnonce: '... UUID ...'
    inputs:
      actor: 'Eve'
      email: ''
      public_key: '...'
  owners:
  - actors:
    - '@bob@scitt.bob.chadig.com'
    emails:
    - 'bob@scitt.bob.chadig.com'
    public_keys:
    - '...'
  - actors:
    - '@alice@scitt.alice.chadig.com'
    emails:
    - 'alice@scitt.alice.chadig.com'
    public_keys:
    - '...'
  secrets:
  - name: 'Apple'
    expected:
      alg: 'sha384'
      digest: '...'
actions:
- name: verify_mod_owner
  description: 'Deny owner additions without sign off from current owners'
  steps:
  - uses: 'publicdomainrelay/verify-mod-owner@main'
- name: add_owner
  description: 'Add a new owner'
  runs-on: physically-secured-owner-device
  steps:
  - uses: 'publicdomainrelay/add-owner@main'
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
