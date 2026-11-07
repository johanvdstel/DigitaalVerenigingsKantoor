"""Local file locations only; no CSV transformation or automatic import."""
from __future__ import annotations

import json
import os
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Iterable


EXPORT_FILENAMES = {
    "leden": "Leden.csv",
    "functies": "Functies.csv",
    "commissies": "Commissies.csv",
    "teams": "Teams.csv",
    "vrijwilligers_periode": "Overzicht per periode.csv",
}


class ExportFileError(ValueError):
    """A local export is missing or cannot be read; no substitute is created."""


def _settings_path() -> Path:
    return Path.home() / ".config" / "dvk" / "settings.json"


def default_export_directory() -> Path:
    """Resolve the configured default for all local import entry points."""
    try:
        settings = json.loads(_settings_path().read_text(encoding="utf-8"))
        directory = Path(settings["sportlink_export_directory"])
        if not directory.is_absolute():
            raise ValueError
    except FileNotFoundError:
        return Path.home() / "Development" / "DVK-Data" / "Sportlink-Exports"
    except (OSError, ValueError, KeyError, TypeError):
        raise ExportFileError("De opgeslagen exportmap is niet leesbaar. Sla de locatie opnieuw op via Databronnen.") from None
    return directory


def save_export_directory(value: str) -> Path:
    try:
        directory = Path(value.strip()).expanduser()
        if not directory.is_absolute():
            raise ValueError
        directory = directory.resolve(strict=True)
        with os.scandir(directory) as entries:
            next(entries, None)
        if not os.access(directory, os.R_OK | os.X_OK):
            raise PermissionError
    except (OSError, ValueError, RuntimeError):
        raise ExportFileError("Kies een bestaande, toegankelijke exportmap met een volledig pad of een pad dat begint met ~/.") from None

    settings = _settings_path()
    temporary = None
    try:
        settings.parent.mkdir(parents=True, exist_ok=True)
        with NamedTemporaryFile(mode="w", encoding="utf-8", dir=settings.parent, delete=False) as handle:
            temporary = Path(handle.name)
            json.dump({"sportlink_export_directory": str(directory)}, handle)
        temporary.replace(settings)
        temporary = None
    except OSError:
        raise ExportFileError("De exportmap kon niet worden opgeslagen in de lokale DVK-instellingen.") from None
    finally:
        if temporary is not None:
            try:
                temporary.unlink(missing_ok=True)
            except OSError:
                pass
    return directory


def export_path(dataset: str, explicit_path: str | Path | None = None) -> Path:
    if explicit_path is not None:
        return Path(explicit_path)
    return default_export_directory() / EXPORT_FILENAMES[dataset]


def export_location_hint(datasets: Iterable[str] = EXPORT_FILENAMES) -> str:
    names = ", ".join(EXPORT_FILENAMES[dataset] for dataset in datasets)
    try:
        directory = default_export_directory()
    except ExportFileError as exc:
        return str(exc)
    return (f"Ingestelde exportmap: {directory}. Verwachte bestanden: {names}. "
            "Gebruik Brongegevens vernieuwen na het vervangen van exports.")


def read_export_text(dataset: str, explicit_path: str | Path | None = None) -> str:
    path = export_path(dataset, explicit_path)
    try:
        if not path.is_file():
            path.stat()  # Preserve the distinction between missing and unreadable.
            raise OSError
        return path.read_text(encoding="utf-8-sig")
    except FileNotFoundError:
        raise ExportFileError(
            f"Bestand '{path.name}' ontbreekt. Verwachte locatie: {path.absolute()}. "
            "Plaats de betreffende Sportlink-export daar."
        ) from None
    except (OSError, UnicodeError):
        raise ExportFileError(
            f"Bestand '{path.name}' is niet leesbaar op {path.absolute()}. "
            "Controleer de leesrechten en UTF-8-export en plaats de betreffende Sportlink-export daar."
        ) from None
