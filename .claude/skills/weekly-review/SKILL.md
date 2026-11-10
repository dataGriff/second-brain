---
name: weekly-review
description: Run the weekly FEEDBACK step. Lists unprocessed inbox items, stale projects (no change in 14 days), projects without an intent link and intent with no active projects, drafts the weekly review note that diffs intent against what actually happened, and proposes archive candidates for approval. Use when the user asks for a weekly review, a review of the week, or what has drifted.
---

# Weekly review

This is the FEEDBACK step of INTENT → SPEC → PLAN → SYSTEM → FEEDBACK. Treat it like `terraform plan`: report the diff between desired and actual state and propose changes. Apply nothing beyond drafting the review note.

## Steps

1. `git pull --rebase origin main`.
2. **Gather the facts.** Run `python3 scripts/vault.py review` (same as `task review`). It reports:
   - unprocessed inbox notes (`status: inbox`)
   - stale projects: `status: active` with no git change to the file in 14+ days
   - overdue active projects (`due` in the past)
   - projects without an `intent` link
   - active intent notes with no active project pointing at them

   Ignore notes tagged `example` once real notes exist.
3. **Read the desired state.** Every `status: active` note in `01-intent/`: objective, key results, period.
4. **Read the actual state.**
   - This ISO week's daily notes in `05-journal/` (Monday to Sunday).
   - `git log --since="7 days ago" --name-status --format="%ad %s" --date=short` for what really changed.
   - Each active project's `## Plan` checkboxes and `## Feedback`.
5. **Draft the review note** at `05-journal/<GGGG>-W<WW>.md` (ISO week, e.g. `2026-W46`), starting from `templates/weekly-review.md` (`python3 scripts/vault.py new weekly` creates it). If the file already exists, add only to empty sections and never change text the user wrote. Fill in:
   - **Desired state**: each active objective with where its key results should be by now.
   - **Actual state**: what happened, with links to the daily notes and projects as evidence. Quote the user's journal wording; don't paraphrase it into something stronger.
   - **Diff**: one table row per objective or key result and per active project: expected, actual, drift, proposed action. If the notes don't say, write "no evidence this week" rather than guessing.
   - **Housekeeping**: the four lists from step 2, with wikilinks.
   - **Archive candidates**: see step 6.
   - **Plan for next week**: at most 3 concrete changes that close the largest drifts, each tied to a project or intent note.

   Keep `status: draft`. The user sets `final`.
6. **Propose archive candidates. Do not move anything.** Candidates:
   - projects with `status: done`
   - projects stale for 30+ days or paused with no plan to resume
   - intent notes that are `achieved`, `dropped`, or whose `period` has ended
   - `status: processed` notes still in `00-inbox/`

   List each with a one-line reason, in the note and in your reply.
7. **Commit and push the draft** (only the review note):

   ```sh
   git add 05-journal/<week>.md
   git commit -m "claude: draft weekly review <week>"
   git pull --rebase origin main && git push origin main
   ```

8. **Reply** with a short summary: counts, the top three drifts, the archive candidates, and a question asking which candidates to archive.
9. **Only after explicit approval**, archive the approved items. Never delete.
   - First commit: set `status: archived` in each note's frontmatter. `claude: mark <names> archived (approved in <week> review)`
   - Second commit: `git mv <path> 99-archive/<filename>` for each. `claude: archive <names>`
   - Run `python3 scripts/vault.py links`, then pull with rebase and push.

## Don'ts

- Don't edit daily notes.
- Don't change project `status`, `due` or `intent` yourself. Propose it in the Diff table.
- Don't archive without a yes that names the items.
