"""Haalt de bronpagina's op van lopen in de komende weken en schrijft ze als platte tekst weg.

Draait in de GitHub Action "Bronpagina's ophalen", zodat de wekelijkse controle de pagina's van
organisatoren en inschrijfplatforms als bestanden kan lezen, zonder dat Claude zelf websites opent.

Gebruik: python3 scripts/haal_bronnen.py <uitvoermap> [--weken 8]
Per loop één bestand <id>.txt met per URL de HTTP-status en de zichtbare tekst; plus overzicht.tsv.
"""
import argparse
import datetime as dt
import html.parser
import json
import pathlib
import re
import sys
import time
import urllib.error
import urllib.request

UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36"
MAX_TEKENS = 40000
OVERSLAAN = ("runphy", "hardlooplijst", "hardloopkalendernederland", "nextrace", "loopkalender")


class Tekst(html.parser.HTMLParser):
    """Zichtbare tekst uit HTML, met regeleinden bij blokelementen."""
    BLOK = {"p", "div", "br", "li", "tr", "h1", "h2", "h3", "h4", "h5", "h6", "section", "article", "table", "dt", "dd"}

    def __init__(self):
        super().__init__()
        self.delen, self.verborgen = [], 0

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style", "noscript", "svg"):
            self.verborgen += 1
        elif tag in self.BLOK:
            self.delen.append("\n")
        if tag == "td":
            self.delen.append(" | ")

    def handle_endtag(self, tag):
        if tag in ("script", "style", "noscript", "svg") and self.verborgen:
            self.verborgen -= 1
        elif tag in self.BLOK:
            self.delen.append("\n")

    def handle_data(self, data):
        if not self.verborgen:
            self.delen.append(data)

    def tekst(self):
        t = "".join(self.delen)
        t = re.sub(r"[ \t\r\f\v]+", " ", t)
        return re.sub(r"\n\s*\n+", "\n", t).strip()


def haal(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "nl,en;q=0.8"})
    try:
        with urllib.request.urlopen(req, timeout=25) as r:
            ruw = r.read(3_000_000)
            enc = r.headers.get_content_charset() or "utf-8"
            status, eind = r.status, r.geturl()
    except urllib.error.HTTPError as e:
        return e.code, url, ""
    except Exception as e:  # time-out, DNS, TLS
        return f"fout: {type(e).__name__}", url, ""
    p = Tekst()
    try:
        p.feed(ruw.decode(enc, errors="replace"))
    except Exception:
        pass
    return status, eind, p.tekst()[:MAX_TEKENS]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("uitvoer")
    ap.add_argument("--weken", type=int, default=8)
    a = ap.parse_args()
    root = pathlib.Path(__file__).resolve().parent.parent
    lopen = json.loads((root / "data" / "wedstrijden.json").read_text(encoding="utf-8"))
    vandaag = dt.date.today()
    tot = vandaag + dt.timedelta(weeks=a.weken)
    uit = pathlib.Path(a.uitvoer)
    uit.mkdir(parents=True, exist_ok=True)
    regels = ["id\tdatum\turl\tstatus\ttekens"]
    gekozen = [w for w in lopen if w.get("datum") and vandaag.isoformat() <= w["datum"] <= tot.isoformat()]
    for w in gekozen:
        urls = []
        for u in [(w.get("inschrijving") or {}).get("url"), w.get("website"), *(w.get("bronnen") or [])[:2]]:
            if u and u.startswith("http") and u not in urls and not any(s in u for s in OVERSLAAN):
                urls.append(u)
        blokken = [f"# {w['naam']} ({w['datum']}, {w['plaats']})", f"opgehaald: {dt.datetime.utcnow():%Y-%m-%d %H:%M} UTC"]
        for u in urls[:3]:
            status, eind, tekst = haal(u)
            regels.append(f"{w['id']}\t{w['datum']}\t{u}\t{status}\t{len(tekst)}")
            blokken.append(f"\n===== {u}\n(status {status}{', doorgestuurd naar ' + eind if eind != u else ''}, {len(tekst)} tekens)\n{tekst}")
            time.sleep(1)
        (uit / f"{w['id']}.txt").write_text("\n".join(blokken) + "\n", encoding="utf-8")
    (uit / "overzicht.tsv").write_text("\n".join(regels) + "\n", encoding="utf-8")
    print(f"{len(gekozen)} lopen tussen {vandaag} en {tot}, {len(regels) - 1} pagina's")


if __name__ == "__main__":
    sys.exit(main())
