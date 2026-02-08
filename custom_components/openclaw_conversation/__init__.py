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


def _register_agent(hass: HomeAssistant, entry: ConfigEntry, agent) -> None:
    from homeassistant.components import conversation
    import inspect

    if not hasattr(conversation, "async_register_agent"):
        return

    fn = conversation.async_register_agent
    params = inspect.signature(fn).parameters
    kwargs = {}

    if "hass" in params:
        kwargs["hass"] = hass
    if "entry" in params:
        kwargs["entry"] = entry
    if "agent" in params:
        kwargs["agent"] = agent
    if "agent_id" in params:
        kwargs["agent_id"] = DOMAIN
    if "name" in params:
        kwargs["name"] = entry.title or "OpenClaw"
    if "supported_languages" in params:
        kwargs["supported_languages"] = None
    if "language" in params:
        kwargs["language"] = None

    try:
        fn(**kwargs)
    except TypeError:
        # Best-effort fallback
        fn(hass, entry, agent)


def _unregister_agent(hass: HomeAssistant, entry: ConfigEntry) -> None:
    from homeassistant.components import conversation
    import inspect

    if not hasattr(conversation, "async_unregister_agent"):
        return

    fn = conversation.async_unregister_agent
    params = inspect.signature(fn).parameters
    kwargs = {}

    if "hass" in params:
        kwargs["hass"] = hass
    if "entry" in params:
        kwargs["entry"] = entry
    if "agent_id" in params:
        kwargs["agent_id"] = DOMAIN

    try:
        fn(**kwargs)
    except TypeError:
        fn(hass, entry)


def _get_agent(hass: HomeAssistant, entry: ConfigEntry):
    from homeassistant.components import conversation

    # Newer HA expects agent_id (string), not ConfigEntry.
    try:
        if conversation.async_get_agent.__code__.co_argcount >= 2:
            try:
                return conversation.async_get_agent(hass, DOMAIN)
            except TypeError:
                return conversation.async_get_agent(hass, entry)
        return conversation.async_get_agent(hass)
    except TypeError:
        return conversation.async_get_agent(hass, DOMAIN)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    agent = OpenClawConversationAgent(hass, entry)
    entry.runtime_data = agent

    _register_agent(hass, entry, agent)
    _set_agent(hass, entry, agent)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    # If HA supported multiple agents we'd restore prior agent; MVP just unloads.
    current = _get_agent(hass, entry)
    if current is entry.runtime_data:
        _set_agent(hass, entry, None)

    _unregister_agent(hass, entry)

    return True
