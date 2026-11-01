# Pixeo — Backend Django

> **Statut : lot A2.** Fondation Django, configuration par environnement et modèle
> utilisateur custom. Aucun endpoint métier, aucune migration, aucun PostgreSQL
> démarré et aucun superutilisateur persistant créé. Le test du manager utilise un
> objet superuser éphémère dans la base SQLite de test.

## 1. Prérequis

| Outil | Version / usage |
|-------|-----------------|
| Python | 3.12.3 |
| Django | 5.2.18 LTS |
| Base locale | SQLite (`backend/db.sqlite3`) |
| Base production | PostgreSQL via `DATABASE_URL` |
| Redis | Optionnel en A2 ; requis pour cache/Celery/rate limiting distribué |

## 2. Installation

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

Créer la configuration locale :

```bash
cp .env.example .env
# Remplacer DJANGO_SECRET_KEY par une valeur locale longue et aléatoire.
```

`backend/.env` et `backend/.venv/` sont ignorés par Git.

## 3. Démarrage

```bash
cd backend
source .venv/bin/activate

# Vérification Django
python manage.py check

# Serveur local
python manage.py runserver 0.0.0.0:8000
```

`manage.py` utilise `config.settings.development` par défaut. Les points d'entrée
WSGI/ASGI utilisent `config.settings.production` par défaut.

Sélection explicite :

```bash
DJANGO_SETTINGS_MODULE=config.settings.development python manage.py check
DJANGO_SETTINGS_MODULE=config.settings.production python manage.py check
```

## 4. Variables d'environnement principales

| Variable | Rôle |
|----------|------|
| `DJANGO_SETTINGS_MODULE` | Module de settings (`development` ou `production`) |
| `DJANGO_SECRET_KEY` | Secret Django, obligatoire |
| `DJANGO_DEBUG` | `True` en local, interdit en production |
| `DJANGO_ALLOWED_HOSTS` | Hôtes autorisés, séparés par des virgules |
| `DJANGO_LOG_LEVEL` | Niveau de journalisation |
| `PIXEO_BASE_DOMAIN` | Domaine de base des tenants (`lvh.me` en local) |
| `PIXEO_APP_URL`, `PIXEO_ADMIN_URL`, `PIXEO_API_URL` | URLs des applications |
| `DATABASE_URL` | SQLite en local, PostgreSQL en production |
| `CORS_ALLOWED_ORIGINS` | Origines frontend autorisées explicitement |
| `CORS_ALLOWED_ORIGIN_REGEXES` | Regex des sous-domaines tenants |
| `CSRF_TRUSTED_ORIGINS` | Origines de confiance CSRF |
| `CACHE_URL` | URL Redis ; vide = cache local en développement |
| `AUTH_REFRESH_COOKIE_*` | Cookie refresh JWT (HttpOnly, SameSite) |
| `STORAGE_BACKEND` | `local` ou `s3` |
| `S3_*` | Configuration S3 / Cloudflare R2 |

La production refuse notamment `DEBUG=True`, SQLite, l'absence de
`ALLOWED_HOSTS`, de `CSRF_TRUSTED_ORIGINS` et de cache Redis.

## 5. Modèle utilisateur

`apps/accounts/models.py` définit `User` avant toute migration :

- `id` UUID, `email` unique comme `USERNAME_FIELD` ;
- pas de champ `username` ;
- `branding_username` unique, normalisé en minuscules, label DNS sûr et noms
  réservés refusés ;
- `role` (`photographer` / `platform_admin`) ;
- `is_active`, `is_suspended`, `suspended_at` ;
- `created_at`, `updated_at`, `date_joined` ;
- manager email + `full_clean()` à la création ;
- `AUTH_USER_MODEL = "accounts.User"`.

Le plan actif ne sera **jamais** stocké sur `User` : il viendra de
`billing.Subscription` dans un lot ultérieur.

## 6. Tests

```bash
cd backend
source .venv/bin/activate
pytest -q
```

`pytest.ini` active `--no-migrations` : les tests utilisent une base SQLite
temporaire créée par syncdb, sans générer ni exécuter de fichier de migration.

Vérifications complémentaires :

```bash
python -m pip check
python manage.py check
python manage.py check --settings=config.settings.production
```

Pour la vérification production, fournir au minimum `DJANGO_SECRET_KEY`,
`DJANGO_ALLOWED_HOSTS`, `DATABASE_URL` PostgreSQL, `CACHE_URL`,
`CORS_ALLOWED_ORIGINS`/`CORS_ALLOWED_ORIGIN_REGEXES` et `CSRF_TRUSTED_ORIGINS`.

## 7. Endpoints techniques A2

| Méthode | URL | Rôle |
|---------|-----|------|
| GET | `/api/v1/health/` | Health check sans accès base |
| GET | `/api/v1/schema/` | Schéma OpenAPI |
| GET | `/api/v1/docs/` | Documentation Swagger UI |
| — | `/admin/` | Admin Django (aucun superutilisateur persistant créé) |

Aucun endpoint d'inscription, de connexion, de galerie ou de paiement n'existe.

## 8. Migrations — avertissement A2

**Aucune migration n'est créée ou exécutée dans ce lot.** Le modèle utilisateur
custom doit être définitivement validé avant la première migration. Les commandes
suivantes sont réservées au lot A3 :

```bash
# NE PAS EXÉCUTER EN A2
# python manage.py makemigrations accounts
# python manage.py migrate
```
