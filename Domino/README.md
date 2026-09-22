# Domino — bot Discord

Bot Discord pour jouer au domino entre amis (scores, sons, memes).

## ⚠️ Avant toute chose

Le token Discord a été retiré du code (il était en clair avant, ce qui est
dangereux sur un repo GitHub). **Si tu utilises encore l'ancien token,
régénère-le maintenant** :

1. Va sur https://discord.com/developers/applications
2. Sélectionne ton appli → onglet **Bot**
3. Clique **Reset Token**, copie le nouveau token (tu ne le reverras plus après)

Ce nouveau token ne doit jamais être écrit dans un fichier `.py`. Il se met
uniquement dans une variable d'environnement `DISCORD_TOKEN` (voir plus bas).

## 1. Mettre le projet sur GitHub

Dans le dossier du projet, en local (ou dans ton terminal Replit) :

```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/zenstrike88/Domino.git
git push -u origin main
```

Le `.gitignore` empêche déjà `.env` (donc le token) d'être envoyé sur GitHub.

**Conseil** : mets le repo en **Private** plutôt que Public si tu peux — même
sans token dedans, ça évite d'exposer inutilement le fonctionnement interne
du bot. Un repo Public fonctionne aussi très bien pour l'hébergement gratuit
ci-dessous, ça ne change rien techniquement.

## 2. Héberger 24/7 gratuitement (Render)

Tu as choisi l'option gratuite et simple. Le compromis : les hébergeurs
gratuits mettent le service en veille après quelques minutes sans requête
HTTP — on contourne ça avec un petit "ping" automatique toutes les 5-10 min
(déjà prévu dans `keep_alive.py`). Ce n'est pas garanti à 100% (le service
peut quand même redémarrer de temps en temps), mais ça tourne en pratique
la grande majorité du temps.

### Étapes sur Render (https://render.com)

1. Crée un compte Render (gratuit, connexion avec GitHub la plus simple)
2. **New +** → **Web Service**
3. Connecte ton repo GitHub `Domino`
4. Renseigne :
   - **Name** : `domino-bot` (ou ce que tu veux)
   - **Runtime** : Python 3
   - **Build Command** : `pip install -r requirements.txt`
   - **Start Command** : `python Domino_bot.py`
   - **Instance Type** : Free
5. Dans **Environment Variables**, ajoute :
   - `DISCORD_TOKEN` = ton token (celui régénéré à l'étape 0)
6. Clique **Create Web Service** → Render build et démarre le bot.
   Regarde les logs, tu dois voir `Logged in as ...`.

Render te donne une URL publique du style `https://domino-bot.onrender.com`
— c'est cette URL qu'on va "pinguer" pour éviter la mise en veille.

### Empêcher la mise en veille (UptimeRobot, gratuit)

1. Crée un compte sur https://uptimerobot.com (gratuit)
2. **Add New Monitor**
   - Monitor Type : `HTTP(s)`
   - URL : ton URL Render (ex: `https://domino-bot.onrender.com`)
   - Monitoring Interval : `5 minutes`
3. Sauvegarde. UptimeRobot va appeler ton bot toutes les 5 min, ce qui
   empêche Render de le mettre en veille.

C'est tout — ton bot doit maintenant tourner en continu.

## 3. Tester en local (optionnel)

```bash
cp .env.example .env
# édite .env et colle ton token à la place de "colle_ton_token_ici"
pip install -r requirements.txt
python Domino_bot.py
```

## Notes techniques

- `ffmpeg` doit être installé sur l'hébergeur pour que les commandes audio
  fonctionnent (Render l'inclut par défaut sur ses images Python).
- Le fichier `keep_alive.py` ouvre juste un petit serveur web (port 8080)
  utilisé uniquement pour le ping ci-dessus ; il ne fait rien d'autre.
