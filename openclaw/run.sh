#!/usr/bin/with-contenv bash
set -euo pipefail

# HA add-on options are mounted at /data/options.json
PORT=$(jq -r '.port // 18789' /data/options.json)
TOKEN=$(jq -r '.auth_token // empty' /data/options.json)
AGENT_ID=$(jq -r '.agent_id // "main"' /data/options.json)
ENABLE_UI=$(jq -r '.enable_control_ui // true' /data/options.json)

if [[ -z "${TOKEN}" || "${TOKEN}" == "CHANGE_ME" ]]; then
  echo "ERROR: You must set a strong auth_token in the add-on configuration." >&2
  exit 1
fi

export OPENCLAW_GATEWAY_TOKEN="${TOKEN}"

mkdir -p /data/openclaw
CONFIG_PATH=/data/openclaw/config.json

cat >"${CONFIG_PATH}" <<JSON
{
  "gateway": {
    "mode": "local",
    "port": ${PORT},
    "bind": "lan",
    "auth": { "mode": "token", "token": "${TOKEN}" },
    "controlUi": {
      "enabled": ${ENABLE_UI},
      "allowInsecureAuth": true,
      "basePath": "/"
    },
    "http": {
      "endpoints": {
        "chatCompletions": { "enabled": true }
      }
    }
  }
}
JSON

echo "Starting OpenClaw Gateway on :${PORT} (agent_id=${AGENT_ID})"
# Run foreground gateway. Config is auto-discovered from /data/openclaw/config.json via OPENCLAW_CONFIG,
# but we set it explicitly.
export OPENCLAW_CONFIG="${CONFIG_PATH}"

exec openclaw gateway run --port "${PORT}" --bind lan --token "${TOKEN}" --allow-unconfigured --verbose
