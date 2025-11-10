#!/usr/bin/env python3
import subprocess
import re
import collections

def get_git_log():
    """Return list of 'name <email> year' lines from git log."""
    result = subprocess.run(
        ["git", "log", "--format=%aN <%aE> %ad", "--date=format:%Y"],
        capture_output=True, text=True, check=True
    )
    return result.stdout.splitlines()

def normalise_name(name: str) -> str:
    """Capitalise each part of the name and replace Z→S."""
    parts = name.strip().split()
    fixed = []
    for p in parts:
        p = p.capitalize().replace("Z", "S").replace("z", "s")
        fixed.append(p)
    return " ".join(fixed)

def normalise_email(email: str) -> str:
    """Lowercase and normalise domain."""
    email = email.strip().lower()
    email = email.replace("@skatelescope.org", "@skao.int")
    return email

def name_key(name: str) -> str:
    """Normalised key for fuzzy name comparison."""
    name = name.lower().strip()
    name = re.sub(r'[^a-z\s]', '', name)   # remove punctuation/numbers
    name = re.sub(r'\s+', ' ', name)
    name = name.replace('z', 's')          # British spelling consistency
    return name

def similar_name(a: str, b: str) -> bool:
    """True if names are similar enough to merge."""
    a_words = set(name_key(a).split())
    b_words = set(name_key(b).split())
    # If one is subset of the other or they share surname
    return bool(a_words & b_words) and (a_words.issubset(b_words) or b_words.issubset(a_words))

def pick_email(emails):
    """Prefer @skao.int, otherwise alphabetically first."""
    return sorted(emails, key=lambda e: (not e.endswith("skao.int"), e))[0]

def merge_contributors(contributors, name, email, year):
    """Merge data into contributors dict, using fuzzy name matching."""
    norm_email = normalise_email(email)
    display_name = normalise_name(name)
    year = int(year)

    match_key = None
    for key, c in contributors.items():
        if norm_email in c["emails"] or similar_name(display_name, c["display_name"]):
            match_key = key
            break

    if match_key is None:
        match_key = display_name
        contributors[match_key] = {
            "display_name": display_name,
            "emails": set(),
            "years": set(),
        }

    entry = contributors[match_key]
    entry["emails"].add(norm_email)
    entry["years"].add(year)
    # Prefer longer, more complete display names
    if len(display_name) > len(entry["display_name"]):
        entry["display_name"] = display_name

def normalise_and_dedupe():
    """Main normalisation and deduplication logic."""
    lines = get_git_log()
    contributors = {}

    for line in lines:
        line = line.strip()
        if not line:
            continue
        m = re.match(r"(.+?)\s*<(.*?)>\s*(\d{4})$", line)
        if not m:
            continue
        name, email, year = m.groups()
        merge_contributors(contributors, name, email, year)

    print("# Contributors\n")
    for key in sorted(contributors, key=lambda k: contributors[k]["display_name"].lower()):
        c = contributors[key]
        email = pick_email(c["emails"])
        years = " ".join(str(y) for y in sorted(c["years"]))
        print(f"- {c['display_name']} <{email}> {years}")

if __name__ == "__main__":
    normalise_and_dedupe()
