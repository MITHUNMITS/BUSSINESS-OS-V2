from __future__ import annotations

from dataclasses import dataclass
from importlib import import_module
from typing import Any

MODULE_CONFIG_PATHS = [
    "business_os.apps.core.module_config",
    "business_os.apps.marketplace.module_config",
    "business_os.apps.websites.module_config",
    "business_os.apps.catalogue.module_config",
    "business_os.apps.inventory.module_config",
    "business_os.apps.commerce.module_config",
    "business_os.apps.payments.module_config",
    "business_os.apps.analytics.module_config",
]


@dataclass(frozen=True)
class ModuleDefinition:
    code: str
    name: str
    description: str
    category: str
    icon: str
    capabilities: tuple[str, ...]
    navigation: tuple[dict[str, Any], ...]
    website_contributions: tuple[dict[str, Any], ...]


def load_module_definitions() -> dict[str, ModuleDefinition]:
    definitions: dict[str, ModuleDefinition] = {}
    for path in MODULE_CONFIG_PATHS:
        module = import_module(path)
        config = getattr(module, "MODULE_CONFIG")
        definitions[config["code"]] = ModuleDefinition(
            code=config["code"],
            name=config["name"],
            description=config.get("description", ""),
            category=config.get("category", "general"),
            icon=config.get("icon", "box"),
            capabilities=tuple(config.get("capabilities", [])),
            navigation=tuple(config.get("navigation", [])),
            website_contributions=tuple(config.get("website_contributions", [])),
        )
    return definitions


def get_navigation(*, organization: Any, user: Any) -> list[dict[str, Any]]:
    from business_os.apps.entitlements.services import has_any_entitlement

    navigation: list[dict[str, Any]] = [
        {"label": "Dashboard", "url_name": "admin-dashboard", "icon": "layout-dashboard"}
    ]
    for definition in load_module_definitions().values():
        if not definition.navigation:
            continue
        if not definition.capabilities or has_any_entitlement(
            organization=organization,
            capability_codes=definition.capabilities,
        ):
            navigation.extend(definition.navigation)
    navigation.append({"label": "Marketplace", "url_name": "admin-marketplace", "icon": "store"})
    navigation.append({"label": "Settings", "url_name": "admin-settings", "icon": "settings"})
    return navigation

