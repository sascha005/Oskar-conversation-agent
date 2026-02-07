from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import Any

import aiohttp

from homeassistant.components.conversation import (
    AbstractConversationAgent,
    ConversationInput,
    ConversationResult,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import (
    CONF_AGENT_ID,
    CONF_HOST,
    CONF_MODE,
    CONF_SECRET,
    CONF_TOKEN,
    DEFAULT_AGENT_ID,
    DEFAULT_MODE,
)


@dataclass
class _Cfg:
    host: str
    token: str | None
    agent_id: str
    mode: str
    secret: str | None


class OpenClawConversationAgent(AbstractConversationAgent):
    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        self.hass = hass
        self.entry = entry

    @property
    def _cfg(self) -> _Cfg:
        data = self.entry.data
        return _Cfg(
            host=data[CONF_HOST].rstrip("/"),
            token=data.get(CONF_TOKEN),
            agent_id=data.get(CONF_AGENT_ID, DEFAULT_AGENT_ID),
            mode=data.get(CONF_MODE, DEFAULT_MODE),
            secret=data.get(CONF_SECRET),
        )

    @property
    def supported_languages(self) -> list[str] | None:
        # Let HA decide; OpenClaw can handle multilingual.
        return None

    async def async_process(self, user_input: ConversationInput) -> ConversationResult:
        cfg = self._cfg
        session = async_get_clientsession(self.hass)

        # Stable per-HA-user sessions inside OpenClaw:
        # OpenClaw derives session key from OpenAI "user".
        user_id = user_input.context.user_id or "anonymous"
        openai_user = f"ha:{user_id}"

        if cfg.mode == "assist_proxy":
            payload = {"text": user_input.text}
            headers = {
                "Content-Type": "application/json",
                "X-OpenClaw-Secret": cfg.secret or "",
            }
            url = f"{cfg.host}/assist"
        else:
            payload = {
                "model": f"openclaw:{cfg.agent_id}",
                "user": openai_user,
                "messages": [
                    {"role": "user", "content": user_input.text},
                ],
            }
            headers = {
                "Authorization": f"Bearer {cfg.token}",
                "Content-Type": "application/json",
                "x-openclaw-agent-id": cfg.agent_id,
            }
            url = f"{cfg.host}/v1/chat/completions"

        try:
            async with session.post(url, json=payload, headers=headers, timeout=aiohttp.ClientTimeout(total=60)) as resp:
                resp.raise_for_status()
                data = await resp.json()
        except (aiohttp.ClientError, asyncio.TimeoutError) as err:
            return ConversationResult(response=err.__class__.__name__, conversation_id=None)

        if cfg.mode == "assist_proxy":
            text = (data.get("text") or "").strip()
        else:
            # OpenAI-style response: choices[0].message.content
            text = (
                data.get("choices", [{}])[0]
                .get("message", {})
                .get("content", "")
                .strip()
            )

        return ConversationResult(response=text, conversation_id=None)
