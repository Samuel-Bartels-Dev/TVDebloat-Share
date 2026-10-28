from __future__ import annotations

from .adb import Client
from .model import DeviceFacts


def read(client: Client) -> DeviceFacts:
    return DeviceFacts(
        manufacturer=client.prop("ro.product.manufacturer"),
        model=client.prop("ro.product.model"),
        device=client.prop("ro.product.device"),
        board=client.prop("ro.product.board"),
        android=client.prop("ro.build.version.release"),
        sdk=client.prop("ro.build.version.sdk"),
        fingerprint=client.prop("ro.build.fingerprint"),
        home=client.resolve_home(),
    )
