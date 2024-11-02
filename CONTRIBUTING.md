# CONTRIBUTING

## Setup: Local Development

```bash
export KCP_SETUP_DIR=cache/setup/kcp
export KCP_VERSION=0.26.0
curl --create-dirs --output-dir "${KCP_SETUP_DIR}" -fLOC - "https://github.com/kcp-dev/kcp/releases/download/v${KCP_VERSION}/kcp_${KCP_VERSION}_checksums.txt"
curl --create-dirs --output-dir "${KCP_SETUP_DIR}" -fLOC - "https://github.com/kcp-dev/kcp/releases/download/v${KCP_VERSION}/kcp_${KCP_VERSION}_linux_amd64.tar.gz"
curl --create-dirs --output-dir "${KCP_SETUP_DIR}" -fLOC - "https://github.com/kcp-dev/kcp/releases/download/v${KCP_VERSION}/kubectl-create-workspace-plugin_${KCP_VERSION}_linux_amd64.tar.gz"
curl --create-dirs --output-dir "${KCP_SETUP_DIR}" -fLOC - "https://github.com/kcp-dev/kcp/releases/download/v${KCP_VERSION}/kubectl-kcp-plugin_${KCP_VERSION}_linux_amd64.tar.gz"
curl --create-dirs --output-dir "${KCP_SETUP_DIR}" -fLOC - "https://github.com/kcp-dev/kcp/releases/download/v${KCP_VERSION}/kubectl-ws-plugin_${KCP_VERSION}_linux_amd64.tar.gz"
```
