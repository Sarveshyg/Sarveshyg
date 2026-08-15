#!/usr/bin/env python3
"""Regenerate the live-status line inside assets/terminal-hero.svg.

The line tagged data-live="1" is replaced with live GitHub profile stats
(public repos + followers) plus an updated UTC timestamp. Falls back to a
timestamp-only value if the GitHub API is unreachable.
"""

import datetime
import json
import os
import pathlib
import re
import urllib.request

SVG_PATH = pathlib.Path("assets/terminal-hero.svg")
API_URL = "https://api.github.com/users/Sarveshyg"


def xml_escape(text: str) -> str:
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def fetch_user() -> dict:
    req = urllib.request.Request(
        API_URL,
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": "profile-hero-updater",
        },
    )
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.load(resp)


def main() -> None:
    now = datetime.datetime.now(datetime.timezone.utc)
    stamp = now.strftime("%Y-%m-%d %H:%M UTC")
    live = f"profile synced {stamp}"

    try:
        data = fetch_user()
        repos = data.get("public_repos", "--")
        followers = data.get("followers", "--")
        live = f"repos {repos} · followers {followers} · synced {stamp}"
        print(f"Fetched live stats: repos={repos} followers={followers}")
    except Exception as exc:
        print(f"GitHub API unavailable, using timestamp only: {exc}")

    svg = SVG_PATH.read_text(encoding="utf-8")
    pattern = re.compile(r'(<text[^>]*data-live="1"[^>]*>)\s*[^<]*(</text>)', re.DOTALL)
    if not pattern.search(svg):
        raise SystemExit("ERROR: data-live line not found in terminal-hero.svg")

    svg = pattern.sub(lambda m: m.group(1) + "   " + xml_escape(live) + m.group(2), svg)
    SVG_PATH.write_text(svg, encoding="utf-8")
    print(f"Updated {SVG_PATH}: {live}")


if __name__ == "__main__":
    main()