# Second brain

Plain markdown in a git repo, opened as an Obsidian vault, with Claude as the thinking layer. The working rules for Claude are in [CLAUDE.md](CLAUDE.md).

The model is a reconciliation loop: **INTENT → SPEC → PLAN → SYSTEM → FEEDBACK**. Intent is the desired state, the weekly review diffs it against what actually happened.

## Layout

| Folder | Holds |
| --- | --- |
| `00-inbox/` | Everything lands here first |
| `01-intent/` | OKRs and goals (desired state) |
| `02-projects/` | Finite work with an outcome and deadline, each linked to an intent note |
| `03-areas/` | Ongoing responsibilities |
| `04-resources/` | Atomic reference notes, one idea each |
| `05-journal/` | Daily notes (`YYYY-MM-DD.md`) and weekly reviews (`YYYY-Www.md`) |
| `99-archive/` | Retired notes |
| `templates/` | Obsidian templates |
| `clipper/` | Web Clipper template |

Notes named `example-*` or tagged `example` show the conventions. Archive them when you have real notes.

## How sync works

```
Phone ⇄ Obsidian Sync ⇄ Mac (hub) ⇄ Obsidian Git plugin ⇄ GitHub ⇄ cloud Claude sessions
```

**The Mac must be on with Obsidian open for changes to flow between the phone and git.** With the Mac off, the phone still syncs to Obsidian Sync and Claude still pushes to GitHub, and the two sides catch up when the Mac next opens Obsidian.

## Setup

### 1. Mac (the hub)

1. Clone the repo:
   ```sh
   git clone git@github.com:dataGriff/second-brain.git ~/second-brain
   ```
2. Obsidian → **Open folder as vault** → choose `~/second-brain`.
3. **Settings → Core plugins → Sync**: sign in and create a new remote vault for this folder. In Sync's settings:
   - turn **off** "Installed community plugins" and "Active community plugin list", so the Git plugin never reaches the phone
   - leave core plugin settings, templates and app settings syncing as you prefer
4. **Settings → Community plugins**: turn on community plugins, browse, install and enable **Git** (by Vinzent, id `obsidian-git`). In its settings:
   - Auto commit-and-sync interval: `5` minutes
   - Pull on startup: on
   - Sync method (pull strategy): `Rebase`
   - Leave the commit message as the default (`vault backup: {{date}}`), so Claude's `claude:` commits stay distinguishable
5. Check it works: edit a note, wait 5 minutes (or run the command **Git: Commit-and-sync**), and confirm the commit appears on GitHub.

The plugin's `data.json` is gitignored because plugin data can hold tokens and device state, so these settings are made once per machine.

### 2. Phone

1. Install Obsidian, sign in, and choose **Set up Obsidian Sync** → connect to the remote vault created above. Don't clone the repo and don't install a git app.
2. Keep community plugins out of the phone: either leave the community plugin sync toggles off (step 1.3) or, if the Git plugin does arrive, disable it in **Settings → Community plugins** on the phone.

### 3. Web Clipper

1. Install [Obsidian Web Clipper](https://obsidian.md/clipper) in your desktop browser and, on iPhone, from the App Store (enable it under **Settings → Apps → Safari → Extensions**).
2. In the extension's settings: **Templates → Import** and choose `clipper/default-template.json`. On the phone, open the file from the vault via the Files app. Move it to the top of the template list to make it the default.
3. In **General**, set the vault name to match this vault.
4. For the 3-bullet TL;DR: **Interpreter** → enable it, add a provider and API key, and pick a model. Without Interpreter the clip still saves; the TL;DR line is left as the raw prompt.

Clips are saved to `00-inbox/` as `YYYY-MM-DD-HHmm-page-title.md` with `type: clip`, `status: inbox`, `source`, `author` and `clipped`.

### 4. Tooling (optional, Mac)

```sh
brew install mise   # if you don't have it
mise trust && mise install
task                # list tasks
```

| Task | Does |
| --- | --- |
| `task review` | Counts unprocessed inbox notes, stale projects, and intent/project gaps |
| `task links` | Broken wikilink check, plus orphan notes |
| `task new:daily` | Creates today's daily note |
| `task new:weekly` | Creates this week's review note |
| `task new:project -- "Name"` | Creates a project note. Add `INTENT=okr-file-name` to set its intent link |

### 5. Claude

Run Claude Code in the vault folder (or a cloud session on the repo). Skills:

| Skill | Does |
| --- | --- |
| `/capture <thought or URL>` | New timestamped inbox note |
| `/distil [note]` | Inbox note → atomic resource notes, linked, original marked processed and archived |
| `/weekly-review` | Reports gaps, drafts the weekly review, proposes archive candidates and waits for approval |
| `/link-check` | Orphan notes and broken wikilinks |

Claude commits with a `claude:` prefix and pushes to `main`.

## Avoiding sync conflicts

- Capture makes a new timestamped file instead of appending to a shared one.
- Keep edits small and let the 5-minute auto-sync run.
- If the Git plugin reports a merge conflict, resolve it on the Mac keeping both sides' text, then run **Git: Commit-and-sync** again.
