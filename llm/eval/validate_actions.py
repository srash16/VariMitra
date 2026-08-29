"""Validate LLM JSON actions against the frozen TRD v2.0 allow-list."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "schemas" / "action.schema.json"
DEFAULT_DATA = ROOT / "data" / "intents" / "intents.jsonl"

ALLOWED_ACTIONS = {
    "OPEN_SECTION",
    "CLOSE_SECTION",
    "GO_BACK",
    "FIND_NEAREST",
    "SHOW_ROUTE",
    "GET_DISTANCE",
    "SELECT_LOCATION",
    "READ_INFORMATION",
    "GENERAL_QUESTION",
    "STOP",
    "GET_WARI_STATUS",
    "LOST_PERSON_REPORT",
    "FAMILY_STATUS",
}

CATEGORIES = {
    "WATER",
    "FOOD",
    "MEDICAL",
    "TOILET",
    "ACCOMMODATION",
    "TRANSPORT",
    "WOMEN",
}


def load_schema() -> dict:
    return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


def validate_action(payload: object) -> list[str]:
    errors: list[str] = []
    if not isinstance(payload, dict):
        return ["action must be a JSON object"]
    action = payload.get("action")
    params = payload.get("parameters")
    if action not in ALLOWED_ACTIONS:
        errors.append(f"unsupported or missing action: {action!r}")
    if action == "SOS":
        errors.append("SOS is not an LLM action")
    if not isinstance(params, dict):
        errors.append("parameters must be an object")
        return errors
    extra_top = set(payload) - {"action", "parameters"}
    if extra_top:
        errors.append(f"unexpected fields: {sorted(extra_top)}")
    if action in {"OPEN_SECTION", "FIND_NEAREST"}:
        if params.get("category") not in CATEGORIES:
            errors.append("category must be a known facility category")
    if action == "GENERAL_QUESTION" and not params.get("text"):
        errors.append("GENERAL_QUESTION requires text")
    if action != "GENERAL_QUESTION" and "text" in params and action not in ALLOWED_ACTIONS:
        errors.append("free text is only allowed for GENERAL_QUESTION")
    if action == "GET_WARI_STATUS" and "date" not in params:
        errors.append("GET_WARI_STATUS requires date")
    if action == "LOST_PERSON_REPORT" and "description" not in params:
        errors.append("LOST_PERSON_REPORT requires description")
    if action in {"GO_BACK", "STOP"} and params:
        errors.append(f"{action} must have empty parameters")
    return errors


def iter_records(path: Path) -> list[tuple[str, dict]]:
    records: list[tuple[str, dict]] = []
    if path.suffix == ".jsonl":
        for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            if not line.strip():
                continue
            records.append((f"{path.name}:{line_no}", json.loads(line)))
        return records
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, list):
        for index, item in enumerate(data, start=1):
            records.append((f"{path.name}[{index}]", item))
    else:
        records.append((path.name, data))
    return records


def validate_dataset(path: Path) -> int:
    failures = 0
    for label, record in iter_records(path):
        action = record.get("action", record)
        errors = validate_action(action)
        if errors:
            failures += 1
            print(f"FAIL {label}: {'; '.join(errors)}")
    if failures:
        print(f"{failures} invalid record(s)")
        return 1
    print(f"OK {path}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--path", type=Path, default=DEFAULT_DATA)
    parser.add_argument("--json", dest="raw_json", default=None, help="Validate one JSON action string")
    args = parser.parse_args(argv)
    if args.raw_json:
        errors = validate_action(json.loads(args.raw_json))
        if errors:
            print("FAIL: " + "; ".join(errors))
            return 1
        print("OK")
        return 0
    if not args.path.exists():
        print(f"missing dataset: {args.path}", file=sys.stderr)
        return 1
    return validate_dataset(args.path)


if __name__ == "__main__":
    raise SystemExit(main())
