"""Identify the checkout containing the launched app, independently of shell cwd."""
from pathlib import Path
import subprocess


def active_application_version(application_file):
    application = Path(application_file).resolve()

    def git(*args):
        return subprocess.run(
            ["git", "-C", str(application.parent), *args], check=True,
            capture_output=True, text=True, timeout=3,
        ).stdout.strip()

    try:
        root = Path(git("rev-parse", "--show-toplevel")).resolve()
        relative = application.relative_to(root)
        git("-C", str(root), "ls-files", "--error-unmatch", "--", relative.as_posix())
        commit = git("rev-parse", "--short=12", "HEAD")
        branch = git("rev-parse", "--abbrev-ref", "HEAD")
        dirty = bool(git("status", "--porcelain", "--untracked-files=normal"))
    except (OSError, ValueError, subprocess.SubprocessError):
        return "Actieve codeversie: versie-informatie niet beschikbaar"
    state = " · lokale wijzigingen" if dirty else ""
    return f"Actieve codeversie: {branch} · {commit}{state} · {root}"
