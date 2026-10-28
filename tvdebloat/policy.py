from __future__ import annotations

from .profile import PACKAGE_RE


PROTECTED_EXACT = {
    "android",
    "android.ext.services",
    "android.ext.shared",
    "com.android.systemui",
    "com.android.shell",
    "com.android.phone",
    "com.android.settings",
    "com.android.tv.settings",
    "com.android.permissioncontroller",
    "com.google.android.permissioncontroller",
    "com.android.packageinstaller",
    "com.google.android.packageinstaller",
    "com.android.modulemetadata",
    "com.google.android.modulemetadata",
    "com.cltv.mal",
    "com.mediatek.tis",
    "com.mediatek.tv.service",
    "com.mediatek.tv.agent",
}
PROTECTED_PREFIXES = (
    "com.google.android.overlay.modules.",
)
PROVIDER_ALLOW = {
    "com.android.providers.calendar",
    "com.android.providers.contacts",
    "com.android.providers.userdictionary",
    "com.android.providers.blockednumber",
}


def is_protected(package: str) -> bool:
    if not PACKAGE_RE.fullmatch(package):
        return True
    if package in PROTECTED_EXACT:
        return True
    if package.startswith("com.android.providers.") and package not in PROVIDER_ALLOW:
        return True
    return package.startswith(PROTECTED_PREFIXES)
