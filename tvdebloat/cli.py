from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
import tomllib

from .adb import AdbError, Client, Target
from .audit import inventory
from .bugreport import write as write_bug
from .drift import inspect as inspect_drift
from .discovery import discover, write as write_discovery
from .author import initialize as init_profile, promote as promote_profile
from .engine import ApplyError, preview, restore
from .facts import read as read_facts
from .preflight import run as run_preflight
from .privacy import audit as privacy_audit
from .profile import ProfileError
from .provision import run as provision
from .safety import SafetyError
from .verify import run as verify


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="tvdebloat", description="Android/Google TV debloating and independent webOS discovery/planning")
    p.add_argument("--host", default=os.environ.get("TV_HOST"))
    p.add_argument("--port", type=int, default=int(os.environ.get("TV_PORT", "5555")))
    p.add_argument("--adb", default=os.environ.get("ADB"))
    p.add_argument("--platform", choices=("android", "webos"), default="android")
    p.add_argument("--ssh-port", type=int, default=22)
    p.add_argument("--ssh-user", default="root")
    p.add_argument("--ssh-key")
    p.add_argument("--plan", help="webOS: save preview here, or read this exact plan for --apply")
    p.add_argument("--approve-plan", help="webOS: digest of the exact operator-approved plan")
    p.add_argument("--pilot", action="store_true", help="webOS: acknowledge candidate pilot")
    p.add_argument("--state-dir", help="webOS: explicit private local recovery directory")
    sub = p.add_subparsers(dest="command", required=True)

    sub.add_parser("probe")
    sub.add_parser("audit")
    sub.add_parser("privacy")
    ds = sub.add_parser("discover"); ds.add_argument("--out", required=True)
    pi = sub.add_parser("profile-init"); pi.add_argument("--name", required=True); pi.add_argument("--vendor", required=True); pi.add_argument("--model", required=True); pi.add_argument("--from", dest="from_file", required=True)
    pp = sub.add_parser("profile-promote"); pp.add_argument("profile")
    pre = sub.add_parser("preflight"); pre.add_argument("profile", nargs="?")
    pv = sub.add_parser("preview"); pv.add_argument("profile")
    pr = sub.add_parser("provision"); pr.add_argument("profile"); pr.add_argument("--apply", action="store_true")
    rs = sub.add_parser("restore"); rs.add_argument("profile"); rs.add_argument("--apply", action="store_true")
    vf = sub.add_parser("verify")
    dr = sub.add_parser("drift"); dr.add_argument("profile")
    br = sub.add_parser("bug-report")
    br.add_argument("--title", required=True); br.add_argument("--operation", required=True); br.add_argument("--error", required=True)
    br.add_argument("--expected", default=""); br.add_argument("--actual", default="")
    return p


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    local_commands = {"profile-init", "profile-promote"}

    try:
        if getattr(args, "profile", None) and not (args.platform == "webos" and args.command == "restore"):
            declared = tomllib.loads(Path(args.profile).read_text(encoding="utf-8")).get("platform", "android")
            if declared != args.platform:
                raise ProfileError("profile platform does not match selected --platform")
        if args.command == "profile-init":
            source = json.loads(Path(args.from_file).read_text(encoding="utf-8"))
            if not isinstance(source, dict):
                raise ProfileError("discovery must be a platform-tagged object")
            if source.get("platform", "android") != args.platform:
                raise ProfileError("discovery platform does not match selected --platform")
        if args.platform == "webos":
            from .webos_cli import run as run_webos
            result = run_webos(args)
            print(json.dumps(result, indent=2, sort_keys=True))
            return 1 if args.command == "preflight" and not result["ready"] else 0
        if args.command == "profile-init":
            path = init_profile(args.from_file, args.vendor, args.model, args.name)
            result = {"profile": str(path), "status": "candidate"}
        elif args.command == "profile-promote":
            path = promote_profile(args.profile)
            result = {"profile": str(path), "status": "validated"}
        else:
            if not args.host:
                if args.command == "bug-report":
                    jp, mp = write_bug(
                        args.title, args.operation, args.error,
                        args.expected, args.actual, {}
                    )
                    result = {"json": str(jp), "markdown": str(mp)}
                    print(json.dumps(result, indent=2, sort_keys=True))
                    return 0
                if args.command == "preflight":
                    result = run_preflight(None, args.profile)
                    print(json.dumps(result, indent=2, sort_keys=True))
                    return 0
                print("error: --host or TV_HOST is required", file=sys.stderr)
                return 2

            client = Client(Target(args.host, args.port), args.adb)
            client.connect()
            if args.command == "probe":
                result = read_facts(client).as_dict()
            elif args.command == "audit":
                result = inventory(client)
            elif args.command == "privacy":
                result = privacy_audit(client)
            elif args.command == "discover":
                data = discover(client)
                out = write_discovery(data, args.out)
                result = {"discovery": str(out), "packages": len(data["packages"])}
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
                jp, mp = write_bug(
                    args.title, args.operation, args.error,
                    args.expected, args.actual, device
                )
                result = {"json": str(jp), "markdown": str(mp)}
    except OSError as exc:
        if args.platform == "webos":
            print("error: local webOS artifact could not be read or written; check permissions and existing files", file=sys.stderr)
            return 1
        if isinstance(exc, FileNotFoundError):
            print(f"error: {exc}", file=sys.stderr)
            return 1
        raise
    except (AdbError, ProfileError, SafetyError, ApplyError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
