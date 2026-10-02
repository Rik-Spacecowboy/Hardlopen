# Hardloopwedstrijden

Overzicht van hardloopwedstrijden van **10 km tot en met de halve marathon** in **Noord-Holland, Zuid-Holland,
Utrecht en Flevoland**: wanneer, waar, wat het kost, of je je nog kunt inschrijven en of de wedstrijd in een even
of oneven week valt. Pure HTML/CSS/JS, geen framework; structureel gebaseerd op het
[Anesthesie](https://github.com/Rik-Spacecowboy/Anesthesie)-project (de opmaak wordt later eigen).

Live: https://rik-spacecowboy.github.io/Hardlopen/

## Wat de site doet

- Drie weergaven: **Kaarten**, een compacte **Lijst** (klik voor de hele kaart) en een **Kaart** van de vier
  provincies met een stip per plaats (groter = meer wedstrijden; klik voor de wedstrijden daar).
- Filters: nog in te schrijven, provincie, afstand (10–11 km, 12–18 km, 20 km – halve), 
  even/oneven week (ISO-weeknummer van de wedstrijddatum), plaats, maand, datumbereik, maximumprijs. Sorteren op
  datum, prijs of sluitingsdatum van de inschrijving.
- Alle filters staan in de URL ("Deel" kopieert de link). Wedstrijden bewaren met de ster (alleen in je eigen
  browser, `localStorage`).
- Afgelopen wedstrijden zijn verborgen; "Ook afgelopen" toont ze weer.

## Data: `data/wedstrijden.json`

Dit is de enige plek waar wedstrijden worden bewerkt. Na elke wijziging:

```bash
python3 scripts/bouw_data.py          # controleert de data en schrijft data/wedstrijden.js
python3 scripts/bouw_data.py --check  # wat de workflow "Controle" draait
```

Alleen wegwedstrijden (trail en cross zijn eruit gehaald). Per wedstrijd: datum, plaats, provincie, coördinaten, type, afstanden met prijs (+ toelichting op staffels),
inschrijving (status, opent, sluit, platform, link), website, organisator, bronnen, notitie en **`gecontroleerd`**:
de datum waarop status en prijs bij de bron zijn nagekeken.

Regels:
- Alleen gegevens die letterlijk bij de organisator of het inschrijfplatform staan. **Nooit schatten**; onbekend is
  `null` of status `"onbekend"`.
- Statussen: `open`, `vol`, `loting`, `wachtlijst`, `nog niet open`, `gesloten`, `geannuleerd`, `onbekend`.
  De site corrigeert zelf een verouderde status als een datum voorbij is (open met een verstreken sluitdatum
  wordt "gesloten").
- Prijs = het standaard voorinschrijftarief voor volwassenen; staffels en toeslagen in `prijsNotitie`.
- Een kaart toont "Gecontroleerd …" in oranje als de laatste controle meer dan 14 dagen oud is.

## Hoe actueel is het?

Dit is het zwakste punt van elke hardloopkalender: of een wedstrijd vol is, verandert per dag. Werkwijze: een
wekelijkse controle (Claude) loopt de komende wedstrijden na bij de bron, werkt status/prijs/`gecontroleerd` bij en
zet dat via een PR live. Aggregators (runphy, hardlooplijst, enz.) worden alleen gebruikt om wedstrijden te
vinden, niet als bron voor de gegevens.

## Lokaal draaien

```bash
python3 -m http.server 8080   # en open http://localhost:8080
```

Provinciegrenzen: CBS/PDOK via [cartomap/nl](https://github.com/cartomap/nl) (`data/provincies.js`).
