from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN
from .conversation import OpenClawConversationAgent


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    agent = OpenClawConversationAgent(hass, entry)
    entry.runtime_data = agent

    # Register as the default conversation agent.
    from homeassistant.components import conversation

    conversation.async_set_agent(hass, agent)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    # If HA supported multiple agents we'd restore prior agent; MVP just unloads.
    from homeassistant.components import conversation

    current = conversation.async_get_agent(hass)
    if current is entry.runtime_data:
        conversation.async_set_agent(hass, None)

    return True
