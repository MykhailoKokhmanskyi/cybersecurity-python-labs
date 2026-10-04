import argparse
import csv
import json
import logging
import re
from collections import defaultdict
from dataclasses import asdict, dataclass
from pathlib import Path

logger = logging.getLogger("arp_audit")

OCTET = r"(?:25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)"
IP_RE = re.compile(rf"(?:{OCTET}\.){{3}}{OCTET}")
MAC_RE = re.compile(r"(?:[0-9A-Fa-f]{2}[:-]){5}[0-9A-Fa-f]{2}")


@dataclass
class Conflict:
    mac: str
    ips: list[str]


def read_rows(path: Path) -> list[list[str]]:
    rows = []
    with path.open(encoding="utf-8", newline="") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue

            if "," in line:
                rows.append([c.strip() for c in next(csv.reader([line]))])
            else:
                rows.append(line.split())
    return rows


def parse_arp(rows: list[list[str]]) -> tuple[list[tuple[str, str]], int]:
    valid = []
    invalid = 0
    for row in rows:
        ip = row[0] if len(row) > 0 else ""
        mac = row[1] if len(row) > 1 else ""
        if IP_RE.fullmatch(ip) and MAC_RE.fullmatch(mac):
            valid.append((ip, mac.lower().replace("-", ":")))
        elif ip.lower().replace(" ", "") in ("ip", "ipadress"):
            continue
        else:
            invalid += 1
            logger.warning("Invalid entry skipped: %s", row)
    return valid, invalid


def detect_spoofing(pairs: list[tuple[str, str]]) -> list[Conflict]:
    by_mac = defaultdict(set)
    for ip, mac in pairs:
        by_mac[mac].add(ip)
    return [Conflict(mac, sorted(ips)) for mac, ips in by_mac.items() if len(ips) > 1]


def add_arguments(parser: argparse.ArgumentParser):
    parser.add_argument("--arp-file", type=Path, required=True)
    parser.add_argument("--output-json", type=Path)
    parser.add_argument("--detect-spoofing", action="store_true")
    parser.add_argument("--log-file", type=Path)


def run(args: argparse.Namespace) -> int:
    handlers: list[logging.Handler] = [logging.StreamHandler()]
    if args.log_file:
        handlers.append(logging.FileHandler(args.log_file, encoding="utf-8"))
    logging.basicConfig(
        level=logging.INFO,
        format="[%(levelname)s] %(message)s",
        handlers=handlers,
        force=True,
    )

    logger.info("Parsing ARP table snapshot from %s...", args.arp_file)
    try:
        rows = read_rows(args.arp_file)
    except OSError as e:
        logger.error("Cannot read %s: %s", args.arp_file, e)
        return 1

    pairs, invalid = parse_arp(rows)
    logger.info("Validated %d IP/MAC entries.", len(pairs) + invalid)
    print("\n=== Validated Entries Summary ===")
    print(f"Valid IP/MAC Pairs : {len(pairs)}")
    print(f"Invalid Syntax     : {invalid}")

    conflicts = []

    if args.detect_spoofing:
        conflicts = detect_spoofing(pairs)
        if conflicts:
            print("\n=== CRITICAL SECURITY ALERTS: ARP-SPOOFING DETECTED ===")
        for c in conflicts:
            print(f"[ALERT] MAC {c.mac} associated with MULTIPLE IP addresses:")
            for ip in c.ips:
                print(f"  - {ip}")
            logger.critical("ARP spoofing: MAC %s bound to %s", c.mac, ",".join(c.ips))

    if args.output_json:
        report = {
            "valid_pairs": len(pairs),
            "invalid_entries": invalid,
            "conflicts": [asdict(c) for c in conflicts],
        }
        try:
            args.output_json.write_text(
                json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8"
            )
        except OSError as e:
            logger.error("Cannot write %s: %s", args.output_json, e)
            return 1
        logger.info("Report saved to %s", args.output_json)
    return 0
