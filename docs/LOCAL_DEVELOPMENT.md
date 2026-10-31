# Pixeo — Développement local et sous-domaines

> **Statut : lot A1.** L'environnement Python et les dépendances sont installés.
> Le projet Django lui-même sera créé au lot A2.

## 1. Prérequis

| Outil | Version utilisée / cible |
|-------|--------------------------|
| Python | 3.12.3 |
| pip | 26.2.2 (dans `backend/.venv`) |
| Node.js | selon le frontend existant |
| pnpm | selon `package.json` |
| PostgreSQL | production ; SQLite accepté en développement |
| Redis | optionnel en A1, requis pour cache/Celery/rate limiting distribué |

## 2. Environnement Python

Le venv est créé dans `backend/.venv` et ignoré par Git.

```bash
cd backend
source .venv/bin/activate
python --version
pip install -r requirements.txt
```

Configuration locale :

```bash
cp .env.example .env
# adapter les valeurs si nécessaire
```

Ne jamais committer `backend/.env`.

## 3. Stratégie de sous-domaines

Pixeo résout le photographe à partir du sous-domaine. Pour reproduire ce
comportement en local, deux options existent.

### Option recommandée : `lvh.me`

`lvh.me` et ses sous-domaines résolvent vers `127.0.0.1` sans modification du
fichier `hosts`. C'est l'option qui se rapproche le plus de la production et qui
fonctionne bien avec les cookies de sous-domaines.

| Usage | URL locale |
|-------|------------|
| Application photographe | `http://app.lvh.me:3000` |
| Console admin | `http://admin.lvh.me:3000` |
| API | `http://api.lvh.me:8000` |
| Homepage photographe | `http://yves.lvh.me:3000` |
| Galerie publique | `http://yves.lvh.me:3000/mariage-2026` |
| Lien pre-release | `http://yves.lvh.me:3000/p/{shareToken}` |

Configuration correspondante :

```dotenv
PIXEO_BASE_DOMAIN=lvh.me
PIXEO_APP_URL=http://app.lvh.me:3000
PIXEO_ADMIN_URL=http://admin.lvh.me:3000
PIXEO_API_URL=http://api.lvh.me:8000
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1,.lvh.me
CORS_ALLOWED_ORIGINS=http://app.lvh.me:3000,http://admin.lvh.me:3000,http://yves.lvh.me:3000
CSRF_TRUSTED_ORIGINS=http://app.lvh.me:3000,http://admin.lvh.me:3000,http://api.lvh.me:8000
```

### Option de repli : `*.pixeo.localhost`

Les navigateurs modernes résolvent `*.localhost` vers la boucle locale. Sur la
machine de développement actuelle, `pixeo.localhost` résout vers `::1` (IPv6).
Cette option est pratique hors ligne, mais les cookies et certains outils HTTP
sont moins prévisibles qu'avec `lvh.me`.

Si nécessaire, ajouter dans `/etc/hosts` :

```text
127.0.0.1 app.pixeo.localhost admin.pixeo.localhost api.pixeo.localhost yves.pixeo.localhost
```

Puis adapter :

```dotenv
PIXEO_BASE_DOMAIN=pixeo.localhost
PIXEO_APP_URL=http://app.pixeo.localhost:3000
PIXEO_ADMIN_URL=http://admin.pixeo.localhost:3000
PIXEO_API_URL=http://api.pixeo.localhost:8000
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1,.pixeo.localhost
```

### Pourquoi pas `localhost` seul ?

`localhost` ne permet pas de distinguer plusieurs photographes par sous-domaine.
Il reste utile pour les tests unitaires et les health checks, mais pas pour
valider le multi-tenant, les cookies et les URLs publiques.

## 4. Cookies, CORS et CSRF en local

- Frontend : `app.lvh.me:3000`, API : `api.lvh.me:8000` → **cross-origin** mais
  **same-site** (même domaine `lvh.me`).
- Les requêtes API utilisent `credentials: "include"`.
- Le refresh token est un cookie `HttpOnly`. Par défaut, il est host-only sur
  `api.lvh.me`, ce qui suffit car seul l'API le lit.
- Si un partage de cookie entre sous-domaines devient nécessaire, définir
  `AUTH_REFRESH_COOKIE_DOMAIN=.lvh.me` (à valider dans le lot auth).
- En local : `AUTH_REFRESH_COOKIE_SECURE=False`, `CSRF_COOKIE_SECURE=False`,
  `SECURE_SSL_REDIRECT=False`.
- En production : HTTPS obligatoire, cookies `Secure`, HSTS.

## 5. Ports

| Service | Port local |
|---------|------------|
| Next.js | 3000 |
| Django / DRF | 8000 |
| PostgreSQL | 5432 |
| Redis | 6379 |

## 6. Base de données locale

A1 ne configure pas PostgreSQL et ne crée aucune migration.

- Développement immédiat : `DATABASE_URL=sqlite:///db.sqlite3`.
- Cible production : PostgreSQL via `DATABASE_URL`.
- Le projet Django et les modèles seront créés au lot A2 ; la première migration
  viendra après validation du modèle utilisateur custom.

## 7. Vérifications rapides

```bash
# Venv et dépendances
backend/.venv/bin/python --version
backend/.venv/bin/pip check

# Le venv et le fichier .env ne doivent pas être suivis par Git
git check-ignore -v backend/.venv backend/.env

# Aucun fichier frontend ne doit être modifié par le backend
git status --short
```

## 8. Production (rappel)

| Élément | Cible |
|---------|-------|
| DNS | `pixeo.com`, wildcard `*.pixeo.com`, `api`, `app`, `admin` |
| TLS | certificat wildcard ou automatique |
| API | `https://api.pixeo.com/` |
| App | `https://app.pixeo.com/` |
| Admin | `https://admin.pixeo.com/` |
| Photographe | `https://{username}.pixeo.com/` |

La disponibilité du domaine, le DNS wildcard et les certificats restent à vérifier
avant la mise en production.
