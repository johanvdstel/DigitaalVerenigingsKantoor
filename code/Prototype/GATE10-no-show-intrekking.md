# Gate 10 — auditbare no-showintrekking (v0.5, in ontwikkeling)

Startpunt: `prototype-v0.5` op `a9732c0654ab13506d376b079f11448ce5189c53`.
Werkbranch: `codex/g10-noshow-revocation`. Dit is geen functionele acceptatie van v0.5.

## Functionele grens

`NoShowEvent` is een immutable registratiefeit. `NoShowRevocation` legt een
expliciete intrekking afzonderlijk vast met identificatie, no-showverwijzing,
verplichte vrije toelichting, actor en tijdstip. Alleen `MANAGE_NO_SHOWS` geeft
via de applicatieservice toegang tot intrekken. Per no-show is maximaal één
intrekking toegestaan, ongeacht sanctietrap. Andere diensten of gebeurtenissen
maken nooit een intrekking aan.

`NoShowApplicationService.current_state(person_id, season)` leidt de actuele
status af uit alle no-shows van die persoon in dat seizoen zonder intrekking.
N1 + N2 + N3 geeft teller 3; intrekken van N2 geeft teller 2. Historische
sanctiebeoordelingen worden niet herschreven en zijn niet de actuele teller.
De bestaande Gate-9-ladder, inclusief de eerste waarschuwing en de verplichting
zelf inzet te regelen, blijft behouden. Het volgen/koppelen/afronden van een
`ReplacementDuty` en de automatische reset daardoor vervallen volledig.

Intrekkingen horen via hun oorspronkelijke no-show bij diens seizoen, ook
wanneer ze later worden geregistreerd. Een nieuw seizoen (1 juli–30 juni)
begint met teller 0 zonder historische feiten te wijzigen of verwijderen.
Deze iteratie voegt geen seizoensafsluiting of housekeeping toe.

## Schema 9 → 10

De bestaande migratieroute voert migratie 010 automatisch uit bij openen van
een prototypedatabase. Hiervoor is SQLite 3.35 of hoger nodig (`DROP COLUMN`).
De migratie en schema-versieregistratie vallen binnen één transactie. Bij een
fout worden de wijzigingen teruggedraaid.

Volgens het expliciete CKC-besluit voor deze iteratie:

- vervallen alle replacement-data en de tabel `replacement_duties`;
- vervallen legacy no-shows met `status='revoked'` en uitsluitend hun afhankelijke
  `sanction_assessments`;
- blijven geldige no-shows, hun oorspronkelijke JSON-payloads en overige gegevens
  behouden, waaronder proposals, beslissingen en assignments;
- ontstaan **geen** intrekkingen uit legacy-data: actor, reden en tijdstip worden
  niet gereconstrueerd of afgeleid.

De gecontroleerde bestaande afhankelijkheden van `no_show_events` zijn alleen
`sanction_assessments` en `replacement_duties`. De migratie verwijdert daarna de
oude statuskolom, maakt de afzonderlijke tabel `no_show_revocations` aan met een
unieke no-showverwijzing en blokkeert UPDATE/DELETE op beide feittabellen.
Het lezen van geldige legacy-payloads negeert uitsluitend de obsolete velden
`status`, `correction_reason`, `corrected_at` en `corrected_by`.
Historische migratie 009 blijft nodig voor de versiegeschiedenis; in het nieuwe
schema blijft geen replacement-tabel achter.

## UI en verificatie

De bestaande sectie No-shows gebruikt de publieke no-showquery en gedeelde
menselijke assignmentpresentatie. Intrekken vraagt een zichtbare verplichte
vrije toelichting en de knop **Intrekking bevestigen**. De applicatieservice
bepaalt welke no-shows beschikbaar zijn en valideert de opdracht opnieuw.
De oude sectie Vervangende inzet en de bijbehorende acties zijn verwijderd.

Gerichte regressies bewaken immutable feiten, afzonderlijke persistence,
autorisatie, toelichting, uniciteit, alle sanctietrappen, seizoensgrenzen,
migratie/rollback en behoud van andere tabellen. Streamlit AppTest voert de
werkelijke UI uit met een tijdelijke database en verifieert menselijke labels,
expliciete bevestiging en foutafhandeling. Historisch geaccepteerde
C/W/I/R/V-cases en fixtures zijn niet aangepast.
