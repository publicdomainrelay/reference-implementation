# CONTRIBUTING

## Setup: Local Development

[![setup-kcp-and-cue](https://asciinema.org/a/687943.svg)](https://asciinema.org/a/687943)

```bash
export KCP_SETUP_DIR=cache/setup/kcp
export KCP_INSTALL_DIR=cache/install/kcp
export KCP_VERSION=0.26.0
curl --create-dirs --output-dir "${KCP_SETUP_DIR}" -fLOC - "https://github.com/kcp-dev/kcp/releases/download/v${KCP_VERSION}/kcp_${KCP_VERSION}_checksums.txt"
curl --create-dirs --output-dir "${KCP_SETUP_DIR}" -fLOC - "https://github.com/kcp-dev/kcp/releases/download/v${KCP_VERSION}/kcp_${KCP_VERSION}_linux_amd64.tar.gz"
curl --create-dirs --output-dir "${KCP_SETUP_DIR}" -fLOC - "https://github.com/kcp-dev/kcp/releases/download/v${KCP_VERSION}/kubectl-create-workspace-plugin_${KCP_VERSION}_linux_amd64.tar.gz"
curl --create-dirs --output-dir "${KCP_SETUP_DIR}" -fLOC - "https://github.com/kcp-dev/kcp/releases/download/v${KCP_VERSION}/kubectl-kcp-plugin_${KCP_VERSION}_linux_amd64.tar.gz"
curl --create-dirs --output-dir "${KCP_SETUP_DIR}" -fLOC - "https://github.com/kcp-dev/kcp/releases/download/v${KCP_VERSION}/kubectl-ws-plugin_${KCP_VERSION}_linux_amd64.tar.gz"
mkdir -pv "${KCP_INSTALL_DIR}"
tar -xvz -C "${KCP_INSTALL_DIR}" -f "${KCP_SETUP_DIR}/kcp_${KCP_VERSION}_linux_amd64.tar.gz"
tar -xvz -C "${KCP_INSTALL_DIR}" -f "${KCP_SETUP_DIR}/kubectl-create-workspace-plugin_${KCP_VERSION}_linux_amd64.tar.gz"
tar -xvz -C "${KCP_INSTALL_DIR}" -f "${KCP_SETUP_DIR}/kubectl-kcp-plugin_${KCP_VERSION}_linux_amd64.tar.gz"
tar -xvz -C "${KCP_INSTALL_DIR}" -f "${KCP_SETUP_DIR}/kubectl-ws-plugin_${KCP_VERSION}_linux_amd64.tar.gz"
export PATH="${PWD}/${KCP_INSTALL_DIR}/bin:${PATH}"

export CUE_SETUP_DIR=cache/setup/cue
export CUE_INSTALL_DIR=cache/install/cue
export CUE_VERSION=0.11.0-alpha.5
# https://cuelang.org/docs/howto/embed-files-in-cue-evaluation/
# export CUE_EXPERIMENT=embed=true
# export CUE_EXPERIMENT=modules=true
export CUE_EXPERIMENT=evalv3=1
curl --create-dirs --output-dir "${CUE_SETUP_DIR}" -fLOC - "https://github.com/cue-lang/cue/releases/download/v${CUE_VERSION}/checksums.txt"
curl --create-dirs --output-dir "${CUE_SETUP_DIR}" -fLOC - "https://github.com/cue-lang/cue/releases/download/v${CUE_VERSION}/cue_v${CUE_VERSION}_linux_amd64.tar.gz"
mkdir -pv "${CUE_INSTALL_DIR}"
tar -xvz -C "${CUE_INSTALL_DIR}" -f "${CUE_SETUP_DIR}/cue_v${CUE_VERSION}_linux_amd64.tar.gz"
export PATH="${PWD}/${CUE_INSTALL_DIR}:${PATH}"
```

## Philosophy

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
