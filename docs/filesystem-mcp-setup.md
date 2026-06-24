# Filesystem MCP — chat-side read access to this repo

**Status: config + groundwork only. Nothing is enabled by this repo.** The last
step (adding the connector) is a manual one you take in the Claude app — see
[What you do to enable it](#what-you-do-to-enable-it).

## Why

The GitHub MCP connector is platform-blocked on this account, so chat-side review
can't read the repo through GitHub. Instead we run the official local
**filesystem** MCP server, scoped to `~/Projects`, so a review session can read
the *live* working tree directly. Chat-side is for **review**; the writes still
happen here in Claude Code.

## Where the repo lives (no move needed)

`daily-driver` is its own standalone git repo, nested inside the website repo at:

```
~/Projects/makerphones/builds/daily-driver        ← canonical path
```

It is gitignored by the parent `makerphones` repo (see `makerphones/.gitignore`,
"hardware build repos"), so it is **already under `~/Projects`** — a server scoped
to `~/Projects` reaches it without moving anything. For convenience there is also
a top-level alias symlink so it shows up as a first-class project:

```
~/Projects/daily-driver -> makerphones/builds/daily-driver   (symlink, resolves within ~/Projects)
```

No files were moved and no paths changed (there are no absolute paths baked into
the repo — verified with `git grep`). You can delete the symlink with
`rm ~/Projects/daily-driver` at any time; the canonical nested path still works.

## The config

Scoped to `~/Projects` **only** (not `$HOME`). Note this exposes *every* project
under `~/Projects` to chat-side review (read-only), not just daily-driver — that's
the intended scope.

```json
{
  "mcpServers": {
    "projects-fs": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-filesystem",
        "/Users/jameywarren/Projects"
      ]
    }
  }
}
```

Pin the version if you want reproducibility:
`"@modelcontextprotocol/server-filesystem@2026.1.14"` (latest at time of writing).

## Read-only — the honest mechanism

The official `@modelcontextprotocol/server-filesystem` has **no `--readonly`
flag**. Its directories are positional arguments, and it always registers write
tools (`write_file`, `edit_file`, `create_directory`, `move_file`) alongside the
read tools. The `readOnly` strings in its source are only advisory
`readOnlyHint` *annotations* on individual tools, not an access mode.

So read-only is enforced **on the client side, by denying the write tools** — not
by the server. After adding the connector, allow only the read tools and deny the
writes:

- **Allow (read):** `read_file`, `read_text_file`, `read_media_file`,
  `list_directory`, `list_directory_with_sizes`, `directory_tree`,
  `search_files`, `get_file_info`, `list_allowed_directories`
- **Deny (write):** `write_file`, `edit_file`, `create_directory`, `move_file`

In Claude Code this is a permissions entry, e.g. in `.claude/settings.json`:

```json
{
  "permissions": {
    "deny": [
      "mcp__projects-fs__write_file",
      "mcp__projects-fs__edit_file",
      "mcp__projects-fs__create_directory",
      "mcp__projects-fs__move_file"
    ]
  }
}
```

In the Claude desktop app, toggle the individual tools off for this connector (or
simply decline any write-tool prompt).

### Switching to read-write later

If you later want chat-side to write too, **remove the deny entries** above (or
re-enable the write tools in the connector's tool list). The server itself needs
no change — it's read-write by default; the lockdown is entirely the client
allow/deny list.

## What you do to enable it

This repo does **not** enable anything. To turn it on (macOS, Claude desktop app):

1. Open the Claude app → **Settings → Developer → Edit Config**. That opens
   `~/Library/Application Support/Claude/claude_desktop_config.json` (create the
   file with `{}` if it doesn't exist yet).
2. Merge the `mcpServers` block above into it (keep any servers already there).
3. **Quit and reopen** the Claude app so it spawns the server.
4. Apply the read-only lockdown (deny the four write tools) as above.
5. In a chat, confirm it's live: ask it to list `~/Projects` — you should see the
   sibling projects and `daily-driver`. The first call may take a few seconds
   while `npx` fetches the server package.

Alternative (Claude Code CLI instead of the desktop app):

```bash
claude mcp add projects-fs -- npx -y @modelcontextprotocol/server-filesystem /Users/jameywarren/Projects
```

then add the same `deny` list to your settings.

### What to expect once it's live

- A new toolset `mcp__projects-fs__*` (read tools only, after the lockdown).
- Read access to the whole of `~/Projects`, including the live daily-driver tree
  at `~/Projects/daily-driver` (or `~/Projects/makerphones/builds/daily-driver`).
- No write ability from chat (by the deny list) — review reads; Claude Code writes.
- Reads reflect the working tree *as saved on disk*, including uncommitted changes.
