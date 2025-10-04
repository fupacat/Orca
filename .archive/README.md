# Archive Directory

This directory contains completed workflow artifacts, execution runs, and implementation plans that have been archived to keep the project root clean.

## Structure

### `workflows/`
Completed Orca workflow artifacts organized by project/feature:
- Each workflow run produces: `discovery.md`, `requirements.md`, `tasks.md`, `architecture.md`, `review.md`, `plan.md`
- Organized by feature name and date

### `executions/`
Completed Orca execution runs:
- Moved from `.orca/executions/` after completion
- Contains execution logs, task results, and summaries

### `plans/`
Standalone implementation plans:
- Independent implementation plans not part of full workflows
- Historical reference for architectural decisions

## Archiving Process

### Manual Archive
```bash
# Archive a completed workflow
bash scripts/archive-workflow.sh <workflow_name>
```

### Automatic Archive
The post-merge git hook suggests archiving when:
- PR merged to develop/main
- Workflow artifacts detected in root
- Execution completes successfully

## Retrieval

All archived files remain in git history and can be referenced for:
- Historical context
- Decision documentation
- Template examples
- Audit trail

Archived files are gitignored by pattern but can be force-added if needed for important reference.
