# Pipeline Management Skill

Automates content ingestion and maintenance workflows.

## Tools Used
- `process_file` — Analyze → route → index → memory pipeline
- `watch_inbox` — Scan inbox for new files
- `rebuild_index` — Rebuild FAISS + SQLite index
- `run_maintenance` — Full maintenance run
- `run_backup` — Workspace backup

## Workflows
### Ingest New Content
1. Call `watch_inbox` to find new files
2. For each file, call `process_file`
3. Return processing summary

### Run Maintenance
1. Call `rebuild_index`
2. Call `run_maintenance`
3. Return status
