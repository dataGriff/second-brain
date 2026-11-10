---
name: distil
description: Turn an inbox note or clip into one or more atomic resource notes in the user's own words, link them to relevant projects, areas and intent, then mark the original processed and move it to 99-archive/inbox/. Use when the user says distil, process the inbox, process this note, or turn this clip into notes.
---

# Distil

Input: one inbox note (a path, a name, or "the next one"). With no argument, list notes in `00-inbox/` with `status: inbox`, oldest first, and ask which to process. Process one note at a time.

## Steps

1. `git pull --rebase origin main`. Read the inbox note in full.
2. **Find the ideas.** List the distinct ideas worth keeping, usually 1 to 3. One idea per resource note. If nothing is worth keeping, say so and ask whether to mark it processed with no resource notes.
3. **Search before writing.** For each idea, grep `04-resources/` (and the rest of the vault) for an existing note on it.
   - Exists: add what is new to that note with a small edit, and add the inbox note under `## Distilled from`. Don't create a duplicate.
   - New: create `04-resources/<idea-as-a-claim>.md` from `templates/resource.md`.
4. **Write each resource note.**
   - Title and filename state the idea as a claim (`reconciliation-loops-beat-plans`), not a topic.
   - First person, plain words, the user's voice. Use their phrasing from the inbox note and their other notes where it exists. No copied passages; at most one short quote, attributed.
   - A few sentences to a few short paragraphs. If it needs headings beyond the template's, it is more than one idea.
   - Frontmatter: `type: resource`, `status: active`, `created: <today>`, `source: <the clip's source URL>` if there is one, `tags`.
   - `## Why it matters`: one or two sentences tying it to the user's work.
   - `## Related`: wikilinks to the active projects, areas and intent notes it supports, and to sibling resource notes. Read `01-intent/`, `02-projects/` and `03-areas/` to find real matches. Link only where there is a real connection; no links is acceptable, forced links are not.
   - `## Distilled from`: `[[<inbox-note-filename>]]`.
5. **Show the user the drafts** (titles plus text) before committing if anything was a judgement call: which ideas to keep, or a link you are unsure about. Otherwise proceed.
6. **Mark the original processed.** Edit only its frontmatter; leave the body untouched:
   - `status: processed`
   - `processed: <today>`
   - `distilled_to: ["[[resource-a]]", "[[resource-b]]"]`
7. **Commit in two steps**, content first and the move second:

   ```sh
   git add 04-resources/<new-or-changed>.md 00-inbox/<note>.md
   git commit -m "claude: distil <note> into <n> resource note(s)"
   git mv 00-inbox/<note>.md 99-archive/inbox/<note>.md
   git commit -m "claude: archive processed inbox note <note>"
   git pull --rebase origin main && git push origin main
   ```

   This move is the one archive action that needs no separate approval.
8. Run `python3 scripts/vault.py links` and fix any link you broke.
9. Report: the resource notes created or extended, what they link to, and how many inbox notes remain.

## Don'ts

- Don't rewrite or delete the original note's text.
- Don't create a resource note that just summarises the article. Each note is one reusable idea.
- Don't add `intent`, `due` or other project fields to resource notes.
