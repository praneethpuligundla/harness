---
description: Guidelines for effective long-running agent workflows with progress tracking, git checkpoints, and feature checklists
triggers:
  - long-running task
  - multi-session work
  - complex feature implementation
  - project initialization
  - tracking progress
---

# Long-Running Agent Harness Workflow

This skill provides guidance for effective long-running agent workflows based on Anthropic's engineering best practices.

## Core Principles

### 1. Session Context Continuity
Each session starts without memory of prior work. The harness provides context through:
- `claude-progress.txt` - Log of what was accomplished
- `claude-features.json` - Checklist of features and their status
- Git history - Commits as checkpoints

### 2. Feature-First Development
- All features start as "failing"
- Work on one feature at a time
- Mark as "passing" only when fully complete and tested
- Never remove or edit tests to make them pass

### 3. Checkpoint Discipline
- Commit frequently with descriptive messages
- Leave code in merge-ready state
- Log checkpoints to progress file
- Each commit should be a safe recovery point

## Session Startup Routine

At the start of each session:
1. Read git log to understand recent changes
2. Read `claude-progress.txt` for context
3. Check `claude-features.json` for next priority
4. Run `init.sh` if it exists (starts dev server, etc.)
5. Run baseline tests before making changes

## During Development

### Before Starting a Feature
```
/harness:feature start [feature-id]
/harness:log started [feature-name]
```

### While Working
- Make incremental changes
- Test frequently
- Create checkpoints for significant progress:
```
/harness:checkpoint [description of progress]
```

### After Completing a Feature
```
/harness:feature pass [feature-id]
/harness:log completed [feature-name]
/harness:checkpoint [final implementation description]
```

## Commands Reference

| Command | Description |
|---------|-------------|
| `/harness:init` | Initialize harness for project |
| `/harness:status` | Show current status |
| `/harness:log [type] [message]` | Add progress entry |
| `/harness:feature [action] [args]` | Manage features |
| `/harness:checkpoint [message]` | Create git checkpoint |

## Progress Log Entry Types

- `started` - Beginning work on a task
- `completed` - Finished a task
- `checkpoint` - Git commit created
- `note` - General observations
- `blocker` - Issues preventing progress

## Feature Statuses

- `failing` - Not yet implemented (default)
- `in_progress` - Currently being worked on
- `passing` - Complete and verified

## Best Practices

1. **Be Specific with Features**
   - Each feature should be testable
   - Include acceptance criteria
   - Break large features into smaller ones

2. **Document Blockers**
   - Log any issues preventing progress
   - Include context for future sessions

3. **Verify Before Marking Complete**
   - Run tests
   - Check manually if needed
   - Use browser automation for UI features

4. **Leave Clear Handoff Notes**
   - What was accomplished
   - What's next
   - Any known issues

## Example Workflow

```
# Session 1
/harness:init
# Add features...
/harness:feature add User login - Email/password authentication
/harness:feature add User registration - Sign up with email verification
/harness:feature start 1
/harness:log started User login implementation
# ... work on feature ...
/harness:checkpoint Implemented login form and basic validation
# ... more work ...
/harness:feature pass 1
/harness:log completed User login with tests passing
/harness:checkpoint Completed user login feature

# Session 2 (reads context automatically)
/harness:status
# Shows: Login complete, registration next
/harness:feature start 2
# ... continue working ...
```
