# Git based Federation

## Status

Draft

## Context

Relay content across namespaces using decentralized governance policies.

- References
  - [publicdomainrelay/reference-implementation: Decentralized Governance](https://github.com/publicdomainrelay/blob/main/docs/adrs/governance.md)

## Requirements

- [ ] Code / implementation discovery MUST be rooted in tree
- [ ] Resolvers MUST be namespaced (ING-4)
  - [ ] namespaces MUST allow for multiple indexes and dynamically sized
        namespaces. This is for network managed orgs.
- [ ] Resolvers MUST be versioned
- [ ] Resolvers SHOULD implement the following common discovery mechanisms
      so as to enable compatibility across implementations.
  - [ ] Git
  - [ ] GitHub
    - `publicdomainrelay/index-github`

## Methodology

```python
class FederationGitCurrentUser:
    git_config_user_email: str

class FederationGitRepo:
    namespace: str
    repo: str
    shared: bool
    # If not specified we assume we federate across all NS indexes
    indexes: list[str]

class FederationGitContext:
    repos: list[FederationGitRepo]

class PolicyIndex:
    name: str
    protocol: str
    data: dict

class FederationGitPolicyDataNamespace:
    indexes: list[PolicyIndex]

class FederationGitPolicyDataNamespace:
    namespaces: dict[str, FederationGitPolicyDataNamespace

class FederationContext:
    current_user: FederationGitCurrentUser
    data: FederationGitPolicyData

def federation_git(ctx: FederationContext, active: FederationGitContext):
    if not ctx.current_user.git_config_user_email in itertools.chain(
        [owner.emails for owner in ctx.policy.data.owners],
    ):
        return

    # TODO Indirect lookup of namespace name to owner email
    current_user_namespace = ...

    for repo in active.repos:
        if (
            not repo.shared
            or current_user_namespace != repo.namespace
        ):
            continue
        git push ...
```

## Examples

```yaml
name: 'Maintainers of main branch'
requires:
  action: verify_mod_owner
applies_to:
  - main
mod_branch:
  - _mod_policy_

data:
  federation:
    - protocol: 'publicdomainrelay/federation-git@v1'
      data:
        repos:
          - 'publicdomainrelay/example-policy-maintainers'
          - 'john/my-repo'
  namespaces:
    publicdomainrelay:
      shared: true
      indexes:
        - protocol: 'publicdomainrelay/index-github@v1'
          data:
            owner: 'publicdomainrelay'
    john:
      indexes:
        - protocol: 'publicdomainrelay/index-atproto-v2@v1'
          data:
            handle: 'john.atproto.chadig.com'
            uri: 'at://did:plc:w4524qnuvc7o6ojwjwtnvh75/app.bsky.feed.post/3lc2smchqf22i'
            cid: 'bafyreiebgxcpue5xjy5hmpfw7mnwdc2ss7nsia2ixmdm4zd7twu6bgqbky'
```
