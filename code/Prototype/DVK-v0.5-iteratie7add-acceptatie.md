# DVK v0.5 — Iteratie 7add: uitvoering en functionele acceptatie

**Acceptatie:** CKC, 3 november 2026  
**Integratiebranch:** `prototype-v0.5`  
**Werkbranch:** `codex/iteratie-7add-ui-correcties`  
**PR:** [#63](https://github.com/johanvdstel/DigitaalVerenigingsKantoor/pull/63) (draft; nog niet gemerged bij vastlegging)  
**Geaccepteerde codecommit:** `e4d6a9df5c599a47751ea79fa3366dd18ac7b3f5`  
**Uitgangsbaseline:** `622e392e010753f0d5802142d1237a1323592a3e` (Iteratie 6 / BL-22)

## Doel en scope

Twee kleine presentatiecorrecties in Ledendienst Planning. Geen wijziging van CKC-beleid, broncontracten, API-gedrag, planning, berekeningen, gegevens of Sportlink-writeback.

## Correctie 1 — melding actuele Sportlink-bezetting

De bestaande melding is uit sectie 2 Databronnen verplaatst naar sectie 3 Diensten, binnen de uitklapbare bediening voor feitelijke Sportlink-inroosteringen, onmiddellijk boven de knop **Sportlink-inroosteringen synchroniseren**.

Geaccepteerde tekst:

> De actuele bezetting van de vrijwilligersdiensten is nog niet beschikbaar voor deze roosterperiode. Haal de roostergegevens op via de onderstaande knop om de bezetting en resterende behoefte te kunnen bepalen.

De bestaande conditie voor het tonen van de melding is behouden. CKC heeft de nieuwe positie lokaal visueel goedgekeurd.

## Correctie 2 — kolombreedtes dienstentabel

Eerste proef: Dienst 140 px, Sportlink 200 px, Vrije capaciteit 125 px. Bij circa 1366 px browserbreedte, 100% zoom en geopende zijbalk was zonder horizontaal scrollen slechts 'Vri' van de laatste kolom zichtbaar. Daarom nog niet geaccepteerd.

Tweede proef, geaccepteerd:

| Kolom | Breedte |
| --- | ---: |
| Dienst | 110 px |
| Sportlink | 140 px |
| Vrije capaciteit | 65 px |

CKC heeft lokaal bevestigd dat de **waarden** in Vrije capaciteit zonder horizontaal scrollen volledig zichtbaar zijn. De kolomkop is afgekapt; dit is uitdrukkelijk toegestaan. Dienstnamen blijven voldoende leesbaar. De volledige oorspronkelijke Sportlink-namen blijven via dubbelklik in de read-only cel te bekijken. Overige kolombreedtes en tabelbediening blijven ongewijzigd.

## Technisch bewijs

- Geaccepteerde codecommit: `e4d6a9df5c599a47751ea79fa3366dd18ac7b3f5`.
- Gewijzigde code: `code/Prototype/streamlit_app.py`; bijbehorende gerichte testasserties aangepast.
- 131 gerichte tests geslaagd.
- 1502 volledige regressietests geslaagd.
- 11 synthetische runners geslaagd.
- Geen mislukte of overgeslagen tests gerapporteerd.
- [GitHub Actions CI #414](https://github.com/johanvdstel/DigitaalVerenigingsKantoor/actions/runs/41540805895) geslaagd.
- Codecommit en CI door ChatGPT op GitHub gecontroleerd vóór functionele afsluiting.

## Functioneel besluit

**Beide correcties zijn functioneel geaccepteerd door CKC op 3 november 2026.** De geaccepteerde codecommit blijft het referentiepunt; latere documentatiecommits wijzigen deze functionele acceptatie niet. PR #63 mag uitsluitend na afzonderlijke expliciete merge-toestemming naar `prototype-v0.5` worden gemerged.

## Aandachtspunten en vervolg

Tijdens de lokale beoordeling startten Streamlit en DVK opvallend traag. De oorzaak is niet vastgesteld; dit is een **afzonderlijk read-only technisch onderzoekspunt na Iteratie 7add**, geen bewezen defect in PR #63 en geen nieuwe productieregel.

De volgende functionele mijlpaal is de **integrale acceptatie van prototype v0.5**. BL-13/RPA blijft een afzonderlijk later traject. Deze iteratie verleent geen Sportlink-schrijfbevoegdheid en is geen productieacceptatie.
