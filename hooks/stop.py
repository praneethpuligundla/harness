#!/usr/bin/env python3
"""Stop hook for agent-harness plugin.

This hook runs when Claude stops responding and:
1. Reminds to update progress file
2. Suggests committing work as a checkpoint
3. Ensures work is left in merge-ready state
"""

import os
import sys
import json
import subprocess
from pathlib import Path

PROGRESS_FILE = "claude-progress.txt"
INIT_MARKER = ".claude-harness-initialized"


def get_working_directory():
    """Get the working directory from environment."""
    return os.environ.get('CLAUDE_WORKING_DIRECTORY', os.getcwd())


def check_harness_initialized(path):
    """Check if harness has been initialized."""
    marker_path = Path(path) / '.claude' / INIT_MARKER
    return marker_path.exists()


def has_uncommitted_changes(path):
    """Check if there are uncommitted changes."""
    try:
        result = subprocess.run(
            ['git', 'status', '--porcelain'],
            cwd=path,
            capture_output=True,
            text=True,
            timeout=5
        )
        return bool(result.stdout.strip())
    except Exception:
        return False


def get_progress_file_updated_recently(path):
    """Check if progress file was updated in the last operation."""
    progress_path = Path(path) / PROGRESS_FILE
    if not progress_path.exists():
        return False

    try:
        # Check if it's been modified (part of uncommitted changes)
        result = subprocess.run(
            ['git', 'status', '--porcelain', PROGRESS_FILE],
            cwd=path,
            capture_output=True,
            text=True,
            timeout=5
        )
        return bool(result.stdout.strip())
    except Exception:
        return False


def build_stop_message(work_dir, input_data):
    """Build reminder message for session stop."""
    if not check_harness_initialized(work_dir):
        return {}

    messages = []
    stop_reason = input_data.get('stopReason', 'unknown')

    # Only provide reminders for normal stops (not errors/interrupts)
    if stop_reason not in ('end_turn', 'stop_sequence'):
        return {}

    has_changes = has_uncommitted_changes(work_dir)
    progress_updated = get_progress_file_updated_recently(work_dir)

    if has_changes:
        messages.append("[Agent Harness Checkpoint Reminder]")

        if not progress_updated:
            messages.append("- Consider updating claude-progress.txt with what was accomplished")

        messages.append("- Consider creating a git commit checkpoint with a descriptive message")
        messages.append("- Ensure code is left in a merge-ready state")

    if messages:
        return {"systemMessage": '\n'.join(messages)}

    return {}


def main():
    """Main entry point for Stop hook."""
    try:
        input_data = json.load(sys.stdin)
        work_dir = get_working_directory()
        result = build_stop_message(work_dir, input_data)
        print(json.dumps(result), file=sys.stdout)

    except Exception as e:
        print(json.dumps({}), file=sys.stdout)

    finally:
        sys.exit(0)


if __name__ == '__main__':
    main()
