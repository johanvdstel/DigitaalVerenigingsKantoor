# DVK v0.5 — Iteratie 9: functionele acceptatie

**Datum:** 4 november 2026  
**Status:** functioneel geaccepteerd door CKC op codecommit `67dd98efe2fb5a2c696d6bb864b4f818a1e24755`, [draft-PR #66](https://github.com/johanvdstel/DigitaalVerenigingsKantoor/pull/66). **Niet gemerged bij vastlegging.**

## Scope en beleidsbesluiten

Teamgebonden selectie: jeugdteams JO/O/MO met leeftijdscategorie tot en met 20; overige teams senioren. Zaterdag vóór 12:30 eerst jeugd-thuis met wedstrijdoverlap, vervolgens senioren-thuis zonder conflict; vanaf 12:30 senioren-thuis zonder conflict. Jeugd-thuis zonder overlap valt in de noodcategorie 'zonder wedstrijd', met behoud van feitelijke thuiswedstrijdcontext. Daarna geschikte uitspelende teams zonder conflict. Alle relevante teamregistraties en wedstrijden worden gecontroleerd; bij enig conflict niet aanbieden, anders gunstigste groep. BL-20 andere weekenddag uitsluitend als laatste noodgroep bij minimumtekort. Binnen groep: actuele openstaande uren E aflopend, positieve historische achterstand vorig seizoen aflopend, vervolgens stabiele persoonssleutel. Historische achterstand telt het gehele lopende seizoen mee, zonder wijziging van actuele A/B/C/D/E. Taakplicht en Sportlink-bronhouderschap blijven ongewijzigd; geen ouderselectie of Sportlink-writeback.

## Lokale functionele acceptatie (CKC)

Getest met actieve codeversie `codex/v05-iteratie9-kandidaatselectie · 67dd98efe2fb · /private/tmp/dvk-iteratie9` en werkende Sportlink-koppeling.

- **A — Zaterdagochtend, bardienst 10:00–12:30:** jeugd-thuis met overlappende wedstrijd bovenaan, actuele E en vervolgens historische achterstand correct; overige geschikte thuisteams en uitteams daarna. Overlappende seniorenwedstrijd van 2-zaterdag leidt terecht niet tot kandidaten. Geen zondagteams aangeboden.
- **B — Zaterdagmiddag, bardienst 12:30–15:00:** overlappende senioren-thuiswedstrijden (2-Zat, VR, 5) leveren geen kandidaten; geschikte jeugd-thuis zonder overlap in noodgroep, daarna geschikte uitteams zonder conflict.
- **C — Kandidaatverklaring:** expliciet 'Jeugdteam met een niet-overlappende thuiswedstrijd: ingedeeld in de prioriteringscategorie zonder wedstrijd; het team speelt wel thuis', terwijl wedstrijdcontext 'Thuiswedstrijd' blijft. Actuele E=10 en historische achterstand=4 zichtbaar.
- **D — Urenprioritering:** CKC heeft kandidaten met gelijke actuele uren en verschillende historische achterstand vergeleken; rangorde correct.
- **E — Bevestiging/Undo:** selectie niet definitief zonder bevestiging; bevestiging en undo handmatig geslaagd.

**Niet handmatig gereproduceerd:** BL-20-noodgroep bij minimumtekort met kandidaten van de andere weekenddag. Deze uitzondering is synthetisch getest; geen claim van lokale CKC-acceptatie voor dit scenario. Ook januari–juni en uitzonderlijke meervoudige teamregistraties zijn niet afzonderlijk handmatig bewezen; synthetische tests dekken de beleidsgrenzen.

## Technische verificatie

Codex rapporteert 1.584 regressietests geslaagd (waaronder 78 nieuwe synthetische tests), 184 afzonderlijke domeintests, 11 acceptatiescripts, syntax- en diff-controle geslaagd. [CI #429](https://github.com/johanvdstel/DigitaalVerenigingsKantoor/actions/runs/41878191393) is op 4 november als **geslaagd** gecontroleerd voor implementatiecommit `67dd98e`.

De bestaande lokale `.venv` overschrijdt de Streamlit-importtimeout van 15 seconden. In een tijdelijke Python-omgeving met dezelfde Streamlit-versie importeert Streamlit binnen 0,27 seconde; daar is de regressiesuite uitgevoerd. Oorzaak onbekend; geen code- of dependencywijziging voor dit omgevingsprobleem. Dit blijft een afzonderlijk aandachtspunt, geen vastgestelde Iteratie 9-regressie.

## Acceptatiegrens en vervolg

Functionele acceptatie geldt voor **de hierboven genoemde codecommit**, niet automatisch voor latere PR-heads, merge, integrale v0.5-acceptatie of productie. Projectdocumentatie wordt op dezelfde PR-branch bijgewerkt. Voor merge zijn een hercontrole van PR-head/CI en **afzonderlijke expliciete toestemming** nodig. **Iteratie 10** is de volgende stap: integrale functionele acceptatie van v0.5 zonder nieuwe functionaliteit. BL-13/RPA blijft later en afzonderlijk.
