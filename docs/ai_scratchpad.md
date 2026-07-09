## [2026-04-10] Session Note

### Mistake
- No prior scratchpad file existed, so project memory could not be consulted.

### Correction
- Create the scratchpad file and keep concise pattern notes here going forward.

### Lesson
- Check for the scratchpad early and initialize it if the project instructions require it.

### Preference (if any)
- Podcast notes in `show-notes` should be stored as direct markdown with real frontmatter, not fenced embedded markdown.

### Action Rule
- When fixing or adding notes in `show-notes`, ensure YAML frontmatter is top-level and never wrapped in code fences.

## [2026-06-21] Session Note

### Mistake
- Initially interpreted cron run "error" status as a complete failure; the run had actually completed all substantive work (file creation + git commit + push) and only failed on a non-critical post-processing tool call ("Update Goal: complete failed").

### Correction
- After seeing an error status on a cron run, check the actual filesystem and git log before concluding the run was a total failure. The `status: error` field can reflect a minor tool failure at the end of an otherwise successful run.

### Lesson
- `openclaw cron runs` `status: error` does not always mean the agent's work product is missing. Cross-reference with: (1) output files on disk, (2) git log, (3) token usage / duration. A long run (285s, 19K output tokens) with a short error message from a single tool is likely a partial success.

### Preference (if any)
- User approved running the Pleros cron manually to catch up on backlog rather than waiting for the next scheduled run.

### Action Rule
- When a cron run shows `status: error` but has substantial duration and token usage, verify filesystem + git before reporting failure.
- Transient "LLM request failed: network connection error" errors affecting ALL cron jobs simultaneously indicate an endpoint outage, not a config problem. Verify with a smoke test (`openclaw agent --agent main --model <id> -m 'test'`) before changing config.
- VTT files downloaded by the Pleros cron persist in `/tmp/pleros_ep*.en.vtt` across runs; a re-run will reuse or re-download them.

## [2026-06-23] Session Note — Telegram Bot Not Responding

### Mistake
- Spent time trying to re-pair via `/pair` command before checking if the pairing system itself was functional. The `/pair` command failed with "missing scope: operator.pairing" because the gateway had scope errors after the update.

### Correction
- User wanted to re-pair but the pairing system was broken post-update. Switched `dmPolicy` from `"pairing"` to `"open"` and added `"allowFrom": ["*"]` to unblock immediately.

### Lesson
- `dmPolicy: "open"` requires `"allowFrom": ["*"]` in the Telegram config. Without `allowFrom`, ALL DMs are dropped silently with only a config warning at startup. The bot receives messages (logs show "Inbound message") but the agent is never invoked.
- The Telegram polling 409 conflict ("terminated by other getUpdates request") was caused by the health monitor restarting the poller every 10-15 min while the old connection was still alive. Updating to 2026.6.9 + gateway restart fixed this.
- Stale ingress spool files in `~/.openclaw/telegram/ingress-spool-default/` (7 days old, 9 files) were blocking message processing. Clearing them was necessary but not sufficient — the `dmPolicy`/`allowFrom` config was the real blocker.
- The `openclaw update` command automatically stops the gateway, updates, and restarts it. No manual gateway restart needed after update.

### Preference (if any)
- User preferred re-pairing over switching to open DM policy, but accepted the open policy when pairing was broken.

### Action Rule
- When Telegram bot receives messages but doesn't respond: (1) check startup logs for config warnings about `dmPolicy`/`allowFrom`, (2) check `~/.openclaw/telegram/ingress-spool-default/` for stale files, (3) verify `dmPolicy` matches the `allowFrom` configuration.
- After OpenClaw updates, always check gateway startup logs for scope errors (`missing scope: operator.read`) which indicate broken pairing/auth systems.
- The `openclaw pairing list --channel telegram` command requires the gateway to have proper scopes. If it returns "No pending" but `/pair` fails on the bot side, the pairing system itself is broken — fall back to `dmPolicy: "open"`.

## [2026-07-09] Session Note

### Mistake
- Used `suggested_create` for a scheduled digest/reminder and described it as set up, but no automation was actually installed.

### Correction
- Verified `~/.codex/automations` was empty, then created the cron and heartbeat automations with `mode: create`.

### Lesson
- Suggested automation cards are not active jobs until accepted. When the user expects a scheduled task to exist, create it directly or clearly say it is only a suggestion.

### Preference (if any)
- Daily Obsidian founder digest should exclude Pleros and church-history material initially, run at 8:00 AM Africa/Lagos, and send a ChatGPT/Codex reminder around 8:05 AM.

### Action Rule
- After creating or suggesting automations, verify whether an automation file/id exists before telling the user it is set up.

## [2026-07-09] Session Note

### Mistake
- No mistake; user clarified preferred transcript-fetching workflow for podcast-note processing.

### Correction
- When processing YouTube links for podcast notes, first try `yt-dlp` to fetch transcripts/captions before asking the user to paste raw notes.

### Lesson
- Podcast-note processing should use available local retrieval tooling before falling back to manual transcript input.

### Preference (if any)
- User prefers `yt-dlp` as the first attempt for YouTube transcript fetching.

### Action Rule
- For YouTube podcast-note links, run `yt-dlp` transcript/caption retrieval first; ask for pasted transcript only if `yt-dlp` cannot retrieve usable captions/transcript.

## [2026-07-09] Session Note

### Mistake
- No mistake; user clarified preferred interaction surface for podcast-note workflow.

### Correction
- User wants to be able to talk to the assistant from their phone, especially for lightweight capture such as sending podcast links.

### Lesson
- Separate capture from processing: mobile should be used for sending links/instructions, while local Codex/Mac handles transcript fetching and vault writes.

### Preference (if any)
- Phone-based interaction is preferred for quick podcast-note requests.

### Action Rule
- When designing or discussing podcast-note workflows, favor a mobile-friendly intake path where the user can paste links from their phone and the assistant processes them into the local Obsidian vault.

## [2026-07-09] Session Note

### Mistake
- Podcast notes had been created from online summaries rather than actual YouTube transcripts.

### Correction
- User asked to fix those notes by pulling actual transcripts with `yt-dlp` and reprocessing, while retaining useful material from the existing notes.

### Lesson
- Summary-derived notes can look plausible but miss transcript-specific arguments, sequence, and examples.

### Preference (if any)
- When repairing or improving existing podcast notes, preserve useful structure, coaching, action items, and wikilinks if they still fit the source.

### Action Rule
- For existing YouTube podcast notes, verify whether the note was transcript-grounded; if not, retrieve captions/transcripts with `yt-dlp`, rebuild the content from the actual transcript, and merge in useful prior material rather than blindly replacing everything.

## [2026-07-09] Session Note

### Mistake
- Finished vault edits without immediately committing and pushing.

### Correction
- User instructed to always commit and push after work.

### Lesson
- For this vault, completing work includes version-control publication unless the user explicitly says not to.

### Preference (if any)
- User wants changes committed and pushed after work.

### Action Rule
- After making meaningful changes in the vault, stage only the files touched for the task, commit with a clear message, and push to the configured remote before reporting completion.
