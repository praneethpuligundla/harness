#!/usr/bin/env python3
"""SessionStart hook for agent-harness plugin.

This hook runs at the start of each Claude Code session and:
1. Checks if harness is initialized for the current project
2. Reads git log for recent commits
3. Reads progress file for context
4. Reads feature checklist status
5. Injects context into the session via systemMessage
"""

import os
import sys
import json
import subprocess
from datetime import datetime
from pathlib import Path

# Constants
PROGRESS_FILE = "claude-progress.txt"
FEATURES_FILE = "claude-features.json"
INIT_MARKER = ".claude-harness-initialized"


def get_working_directory():
    """Get the working directory from environment or input."""
    return os.environ.get('CLAUDE_WORKING_DIRECTORY', os.getcwd())


def is_git_repo(path):
    """Check if path is inside a git repository."""
    try:
        result = subprocess.run(
            ['git', 'rev-parse', '--is-inside-work-tree'],
            cwd=path,
            capture_output=True,
            text=True,
            timeout=5
        )
        return result.returncode == 0
    except Exception:
        return False


def get_git_log(path, num_commits=10):
    """Get recent git commits."""
    try:
        result = subprocess.run(
            ['git', 'log', f'-{num_commits}', '--oneline', '--no-decorate'],
            cwd=path,
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            return result.stdout.strip()
        return None
    except Exception:
        return None


def get_git_status(path):
    """Get git status summary."""
    try:
        result = subprocess.run(
            ['git', 'status', '--short'],
            cwd=path,
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            return result.stdout.strip()
        return None
    except Exception:
        return None


def read_progress_file(path):
    """Read the progress tracking file."""
    progress_path = Path(path) / PROGRESS_FILE
    if progress_path.exists():
        try:
            content = progress_path.read_text()
            # Return last 50 lines to avoid overwhelming context
            lines = content.strip().split('\n')
            if len(lines) > 50:
                return '\n'.join(['[...truncated...]'] + lines[-50:])
            return content
        except Exception:
            return None
    return None


def read_features_file(path):
    """Read and summarize the features checklist."""
    features_path = Path(path) / FEATURES_FILE
    if features_path.exists():
        try:
            with open(features_path, 'r') as f:
                features = json.load(f)

            # Count statuses
            total = len(features.get('features', []))
            passing = sum(1 for f in features.get('features', []) if f.get('status') == 'passing')
            failing = sum(1 for f in features.get('features', []) if f.get('status') == 'failing')
            in_progress = sum(1 for f in features.get('features', []) if f.get('status') == 'in_progress')

            # Get next priority items
            next_items = [
                f for f in features.get('features', [])
                if f.get('status') in ('failing', 'in_progress')
            ][:5]

            summary = {
                'total': total,
                'passing': passing,
                'failing': failing,
                'in_progress': in_progress,
                'next_items': next_items
            }
            return summary
        except Exception:
            return None
    return None


def check_harness_initialized(path):
    """Check if harness has been initialized for this project."""
    marker_path = Path(path) / '.claude' / INIT_MARKER
    return marker_path.exists()


def build_context_message(work_dir):
    """Build the context message for session startup."""
    messages = []

    # Check if harness is initialized
    if not check_harness_initialized(work_dir):
        return {
            "systemMessage": (
                "[Agent Harness] This project has not been initialized with the agent harness. "
                "Run `/harness:init` to set up progress tracking, feature checklists, and git checkpoints. "
                "This enables effective long-running agent workflows."
            )
        }

    messages.append("=== AGENT HARNESS SESSION STARTUP ===")
    messages.append(f"Session started: {datetime.now().isoformat()}")
    messages.append(f"Working directory: {work_dir}")
    messages.append("")

    # Git status and log
    if is_git_repo(work_dir):
        messages.append("--- GIT STATUS ---")
        git_status = get_git_status(work_dir)
        if git_status:
            messages.append(git_status if git_status else "(clean)")
        else:
            messages.append("(clean)")
        messages.append("")

        messages.append("--- RECENT COMMITS ---")
        git_log = get_git_log(work_dir)
        if git_log:
            messages.append(git_log)
        else:
            messages.append("(no commits)")
        messages.append("")

    # Progress file
    progress = read_progress_file(work_dir)
    if progress:
        messages.append("--- PROGRESS LOG ---")
        messages.append(progress)
        messages.append("")

    # Features checklist
    features = read_features_file(work_dir)
    if features:
        messages.append("--- FEATURE CHECKLIST STATUS ---")
        messages.append(f"Total: {features['total']} | Passing: {features['passing']} | Failing: {features['failing']} | In Progress: {features['in_progress']}")
        if features['next_items']:
            messages.append("")
            messages.append("Next priority items:")
            for item in features['next_items']:
                status_icon = "[IN PROGRESS]" if item.get('status') == 'in_progress' else "[FAILING]"
                messages.append(f"  {status_icon} {item.get('name', 'Unnamed')}: {item.get('description', '')[:60]}")
        messages.append("")

    messages.append("=== END SESSION CONTEXT ===")
    messages.append("")
    messages.append("IMPORTANT: Review the above context before starting work. "
                   "Select the highest-priority incomplete feature and update the progress log as you work.")

    return {"systemMessage": '\n'.join(messages)}


def main():
    """Main entry point for SessionStart hook."""
    try:
        # Read input from stdin (contains session info)
        input_data = json.load(sys.stdin)

        # Get working directory
        work_dir = get_working_directory()

        # Build and output context message
        result = build_context_message(work_dir)
        print(json.dumps(result), file=sys.stdout)

    except Exception as e:
        # On error, output informative message but don't block
        error_output = {
            "systemMessage": f"[Agent Harness] Session startup check failed: {str(e)}"
        }
        print(json.dumps(error_output), file=sys.stdout)

    finally:
        sys.exit(0)


if __name__ == '__main__':
    main()
