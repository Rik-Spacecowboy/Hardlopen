"""Bewaking: is de wekelijkse controle (maandag 09:00 Amsterdam) deze week gedraaid?

Kijkt naar het nieuwste `gecontroleerd` in data/wedstrijden.json. Staat dat niet op of na de maandag
van deze week, dan is de weekcontrole uitgebleven en opent de workflow een issue voor Rik (GitHub stuurt
daar een melding van). Draaide hij wel, dan sluit de workflow een eventueel openstaand bewakingsissue.

Gebruik: python3 scripts/bewaak_weekcontrole.py  -> schrijft `status`, `maandag`, `laatste` naar $GITHUB_OUTPUT
"""
import datetime as dt
import json
import os
import sys
from zoneinfo import ZoneInfo

nu = dt.datetime.now(ZoneInfo("Europe/Amsterdam"))
maandag = nu.date() - dt.timedelta(days=nu.weekday())
if nu.weekday() == 0 and nu.hour < 12:  # maandagochtend: de controle van vandaag kan nog bezig zijn
    maandag -= dt.timedelta(days=7)

lopen = json.load(open("data/wedstrijden.json", encoding="utf-8"))
laatste = max((w.get("gecontroleerd") or "" for w in lopen), default="")
status = "ok" if laatste >= maandag.isoformat() else "gemist"

regels = {"status": status, "maandag": maandag.isoformat(), "laatste": laatste or "onbekend"}
print(regels)
uit = os.environ.get("GITHUB_OUTPUT")
if uit:
    with open(uit, "a", encoding="utf-8") as f:
        for k, v in regels.items():
            f.write(f"{k}={v}\n")
sys.exit(0)
