# Decentralized Governance

```yaml
owners:
- Bob
- Alice
actions:
- name: add_owner
deny:
- mods_to_owners
allow:
- this_branch
pending_changes:
- action: add_owner
  signers: &owners
  value: Eve
```
