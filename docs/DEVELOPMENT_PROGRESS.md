# Pixeo — Développement backend

> Dernière mise à jour : 2026-11-03
> Lot en cours : **A5 — Authentification JWT et sessions** (réalisé, en attente de validation)

## 1. Méthode de travail

Le backend est développé par lots incrémentaux. Chaque lot suit ce cycle :

1. Présentation du périmètre.
2. Implémentation limitée au lot.
3. Vérifications réelles (commandes et résultats).
4. Compte rendu.
5. Validation explicite de l'utilisateur.
6. Commit Git séparé.

Aucun lot suivant n'est démarré sans validation explicite. Aucun fichier frontend
n'est modifié par les lots backend avant la Phase E.

## 2. État des lots

| Phase | Lot | Périmètre | Statut |
|-------|-----|-----------|--------|
| A | **A1** | Squelette `backend/`, venv, dépendances, `.env.example`, `.gitignore`, documentation, stratégie sous-domaines, audit nommage | **Réalisé — validé** |
| A | **A2** | Projet Django, settings, configuration, utilisateur custom | **Réalisé — validé** |
| A | **A3** | PostgreSQL, migration initiale, superutilisateur, Django Admin, health DB | **Réalisé — validé** |
| A | **A4** | Fondation API REST : versionnement, erreurs, pagination, camelCase, permissions, OpenAPI | **Réalisé — en attente de validation** |
| A | **A5** | Authentification JWT, cookie refresh, rotation/blacklist, CSRF/CORS, profil courant | **Réalisé — en attente de validation** |
| B | — | Studio, branding, homepage, plans/abonnements | Non démarré |
| C | — | Collections, photos, stockage, accès publics, favoris/notes | Non démarré |
| D | — | Intégration frontend et retrait du `localStorage` | Non démarré |
| E | — | Finalisation, durcissement et mise en production | Non démarré |

## 3. Lot A1 — livrables

| Élément | Chemin | État |
|---------|--------|------|
| Dossier backend | `backend/` | Créé |
| Environnement virtuel | `backend/.venv/` | Créé (ignoré par Git) |
| Dépendances runtime | `backend/requirements.txt` | Créé, versions figées |
| Configuration exemple | `backend/.env.example` | Créé |
| Règles d'ignore | `.gitignore` | Complété, règles existantes préservées |
| Architecture cible | `docs/ARCHITECTURE.md` | Mis à jour vers Django/DRF/Pixeo |
| Contrat API | `docs/API_DOCUMENTATION.md` | Créé (conception, aucun endpoint implémenté) |
| Développement local | `docs/LOCAL_DEVELOPMENT.md` | Créé (stratégie sous-domaines) |
| Suivi | `docs/DEVELOPMENT_PROGRESS.md` | Créé (ce document) |

## 4. Vérifications A1

| Vérification | Résultat |
|--------------|----------|
| Version Python | 3.12.3 |
| Venv | `backend/.venv` créé |
| pip dans le venv | 26.2.2 |
| Installation des dépendances | 53 paquets applicatifs (57 distributions avec pip/setuptools/wheel/packaging) |
| `pip check` | `No broken requirements found.` |
| Imports critiques | 19/19 modules importés avec succès |
| Django | 5.2.18 (`django.get_version()`) |
| DRF | 3.18.3 |
| Redis retenu | 6.4.0 (compatible `kombu[redis] < 6.5`) |
| Audit SimpleShoot | 0 référence trouvée |
| Fichiers frontend modifiés par A1 | 0 |
| Projet Django créé | Non (hors périmètre A1) |
| Modèles / migrations | Aucun (hors périmètre A1) |
| PostgreSQL configuré | Non (hors périmètre A1) |

## 5. Lot A2 — livrables et vérifications

### Livrables

| Élément | Chemin | État |
|---------|--------|------|
| Entrée Django | `backend/manage.py` | Créé |
| Configuration commune | `backend/config/settings/base.py` | Créé |
| Configuration locale | `backend/config/settings/development.py` | Créée |
| Configuration production | `backend/config/settings/production.py` | Créée |
| URLs techniques | `backend/config/urls.py`, `backend/config/views.py` | Créés |
| ASGI / WSGI | `backend/config/asgi.py`, `backend/config/wsgi.py` | Créés |
| Application accounts | `backend/apps/accounts/` | Créée |
| Modèle utilisateur | `backend/apps/accounts/models.py` | Créé |
| Validation branding | `backend/apps/accounts/validators.py` | Créée |
| Tests | `backend/apps/accounts/tests/` | 110 tests |
| Dépendances de test | `backend/requirements-dev.txt` | pytest 9.2.0, pytest-django 4.14.0 |
| Configuration pytest | `backend/pytest.ini` | Créée (`--no-migrations`) |
| Configuration exemple | `backend/.env.example` | Complétée |
| Guide backend | `backend/README.md` | Créé |

`backend/.env` a été créé localement pour les vérifications ; il est ignoré par
Git et ne fait pas partie du livrable. `backend/.venv/` reste inchangé et ignoré.

### Vérifications réellement exécutées

| Vérification | Résultat |
|--------------|----------|
| `pip install -r requirements-dev.txt` | pytest 9.2.0 et pytest-django 4.14.0 installés |
| `pip check` | `No broken requirements found.` |
| `python manage.py check` | `System check identified no issues (0 silenced).` |
| `manage.py check --settings=config.settings.production` (env de test) | `System check identified no issues (0 silenced).` |
| `pytest -q` | **110 passed**, 1 warning |
| `pytest --collect-only -q` | 110 tests collectés |
| Tests des 3 configurations | base, development et production chargées |
| Tests du modèle | `AUTH_USER_MODEL`, email, UUID, rôles, statuts, manager |
| Tests `branding_username` | format, noms réservés, minuscules, longueur, unicité |
| Test d'unicité en base | `IntegrityError` vérifiée sur une base SQLite de test isolée |
| Tests de sécurité | secrets, CORS, CSRF, cookies, HTTPS, Argon2, production |
| Migrations créées | **Aucune** |
| Migrations exécutées sur une base de développement | **Aucune** |
| PostgreSQL configuré / démarré | Non (hors périmètre A2) |
| Superutilisateur persistant créé | Non ; un objet éphémère est utilisé dans la base SQLite de test |
| Endpoints métier | Aucun (hors périmètre A2) |
| Fichiers frontend modifiés par A2 | 0 |

Le test de la base de test utilise `pytest-django --no-migrations` : les tables
sont créées par syncdb dans une base SQLite temporaire isolée, sans générer ni
exécuter de fichier de migration. La première migration réelle reste prévue en A3.

## 6. Lot A3 — livrables et vérifications

### Livrables

| Élément | Chemin | État |
|---------|--------|------|
| PostgreSQL local | `backend/docker-compose.yml` | Créé (`postgres:17.6-alpine`) |
| Migration initiale | `backend/apps/accounts/migrations/0001_initial.py` | Créée, versionnée et appliquée |
| Administration utilisateur | `backend/apps/accounts/admin.py` | Créée |
| Formulaires admin | `backend/apps/accounts/forms.py` | Créés |
| Health check base | `backend/config/views.py` | Mis à jour (`SELECT 1`, HTTP 503) |
| Tests admin | `backend/apps/accounts/tests/test_admin.py` | Créés |
| Tests schéma/migrations | `backend/apps/accounts/tests/test_database_schema.py`, `test_migrations.py` | Créés |
| Tests health | `backend/config/tests/test_health.py` | Créés |
| Configuration pytest | `backend/pytest.ini` | Étendue à `apps` et `config` |
| Guide backend | `backend/README.md` | Mis à jour |
| Documentation locale | `docs/LOCAL_DEVELOPMENT.md` | Mise à jour |

`backend/.env` contient le mot de passe PostgreSQL local et reste ignoré par Git.
Aucun secret réel n'est présent dans `backend/.env.example` ou dans le Compose.

### Vérifications réellement exécutées

| Vérification | Résultat |
|--------------|----------|
| Docker Compose | service `pixeo-postgres` démarré, healthcheck `healthy` |
| Version PostgreSQL | 17.6 (`pg_version=170006`) |
| Connexion Django réelle | `vendor=postgresql`, base `pixeo`, utilisateur `pixeo` |
| Migration `accounts.0001_initial` | appliquée sur PostgreSQL |
| `showmigrations` | toutes les migrations `[X]`, aucune en attente |
| `makemigrations --check --dry-run` | `No changes detected` |
| Table `accounts_user` | présente dans PostgreSQL |
| Contraintes | PK `id` UUID, `UNIQUE (email)`, `UNIQUE (branding_username)` |
| Superutilisateur local | créé, `platform_admin`, `is_staff=True`, `is_superuser=True`, hash Argon2 |
| Invariant rôle / superutilisateur | vérifié par `full_clean()` et refusé par le formulaire admin |
| Authentification par e-mail | `authenticate()` OK, insensible à la casse |
| Django Admin | `/admin/`, liste, recherche, filtres et fiche utilisateur accessibles (HTTP 200) |
| Health PostgreSQL disponible | HTTP 200, `database: available` |
| Health PostgreSQL indisponible | HTTP 503 après arrêt contrôlé du conteneur, sans fuite de détails |
| Persistance | superutilisateur toujours présent après `docker compose stop/start` |
| `pytest` PostgreSQL (`--no-migrations`) | **127 passed** |
| `pytest` PostgreSQL avec migrations | **127 passed** |
| `pytest` SQLite en mémoire | **127 passed** |
| `pip check` | `No broken requirements found.` |
| `manage.py check` | `System check identified no issues (0 silenced).` |
| Fichiers frontend modifiés par A3 | 0 |

Les tests PostgreSQL utilisent une base de test créée et détruite par pytest
(`test_pixeo`) ; la base persistante `pixeo` n'est pas modifiée par la suite de
tests. Le superutilisateur de validation est local ; son mot de passe n'est ni
versionné ni écrit dans un fichier du dépôt.

## 7. Lot A4 — fondation de l'API REST

### Livrables

| Élément | Chemin | État |
|---------|--------|------|
| Application API | `backend/apps/api/` | Créée |
| Serializers camelCase | `backend/apps/api/serializers.py` | Créé |
| Pagination | `backend/apps/api/pagination.py` | Créée |
| Gestion des erreurs | `backend/apps/api/exceptions.py` | Créée |
| Permissions de base | `backend/apps/api/permissions.py` | Créées |
| Racine versionnée | `backend/apps/api/views.py`, `urls.py` | Créées |
| Routeur versionné | `backend/config/urls.py`, `config/settings/base.py` | Configurés |
| Documentation OpenAPI | `config/urls.py`, `SPECTACULAR_SETTINGS` | Swagger UI, ReDoc et schéma |
| Tests API | `backend/apps/api/tests/` | Créés |
| Documentation | `backend/README.md`, `docs/API_DOCUMENTATION.md`, `docs/ARCHITECTURE.md` | Mise à jour |

Aucun endpoint métier, aucune authentification JWT, aucun modèle supplémentaire
et aucune migration ne sont ajoutés en A4.

### Vérifications réellement exécutées

| Vérification | Résultat |
|--------------|----------|
| `pytest -q` PostgreSQL (`--no-migrations`) | **157 passed** |
| `pytest -q -o addopts='-ra --strict-markers'` | **157 passed** |
| `DATABASE_URL='sqlite:///:memory:' pytest -q` | **157 passed** |
| `manage.py check` | `System check identified no issues (0 silenced).` |
| `manage.py check --settings=config.settings.production` | `System check identified no issues (0 silenced).` |
| `manage.py makemigrations --check --dry-run` | `No changes detected` |
| `manage.py spectacular --validate` | Schéma OpenAPI 3.0.3 valide |
| Versionnement `/api/v1/` | Racine et health vérifiés |
| Documentation en production | Schéma/Swagger/ReDoc refusés (403) aux anonymes |
| Erreurs 400/401/403/404/405/429/500 | Enveloppes et statuts vérifiés |
| Pagination | 20 par défaut, 100 maximum, `pageSize` vérifié |
| camelCase | Entrée, sortie, structures imbriquées et erreurs vérifiées |
| OpenAPI | Schéma JSON, Swagger UI et ReDoc vérifiés en développement |
| Fichiers frontend modifiés par A4 | 0 |

## 8. Lot A5 — authentification JWT et sessions

### Livrables

| Élément | Chemin | État |
|---------|--------|------|
| Package d'authentification | `backend/apps/accounts/auth/` | Créé |
| Vues login/refresh/logout/me/csrf | `backend/apps/accounts/auth/views.py` | Créées |
| Routes `/api/v1/auth/` | `backend/apps/accounts/auth/urls.py`, `apps/api/urls.py` | Créées |
| Serializers d'auth | `backend/apps/accounts/auth/serializers.py` | Créés |
| Services de session | `backend/apps/accounts/auth/services.py` | Créés |
| Cookie refresh | `backend/apps/accounts/auth/cookies.py` | Créé |
| Vérification CSRF | `backend/apps/accounts/auth/csrf.py` | Créée |
| Protection Login CSRF + parser JSON | `backend/apps/accounts/auth/views.py` | Ajoutée à l'audit |
| Journalisation SQL sans tokens | `backend/config/settings/base.py` | Ajoutée à l'audit |
| Throttling | `backend/apps/accounts/auth/throttles.py` | Créé |
| Exceptions stables | `backend/apps/accounts/auth/exceptions.py` | Créées |
| Authentification DRF | `backend/apps/accounts/authentication.py` | Créée |
| Extensions OpenAPI | `backend/apps/accounts/schema.py` | Créées |
| Permissions de rôle/statut | `backend/apps/api/permissions.py` | Mises à jour |
| Mapping des codes d'erreur | `backend/apps/api/exceptions.py` | Mis à jour |
| Settings JWT/CSRF/CORS | `backend/config/settings/base.py`, `production.py` | Mis à jour |
| Exemple d'environnement | `backend/.env.example` | Mis à jour |
| Tests d'authentification | `backend/apps/accounts/tests/test_auth_*.py` | Créés |
| Tests permissions/statut | `backend/apps/api/tests/test_permissions.py` | Complétés |
| Documentation | `backend/README.md`, `docs/API_DOCUMENTATION.md`, `docs/ARCHITECTURE.md`, `docs/LOCAL_DEVELOPMENT.md` | Mise à jour |

Aucun modèle métier, aucune inscription, aucun endpoint de galerie/photo et
aucune migration supplémentaire ne sont ajoutés en A5. `token_blacklist` était
déjà installé et ses migrations déjà appliquées.

### Vérifications réellement exécutées

| Vérification | Résultat |
|--------------|----------|
| `pytest -q` PostgreSQL (`--no-migrations`) | **217 passed** |
| `pytest -q -o addopts='' --create-db` avec migrations appliquées | **217 passed** |
| `DATABASE_URL='sqlite:///:memory:' pytest -q` | **217 passed** |
| `python -m pip check` | `No broken requirements found.` |
| `manage.py check` | `System check identified no issues (0 silenced).` |
| `manage.py check --settings=config.settings.production` | `System check identified no issues (0 silenced).` |
| `manage.py check --deploy --settings=config.settings.production` | Aucun problème avec secret fort et `SECURE_HSTS_PRELOAD=True` explicites |
| `manage.py makemigrations --check --dry-run` | `No changes detected` |
| `manage.py spectacular --validate` | Schéma OpenAPI 3.0.3 valide, sans warning |
| Migrations `token_blacklist` | Déjà appliquées (13 migrations) |
| Tests login/refresh/logout/me/csrf | Couverts |
| Login sans CSRF / avec CSRF valide | `403 CSRF_FAILED` / `200` vérifiés |
| Login depuis origine non autorisée | `403 CSRF_FAILED`, aucun cookie ni token |
| Login avec Content-Type non JSON | Refusé (400/415), aucun cookie ni token |
| Multipart malformé | `400 INVALID_REQUEST`, pas de 500 |
| Preflight CORS login | Origine non autorisée sans `Access-Control-Allow-Origin` |
| Rotation et réutilisation d'un ancien refresh | `TOKEN_REVOKED` vérifié |
| Session après rejeu de R1 | R2 reste valide (pas de révocation de famille) |
| Vérification réelle login → me → refresh → logout | 200/200/200/200, puis `401 TOKEN_REVOKED` et `403 CSRF_FAILED` |
| CSRF absent/invalide/origine refusée | `CSRF_FAILED` vérifié |
| Fuite de tokens dans les logs/réponses | Aucune fuite détectée ; logger SQL forcé à `INFO` |
| CORS avec/sans origine autorisée | En-têtes vérifiés |
| Throttling login et refresh | `RATE_LIMITED` vérifié |
| Compte suspendu/désactivé | Refus au login, refresh et requête authentifiée |
| Cookie de refresh | HttpOnly, path, SameSite, Secure local/production, host-only |
| Access token dans le JSON, refresh absent | Vérifié |
| OpenAPI | `jwtAuth` et `cookieAuth` documentés |
| Fichiers frontend modifiés par A5 | 0 (les 8 modifications antérieures restent intactes) |

### État de la base et Git

- PostgreSQL local `pixeo` : 1 utilisateur (`admin@pixeo.test`,
  `platform_admin`, superuser), 0 compte suspendu.
- Aucun utilisateur de test persistant n'a été créé dans la base de
  développement. La vérification HTTP réelle a utilisé un utilisateur temporaire
  dans une transaction annulée (0 utilisateur persisté).
- Aucune migration A5 n'est nécessaire ; `token_blacklist` est déjà appliqué.
- A4 reste un commit local non poussé ; A5 reste non commité jusqu'à validation
  explicite. `origin/main` pointe toujours sur A3.

## 9. Décisions structurantes

- Nom officiel : **Pixeo**. Aucune référence à SimpleShoot.
- Tenant = `accounts.User` via `branding_username` ; pas de modèle `Tenant`.
- Le plan actif vient de `billing.Subscription`, jamais d'un champ `User.plan`.
- Aucune limite de nombre de galeries ; seul le stockage est limité.
- Mots de passe, PIN et codes d'accès sont hashés ; réinitialisation uniquement.
- Access token en mémoire, refresh token en cookie HttpOnly.
- Sessions photographe et accès public séparés.
- `pre-release` accessible uniquement par lien privé, jamais sur la homepage.
- `?preview=1` ne contourne jamais les contrôles.
- Stockage abstrait local/S3-R2.
- Aucun faux succès : `not_configured` ou endpoint désactivé si non configuré.
- Python en `snake_case`, API en `camelCase`.
- L'API est versionnée par URL (`/api/v1/`) ; seule `v1` est autorisée en A5.
- Les erreurs utilisent des codes stables en majuscules et une enveloppe unique.
- La pagination expose 20 éléments par défaut, 100 maximum et `pageSize`.
- Les permissions de base sont `IsPhotographer` et `IsPlatformAdmin` ; les vues
  publiques déclarent explicitement `AllowAny`.
- La documentation OpenAPI est publique en développement et réservée aux
  administrateurs en production.
- L'access token dure 10 minutes par défaut et le refresh 7 jours ; ces valeurs
  sont configurables par environnement.
- Le refresh token est uniquement dans un cookie HttpOnly, host-only, de chemin
  `/api/v1/auth/`, `SameSite=Lax`, `Secure` en production.
- Le login crée une session : il exige donc aussi CSRF, en plus du refresh et du
  logout. Il n'accepte que `application/json`.
- La réutilisation d'un ancien refresh est refusée (`TOKEN_REVOKED`), mais
  SimpleJWT ne révoque pas la famille : le refresh suivant reste valide dans la
  politique A5.
- Le statut du compte est vérifié à la connexion, au refresh et à chaque requête
  authentifiée. Une suspension prend effet sans attendre l'expiration du token.
- La production n'active aucun wildcard CORS implicite : les origines doivent
  être déclarées explicitement.
- Un logout révoque le refresh mais pas un access token déjà émis ; sa courte
  durée de vie limite la fenêtre résiduelle.

## 10. Problèmes rencontrés et points d'attention

### Problèmes résolus pendant A1

- Première installation : `redis==8.1.0` entrait en conflit avec `kombu[redis]`
  (contrainte `redis < 6.5`) utilisé par Celery. La version a été ramenée à
  `redis==6.4.0`, puis l'installation et `pip check` ont réussi.
- Le miroir PyPI utilisé était lent ; aucune incidence sur le résultat final.

### Problèmes résolus pendant A2

- `pytest-django` force `DEBUG=False` dans le processus de test. Le test de
  développement a donc été déplacé dans un sous-processus isolé avec
  `DJANGO_DEBUG=True`.
- Une valeur `SECURE_SSL_REDIRECT=False` de `backend/.env` fuyait dans le
  sous-processus de production. Les variables de production sont désormais
  injectées explicitement dans les tests.
- L'avertissement `No directory at: .../staticfiles/` est attendu tant que
  `collectstatic` n'a pas été exécuté ; il n'est pas bloquant.

### Problèmes résolus pendant A3

- Le tag PostgreSQL `postgres:17.6-alpine` a été vérifié avant le démarrage ;
  aucun volume existant n'a été supprimé.
- Le `Client` de test Django utilisait `testserver`, absent de
  `DJANGO_ALLOWED_HOSTS` ; les vérifications réelles ont été refaites avec
  `HTTP_HOST=localhost`.
- Le texte d'aide du champ mot de passe est localisé en français ; le test
  d'administration vérifie l'absence du hash et la présence du lien de
  réinitialisation, sans dépendre d'une chaîne anglaise.
- Les tests rapides utilisent `--no-migrations` (syncdb). Une seconde exécution
  avec `-o addopts='-ra --strict-markers'` applique réellement les migrations à
  la base de test PostgreSQL.
- Le niveau `DEBUG` de `backend/.env` rend les logs applicatifs verbeux ; depuis
  A5, le logger `django.db.backends` reste à `INFO` pour ne jamais journaliser
  les refresh tokens stockés en base.

### Problèmes résolus pendant A4

- Le versionnement `URLPathVersioning` transmet le paramètre `version` aux vues ;
  les vues de test doivent accepter `**kwargs`, comme les futures vues métier.
- Le health check est resté une vue Django hors routeur afin de préserver
  exactement sa réponse historique ; il est toujours disponible sous
  `/api/v1/health/`.
- La conversion camelCase des erreurs de validation est effectuée dans le
  gestionnaire global, après la validation du serializer, pour conserver les
  messages et les champs imbriqués.
- La documentation OpenAPI est publique en développement, mais protégée par
  session administrateur en production ; les tests de documentation ciblent
  l'environnement de développement.

### Problèmes résolus pendant A5

- Le client de test DRF désactive CSRF par défaut. Les tests d'authentification
  utilisent `APIClient(enforce_csrf_checks=True)` pour simuler réellement le
  navigateur sur `login`, `refresh` et `logout`.
- `drf-spectacular` ne reconnaissait pas les classes d'authentification
  personnalisées. Des extensions `jwtAuth` et `cookieAuth` ont été ajoutées dans
  `apps/accounts/schema.py` et chargées par `AccountsConfig.ready()`.
- Le fichier `.env` local conservait les anciennes durées (15/14) et une regex
  CORS de développement. Les durées locales ont été alignées sur 10/7 ; les
  tests de production neutralisent explicitement les valeurs CORS héritées de
  `.env` pour vérifier les garde-fous.
- `token_blacklist` était déjà installé et migré ; aucune migration A5 n'a été
  créée.
- La rotation SimpleJWT blackliste l'ancien refresh avant de changer son JTI. Un
  ancien refresh réutilisé renvoie bien `TOKEN_REVOKED`.
- L'audit complémentaire a identifié que le login créait une session sans
  vérification CSRF. `enforce_csrf()` est désormais appliqué au login et le
  parser est limité à JSON ; les formulaires HTML ne peuvent plus créer de
  session.
- Un corps multipart malformé pouvait remonter en 500 via `request.POST` avant
  la sélection du parser. Le gestionnaire central le convertit désormais en
  `400 INVALID_REQUEST`, sans authentification ni cookie.
- SimpleJWT ne fournit pas de révocation de famille. La politique A5 est
  explicite : R1 rejoué est refusé, R2 reste valide. Aucun suivi de famille
  complexe n'a été ajouté.
- Les requêtes SQL peuvent contenir les refresh tokens stockés dans
  `OutstandingToken`. Le logger `django.db.backends` est forcé à `INFO` pour ne
  jamais journaliser ces valeurs, même quand le niveau applicatif local est
  `DEBUG`.
- Le cookie CSRF contient un secret masqué différent du jeton JSON. Le frontend
  doit utiliser `data.csrfToken` et non lire `document.cookie`.
- Un logout ne peut pas révoquer un access token déjà émis ; la durée courte de
  l'access token est la mesure de limitation retenue.

### Points d'attention

- **Travail frontend antérieur non commité** : 8 fichiers modifiés (limites de
  galeries) ont été laissés intacts pendant A1, A2, A3, A4 et A5. Ils devront
  être commités séparément après validation.
- Le superutilisateur créé pour la validation A3 est local ; son mot de passe
  n'est pas versionné. Il devra être remplacé par un compte de production créé
  selon la procédure d'exploitation.
- Le volume Docker `pixeo_postgres_data` contient les données locales ; ne jamais
  lancer `docker compose down -v` sans autorisation explicite.
- `README.md` racine reste modifié par le travail frontend antérieur ; le guide
  backend est dans `backend/README.md` pour ne pas mélanger les deux.
- `pixeo.com`, le DNS wildcard et les certificats TLS ne sont pas vérifiés.
- `docs/LAUNCH.md` mentionne encore Supabase ; il sera actualisé en Phase E.
- Les dépendances de test (pytest, pytest-django) sont maintenant dans
  `backend/requirements-dev.txt`.

## 11. Prochain lot

**A5 — en attente de validation explicite.**

- A5 est implémenté et vérifié, mais volontairement non commité.
- Aucun lot suivant (A6, modèles métier, inscription, galeries, photos,
  abonnements) ne doit démarrer avant validation.
- A4 reste un commit local non poussé ; `origin/main` pointe sur A3.
- Le commit A5 sera créé séparément après validation.

## 12. Commandes utiles

```bash
# Backend
cd backend
source .venv/bin/activate
python --version
pip install -r requirements.txt
pip install -r requirements-dev.txt
pip check
python manage.py check

# PostgreSQL local
docker compose up -d
docker compose ps
docker compose exec postgres pg_isready -U pixeo -d pixeo

# Migrations
python manage.py makemigrations --check --dry-run
python manage.py migrate
python manage.py showmigrations

# Tests
pytest -q
pytest -q -o addopts='-ra --strict-markers'
DATABASE_URL='sqlite:///:memory:' pytest -q

# API technique
curl -i http://localhost:8000/api/v1/health/
curl -s http://localhost:8000/api/v1/schema/?format=json | head
# Swagger UI : http://localhost:8000/api/v1/docs/
# ReDoc     : http://localhost:8000/api/v1/redoc/

# Frontend (existant)
pnpm dev
pnpm build

# État Git
git status --short
```
