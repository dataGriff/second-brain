---
name: link-check
description: Find broken wikilinks and orphan notes in the vault and propose fixes. Use when the user asks to check links, find orphans, find broken links, or after notes have been moved, renamed or archived.
---

# Link check

## Steps

1. `git pull --rebase origin main`.
2. Run `python3 scripts/vault.py links` (same as `task links`). It prints:
   - **Broken wikilinks**: `source -> [[target]]` where no file matches the target. Exit code 1 if any exist.
   - **Orphan notes**: notes with no inbound links. Inbox, journal and archive notes are exempt, as are `templates/`, `README.md` and `CLAUDE.md`.
3. **Broken links.** For each, find the cause:
   - Renamed or moved note: search for the likely new name (`git log --diff-filter=R --name-status`, or grep for similar filenames). Fix the link with a minimal edit.
   - Typo: fix it if exactly one note is the obvious match.
   - Note never existed: report it. Don't create a stub note and don't remove the link.
   - Broken link inside a journal note or an inbox note body: report it, don't edit. Those are the user's words.
4. **Orphans.** For each, read it and suggest where it belongs:
   - a project with no inbound link should be listed under `## Projects` in its intent note
   - a resource should be linked from a related project, area or resource
   - an intent note with nothing linking to it has no projects: flag it for the weekly review

   Suggest the links; add them only where the connection is certain and the edit is a one-line addition. Otherwise list them for the user to decide. Never archive an orphan without approval.
5. If you changed files, re-run the check, then commit only those files and push:

   ```sh
   git add <changed files>
   git commit -m "claude: fix <n> broken links"
   git pull --rebase origin main && git push origin main
   ```

6. Report: what was fixed, what still needs a decision, and the remaining counts.
