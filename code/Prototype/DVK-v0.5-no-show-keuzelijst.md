# PR #38 — complete, begrijpelijk gesorteerde No-Show-keuzelijst

Uitgangscommit: `a20380ccf93ce852ac92261c865ce27707fcf948`, bestaande werkbranch `codex/vrijwilligers-planning-integratie`, doel `prototype-v0.5`. Ontwerpbaseline: BL-16 / PR #39; functionele acceptatie van de nieuwe sessiebediening is nog gaande. De releasebaseline blijft v0.4 op main. Aanleiding is de expliciete correctieopdracht bij lokale BL-16-acceptatie stap 21.

Vastgesteld: `available_assignments()` en `assignment_contexts()` hadden beide een standaardlimiet van 50. De onderliggende opslag retourneerde de boekingen op aflopende invoervolgorde, zonder functionele sortering. Daardoor ontbraken geschikte boekingen en was de presentatievolgorde onbegrijpelijk.

De minimale correctie in `dvk/application_services.py` maakt beide standaardquery's onbeperkt (`limit=None`). De bestaande mogelijkheid om voor een expliciete aanroeper een kleinere selectie te vragen blijft beschikbaar; Streamlit geeft geen limiet mee en ontvangt dus alle geschikte boekingen. Eerst wordt gefilterd met de bestaande actieve-bron-, periode- en identiteitscontroles. Daarna volgt oplopende sortering op Nederlandse lokale datum, lokale begintijd, dienstomschrijving, originele Sportlink-vrijwilligersnaam en uitsluitend als laatste de stabiele boekingssleutel. Er is geen nieuwe naamnormalisatie, persoonskoppeling of wijziging van zichtbare selectielabels.

De hercontrole van actieve sessie/bronrevisie tijdens selectie en daadwerkelijke registratie blijft ongewijzigd. Geen wijziging van synchronisatie, sancties, intrekkingen, database, schema, UI of bezettingsberekening. Er zijn geen echte CKC-gegevens of bestaande lokale databases gelezen.

Gewijzigde tests:

- `tests/test_no_show_choices_v05.py`: acht synthetische gevallen voor 73 geschikte boekingen naast ongeschikte boekingen, beide aanlevervolgordes, meerdere dagen/diensten/tijden/namen, laatste technische sorteersleutel, Nederlandse tijd over de UTC-datumgrens, read-only queries en behoud van periode-/bron-/registratieweigering.
- `tests/test_gate10c_application_v05.py`: de expliciete `limit=1`-verwachting volgt nu de opgedragen chronologische sortering; broncontext en historische feitenverwachtingen blijven behouden.

Verificatie vanuit `code/Prototype`:

```text
python -m pytest -q tests/test_no_show_choices_v05.py tests/test_gate10c_application_v05.py tests/test_planning_session_source_v05.py tests/test_volunteer_identity_v05.py
73 geslaagd

python -m pytest -q
900 geslaagd
```

Geen mislukte of overgeslagen tests in de definitieve runs. De eerste gerichte aanroep vanuit de repositoryroot vond de relatieve testpaden niet; opnieuw uitgevoerd vanuit `code/Prototype`. CI en commit worden bij oplevering in PR #38 vermeld.

Lokale acceptatie: herstart de bijgewerkte applicatie, hervat de bestaande planning en open de No-Show-keuzelijst. Hiervoor is geen reset of nieuwe synchronisatie nodig. Controleer een gevalideerde periode met meer dan 50 betrouwbaar gekoppelde boekingen: alle geschikte boekingen moeten beschikbaar zijn, in datum-/tijd-/dienst-/naamvolgorde. Controleer meerdere vrijwilligers bij dezelfde dienst en dat de bestaande betekenisvolle labels intact blijven. Afgeschermde/ambigue boekingen en boekingen uit een andere actieve bronperiode blijven uitgesloten. Registreer uitsluitend bedoelde acceptatiegevallen; deel alleen niet-herleidbare uitkomsten.

Nog niet aangetoond: de volledigheid tegenover echte lokale CKC-brondata en de functionele acceptatie door de planner. Dit is een gerichte prototypecorrectie, geen integrale v0.5-acceptatie. De twee vooraf aanwezige lokale wijzigingen in `streamlit_app.py` en `DVK-v0.5-vrijwilligers-integratie.md` blijven buiten deze wijziging. PR #38 blijft open en ongemerged.
