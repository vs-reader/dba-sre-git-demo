"""Check fictional configuration profiles without connecting to any server."""

import configparser
from pathlib import Path
import sys


# Training policy, not PostgreSQL sizing advice or hardware measurements.
PROFILES = {"small": ("db01", 100), "large": ("db02", 300)}


def validate(text):
    config = configparser.ConfigParser(interpolation=None)
    try:
        config.read_string(text)
    except configparser.Error as error:
        return False, [f"ERROR: invalid INI: {error}"]

    messages = []
    valid = True
    if config.defaults():
        messages.append("ERROR: DEFAULT values are not allowed; set each profile explicitly")
        valid = False
    extra = set(config.sections()) - set(PROFILES)
    if extra:
        messages.append(f"ERROR: unknown profiles: {', '.join(sorted(extra))}")
        valid = False

    for profile, (host, limit) in PROFILES.items():
        if profile not in config:
            messages.append(f"ERROR: missing profile [{profile}] for {host}")
            valid = False
            continue
        if set(config[profile]) != {"max_connections"}:
            messages.append(f"ERROR: [{profile}] must contain only max_connections")
            valid = False
            continue
        try:
            value = config.getint(profile, "max_connections")
        except ValueError:
            messages.append(f"ERROR: {host} ({profile}): max_connections must be an integer")
            valid = False
            continue

        if not 1 <= value <= limit:
            messages.append(
                f"FAIL: {host} ({profile}): max_connections={value}; allowed range: 1..{limit}"
            )
            valid = False
        else:
            messages.append(
                f"PASS: {host} ({profile}): max_connections={value}; allowed range: 1..{limit}"
            )
    return valid, messages


def main():
    path = Path(__file__).with_name("config.ini")
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as error:
        print(f"ERROR: cannot read config.ini: {error}")
        return 1
    valid, messages = validate(text)
    print("Training policy only. No connection to VMs or PostgreSQL.")
    for message in messages:
        print(message)
    print("RESULT: PASS" if valid else "RESULT: FAIL")
    return 0 if valid else 1


if __name__ == "__main__":
    sys.exit(main())
