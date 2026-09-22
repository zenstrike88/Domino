"""
Petit serveur web utilisé uniquement pour garder le bot "réveillé"
sur un hébergeur gratuit qui coupe les services inactifs (ex: Render Free).

Un service externe (ex: UptimeRobot, cron-job.org) doit appeler l'URL
publique de ce service toutes les 5-10 minutes pour éviter la mise en veille.

Si tu héberges sur une VM/VPS classique (Oracle Cloud, etc.), tu peux
laisser ce fichier tel quel : il ne fait aucun mal, il ouvre juste un
petit port web en plus du bot.
"""

from flask import Flask
from threading import Thread

app = Flask(__name__)


@app.route("/")
def home():
    return "Domino bot is alive!"


def run():
    app.run(host="0.0.0.0", port=8080)


def keep_alive():
    t = Thread(target=run)
    t.daemon = True
    t.start()
