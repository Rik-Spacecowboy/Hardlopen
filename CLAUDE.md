# Hardloopwedstrijden

Nederlandstalige site; Rik is (vooralsnog) de enige gebruiker. Scope: 10 km t/m halve marathon, provincies
Noord-Holland, Zuid-Holland, Utrecht en Flevoland, de komende 12 maanden. Alleen wegwedstrijden: geen trail of cross (Rik, 2026-10-02).

## Data

- Bewerk alleen `data/wedstrijden.json`; daarna `python3 scripts/bouw_data.py` en `python3 scripts/bouw_agenda.py`, en
  `data/wedstrijden.js` + `agenda.ics` meecommitten (de workflow "Controle" faalt anders).
- Vorige-editieprijs per afstand: `prijsVorigJaar: {prijs, jaar, bron}`, alleen letterlijk van de organisator.
- Alleen gegevens die letterlijk bij de organisator of het inschrijfplatform staan. Nooit schatten; bij twijfel
  `null` / status `"onbekend"`. Altijd `gecontroleerd` bijwerken naar de datum waarop je het nakeek, en de
  gebruikte pagina's in `bronnen`.
- Aggregators (runphy, hardlooplijst, hardloopkalendernederland, nextrace) alleen om wedstrijden te vinden,
  niet als bron voor prijs/status.
- Datum "vóór 13 dec" wordt `2026-12-12` (laatste dag die zeker nog telt).

## Live zetten

1. Lokaal testen: `python3 -m http.server 8080` en controleren in de browser (Playwright/Chromium).
2. Via een PR naar `main`; Claude maakt én merget die zelf (Rik doet geen PR's). GitHub Pages publiceert dan
   vanzelf; controleer dat "pages build and deployment" slaagde.
3. Nog geen claude.ai-artifact (bewust uitgesteld).

## Later (afgesproken, nog niet gebouwd)

iPhone-tegel, meldformulier, herinnering bij openen inschrijving. (Agenda-abonnement, afstand tot huis, starttijdfilter, eigen status en vorige-editieprijs zijn gebouwd; `prijsVorigJaar` is nog nergens ingevuld.)
