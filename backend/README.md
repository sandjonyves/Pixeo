# Pixeo — Backend Django

> **Statut : lot A4.** PostgreSQL 17.6 est disponible via Docker Compose, la
> migration initiale `accounts.0001_initial` est versionnée et appliquée, Django
> Admin gère le modèle utilisateur Pixeo et le health check vérifie réellement la
> base. La fondation API REST est en place : versionnement `/api/v1/`, enveloppes
> de réponse, erreurs centralisées, pagination, permissions de base, camelCase et
> documentation OpenAPI. Aucun endpoint métier ni authentification JWT n'est
> encore exposé.

## 1. Prérequis

| Outil | Version / usage |
|-------|-----------------|
| Python | 3.12.3 |
| Django | 5.2.18 LTS |
| PostgreSQL | 17.6 (Docker Compose) |
| Docker | Docker Engine + plugin Compose v2 |
| Base de développement | PostgreSQL (`backend/docker-compose.yml`) |
| Base de production | PostgreSQL via `DATABASE_URL` |
| Redis | Optionnel en A4 ; requis pour cache/Celery/rate limiting distribué |

SQLite reste utilisable uniquement pour des tests unitaires isolés en mémoire.

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
```

Renseigner au minimum :

- `DJANGO_SECRET_KEY` avec une valeur locale longue et aléatoire ;
- `POSTGRES_PASSWORD` avec un mot de passe fort et unique ;
- `DATABASE_URL` avec le même mot de passe que `POSTGRES_PASSWORD`.

`backend/.env` et `backend/.venv/` sont ignorés par Git. Ne jamais committer
`backend/.env` ni y placer un secret de production.

## 3. PostgreSQL local avec Docker Compose

Le fichier `backend/docker-compose.yml` définit :

- l'image `postgres:17.6-alpine` ;
- la base `pixeo` et l'utilisateur `pixeo` ;
- un mot de passe lu depuis `POSTGRES_PASSWORD` ;
- un port configurable via `POSTGRES_PORT` (5432 par défaut), publié uniquement
  sur `127.0.0.1` ;
- un volume persistant nommé `pixeo_postgres_data` ;
- un healthcheck `pg_isready` et un redémarrage `unless-stopped`.

Commandes, depuis `backend/` :

```bash
# Démarrer PostgreSQL
docker compose up -d

# Vérifier le service et son healthcheck
docker compose ps

# Vérifier PostgreSQL directement
docker compose exec postgres pg_isready -U pixeo -d pixeo

# Consulter les logs
docker compose logs -f postgres

# Arrêter sans supprimer les données
docker compose stop postgres

# Redémarrer
docker compose start postgres
```

**Ne jamais exécuter `docker compose down -v`** : cela supprimerait le volume et
les données locales. En cas de problème de connexion, diagnostiquer les logs et
le healthcheck sans supprimer le volume.

## 4. Connexion Django et migrations

`manage.py` charge `config.settings.development` par défaut. La connexion est
centralisée dans `DATABASE_URL`, avec `DATABASE_CONN_MAX_AGE` pour les connexions
persistantes et `CONN_HEALTH_CHECKS` activé lorsqu'elles sont utilisées.

Vérifier la connexion réelle avant toute migration :

```bash
python manage.py check
python manage.py shell -c "from django.db import connection; connection.ensure_connection(); print(connection.vendor, connection.pg_version)"
```

Appliquer et contrôler les migrations :

```bash
# Aucun changement de modèle ne doit être en attente
python manage.py makemigrations --check --dry-run

# Appliquer les migrations versionnées
python manage.py migrate

# Vérifier qu'aucune migration n'est en attente
python manage.py showmigrations
```

La migration initiale est `backend/apps/accounts/migrations/0001_initial.py`.
Elle crée `accounts.User` avec une clé primaire UUID, l'e-mail unique et le
`branding_username` unique. Les migrations font partie du code source et doivent
être versionnées.

## 5. Superutilisateur et Django Admin

Créer un superutilisateur avec la commande Django standard :

```bash
python manage.py createsuperuser
```

La commande demande l'e-mail, le `branding_username` et le mot de passe. Le
manager Pixeo force `is_staff=True`, `is_superuser=True` et
`role=platform_admin`. Le mot de passe est hashé et n'est jamais enregistré dans
le dépôt, une migration ou un fichier `.env` versionné.

Django Admin est accessible sur :

```text
http://localhost:8000/admin/
```

La fiche utilisateur permet de consulter et gérer :

- l'e-mail et le nom public `branding_username` ;
- le rôle, le statut actif et la suspension ;
- les dates de création et de modification ;
- la recherche par e-mail, nom public, prénom et nom ;
- les filtres par rôle et statut (actif / inactif / suspendu).

Le hash du mot de passe est affiché en lecture seule et n'est jamais modifiable
comme un champ ordinaire. Le formulaire de création hash le mot de passe et
applique les validateurs du modèle. `suspended_at` est maintenu automatiquement
lorsqu'un administrateur active ou retire la suspension. Un superutilisateur doit
conserver `role=platform_admin` : le formulaire admin refuse toute combinaison
contraire via `full_clean()`.

## 6. Fondation API REST (A4)

L'API publique est versionnée sous `/api/v1/`. Le routeur DRF est défini dans
`apps/api/urls.py` ; les futurs ViewSets y seront enregistrés.

### Enveloppes

Succès :

```json
{
  "ok": true,
  "data": {}
}
```

Erreur :

```json
{
  "ok": false,
  "error": "Les données fournies sont invalides.",
  "code": "VALIDATION_ERROR",
  "details": {
    "fieldName": ["Message"]
  }
}
```

Les codes sont stables et en majuscules. Les erreurs 400, 401, 403, 404, 405,
429 et 500 sont normalisées par `apps/api/exceptions.py`. Les erreurs internes
ne renvoient ni trace Python, ni secret, ni détail base de données.

### Pagination et camelCase

Les listes acceptent `page` et `page_size` (20 par défaut, 100 maximum). La
réponse contient `items`, `total`, `page` et `pageSize`.

Les serializers métier doivent hériter de `PixeoSerializer` ou
`PixeoModelSerializer`. Ils convertissent récursivement les clés en camelCase à
l'entrée et à la sortie, y compris dans les structures imbriquées et les erreurs
de validation.

### Permissions

- `IsPhotographer` : compte photographe authentifié ;
- `IsPlatformAdmin` : administrateur plateforme ;
- `AllowAny` : vue publique explicitement déclarée.

La permission par défaut reste `IsAuthenticated`. L'isolation multi-tenant sera
ajoutée dans les lots métier.

## 7. Health endpoint

| Méthode | URL | Rôle |
|---------|-----|------|
| GET | `/api/v1/health/` | Vérifie Django et exécute `SELECT 1` sur PostgreSQL |

Réponse lorsque la base est disponible (HTTP 200) :

```json
{
  "ok": true,
  "service": "pixeo",
  "database": "available"
}
```

Réponse lorsque la base est indisponible (HTTP 503) :

```json
{
  "ok": false,
  "service": "pixeo",
  "database": "unavailable"
}
```

La réponse n'expose ni identifiants, ni hôte, ni détail d'exception.

## 8. Variables d'environnement principales

| Variable | Rôle |
|----------|------|
| `DJANGO_SETTINGS_MODULE` | Module de settings (`development` ou `production`) |
| `DJANGO_SECRET_KEY` | Secret Django, obligatoire |
| `DJANGO_DEBUG` | `True` en local, interdit en production |
| `DJANGO_ALLOWED_HOSTS` | Hôtes autorisés, séparés par des virgules |
| `DJANGO_LOG_LEVEL` | Niveau de journalisation |
| `PIXEO_BASE_DOMAIN` | Domaine de base des tenants (`lvh.me` en local) |
| `PIXEO_APP_URL`, `PIXEO_ADMIN_URL`, `PIXEO_API_URL` | URLs des applications |
| `POSTGRES_DB`, `POSTGRES_USER` | Base et utilisateur du conteneur PostgreSQL |
| `POSTGRES_PASSWORD` | Mot de passe PostgreSQL, jamais versionné |
| `POSTGRES_PORT` | Port local PostgreSQL (5432 par défaut) |
| `DATABASE_URL` | URL PostgreSQL de Django |
| `DATABASE_CONN_MAX_AGE` | Durée de réutilisation des connexions |
| `CORS_ALLOWED_ORIGINS` | Origines frontend autorisées explicitement |
| `CORS_ALLOWED_ORIGIN_REGEXES` | Regex des sous-domaines tenants |
| `CSRF_TRUSTED_ORIGINS` | Origines de confiance CSRF |
| `CACHE_URL` | URL Redis ; vide = cache local en développement |
| `AUTH_REFRESH_COOKIE_*` | Cookie refresh JWT (HttpOnly, SameSite) |
| `STORAGE_BACKEND` | `local` ou `s3` |
| `S3_*` | Configuration S3 / Cloudflare R2 |

La production refuse notamment `DEBUG=True`, SQLite, l'absence de
`ALLOWED_HOSTS`, de `CSRF_TRUSTED_ORIGINS` et de cache Redis.

## 9. Tests et vérifications

```bash
cd backend
source .venv/bin/activate

# Tests d'intégration sur PostgreSQL (base de test créée par pytest)
pytest -q

# Tests ciblés de la fondation API
pytest apps/api/tests -q

# Même suite avec application des migrations dans la base de test
pytest -q -o addopts='-ra --strict-markers'

# Tests unitaires isolés sur SQLite en mémoire
DATABASE_URL='sqlite:///:memory:' pytest -q

# Vérifications statiques
python -m pip check
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py showmigrations

# Validation du schéma OpenAPI
python manage.py spectacular --validate --file /tmp/pixeo-openapi.yaml
```

`pytest.ini` active `--no-migrations` pour les exécutions rapides : la base de
test est alors créée par syncdb. L'option `-o addopts=...` ci-dessus retire
`--no-migrations` et applique réellement les migrations. La base PostgreSQL
persistante `pixeo` n'est pas utilisée par pytest : pytest crée et détruit une
base de test séparée.

Pour la vérification production, fournir au minimum `DJANGO_SECRET_KEY`,
`DJANGO_ALLOWED_HOSTS`, `DATABASE_URL` PostgreSQL, `CACHE_URL`,
`CORS_ALLOWED_ORIGINS`/`CORS_ALLOWED_ORIGIN_REGEXES` et `CSRF_TRUSTED_ORIGINS`.

## 10. Endpoints techniques A4

| Méthode | URL | Rôle |
|---------|-----|------|
| GET | `/api/v1/` | Racine versionnée, enveloppe de succès |
| GET | `/api/v1/health/` | Health check Django + PostgreSQL |
| GET | `/api/v1/schema/` | Schéma OpenAPI (`?format=json` pour JSON) |
| GET | `/api/v1/docs/` | Documentation Swagger UI |
| GET | `/api/v1/redoc/` | Documentation ReDoc |
| — | `/admin/` | Django Admin du modèle `User` |

La documentation OpenAPI est publique en développement et réservée aux
administrateurs authentifiés par session Django en production.

Aucun endpoint d'inscription, de connexion JWT, de galerie ou de paiement
n'existe encore.
