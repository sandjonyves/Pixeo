# Pixeo — Développement local et sous-domaines

> **Statut : lot A4.** PostgreSQL 17.6 est disponible via Docker Compose, la
> migration initiale `accounts.0001_initial` est appliquée, Django Admin gère le
> modèle utilisateur, le health check vérifie la base et la fondation API REST
> (`/api/v1/`, erreurs, pagination, camelCase, OpenAPI) est en place. Aucun
> endpoint métier ni authentification JWT n'est encore exposé.

## 1. Prérequis

| Outil | Version utilisée / cible |
|-------|--------------------------|
| Python | 3.12.3 |
| pip | 26.2.2 (dans `backend/.venv`) |
| Node.js | selon le frontend existant |
| pnpm | selon `package.json` |
| PostgreSQL | 17.6 via Docker Compose (développement et production) |
| Docker | Docker Engine + plugin Compose v2 |
| SQLite | tests unitaires isolés en mémoire uniquement |
| Redis | optionnel en A3, requis pour cache/Celery/rate limiting distribué |

## 2. Environnement Python

Le venv est créé dans `backend/.venv` et ignoré par Git.

```bash
cd backend
source .venv/bin/activate
python --version
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

Configuration locale :

```bash
cp .env.example .env
# adapter DJANGO_SECRET_KEY, POSTGRES_PASSWORD et DATABASE_URL
```

Générer un mot de passe PostgreSQL fort, puis reporter la même valeur dans
`POSTGRES_PASSWORD` et dans l'URL `DATABASE_URL`. Ne jamais committer
`backend/.env`.

Vérification et démarrage (démarrer PostgreSQL et appliquer les migrations au
préalable, voir section 6) :

```bash
python manage.py check
python manage.py migrate
python manage.py runserver 0.0.0.0:8000
```

`manage.py` charge `config.settings.development` par défaut. Les points d'entrée
WSGI/ASGI utilisent `config.settings.production` par défaut.

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
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1,.lvh.me,.pixeo.localhost
CORS_ALLOWED_ORIGINS=http://app.lvh.me:3000,http://admin.lvh.me:3000,http://yves.lvh.me:3000
CORS_ALLOWED_ORIGIN_REGEXES=^http://[a-z0-9-]+\.lvh\.me:3000$
CSRF_TRUSTED_ORIGINS=http://app.lvh.me:3000,http://admin.lvh.me:3000,http://api.lvh.me:8000,http://*.lvh.me:3000
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
- Le refresh token est un cookie `HttpOnly`. En A3, les cookies restent host-only ;
  aucun domaine global `.lvh.me` ou `.pixeo.com` n'est imposé.
- La stratégie inter-sous-domaines (partage éventuel des cookies) sera décidée et
  testée aux lots C2/C3.
- En local : `AUTH_REFRESH_COOKIE_SECURE=False`, `CSRF_COOKIE_SECURE=False`,
  `SECURE_SSL_REDIRECT=False`.
- En production : HTTPS obligatoire, cookies `Secure`, HSTS.

## 5. Ports

| Service | Port local |
|---------|------------|
| Next.js | 3000 |
| Django / DRF | 8000 |
| PostgreSQL | 5432 (`POSTGRES_PORT`, configurable) |
| Redis | 6379 |

## 6. PostgreSQL local

Le service PostgreSQL est défini dans `backend/docker-compose.yml` :

- image stable `postgres:17.6-alpine` ;
- base `pixeo`, utilisateur `pixeo` ;
- mot de passe lu depuis `POSTGRES_PASSWORD` ;
- port local configurable via `POSTGRES_PORT` (5432 par défaut), exposé
  uniquement sur `127.0.0.1` ;
- volume persistant `pixeo_postgres_data` ;
- healthcheck `pg_isready` et redémarrage `unless-stopped`.

Depuis `backend/` :

```bash
# Démarrer
docker compose up -d

# Attendre le healthcheck
docker compose ps

# Vérifier PostgreSQL
docker compose exec postgres pg_isready -U pixeo -d pixeo

# Logs
docker compose logs -f postgres

# Arrêt / redémarrage sans perte de données
docker compose stop postgres
docker compose start postgres
```

**Ne jamais exécuter `docker compose down -v`** sans autorisation explicite :
cette commande supprime le volume et toutes les données locales.

Django se connecte avec `DATABASE_URL`, par exemple :

```dotenv
POSTGRES_DB=pixeo
POSTGRES_USER=pixeo
POSTGRES_PASSWORD=<mot-de-passe-fort>
POSTGRES_PORT=5432
DATABASE_URL=postgresql://pixeo:<mot-de-passe-fort>@127.0.0.1:5432/pixeo
DATABASE_CONN_MAX_AGE=60
```

Les connexions persistantes utilisent `CONN_HEALTH_CHECKS` lorsque
`DATABASE_CONN_MAX_AGE` est supérieur à zéro.

### Migrations

```bash
cd backend
source .venv/bin/activate

python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py migrate
python manage.py showmigrations
```

La migration initiale `accounts.0001_initial` crée `accounts_user` avec une clé
primaire UUID et les contraintes d'unicité sur `email` et `branding_username`.
Elle est versionnée dans Git.

### Superutilisateur et admin

```bash
python manage.py createsuperuser
```

La commande demande l'e-mail, le `branding_username` et le mot de passe. Le
compte est créé avec `is_staff=True`, `is_superuser=True` et
`role=platform_admin`. Le mot de passe est hashé et ne doit jamais être placé
dans un fichier versionné.

Django Admin : `http://localhost:8000/admin/`.

### Health endpoint

```bash
curl -i http://localhost:8000/api/v1/health/
```

- HTTP 200 : `{"ok": true, "service": "pixeo", "database": "available"}` ;
- HTTP 503 : `{"ok": false, "service": "pixeo", "database": "unavailable"}`.

La réponse n'expose aucun identifiant ni détail d'exception.

### Documentation et racine API

En développement, la documentation OpenAPI est librement accessible :

```bash
curl -i http://localhost:8000/api/v1/
curl -s http://localhost:8000/api/v1/schema/?format=json | head
```

- Swagger UI : <http://localhost:8000/api/v1/docs/>
- ReDoc : <http://localhost:8000/api/v1/redoc/>

En production, ces trois routes de documentation sont réservées aux
administrateurs authentifiés via la session Django. Le health check reste
disponible publiquement pour les sondes d'infrastructure.

## 7. Vérifications rapides

```bash
# Venv et dépendances
backend/.venv/bin/python --version
backend/.venv/bin/pip check

# PostgreSQL
cd backend
docker compose ps
docker compose exec postgres pg_isready -U pixeo -d pixeo

# Django, migrations et tests
.venv/bin/python manage.py check
.venv/bin/python manage.py makemigrations --check --dry-run
.venv/bin/python manage.py showmigrations
.venv/bin/python -m pytest -q

# Suite avec migrations réellement appliquées à la base de test
.venv/bin/python -m pytest -q -o addopts='-ra --strict-markers'

# Tests unitaires SQLite en mémoire
DATABASE_URL='sqlite:///:memory:' .venv/bin/python -m pytest -q

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
