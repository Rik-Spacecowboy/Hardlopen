# Hardloopwedstrijden

Nederlandstalige site; Rik is (vooralsnog) de enige gebruiker. Scope: 10 km t/m halve marathon, provincies
Noord-Holland, Zuid-Holland, Utrecht en Flevoland, de komende 12 maanden. Weg, trail en cross.

## Data

- Bewerk alleen `data/wedstrijden.json`; daarna `python3 scripts/bouw_data.py` en `data/wedstrijden.js`
  meecommitten (de workflow "Controle" faalt anders).
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

Agenda-abonnement, iPhone-tegel, meldformulier, filter "binnen X km van huis", herinnering bij openen inschrijving.
