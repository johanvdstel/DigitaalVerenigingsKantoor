"""Read-only application/presentation boundary for local duty controls."""
import csv
import re
from dataclasses import dataclass
from datetime import date
from io import StringIO

from .duty_control_selection import SelectionRow, select_population
from .no_show import season_id
from .real_data_import import SportlinkRealDataAdapter, RealDataImportResult

EXPORTS = {
    "leden": ("Leden", "members_path"),
    "functies": ("Functies", "functions_path"),
    "commissies": ("Commissies", "committees_path"),
    "teams": ("Teams", "teams_path"),
    "vrijwilligers_periode": ("Overzicht per periode", "duty_path"),
}
FILTERS = {"Alle": None, "Alleen afwijkingen": "afwijking",
           "Alleen niet betrouwbaar beoordeelbaar": "niet betrouwbaar beoordeelbaar"}
GROUND_TEXT = {
    "no_exemption_found": "Geen vrijstellingsgrond gevonden",
    "personal_function": "Persoonlijke vrijstelling wegens functie",
    "household_function": "Huishoudvrijstelling wegens functie van {name}",
    "honorary": "Vrijstelling als erelid of lid van verdienste",
    "recreational": "Recreatieve deelname",
    "not_playing": "Geen relevante voetbaldeelname",
    "inactive_membership": "Geen actueel lidmaatschap op de peildatum",
    "younger_minor": "Gezinsregel minderjarigen: jonger kind; oudste kwalificerende kind is {name}",
    "oldest_minor": "Gezinsregel minderjarigen: oudste kwalificerende minderjarige",
    "membership_unknown": "Lidmaatschapsinformatie ontbreekt of is onzeker",
    "function_classification_unknown": "Onbekende functieclassificatie",
    "household_function_classification_unknown": "Onbekende functieclassificatie bij huishoudlid {name}",
    "household_membership_unknown": "Onzeker lidmaatschap van huishoudlid {name}",
    "household_address_insufficient": "Onvoldoende of tegenstrijdige adresgegevens voor huishoudvrijstelling met {name}",
    "birth_date_insufficient": "Geboortedatum ontbreekt of is ongeldig",
    "family_data_insufficient": "Onvoldoende gezins- of adresgegevens voor de gezinsregel",
    "family_birth_date_insufficient": "Geboortedatum van mogelijk gezinslid {name} ontbreekt of is ongeldig",
    "family_membership_unknown": "Onzeker lidmaatschap van mogelijk gezinslid {name}",
    "oldest_minor_undetermined": "Oudste kwalificerende minderjarige niet eenduidig vast te stellen met {name}",
}
SIGNAL_TEXT = {
    "MISSING_DUTY_POSITION": "Urenpositie ontbreekt of kan niet betrouwbaar gekoppeld worden",
    "AMBIGUOUS_DUTY_POSITION": "Meerdere urenposities; niet eenduidig beoordeelbaar",
    "INVALID_DUTY_VALUE": "Ongeldige of ontbrekende waarde in de urenpositie",
    "DUTY_REMAINING_MISMATCH": "Aangeleverde resterende uren wijken af van A − B − C − D",
    "REQUIRED_HOURS_REASSESSMENT": "Menselijke herbeoordeling nodig",
    "UNMATCHED_PERSON_REFERENCE": "Bronregel kan niet via relatiecode aan een lid gekoppeld worden",
    "CONFLICTING_DUPLICATE_IDENTITY": "Tegenstrijdige naam of geboortedatum bij dezelfde relatiecode",
    "CONFLICTING_DUPLICATE_MEMBERSHIP": "Tegenstrijdige lidmaatschapsgegevens bij dezelfde relatiecode",
    "INVALID_TERMINATION_DATE": "Ongeldige afmelddatum",
    "INVALID_FUNCTION_DATE": "Ongeldige geldigheidsdatum van een functie",
    "INVALID_COMMITTEE_START_DATE": "Ongeldige begindatum van een commissie",
    "INVALID_COMMITTEE_END_DATE": "Ongeldige einddatum van een commissie",
}


@dataclass(frozen=True)
class DutyControlRow:
    person_id: str
    member: str
    expected: str
    why: str
    registered: str
    status: str


@dataclass(frozen=True)
class DutyControlDashboard:
    rows: tuple[DutyControlRow, ...]
    source: RealDataImportResult
    selection: tuple[SelectionRow, ...] = ()

    @property
    def selection_counts(self):
        return {"Ingelezen unieke leden": len(self.selection), **{label: sum(r.outcome == outcome for r in self.selection)
                for label, outcome in (("Meegenomen", "Meegenomen"), ("Uitgesloten", "Uitgesloten"),
                                       ("Selectieproblemen", "Selectieprobleem"))}}

    def filtered(self, selection="Alle"):
        status = FILTERS[selection]
        return tuple(r for r in self.rows if status is None or r.status == status)

    @property
    def counts(self):
        return {"totaal": len(self.rows), **{status: sum(r.status == status for r in self.rows)
                for status in ("overeenkomst", "afwijking", "niet betrouwbaar beoordeelbaar")}}


def present_controls(source, controls):
    names = {p.person_id: p.name for p in source.persons}
    rows = []
    for control in controls:
        explanations = []
        for ground in control.expectation.grounds:
            name = names.get(ground.supporting_person_id) or "lid met onbekende naam"
            text = GROUND_TEXT.get(ground.code, "Afleidingsgrond vereist nadere beoordeling").format(name=name)
            titles = [getattr(r.source, "role", None) or getattr(r.source, "committee_role", "")
                      for r in ground.registrations]
            if titles:
                text += ": " + ", ".join(dict.fromkeys(titles))
            explanations.append(text)
        for signal in control.signals:
            explanations.append(SIGNAL_TEXT.get(signal.code, signal.message))
        rows.append(DutyControlRow(control.person_id, names.get(control.person_id) or "Naam onbekend",
                    "—" if control.expected_required_hours is None else str(control.expected_required_hours),
                    "; ".join(dict.fromkeys(explanations)),
                    "—" if control.registered_required_hours is None else str(control.registered_required_hours),
                    control.status))
    return DutyControlDashboard(tuple(rows), source)


def suggested_season(as_of: date) -> str:
    return season_id(as_of).replace("/", "-")


def validate_season(value: str) -> str:
    value = value.strip()
    if not re.fullmatch(r"[0-9]{4}-[0-9]{4}", value):
        raise ValueError("Gebruik JJJJ-JJJJ voor het seizoen, bijvoorbeeld 2026-2027.")
    start, end = map(int, value.split("-"))
    if not 1 <= start < 9999 or end != start + 1:
        raise ValueError("Gebruik twee opeenvolgende jaren, bijvoorbeeld 2026-2027.")
    return value


def load_duty_dashboard(exports: dict[str, bytes], *, as_of: date, source_period: str):
    """Use the existing adapter with in-memory text streams; never persist uploads."""
    if not source_period.strip():
        raise ValueError("Vul de periode of het seizoen van Overzicht per periode in.")
    streams = {}
    member_rows = []
    for dataset, (label, argument) in EXPORTS.items():
        if exports.get(dataset) is None:
            raise ValueError(f"Selecteer het bestand {label}.")
        try:
            text = exports[dataset].decode("utf-8-sig")
            rows = SportlinkRealDataAdapter.read_rows_text(text, dataset)
            try:
                delimiter = csv.Sniffer().sniff(text[:8192], delimiters=";,\t").delimiter
            except csv.Error:
                delimiter = ";"
            # Validate CSV syntax without repairing or changing source values.
            list(csv.reader(StringIO(text), delimiter=delimiter, strict=True))
            if any(None in row or any(value is None for value in row.values()) for row in rows):
                raise ValueError("Een bronregel heeft een ander aantal velden dan de kolomkoppen.")
        except UnicodeError:
            raise ValueError(f"{label}: CSV is niet leesbaar als UTF-8. Exporteer opnieuw als UTF-8.") from None
        except (ValueError, csv.Error) as exc:
            message = str(exc).replace("missing columns", "ontbrekende verplichte kolommen")
            raise ValueError(f"{label}: {message}") from None
        streams[argument] = StringIO(text)
        if dataset == "leden":
            member_rows = rows
    try:
        source = SportlinkRealDataAdapter().load_exports(**streams, as_of=as_of, source_period=source_period.strip())
    except (ValueError, csv.Error, TypeError, AttributeError):
        raise ValueError("De CSV's bevatten een onleesbare regel of ongeldige bronwaarde. Controleer de exports, waaronder datums en kolomwaarden.") from None
    selection = select_population(member_rows, source, as_of)
    included = {r.person_id for r in selection if r.outcome == "Meegenomen"}
    # Derive with the complete source context; selection must not remove household evidence.
    dashboard = present_controls(source, tuple(c for c in source.compare_required_hours(as_of)
                                               if c.person_id in included))
    return DutyControlDashboard(dashboard.rows, source, selection)
