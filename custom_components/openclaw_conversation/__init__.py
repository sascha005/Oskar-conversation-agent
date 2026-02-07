from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN
from .conversation import OpenClawConversationAgent


def _set_agent(hass: HomeAssistant, entry: ConfigEntry, agent) -> None:
    from homeassistant.components import conversation

    # HA 2025+ uses async_set_agent(hass, entry, agent)
    try:
        if conversation.async_set_agent.__code__.co_argcount >= 3:
            conversation.async_set_agent(hass, entry, agent)
        else:
            conversation.async_set_agent(hass, agent)
    except TypeError:
        conversation.async_set_agent(hass, entry, agent)


def _get_agent(hass: HomeAssistant, entry: ConfigEntry):
    from homeassistant.components import conversation

    try:
        if conversation.async_get_agent.__code__.co_argcount >= 2:
            return conversation.async_get_agent(hass, entry)
        return conversation.async_get_agent(hass)
    except TypeError:
        return conversation.async_get_agent(hass, entry)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    agent = OpenClawConversationAgent(hass, entry)
    entry.runtime_data = agent

    _set_agent(hass, entry, agent)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    # If HA supported multiple agents we'd restore prior agent; MVP just unloads.
    current = _get_agent(hass, entry)
    if current is entry.runtime_data:
        _set_agent(hass, entry, None)

    return True
