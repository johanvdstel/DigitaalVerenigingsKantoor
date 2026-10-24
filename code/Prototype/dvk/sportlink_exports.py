"""Local file locations only; no CSV transformation or automatic import."""
from __future__ import annotations

from pathlib import Path
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


def default_export_directory() -> Path:
    return Path.home() / "Documents" / "DVK-Sportlink-exports"


def export_path(dataset: str, explicit_path: str | Path | None = None) -> Path:
    if explicit_path is not None:
        return Path(explicit_path)
    return default_export_directory() / EXPORT_FILENAMES[dataset]


def export_location_hint(datasets: Iterable[str] = EXPORT_FILENAMES) -> str:
    names = ", ".join(EXPORT_FILENAMES[dataset] for dataset in datasets)
    return (f"Standaardmap: {default_export_directory()}. Verwachte bestanden: {names}. "
            "Plaats hier handmatig vernieuwde Sportlink-exports en selecteer ze via de bestaande upload; "
            "DVK haalt deze CSV-bestanden niet automatisch op.")


def read_export_text(dataset: str, explicit_path: str | Path | None = None) -> str:
    path = export_path(dataset, explicit_path)
    try:
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
