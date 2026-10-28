from __future__ import annotations

import argparse
import json
import os
import sys

from .adb import AdbError, Client, Target
from .audit import inventory
from .bugreport import write as write_bug
from .drift import inspect as inspect_drift
from .engine import ApplyError, preview, restore
from .facts import read as read_facts
from .preflight import run as run_preflight
from .privacy import audit as privacy_audit
from .profile import ProfileError
from .provision import run as provision
from .safety import SafetyError
from .verify import run as verify


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="tvdebloat", description="Safe Android TV / Google TV debloating")
    p.add_argument("--host", default=os.environ.get("TV_HOST"))
    p.add_argument("--port", type=int, default=int(os.environ.get("TV_PORT", "5555")))
    p.add_argument("--adb", default=os.environ.get("ADB"))
    sub = p.add_subparsers(dest="command", required=True)

    sub.add_parser("probe")
    sub.add_parser("audit")
    sub.add_parser("privacy")
    pre = sub.add_parser("preflight"); pre.add_argument("profile", nargs="?")
    pv = sub.add_parser("preview"); pv.add_argument("profile")
    pr = sub.add_parser("provision"); pr.add_argument("profile"); pr.add_argument("--apply", action="store_true")
    rs = sub.add_parser("restore"); rs.add_argument("profile")
    vf = sub.add_parser("verify")
    dr = sub.add_parser("drift"); dr.add_argument("profile")
    br = sub.add_parser("bug-report")
    br.add_argument("--title", required=True); br.add_argument("--operation", required=True); br.add_argument("--error", required=True)
    br.add_argument("--expected", default=""); br.add_argument("--actual", default="")
    return p


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    if not args.host:
        print("error: --host or TV_HOST is required", file=sys.stderr)
        return 2
    try:
        client = Client(Target(args.host, args.port), args.adb)
        client.connect()
        if args.command == "probe":
            result = read_facts(client).as_dict()
        elif args.command == "audit":
            result = inventory(client)
        elif args.command == "privacy":
            result = privacy_audit(client)
        elif args.command == "preflight":
            result = run_preflight(client, args.profile)
        elif args.command == "preview":
            result = preview(client, args.profile)
        elif args.command == "provision":
            result = provision(client, args.profile, args.apply)
        elif args.command == "restore":
            result = restore(client, args.profile)
        elif args.command == "verify":
            result = verify(client)
        elif args.command == "drift":
            result = inspect_drift(client, args.profile)
        else:
            try:
                device = read_facts(client).as_dict()
            except Exception:
                device = {}
            jp, mp = write_bug(args.title, args.operation, args.error, args.expected, args.actual, device)
            result = {"json": str(jp), "markdown": str(mp)}
    except (AdbError, ProfileError, SafetyError, ApplyError, FileNotFoundError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
