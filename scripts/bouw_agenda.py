#!/usr/bin/env python3
"""Bouwt agenda.ics uit data/wedstrijden.json: één hele-dag-afspraak per wedstrijd met bevestigde datum.

Abonneren kan via webcal://rik-spacecowboy.github.io/Hardlopen/agenda.ics (iPhone: Instellingen > Agenda >
Accounts > Agenda-abonnement). De starttijd staat in de titel, niet als tijdstip: dan hoeven we geen
einde te schatten.

    python3 scripts/bouw_agenda.py           # agenda.ics schrijven
    python3 scripts/bouw_agenda.py --check   # exit 1 als agenda.ics achterloopt
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BRON = ROOT / "data" / "wedstrijden.json"
DOEL = ROOT / "agenda.ics"
SITE = "https://rik-spacecowboy.github.io/Hardlopen/"


def esc(t):
    return str(t).replace("\\", "\\\\").replace(";", "\;").replace(",", "\\,").replace("\n", "\\n")


def vouw(regel):
    """Regels langer dan 75 bytes horen (RFC 5545) gevouwen te worden."""
    b, delen = regel.encode("utf-8"), []
    while len(b) > 75:
        knip = 75
        while (b[knip] & 0xC0) == 0x80:  # niet midden in een teken knippen
            knip -= 1
        delen.append(b[:knip].decode("utf-8"))
        b = b" " + b[knip:]
    delen.append(b.decode("utf-8"))
    return "\r\n".join(delen)


def km(x):
    return str(x).replace(".", ",")


def bouw():
    wedstrijden = [w for w in json.loads(BRON.read_text(encoding="utf-8")) if w.get("datum")]
    wedstrijden.sort(key=lambda w: (w["datum"], w["naam"]))
    stempel = max(w["gecontroleerd"] for w in wedstrijden).replace("-", "") + "T000000Z"
    regels = [
        "BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//Hardloopwedstrijden//NL", "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH", "X-WR-CALNAME:Hardloopwedstrijden", "X-WR-TIMEZONE:Europe/Amsterdam",
        "REFRESH-INTERVAL;VALUE=DURATION:P1D", "X-PUBLISHED-TTL:P1D",
    ]
    for w in wedstrijden:
        dag = w["datum"].replace("-", "")
        titel = w["naam"] + (f" (start {w['starttijd']})" if w.get("starttijd") else "")
        afst = ", ".join(f"{a.get('label') or km(a['km']) + ' km'}" + (f" € {km(a['prijs'])}" if a.get("prijs") is not None else "") for a in w["afstanden"])
        ins = w["inschrijving"]
        beschrijving = [f"Afstanden: {afst}", f"Inschrijving: {ins['status']}"]
        if ins.get("sluit"):
            beschrijving.append(f"Sluit: {ins['sluit']}")
        if ins.get("url") or w.get("website"):
            beschrijving.append(ins.get("url") or w["website"])
        beschrijving.append(f"Gecontroleerd {w['gecontroleerd']}; check de inschrijflink voor de actuele stand.")
        regels += [
            "BEGIN:VEVENT", f"UID:{w['id']}@rik-spacecowboy.github.io", f"DTSTAMP:{stempel}",
            f"DTSTART;VALUE=DATE:{dag}", f"SUMMARY:{esc(titel)}", f"LOCATION:{esc(w['plaats'] + ', ' + w['provincie'])}",
            f"DESCRIPTION:{esc(chr(10).join(beschrijving))}", f"URL:{w.get('website') or SITE}",
            "TRANSP:TRANSPARENT",
            "BEGIN:VALARM", "ACTION:DISPLAY", f"DESCRIPTION:{esc(w['naam'])} is morgen", "TRIGGER:-PT15H", "END:VALARM",
            "END:VEVENT",
        ]
    regels.append("END:VCALENDAR")
    return "\r\n".join(vouw(r) for r in regels) + "\r\n", len(wedstrijden)


def main():
    ics, n = bouw()
    huidig = DOEL.read_bytes().decode("utf-8") if DOEL.exists() else ""
    if "--check" in sys.argv:
        if huidig != ics:
            print("agenda.ics loopt achter: draai python3 scripts/bouw_agenda.py")
            sys.exit(1)
        print("OK")
        return
    DOEL.write_bytes(ics.encode("utf-8"))
    print(f"agenda.ics geschreven ({n} wedstrijden)")


if __name__ == "__main__":
    main()
