#!/usr/bin/env python3
"""Vault helper used by Taskfile.yml and the Claude skills.

Standard library only. Subcommands:
  review                 inbox / stale / unlinked report (the FEEDBACK inputs)
  links                  broken wikilinks and orphan notes (exit 1 if any broken)
  new daily              create today's daily note from templates/daily.md
  new weekly             create this week's review from templates/weekly-review.md
  new project "Name"     create a project note (optionally --intent okr-file-name)
"""
from __future__ import annotations

import argparse
import datetime as dt
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKIP_DIRS = {".git", ".obsidian", ".claude", ".trash", "templates", "clipper", "scripts", "attachments", "node_modules"}
ROOT_DOCS = {"README.md", "CLAUDE.md"}
STALE_DAYS = 14

WIKILINK = re.compile(r"!?\[\[([^\]\|#\^]*)(?:[#\^][^\]\|]*)?(?:\|[^\]]*)?\]\]")
FENCE = re.compile(r"```.*?```", re.S)
INLINE_CODE = re.compile(r"`[^`\n]*`")
HTML_COMMENT = re.compile(r"<!--.*?-->", re.S)


# ---------- reading the vault ----------

def notes() -> list[Path]:
    out = []
    for p in sorted(ROOT.rglob("*.md")):
        rel = p.relative_to(ROOT)
        if rel.parts[0] in SKIP_DIRS or (len(rel.parts) == 1 and rel.name in ROOT_DOCS):
            continue
        out.append(p)
    return out


def frontmatter(text: str) -> dict[str, str]:
    """Top-level `key: value` pairs only; enough for type/status/intent/due."""
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    if end == -1:
        return {}
    fm = {}
    for line in text[3:end].splitlines():
        m = re.match(r"^([A-Za-z_][\w-]*):\s*(.*)$", line)
        if m:
            fm[m.group(1)] = m.group(2).strip().strip("\"'")
    return fm


def links_in(text: str) -> list[str]:
    body = INLINE_CODE.sub("", FENCE.sub("", HTML_COMMENT.sub("", text)))
    return [t.strip() for t in WIKILINK.findall(body) if t.strip()]


def rel(p: Path) -> str:
    return p.relative_to(ROOT).as_posix()


def last_changed(p: Path) -> dt.datetime:
    """Last git commit touching the file; falls back to mtime if uncommitted."""
    try:
        ts = subprocess.run(
            ["git", "log", "-1", "--format=%ct", "--", rel(p)],
            cwd=ROOT, capture_output=True, text=True, check=True,
        ).stdout.strip()
        dirty = subprocess.run(
            ["git", "status", "--porcelain", "--", rel(p)],
            cwd=ROOT, capture_output=True, text=True, check=True,
        ).stdout.strip()
        if ts and not dirty:
            return dt.datetime.fromtimestamp(int(ts))
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass
    return dt.datetime.fromtimestamp(p.stat().st_mtime)


def resolver():
    """Resolve a wikilink target the way Obsidian does: by path, else by file name."""
    by_name: dict[str, list[Path]] = {}
    by_path: dict[str, Path] = {}
    for p in ROOT.rglob("*"):
        if not p.is_file():
            continue
        r = p.relative_to(ROOT)
        if r.parts[0] in {".git", ".obsidian", ".trash"}:
            continue
        key = r.as_posix().lower()
        by_path[key] = p
        by_name.setdefault(p.name.lower(), []).append(p)
        if p.suffix == ".md":
            by_path[key[:-3]] = p
            by_name.setdefault(p.stem.lower(), []).append(p)

    def resolve(target: str) -> Path | None:
        t = target.lower().strip("/")
        if t in by_path:
            return by_path[t]
        hits = by_name.get(t.split("/")[-1])
        return hits[0] if hits else None

    return resolve


# ---------- review ----------

def cmd_review(_args) -> int:
    now = dt.datetime.now()
    all_notes = [(p, frontmatter(p.read_text(encoding="utf-8"))) for p in notes()]
    live = [(p, fm) for p, fm in all_notes if rel(p).split("/")[0] != "99-archive"]

    inbox = [p for p, fm in live if fm.get("status") == "inbox"]
    projects = [(p, fm) for p, fm in live if fm.get("type") == "project"]
    active = [(p, fm) for p, fm in projects if fm.get("status") == "active"]
    stale = [(p, (now - last_changed(p)).days) for p, _ in active]
    stale = [(p, d) for p, d in stale if d >= STALE_DAYS]
    no_intent = [p for p, fm in projects if not WIKILINK.search(fm.get("intent", ""))]
    overdue = [(p, fm["due"]) for p, fm in active
               if re.match(r"\d{4}-\d{2}-\d{2}$", fm.get("due", "")) and fm["due"] < now.date().isoformat()]

    resolve = resolver()
    served = set()
    for p, fm in active:
        m = WIKILINK.search(fm.get("intent", ""))
        target = resolve(m.group(1)) if m else None
        if target:
            served.add(target)
    intents = [p for p, fm in live if fm.get("type") == "okr" and fm.get("status") == "active"]
    idle_intent = [p for p in intents if p not in served]

    def section(title, rows):
        print(f"\n{title}: {len(rows)}")
        for r in rows:
            print(f"  - {r}")

    print(f"Vault review, {now:%Y-%m-%d %H:%M}")
    section("Unprocessed inbox notes", [rel(p) for p in inbox])
    section(f"Stale active projects (no change in {STALE_DAYS}+ days)", [f"{rel(p)} ({d} days)" for p, d in stale])
    section("Overdue active projects", [f"{rel(p)} (due {d})" for p, d in overdue])
    section("Projects without an intent link", [rel(p) for p in no_intent])
    section("Active intent with no active project", [rel(p) for p in idle_intent])
    return 0


# ---------- links ----------

def cmd_links(_args) -> int:
    resolve = resolver()
    broken: list[tuple[str, str]] = []
    inbound: dict[Path, int] = {}
    all_notes = notes()
    for p in all_notes:
        for target in links_in(p.read_text(encoding="utf-8")):
            hit = resolve(target)
            if hit is None:
                broken.append((rel(p), target))
            elif hit != p:
                inbound[hit] = inbound.get(hit, 0) + 1

    # Journal, inbox and archive notes are not expected to have inbound links.
    exempt = {"00-inbox", "05-journal", "99-archive"}
    orphans = [rel(p) for p in all_notes
               if inbound.get(p, 0) == 0 and rel(p).split("/")[0] not in exempt]

    print(f"Broken wikilinks: {len(broken)}")
    for src, target in broken:
        print(f"  - {src} -> [[{target}]]")
    print(f"\nOrphan notes (no inbound links): {len(orphans)}")
    for o in orphans:
        print(f"  - {o}")
    return 1 if broken else 0


# ---------- new ----------

def slugify(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


def render(template: str, title: str, now: dt.datetime) -> str:
    """Expand the Obsidian core-template variables the vault's templates use."""
    iso_year, iso_week, _ = now.isocalendar()
    tokens = {"GGGG": f"{iso_year}", "YYYY": f"{now:%Y}", "MM": f"{now:%m}", "DD": f"{now:%d}",
              "WW": f"{iso_week:02d}", "HH": f"{now:%H}", "mm": f"{now:%M}"}

    def fmt(pattern: str) -> str:
        out, i = "", 0
        while i < len(pattern):
            if pattern[i] == "[":
                j = pattern.index("]", i)
                out, i = out + pattern[i + 1:j], j + 1
                continue
            for tok, val in tokens.items():
                if pattern.startswith(tok, i):
                    out, i = out + val, i + len(tok)
                    break
            else:
                out, i = out + pattern[i], i + 1
        return out

    text = re.sub(r"\{\{date:([^}]+)\}\}", lambda m: fmt(m.group(1)), template)
    text = text.replace("{{date}}", fmt("YYYY-MM-DD")).replace("{{time}}", fmt("HH:mm"))
    return text.replace("{{title}}", title)


def create(path: Path, template_name: str, title: str) -> int:
    if path.exists():
        print(f"exists, left untouched: {rel(path)}")
        return 0
    template = (ROOT / "templates" / template_name).read_text(encoding="utf-8")
    path.write_text(render(template, title, dt.datetime.now()), encoding="utf-8")
    print(f"created: {rel(path)}")
    return 0


def cmd_new(args) -> int:
    now = dt.datetime.now()
    if args.kind == "daily":
        name = f"{now:%Y-%m-%d}"
        return create(ROOT / "05-journal" / f"{name}.md", "daily.md", name)
    if args.kind == "weekly":
        y, w, _ = now.isocalendar()
        name = f"{y}-W{w:02d}"
        return create(ROOT / "05-journal" / f"{name}.md", "weekly-review.md", name)
    title = " ".join(args.name).strip()
    if not title:
        print('usage: task new:project -- "Project name"', file=sys.stderr)
        return 2
    path = ROOT / "02-projects" / f"{slugify(title)}.md"
    existed = path.exists()
    code = create(path, "project.md", title)
    if args.intent and not existed:
        text = path.read_text(encoding="utf-8")
        path.write_text(text.replace('intent: "[[]]"', f'intent: "[[{args.intent}]]"'), encoding="utf-8")
    elif not existed:
        print("  remember to set `intent:` to an OKR note in 01-intent/")
    return code


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("review").set_defaults(fn=cmd_review)
    sub.add_parser("links").set_defaults(fn=cmd_links)
    new = sub.add_parser("new")
    new.add_argument("kind", choices=["daily", "weekly", "project"])
    new.add_argument("name", nargs="*")
    new.add_argument("--intent", default="")
    new.set_defaults(fn=cmd_new)
    args = ap.parse_args()
    return args.fn(args)


if __name__ == "__main__":
    sys.exit(main())
