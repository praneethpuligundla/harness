# Agent Harness Plugin for Claude Code

A Claude Code plugin implementing Anthropic's engineering best practices for effective long-running agent workflows.

## Overview

Long-running AI agents struggle across multiple context windows because each new session begins without memory of prior work. This plugin solves that problem by providing:

- **Progress Tracking** - Persistent log file (`claude-progress.txt`) that records accomplishments
- **Feature Checklists** - JSON file (`claude-features.json`) tracking feature status
- **Git Checkpoints** - Encourages frequent commits as safe recovery points
- **Session Startup Routine** - Automatically reads context at session start
- **Session End Reminders** - Prompts to commit work and update progress

Based on: [Effective Harnesses for Long-Running Agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)

## Installation

### Option 1: Install from GitHub (Recommended)

```bash
# In Claude Code, run:
/install-plugin https://github.com/praneethpuligundla/agent-harness
```

### Option 2: Manual Installation

1. Clone this repository:
```bash
git clone https://github.com/praneethpuligundla/agent-harness.git ~/.claude/plugins/agent-harness
```

2. Add to your Claude Code settings (`~/.claude/settings.json`):
```json
{
  "plugins": {
    "agent-harness": {
      "path": "~/.claude/plugins/agent-harness"
    }
  }
}
```

3. Restart Claude Code

## Quick Start

### 1. Initialize a Project

```
/harness:init
```

This creates:
- `claude-progress.txt` - Progress log
- `claude-features.json` - Feature checklist
- `.claude/.claude-harness-initialized` - Marker file
- Optionally: `init.sh` - Startup script

### 2. Add Features to Track

```
/harness:feature add User authentication - Login, logout, session management
/harness:feature add API endpoints - REST API for data access
/harness:feature add Frontend dashboard - Main UI components
```

### 3. Start Working on Features

```
/harness:feature start 1
/harness:log started User authentication
```

### 4. Create Checkpoints

```
/harness:checkpoint Implemented login form and validation
```

### 5. Complete Features

```
/harness:feature pass 1
/harness:log completed User authentication with tests passing
```

## Commands

| Command | Description |
|---------|-------------|
| `/harness:init` | Initialize harness for project |
| `/harness:status` | Show current status (git, progress, features) |
| `/harness:log [type] [message]` | Add progress entry |
| `/harness:feature [action] [args]` | Manage features |
| `/harness:checkpoint [message]` | Create git checkpoint |

### Progress Log Entry Types

```
/harness:log started [task]      # Beginning work
/harness:log completed [task]    # Finished task
/harness:log checkpoint [msg]    # Git commit
/harness:log note [message]      # Observation
/harness:log blocker [issue]     # Problem
```

### Feature Management

```
/harness:feature add [name] - [description]  # Add new feature
/harness:feature start [id]                   # Mark as in_progress
/harness:feature pass [id]                    # Mark as passing
/harness:feature fail [id]                    # Mark as failing
/harness:feature list                         # List all features
/harness:feature next                         # Show next priorities
```

## How It Works

### Session Start Hook

When a Claude Code session starts in an initialized project:
1. Reads git log for recent commits
2. Reads progress file for context
3. Summarizes feature checklist status
4. Injects this context into the session

This ensures Claude has full context of prior work.

### Session Stop Hook

When Claude stops responding:
1. Reminds to update progress file
2. Suggests committing work as checkpoint
3. Encourages merge-ready state

### Feature Status Flow

```
failing -> in_progress -> passing
   ^           |
   +-----------+
   (if needs more work)
```

All features start as "failing" per Anthropic's guidance - this prevents premature completion claims.

## File Structure

### In Your Project
```
your-project/
├── claude-progress.txt      # Progress log
├── claude-features.json     # Feature checklist
├── init.sh                  # Optional startup script
└── .claude/
    └── .claude-harness-initialized  # Marker file
```

### Plugin Structure
```
agent-harness/
├── .claude-plugin/
│   └── plugin.json          # Plugin metadata
├── commands/
│   ├── init.md              # /harness:init
│   ├── status.md            # /harness:status
│   ├── log.md               # /harness:log
│   ├── feature.md           # /harness:feature
│   └── checkpoint.md        # /harness:checkpoint
├── hooks/
│   ├── hooks.json           # Hook configuration
│   ├── session_start.py     # Session startup
│   └── stop.py              # Session end
├── skills/
│   └── harness-workflow.md  # Workflow guidance
├── core/
│   ├── features.py          # Feature utilities
│   └── progress.py          # Progress utilities
└── README.md
```

## Best Practices

### 1. Initialize Early
Set up the harness at the start of any significant project.

### 2. Be Specific with Features
Each feature should be:
- Testable
- Well-defined
- Appropriately scoped

Break large features into smaller ones.

### 3. Commit Often
Each commit is a recovery point. Create checkpoints:
- After completing any sub-task
- Before trying risky changes
- At natural stopping points

### 4. Log Everything
Future sessions depend on this context. Log:
- What was accomplished
- What blocked progress
- Important decisions
- Next steps

### 5. Verify Before Marking Complete
Only mark features as "passing" when:
- Tests pass
- Manual verification done
- Code is merge-ready

## Example Workflow

```
# Session 1 - Project Setup
/harness:init

# Add all features upfront
/harness:feature add User login - Email/password authentication
/harness:feature add User registration - Sign up with email verification
/harness:feature add Password reset - Forgot password flow
/harness:feature add User profile - View and edit profile

# Start first feature
/harness:feature start 1
/harness:log started User login implementation

# ... work on feature ...
/harness:checkpoint Implemented login form UI

# ... more work ...
/harness:checkpoint Added authentication API integration

# Complete feature
/harness:feature pass 1
/harness:log completed User login - all tests passing

# Session 2 - Continues with context
/harness:status
# Shows: Login complete, next is registration

/harness:feature start 2
# ... continue working ...
```

## Troubleshooting

### Commands not recognized?
- Restart Claude Code after installation
- Verify plugin is in correct location
- Check `~/.claude/settings.json` for plugin configuration

### Session hooks not firing?
- Ensure `.claude/.claude-harness-initialized` exists
- Run `/harness:init` if not initialized
- Check Python 3 is available in PATH

### Features not updating?
- Check `claude-features.json` exists and is valid JSON
- Verify file permissions

## Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Credits

Based on engineering practices from [Anthropic](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents).
