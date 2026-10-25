"""One local source input boundary for prototype functions; no background polling."""
from dataclasses import dataclass
from datetime import datetime
from .sportlink_exports import EXPORT_FILENAMES, read_export_text
from .real_data_import import SportlinkRealDataAdapter


@dataclass(frozen=True)
class LoadedLocalExports:
    exports: dict[str, bytes]
    loaded_at: datetime
    filenames: tuple[str, ...]


@dataclass(frozen=True)
class LocalDutyControl:
    dashboard: object
    sources: LoadedLocalExports


class LocalCsvSourceApplicationService:
    def load(self):
        exports = {dataset: read_export_text(dataset).encode("utf-8") for dataset in EXPORT_FILENAMES}
        return LoadedLocalExports(exports, datetime.now().astimezone(), tuple(EXPORT_FILENAMES.values()))

    def duty_control(self, *, as_of, source_period):
        from .duty_control_presenter import load_duty_dashboard
        sources = self.load()
        return LocalDutyControl(load_duty_dashboard(sources.exports, as_of=as_of,
                                                   source_period=source_period), sources)

    def volunteer_persons(self):
        # Synchronization needs only Leden.csv; retain the existing name validation.
        return SportlinkRealDataAdapter.read_volunteer_persons(read_export_text("leden"))
