# Home Assistant OpenClaw (local)

Private repo intended to run OpenClaw *locally* inside Home Assistant OS and use it as the default Assist conversation agent.

## What you get (MVP)

- Home Assistant **Add-on** `openclaw` that runs `openclaw gateway run` locally.
- Gateway exposes an OpenAI-compatible endpoint: `POST /v1/chat/completions`.
- Home Assistant **Custom Integration** `openclaw_conversation` that registers itself as the **default** conversation agent and forwards Assist text to OpenClaw.
- Optional **Assist Proxy** mode for a simple LAN HTTP proxy (`/assist`) that forwards to OpenClaw.
- Session behavior: **per HA user** using the OpenAI `user` field (`ha:<user_id>`), so OpenClaw keeps a stable conversation per user.

## Install

### 1) Add-on repository (Supervisor)

1. Home Assistant → **Settings → Add-ons → Add-on Store → ⋮ → Repositories**
2. Add this repo URL (after you create it on GitHub):
   - `https://github.com/sascha005/homeassistant-openclaw`
3. Install add-on **OpenClaw**.
4. Configure add-on:
   - `auth_token`: generate a strong token (32+ random chars)
   - keep `port: 18789`
5. Start the add-on.

### 2) Custom Integration

Copy `custom_components/openclaw_conversation` into your HA config directory:

- `<config>/custom_components/openclaw_conversation`

Then restart Home Assistant.

Add Integration:

- Settings → Devices & services → Add integration → **OpenClaw Conversation Agent**
- Host: `http://a0d7b954-openclaw:18789` (default add-on hostname)
- Token: same `auth_token` you set in the add-on
- Agent id: `main`

### 3) Make it the default Assist agent

This integration sets itself as the global conversation agent on load.

## Assist Proxy (LAN)

If you run a simple LAN proxy that exposes `POST /assist` and returns `{ "text": "..." }`,
you can use **Mode: assist_proxy** in the integration setup.

Required fields in the UI:
- Host: `http://<openclaw-host>:8088`
- Mode: `assist_proxy`
- Secret: shared secret used in the `X-OpenClaw-Secret` header
- Agent id: `main`

## Notes / Security

- This is **local-only** by design.
- Do NOT expose port 18789 to the internet.

## Next ideas

- Home Assistant Ingress sidebar for OpenClaw Control UI (already enabled in add-on config).
- Proactive prompts + confirmations (HA automations + OpenClaw suggestion toolchain).
