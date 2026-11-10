---
name: capture
description: File a thought, quote, idea or URL as a new timestamped note in 00-inbox/ with correct frontmatter. Use when the user says capture, save this, note this down, remember this, add to inbox, or pastes a URL to keep for later.
---

# Capture

Get the item into the inbox quickly and exactly. No distilling, no judging, no filing elsewhere.

## Steps

1. `git pull --rebase origin main`.
2. Work out the timestamp and slug:
   - Timestamp: `date +%Y-%m-%d-%H%M` (local time).
   - Slug: 2 to 5 kebab-case words naming the topic.
   - Path: `00-inbox/<timestamp>-<slug>.md`. If it exists, add a word to the slug. Never append to an existing file.
3. Write the note.

   A thought:

   ```markdown
   ---
   type: note
   status: inbox
   created: YYYY-MM-DD
   tags: []
   ---
   <the user's words, verbatim>
   ```

   A URL:

   ```markdown
   ---
   type: clip
   status: inbox
   title: "<page title>"
   source: <url>
   author: <author if known, else leave empty>
   clipped: YYYY-MM-DDTHH:mm
   created: YYYY-MM-DD
   tags: [clip]
   ---
   <the user's comment about it, verbatim, if they gave one>

   ## TL;DR

   - <3 bullets, only if the page could be fetched>
   ```

   - Keep the user's wording exactly. Don't tidy, expand or summarise their thought.
   - Fetch the URL for the title and TL;DR if a fetch tool is available. If it fails, save the URL anyway with the title left empty and no TL;DR section. Never invent a summary of a page you couldn't read.
   - Add 1 to 3 tags only when they are obvious. Reuse tags already in the vault.
   - If the thought clearly concerns an existing project, area or intent note, add a final line `Related: [[note-name]]`. Don't guess.
4. Several items in one request become several files, one each.
5. Commit only the new file(s) and push:

   ```sh
   git add 00-inbox/<file>.md
   git commit -m "claude: capture <slug>"
   git pull --rebase origin main && git push origin main
   ```

6. Reply with the file path, one line.
