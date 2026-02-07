ARG BUILD_FROM=ghcr.io/hassio-addons/base:15.0.7
FROM ${BUILD_FROM}

# Home Assistant add-on base is Alpine.
# Install nodejs + npm, then install OpenClaw.
# Toolchain deps: some npm packages use native addons.
RUN apk add --no-cache \
  nodejs npm bash curl jq git \
  python3 make g++ libc6-compat cmake

# Avoid installing heavy peer deps (node-llama-cpp) inside HA OS add-on.
# We don't need local llama.cpp; we use remote models via OpenAI-compatible providers.
RUN npm install -g --omit=peer openclaw

COPY run.sh /run.sh
RUN chmod +x /run.sh

CMD [ "/run.sh" ]
