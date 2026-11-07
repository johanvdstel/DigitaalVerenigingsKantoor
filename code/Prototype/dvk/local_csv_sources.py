"""One local source input boundary for prototype functions; no background polling."""
from dataclasses import dataclass, replace
from datetime import datetime
from pathlib import Path
from .sportlink_exports import EXPORT_FILENAMES, read_export_text, default_export_directory, ExportFileError
from .real_data_import import SportlinkRealDataAdapter
from .historical_backlog import HISTORICAL_FILENAME, import_historical_backlog, unavailable_history


@dataclass(frozen=True)
class LoadedLocalExports:
    exports: dict[str, bytes]
    loaded_at: datetime
    filenames: tuple[str, ...]
    directory: Path | None = None


@dataclass(frozen=True)
class LocalDutyControl:
    dashboard: object
    sources: LoadedLocalExports


class LocalCsvSourceApplicationService:
    def __init__(self):
        self._directory = None

    @property
    def directory(self) -> Path:
        if self._directory is None:
            self._directory = default_export_directory()
        return self._directory

    def availability(self):
        """Check current file access without importing or validating contents."""
        sources = (*EXPORT_FILENAMES.values(), HISTORICAL_FILENAME)
        folder = self.directory
        rows = {}
        for name in sources:
            path = folder / name
            try:
                if not path.is_file():
                    path.stat()
                    raise OSError
                with path.open("rb"):
                    rows[name] = "Aanwezig en toegankelijk"
            except FileNotFoundError:
                rows[name] = "Ontbreekt"
            except OSError:
                rows[name] = "Niet leesbaar"
        return rows

    def historical_backlog(self, *, person_ids):
        # Deliberately separate from load(): duty control still needs only five files.
        try:
            text = read_export_text("vrijwilligers_periode", self.directory / HISTORICAL_FILENAME)
        except ExportFileError as exc:
            return unavailable_history(f"Historische urenbron: {exc}")
        return replace(import_historical_backlog(text, person_ids),
                       loaded_at=datetime.now().astimezone())

    def read_members(self) -> str:
        return read_export_text("leden", self.directory / EXPORT_FILENAMES["leden"])

    def load(self, *, members_text=None):
        directory = self.directory
        exports = {dataset: (members_text if dataset == "leden" and members_text is not None
                             else read_export_text(dataset, directory / filename)).encode("utf-8")
                   for dataset, filename in EXPORT_FILENAMES.items()}
        return LoadedLocalExports(exports, datetime.now().astimezone(), tuple(EXPORT_FILENAMES.values()), directory)

    def duty_control(self, *, as_of, source_period):
        from .duty_control_presenter import load_duty_dashboard
        sources = self.load()
        return LocalDutyControl(load_duty_dashboard(sources.exports, as_of=as_of,
                                                   source_period=source_period), sources)

    def volunteer_persons(self, *, members_text=None):
        # Synchronization needs only Leden.csv; retain the existing name validation.
        text = self.read_members() if members_text is None else members_text
        return SportlinkRealDataAdapter.read_volunteer_persons(text)
