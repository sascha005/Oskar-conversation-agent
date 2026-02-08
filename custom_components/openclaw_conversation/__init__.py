from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN
from .conversation import OpenClawConversationAgent


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


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    agent = OpenClawConversationAgent(hass, entry)
    entry.runtime_data = agent

    # Register only; don't force default agent
    _register_agent(hass, entry, agent)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    _unregister_agent(hass, entry)

    return True
