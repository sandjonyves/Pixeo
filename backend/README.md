# Pixeo — Backend Django

> **Statut : lot A5.** PostgreSQL 17.6 est disponible via Docker Compose, la
> migration initiale `accounts.0001_initial` est versionnée et appliquée, Django
> Admin gère le modèle utilisateur Pixeo et le health check vérifie réellement la
> base. La fondation API REST et l'authentification JWT sont en place :
> versionnement `/api/v1/`, enveloppes de réponse, erreurs centralisées,
> pagination, permissions, camelCase, OpenAPI, login/refresh/logout/profil,
> cookie HttpOnly, rotation/blacklist et CSRF/CORS. Aucun endpoint métier,
> d'inscription ou de paiement n'est encore exposé.

## 1. Prérequis

| Outil | Version / usage |
|-------|-----------------|
| Python | 3.12.3 |
| Django | 5.2.18 LTS |
| PostgreSQL | 17.6 (Docker Compose) |
| Docker | Docker Engine + plugin Compose v2 |
| Base de développement | PostgreSQL (`backend/docker-compose.yml`) |
| Base de production | PostgreSQL via `DATABASE_URL` |
| Redis | Optionnel en local ; requis pour cache/Celery/rate limiting distribué |

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

## 6. Fondation API REST (A4) et authentification (A5)

L'API publique est versionnée sous `/api/v1/`. Le routeur DRF est défini dans
`apps/api/urls.py` ; les routes d'authentification y sont montées sous
`/api/v1/auth/` et les futurs ViewSets pourront être enregistrés sans changer le
préfixe public.

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

- `IsPhotographer` : compte photographe authentifié, actif et non suspendu ;
- `IsPlatformAdmin` : administrateur plateforme actif et non suspendu ;
- `AllowAny` : vue publique explicitement déclarée.

La permission par défaut reste `IsAuthenticated`. Les classes d'authentification
rechargent le compte à chaque requête ; une suspension ou une désactivation est
donc appliquée immédiatement, même avec un ancien token. L'isolation
multi-tenant sera ajoutée dans les lots métier.

### Authentification A5

| Méthode | URL | Rôle |
|---------|-----|------|
| POST | `/api/v1/auth/login/` | Vérifie les identifiants, retourne l'access token et pose le cookie de refresh (CSRF + JSON obligatoires) |
| POST | `/api/v1/auth/refresh/` | Rotation du refresh token, protégée par CSRF |
| POST | `/api/v1/auth/logout/` | Blacklist du refresh et suppression du cookie, protégé par CSRF |
| GET | `/api/v1/auth/me/` | Profil courant sans mot de passe ni jeton |
| GET | `/api/v1/auth/csrf/` | Retourne un jeton CSRF et pose le cookie CSRF |

Règles appliquées :

- l'access token est un JWT de 10 minutes par défaut, envoyé dans
  `Authorization: Bearer <token>` et conservé en mémoire côté frontend ;
- le refresh token est uniquement dans un cookie `HttpOnly`, `SameSite=Lax`,
  `Secure` en production, host-only et limité au chemin `/api/v1/auth/` ;
- le refresh est tourné et l'ancien jeton blacklisté à chaque renouvellement ;
- la réutilisation d'un ancien refresh est refusée avec `TOKEN_REVOKED` ;
  SimpleJWT ne révoque pas toute la famille : le refresh suivant reste valide
  dans la politique A5 ;
- le frontend envoie `X-CSRFToken` sur `login`, `refresh` et `logout` ; le login
  exige aussi le CSRF car il crée une session et dépose un cookie ;
- le login n'accepte que `application/json` ; les formulaires HTML classiques ne
  peuvent pas créer de session ;
- un compte `is_active=False` ou `is_suspended=True` est refusé avec
  `ACCOUNT_DISABLED` ou `ACCOUNT_SUSPENDED`, au login, au refresh et à chaque
  requête authentifiée ;
- le login est limité à 5 tentatives/minute et le refresh à 30/minute par défaut ;
- aucun refresh token, mot de passe ou hash n'est renvoyé ou journalisé.

Un logout révoque le refresh, mais un access token déjà émis reste valide
jusqu'à son expiration. Aucun endpoint d'inscription, de changement de mot de
passe ou de récupération de mot de passe n'est exposé en A5.

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
| `CORS_ALLOWED_ORIGIN_REGEXES` | Regex CORS explicites ; vide par défaut en production |
| `CSRF_TRUSTED_ORIGINS` | Origines de confiance CSRF |
| `CACHE_URL` | URL Redis ; vide = cache local en développement |
| `AUTH_REFRESH_COOKIE_NAME` | Nom du cookie refresh (`pixeo_refresh`) |
| `AUTH_REFRESH_COOKIE_SECURE` | `False` en local, `True` en production |
| `AUTH_REFRESH_COOKIE_SAMESITE` | `Lax` par défaut |
| `AUTH_REFRESH_COOKIE_PATH` | `/api/v1/auth/` par défaut |
| `AUTH_REFRESH_COOKIE_DOMAIN` | Vide = cookie host-only |
| `AUTH_ACCESS_TOKEN_LIFETIME_MINUTES` | Durée de l'access token (10 par défaut) |
| `AUTH_REFRESH_TOKEN_LIFETIME_DAYS` | Durée du refresh token (7 par défaut) |
| `AUTH_LOGIN_RATE` | Quota login (`5/min` par défaut) |
| `AUTH_REFRESH_RATE` | Quota refresh (`30/min` par défaut) |
| `CSRF_COOKIE_PATH`, `CSRF_COOKIE_SAMESITE` | Cookie CSRF ; `/` et `Lax` par défaut |
| `STORAGE_BACKEND` | `local` ou `s3` |
| `S3_*` | Configuration S3 / Cloudflare R2 |

La production refuse notamment `DEBUG=True`, SQLite, l'absence de
`ALLOWED_HOSTS`, de `CSRF_TRUSTED_ORIGINS` et de cache Redis. Elle exige au moins
une origine CORS explicite et n'active aucun wildcard CORS de sous-domaines
tenants par défaut. Les cookies de refresh et CSRF restent host-only.

## 9. Tests et vérifications

```bash
cd backend
source .venv/bin/activate

# Tests d'intégration sur PostgreSQL (base de test créée par pytest)
pytest -q

# Tests ciblés de la fondation API et de l'authentification
pytest apps/api/tests apps/accounts/tests/test_auth_*.py -q

# Même suite avec application des migrations dans la base de test
pytest -q -o addopts=''

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
test est alors créée par syncdb. L'option `-o addopts=''` ci-dessus retire
`--no-migrations` et applique réellement les migrations. La base PostgreSQL
persistante `pixeo` n'est pas utilisée par pytest : pytest crée et détruit une
base de test séparée. La suite A5 compte **217 tests**.

Pour la vérification production, fournir au minimum `DJANGO_SECRET_KEY`,
`DJANGO_ALLOWED_HOSTS`, `DATABASE_URL` PostgreSQL, `CACHE_URL`, au moins une
origine CORS explicite et `CSRF_TRUSTED_ORIGINS`. `AUTH_REFRESH_COOKIE_SECURE`
passe à `True` et les cookies CSRF/session sont `Secure` en production.

## 10. Endpoints techniques et d'authentification

| Méthode | URL | Rôle |
|---------|-----|------|
| GET | `/api/v1/` | Racine versionnée, enveloppe de succès |
| GET | `/api/v1/health/` | Health check Django + PostgreSQL |
| GET | `/api/v1/schema/` | Schéma OpenAPI (`?format=json` pour JSON) |
| GET | `/api/v1/docs/` | Documentation Swagger UI |
| GET | `/api/v1/redoc/` | Documentation ReDoc |
| POST | `/api/v1/auth/login/` | Connexion et cookie de refresh |
| POST | `/api/v1/auth/refresh/` | Rotation du refresh, avec CSRF |
| POST | `/api/v1/auth/logout/` | Révocation du refresh, avec CSRF |
| GET | `/api/v1/auth/me/` | Profil courant authentifié |
| GET | `/api/v1/auth/csrf/` | Jeton CSRF |
| — | `/admin/` | Django Admin du modèle `User` |

La documentation OpenAPI est publique en développement et réservée aux
administrateurs authentifiés par session Django en production.

Aucun endpoint d'inscription, de galerie, de photo, d'abonnement ou de paiement
n'existe encore. Les endpoints `PATCH /auth/me/`, de changement de mot de passe
et de réinitialisation restent à implémenter dans les lots ultérieurs.
