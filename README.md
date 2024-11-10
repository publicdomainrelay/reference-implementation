# Reference Implementation

> An implementation of the Open Architecture, an abstract compute architecture.

## Philosophy

> *source is truth, truth is source*

- The approach we aim to take is to enable the current default most widely adopted methodology first: git + CI/CD
  - First centralized: GitHub + GitHub Actions
  - Next decentralized: Forgejo + Forgejo Workflows
- We'll later move into the next phase which will be SCITT + ORAS.

We aim to leverage as many existing codebases as possible. We aim to write as
little code as possible. The goal being to enable effective use of policy to
gate AI based contributions of code and modifications to policy. Thereby scoping
the AI's range of influence.

Our policies will at first be purely technical. We'll later move into code
review based on alignment to a repositories values and strategic plans and
principles. These will likely translate into granular technical policy
definition.

## References

- [Architecture Design Records](docs/adrs/)
  - [Decentralized Governance](docs/adrs/governance.md)
- [Notes](docs/notes/)
  - [Attestations as a Backbone for Trust and Verification](docs/notes/backbone.md)
- [Living Threat Models](https://github.com/johnlwhiteman/living-threat-models)
  - [Securing Rolling Releases in Poly-Repo Environments](https://github.com/dffml/dffml/blob/main/docs/tutorials/rolling_alice/0000_architecting_alice/)
