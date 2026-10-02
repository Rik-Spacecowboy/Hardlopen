#!/usr/bin/env python3
"""Controleert data/wedstrijden.json en schrijft data/wedstrijden.js voor de site.

data/wedstrijden.json is de enige plek waar wedstrijden met de hand worden bewerkt. De site laadt
data/wedstrijden.js (een gewoon script, zodat index.html ook werkt als je het lokaal opent).

    python3 scripts/bouw_data.py           # controleren en data/wedstrijden.js schrijven
    python3 scripts/bouw_data.py --check   # exit 1 als er fouten zijn of de .js achterloopt
"""
import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BRON = ROOT / "data" / "wedstrijden.json"
DOEL = ROOT / "data" / "wedstrijden.js"
INDEX = ROOT / "index.html"
# index.html laadt data/wedstrijden.js?v=<hash>. Zo haalt de browser na elke data-update de nieuwe versie op
# in plaats van een oude uit de cache (GitHub Pages laat bestanden 10 minuten cachen).
SCRIPT_TAG = re.compile(r'<script src="data/wedstrijden\.js(\?v=[0-9a-f]*)?"></script>')

PROVINCIES = {"Noord-Holland", "Zuid-Holland", "Utrecht", "Flevoland"}
TYPES = {"weg"}  # trail en cross bewust niet (Rik, 2026-10-02)
STATUSSEN = {"open", "vol", "loting", "wachtlijst", "nog niet open", "gesloten", "geannuleerd", "onbekend"}
MIN_KM, MAX_KM = 9.5, 21.2  # 10 km t/m halve marathon
DATUM = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def fouten_in(w):
    f = []
    naam = w.get("naam") or "?"
    for veld in ("id", "naam", "plaats", "provincie", "lat", "lon", "afstanden", "inschrijving", "gecontroleerd"):
        if w.get(veld) in (None, "", []):
            f.append(f"{naam}: veld '{veld}' ontbreekt")
    if w.get("provincie") not in PROVINCIES:
        f.append(f"{naam}: provincie '{w.get('provincie')}' hoort niet bij {sorted(PROVINCIES)}")
    if w.get("type") is not None and w["type"] not in TYPES:  # null = ondergrond niet vermeld
        f.append(f"{naam}: type '{w.get('type')}' moet een van {sorted(TYPES)} of null zijn")
    # Zonder bevestigde datum: verwacht.maand (JJJJ-MM) op basis van de vorige editie.
    verwacht = w.get("verwacht") or {}
    if not w.get("datum"):
        if not re.match(r"^\d{4}-\d{2}$", verwacht.get("maand") or ""):
            f.append(f"{naam}: geen datum en geen verwacht.maand (JJJJ-MM)")
        if any(a.get("prijs") is not None for a in w.get("afstanden") or []):
            f.append(f"{naam}: verwachte loop mag geen prijs hebben (alleen prijsNotitie van de vorige editie)")
    for veld in ("datum", "gecontroleerd"):
        if w.get(veld) and not DATUM.match(w[veld]):
            f.append(f"{naam}: {veld} '{w[veld]}' is geen JJJJ-MM-DD")
    ins = w.get("inschrijving") or {}
    if ins.get("status") not in STATUSSEN:
        f.append(f"{naam}: status '{ins.get('status')}' moet een van {sorted(STATUSSEN)} zijn")
    for veld in ("opent", "sluit"):
        if ins.get(veld) and not DATUM.match(ins[veld]):
            f.append(f"{naam}: inschrijving.{veld} '{ins[veld]}' is geen JJJJ-MM-DD")
    for a in w.get("afstanden") or []:
        km = a.get("km")
        if not isinstance(km, (int, float)) or not MIN_KM <= km <= MAX_KM:
            f.append(f"{naam}: afstand {km} valt buiten 10 km t/m halve marathon")
        if a.get("prijs") is not None and not isinstance(a["prijs"], (int, float)):
            f.append(f"{naam}: prijs '{a['prijs']}' is geen getal")
    lat, lon = w.get("lat"), w.get("lon")
    if isinstance(lat, (int, float)) and isinstance(lon, (int, float)):
        if not (51.6 <= lat <= 53.2 and 3.8 <= lon <= 6.0):
            f.append(f"{naam}: coördinaten {lat},{lon} liggen niet in NH/ZH/Utrecht/Flevoland")
    for url in [ins.get("url"), w.get("website"), *(w.get("bronnen") or [])]:
        if url and not url.startswith("https://") and not url.startswith("http://"):
            f.append(f"{naam}: '{url}' is geen URL")
    return f


def bouw():
    wedstrijden = json.loads(BRON.read_text(encoding="utf-8"))
    fouten = [x for w in wedstrijden for x in fouten_in(w)]
    ids = [w.get("id") for w in wedstrijden]
    fouten += [f"id '{i}' komt dubbel voor" for i in sorted({i for i in ids if ids.count(i) > 1})]
    wedstrijden.sort(key=lambda w: (w.get("datum") or (w.get("verwacht") or {}).get("maand", "") + "-99", w.get("naam") or ""))
    js = (
        "// Gegenereerd door scripts/bouw_data.py uit data/wedstrijden.json. Niet met de hand bewerken.\n"
        "const WEDSTRIJDEN = " + json.dumps(wedstrijden, ensure_ascii=False, indent=1) + ";\n"
    )
    return fouten, js


def met_versie(index_html, js):
    versie = hashlib.sha1(js.encode("utf-8")).hexdigest()[:10]
    return SCRIPT_TAG.sub(f'<script src="data/wedstrijden.js?v={versie}"></script>', index_html)


def main():
    check = "--check" in sys.argv
    fouten, js = bouw()
    for f in fouten:
        print("FOUT:", f)
    if fouten:
        sys.exit(1)
    huidig = DOEL.read_text(encoding="utf-8") if DOEL.exists() else ""
    index = INDEX.read_text(encoding="utf-8")
    if not SCRIPT_TAG.search(index):
        print("FOUT: index.html laadt data/wedstrijden.js niet meer via de verwachte <script>-tag")
        sys.exit(1)
    nieuwe_index = met_versie(index, js)
    if check:
        if huidig != js or index != nieuwe_index:
            print("data/wedstrijden.js of de versie in index.html loopt achter: draai python3 scripts/bouw_data.py")
            sys.exit(1)
        print("OK")
        return
    DOEL.write_text(js, encoding="utf-8")
    INDEX.write_text(nieuwe_index, encoding="utf-8")
    print(f"data/wedstrijden.js geschreven ({len(json.loads(BRON.read_text(encoding='utf-8')))} wedstrijden)")


if __name__ == "__main__":
    main()
