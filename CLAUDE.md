# Second brain

A personal knowledge base: plain markdown in a git repo, opened as an Obsidian vault. Claude is the thinking layer. This file is the contract for every Claude session, local or cloud.

## The loop

Everything here serves one reconciliation loop, Terraform-style (desired state vs actual state):

**INTENT → SPEC → PLAN → SYSTEM → FEEDBACK**

| Step | Meaning | Where it lives |
| --- | --- | --- |
| INTENT | Desired state: objectives and key results | `01-intent/` |
| SPEC | What "done" looks like for one piece of work | `## Spec` in a project note |
| PLAN | Steps from actual state to the spec | `## Plan` in a project note |
| SYSTEM | The routine that executes the plan | `## System` in a project, `03-areas/`, daily notes |
| FEEDBACK | Diff of intent against what actually happened | Weekly review in `05-journal/` |

The weekly review is the `plan` output: it reports drift and proposes changes. I decide what to apply.

## Structure

| Folder | Holds |
| --- | --- |
| `00-inbox/` | Everything lands here first: manual notes, Web Clipper, Claude captures |
| `01-intent/` | OKRs. One note per objective, key results as a checklist inside it |
| `02-projects/` | Finite work with an outcome and a deadline. Each links up to an intent note |
| `03-areas/` | Ongoing responsibilities with no end date |
| `04-resources/` | Distilled reference notes. Atomic: one idea per note, in my own words |
| `05-journal/` | Daily notes `YYYY-MM-DD.md` and weekly reviews `YYYY-Www.md` |
| `99-archive/` | Anything retired. Processed inbox notes go to `99-archive/inbox/` |
| `templates/` | Obsidian templates: daily, weekly-review, project, area, resource, okr |
| `attachments/` | Images and files embedded in notes |
| `clipper/` | Obsidian Web Clipper template (`default-template.json`) |
| `scripts/`, `Taskfile.yml`, `mise.toml` | Helper tooling. `task review`, `task links`, `task new:daily`, `task new:weekly`, `task new:project -- "Name"` |
| `.claude/skills/` | `capture`, `distil`, `weekly-review`, `link-check` |

Notes prefixed `example-` or tagged `example` are seeded examples of the conventions, not real content. Ignore them in reviews once real notes exist.

## Frontmatter schema

Every note starts with YAML frontmatter. Required on all notes: `type`, `status`, `created` (`YYYY-MM-DD`), `tags` (a list).

| `type` | Folder | `status` values | Extra fields |
| --- | --- | --- | --- |
| `note` | `00-inbox/` | `inbox`, `processed` | `processed`, `distilled_to` once distilled |
| `clip` | `00-inbox/` | `inbox`, `processed` | `source` (URL, required), `title`, `author`, `clipped`; `processed`, `distilled_to` once distilled |
| `okr` | `01-intent/` | `active`, `achieved`, `dropped` | `period` (e.g. `2026-Q4`) |
| `project` | `02-projects/` | `planned`, `active`, `paused`, `done`, `archived` | `intent` (required), `due` (`YYYY-MM-DD`) |
| `area` | `03-areas/` | `active`, `archived` | |
| `resource` | `04-resources/` | `active`, `archived` | `source` when it came from a clip or URL |
| `daily` | `05-journal/` | `active` | |
| `weekly-review` | `05-journal/` | `draft`, `final` | `week` (e.g. `2026-W46`) |

Rules:

- Wikilinks in frontmatter must be quoted, or YAML reads them as nested lists: `intent: "[[okr-note-name]]"`.
- Every project has `intent: "[[...]]"`, `status` and `due`. A project with no intent link is a defect that the weekly review reports.
- Inbox notes keep `status: inbox` until processed. Anything moved to `99-archive/` gets `status: archived` (processed inbox notes keep `status: processed`).
- Don't invent new `type` or `status` values. If one seems needed, ask.

## Naming and linking

- Filenames are kebab-case, lowercase, ASCII, `.md`.
- Inbox captures are timestamped: `00-inbox/YYYY-MM-DD-HHmm-topic.md` (24-hour, local time of the writer).
- Resource filenames state the idea (`reconciliation-loops-beat-plans.md`), not a topic (`loops.md`).
- Link with `[[wikilinks]]` using the bare filename without folder or extension, so links survive moves between folders. Use `[[file-name|display text]]` for readable text.
- Filenames must be unique across the whole vault, because links resolve by name.
- Before creating a note, search for an existing one on the same idea. Link to or extend it instead of duplicating.
- Links go up the loop: resources link to the projects, areas or intent they support; projects link to their intent; intent notes list their projects.
- Run `task links` (or `python3 scripts/vault.py links`) after moving or renaming anything.

## Sync architecture

```
Phone (Obsidian) ⇄ Obsidian Sync ⇄ Mac (Obsidian, the hub) ⇄ Obsidian Git plugin ⇄ GitHub (private) ⇄ cloud Claude sessions
                                         ⇅
                                   local Claude Code
```

- The Mac is the hub. Obsidian Sync carries the vault to the phone. The Obsidian Git plugin (desktop only) auto-commits, pulls and pushes every 5 minutes.
- The phone has no git. Phone changes reach GitHub only when the Mac is on with Obsidian open.
- Cloud Claude sessions clone from GitHub and push back. Their changes reach the phone via the Mac.
- Writers: me on the Mac, me on the phone, local Claude, cloud Claude, the Web Clipper. Any of them can be minutes behind the others.

So design every change to be small, frequent and non-conflicting:

- Capture creates a new timestamped file. Never append to a shared file to capture something.
- Prefer adding a new file over editing an existing one, and a small targeted edit over rewriting a file.
- Don't reformat, reorder or re-wrap content you aren't changing. Whitespace churn causes conflicts.
- One logical change per commit. Commit and push soon after making it; don't hold work back.
- Move files with `git mv`, and do moves in their own commit, separate from content edits.
- The auto-commits from the Git plugin (messages like `vault backup: ...`) are mine, not yours. Leave them alone.

## Rules for Claude

1. **Never delete notes.** Retire a note by moving it to `99-archive/` (keep the filename) and setting its status. Never use `rm` or `git rm` on a note.
2. **Never rewrite my wording in journal notes** (`05-journal/`). You may add clearly separate sections or lines when asked, and draft new weekly reviews. Existing sentences of mine stay exactly as written, typos included. The same applies to the body of inbox notes: distil into new notes, leave the original text alone.
3. **Link, don't duplicate.** Search first; link to existing notes.
4. **Archiving needs approval.** Propose archive candidates and wait for a yes. The one standing exception: `distil` moves the inbox note it just processed to `99-archive/inbox/`.
5. **Don't touch `.obsidian/`** unless I ask.
6. **Resource notes are in my voice**: first person, plain words, one idea each. No copied passages beyond a short attributed quote.
7. Keep the examples' shape: use the templates in `templates/` as the starting point for any new note.

## Git workflow

This repo uses `main` only. No feature branches, no pull requests.

1. Before starting work: `git pull --rebase origin main`.
2. Make the change. Stage only the files you changed (`git add <paths>`, not `git add -A`), so you never sweep up my in-progress edits.
3. Commit with a clear message prefixed `claude:`, e.g. `claude: distil 2026-11-10-1950-example-clip into 2 resource notes`.
4. `git pull --rebase origin main` again, then `git push origin main`. If the push is rejected, pull with rebase and retry.
5. On a rebase conflict: if it is in a file you changed, keep both sides' content and never drop my text. If you can't resolve it cleanly, run `git rebase --abort`, stop, and tell me.
6. Never force-push, never rewrite history, never amend a commit that isn't yours.

Cloud sessions: push to `main` as above. If the session's environment refuses pushes to `main` and only allows its own session branch, push there, don't open a PR, and tell me the commands to fast-forward `main` from the Mac:
`git fetch origin && git merge --ff-only origin/<session-branch> && git push origin main`.

## Skills

| Skill | Use |
| --- | --- |
| `/capture` | File a thought or URL as a new timestamped inbox note |
| `/distil` | Turn an inbox note into atomic resource notes, link them, mark the original processed |
| `/weekly-review` | Run the FEEDBACK step: report gaps, draft the weekly review, propose archive candidates |
| `/link-check` | Find broken wikilinks and orphan notes |
