# Pixeo — Développement backend

> Dernière mise à jour : 2026-11-26
> Lot en cours : **A9 — import, lecture, suppression et ordre des photos**
> (réalisé, commité et poussé)

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
| A | **A4** | Fondation API REST : versionnement, erreurs, pagination, camelCase, permissions, OpenAPI | **Réalisé — validé** |
| A | **A5** | Authentification JWT, cookie refresh, rotation/blacklist, CSRF/CORS, profil courant | **Réalisé — validé** |
| A | **A6** | Inscription publique, plan Free, branding, homepage initiale | **Réalisé — validé** |
| A | **A7** | Modèle `Gallery`, contrainte slug par photographe, admin et migration | **Réalisé — validé** |
| A | **A8** | API REST CRUD des galeries, isolation multi-tenant, tests et documentation | **Réalisé — commité (`ec99da8`)** |
| A | **A9** | Modèle `Photo`, import multipart validé par Pillow, lecture, suppression, réorganisation | **Réalisé — commité et poussé** |
| B | — | Studio, branding, homepage, plans/abonnements | Partiellement préparé par A6 (modèles initiaux) |
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

## 9. Lot A6 — inscription et initialisation de l'espace

### Livrables

| Élément | Chemin | État |
|---------|--------|------|
| Application billing | `backend/apps/billing/` | Créée |
| Plan et abonnement | `backend/apps/billing/models.py` | Créés |
| Migration billing | `backend/apps/billing/migrations/0001_initial.py` | Créée |
| Seed plan Free | `backend/apps/billing/migrations/0002_seed_free_plan.py` | Créée |
| Application studios | `backend/apps/studios/` | Créée |
| Branding et homepage | `backend/apps/studios/models.py` | Créés |
| Migration studios | `backend/apps/studios/migrations/0001_initial.py` | Créée |
| Service d'inscription | `backend/apps/accounts/registration/services.py` | Créé |
| Serializer d'inscription | `backend/apps/accounts/registration/serializers.py` | Créé |
| Vue d'inscription | `backend/apps/accounts/registration/views.py` | Créée |
| Route `/api/v1/auth/register/` | `backend/apps/accounts/auth/urls.py` | Ajoutée |
| Throttling inscription | `backend/apps/accounts/auth/throttles.py` | Ajouté |
| Codes conflit/configuration | `backend/apps/accounts/auth/exceptions.py`, `apps/api/exceptions.py` | Ajoutés |
| Admin billing/studios | `backend/apps/billing/admin.py`, `apps/studios/admin.py` | Créés |
| Settings | `backend/config/settings/base.py` | Apps et throttle ajoutés |
| Exemple d'environnement | `backend/.env.example` | `AUTH_REGISTER_RATE` ajouté |
| Tests inscription | `backend/apps/accounts/tests/test_auth_register.py` | Créés |
| Tests modèles | `backend/apps/billing/tests/`, `backend/apps/studios/tests/` | Créés |
| OpenAPI | `backend/apps/api/tests/test_documentation.py`, schéma register | Mis à jour |
| Documentation | `backend/README.md`, `docs/API_DOCUMENTATION.md`, `docs/ARCHITECTURE.md`, `docs/LOCAL_DEVELOPMENT.md` | Mise à jour |

Aucun endpoint de galerie, photo, abonnement payant, paiement, e-mail réel,
vérification d'e-mail, récupération de mot de passe ou modification de profil
n'est ajouté en A6.

### Modèles et contraintes

- `billing.Plan` : `code` unique, nom, prix FCFA, quota de stockage,
  fonctionnalités JSON, actif, ordre, dates.
- `billing.Subscription` : `user`, `plan`, statut, période courante,
  `cancel_at_period_end`, dates. Contrainte partielle d'unicité d'un abonnement
  actif par utilisateur.
- `studios.BrandingSettings` : 1:1 `User`, domaine custom, logo, favicon,
  filigrane, texte, dates. Le `branding_username` n'est pas dupliqué.
- `studios.HomepageSettings` : 1:1 `User`, activation, biographie, nom de marque,
  dates.
- Le plan `free` est seedé par migration de données. Aucun autre plan n'est seedé
  en A6.

### Vérifications réellement exécutées

| Vérification | Résultat |
|--------------|----------|
| `pytest -q` PostgreSQL (`--no-migrations`) | **277 passed** |
| `pytest -q -o addopts='' --create-db` avec migrations | **277 passed** |
| `DATABASE_URL='sqlite:///:memory:' pytest -q` | **277 passed** |
| `DATABASE_URL='sqlite:///:memory:' pytest -q -o addopts='' --create-db` | **277 passed** |
| `python -m pip check` | `No broken requirements found.` |
| `manage.py check` | `System check identified no issues (0 silenced).` |
| `manage.py check --settings=config.settings.production` | `System check identified no issues (0 silenced).` |
| `manage.py check --deploy --settings=config.settings.production` | Aucun problème avec `SECURE_SSL_REDIRECT=True`, `SECURE_HSTS_PRELOAD=True` et `CACHE_URL` explicites |
| `manage.py makemigrations --check --dry-run` | `No changes detected` |
| `manage.py spectacular --validate` | Schéma OpenAPI 3.0.3 valide |
| Migrations `billing` et `studios` | Appliquées sur PostgreSQL de développement |
| Plan Free seedé | `free`, actif, 5 Go |
| Smoke test HTTP réel | `201`, compte `photographer`, Free actif, branding/homepage créés, rollback sans résidu |
| Compte administrateur existant | Conservé (`admin@pixeo.test`, `platform_admin`, superuser) |
| Tests inscription réussie | Compte, rôle, Free, branding, homepage, hash, login A5 |
| Tests validations | Email, doublons, casse, mot de passe, confirmation, branding, champs inconnus |
| Tests sécurité | Aucun admin, aucun mot de passe/hash retourné ou journalisé, JSON-only, throttling |
| Tests atomicité | Échec subscription/branding/homepage → rollback complet |
| Tests CORS inscription | Preflight origine autorisée/refusée |
| OpenAPI inscription | Schéma camelCase, `201`, exemple, sans `X-CSRFToken` |
| Fichiers frontend modifiés par A6 | 0 (les 8 modifications antérieures restent intactes) |

### État de la base et Git

- PostgreSQL local `pixeo` : 1 utilisateur, 1 superuser, 0 suspendu.
- Plan Free : 1 ligne active. Aucun abonnement, branding ou homepage persistants
  n'ont été créés par les tests.
- Les migrations A1–A5 n'ont pas été modifiées.
- A6 est validé et commité (`bcd36ea`), puis poussé avec A7 ; le worktree
  conserve les 8 modifications frontend préexistantes.
- `origin/main` pointe sur le commit A7 `71dccd1`.

## 10. Lot A7 — modèle de données des galeries

### Livrables

| Élément | Chemin | État |
|---------|--------|------|
| Application galleries | `backend/apps/galleries/` | Créée |
| Modèle Gallery | `backend/apps/galleries/models.py` | Créé |
| Statuts de galerie | `backend/apps/galleries/models.py` | Ajoutés |
| Administration | `backend/apps/galleries/admin.py` | Créée |
| Migration initiale | `backend/apps/galleries/migrations/0001_initial.py` | Créée |
| Migration des contraintes | `backend/apps/galleries/migrations/0002_gallery_constraints.py` | Créée |
| Tests du modèle | `backend/apps/galleries/tests/test_models.py` | Créés |
| Tests de l'admin | `backend/apps/galleries/tests/test_admin.py` | Créés |
| Settings | `backend/config/settings/base.py` | Application enregistrée |
| Documentation | `docs/ARCHITECTURE.md`, `docs/DEVELOPMENT_PROGRESS.md` | Mise à jour |

Aucun serializer, view, endpoint, route publique, upload, modèle `Photo` ou
`PhotoSet`, PIN ou mot de passe de galerie n'est ajouté en A7. Les
fonctionnalités A5/A6 et le frontend restent inchangés ; seul l'enregistrement
de `apps.galleries` est ajouté aux settings.

### Modèle et contraintes

- `Gallery.id` : `UUIDField`, clé primaire générée par `uuid.uuid4`.
- `Gallery.photographer` : clé étrangère obligatoire vers `AUTH_USER_MODEL`,
  avec `on_delete=CASCADE`.
- `Gallery.title` : `CharField(max_length=150)`, non vide.
- `Gallery.slug` : `SlugField(max_length=100)`, non vide.
- `Gallery.description` : `TextField` facultatif, vide par défaut.
- `Gallery.status` : `draft`, `published`, `hidden` ou `pre_release`, avec
  `draft` par défaut. Le CRUD et l'administration le laissent en lecture seule ;
  les transitions seront gérées par un futur service de publication.
- `Gallery.published_at` : `DateTimeField` nullable. Il représente la date de
  première publication, reste `null` avant celle-ci, puis est conservé après
  une dépublication ou un masquage. Le CRUD et l'administration ne peuvent pas
  le modifier.
- `Gallery.created_at` et `Gallery.updated_at` : dates automatiques.
- Contrainte `UniqueConstraint(fields=["photographer", "slug"])` nommée
  `unique_gallery_slug_per_photographer`.
- Contraintes SQL `CHECK` `gallery_title_not_empty` et
  `gallery_slug_not_empty` : les champs ne peuvent pas être vides, même via
  `save()`, `objects.create()` ou `bulk_create()`.
- Contrainte SQL `CHECK` `gallery_status_valid` : seules les quatre valeurs
  autorisées peuvent être enregistrées.
- Contrainte SQL `CHECK` `gallery_published_requires_published_at` : une
  galerie `published` doit avoir un `published_at` non nul. Une galerie non
  publiée peut conserver une date de première publication.
- `Gallery.clean()` et `Gallery.save()` refusent un propriétaire dont le rôle
  n'est pas `photographer`, ainsi qu'une galerie `published` sans
  `published_at`. Une contrainte SQL ne peut pas vérifier le rôle d'une table
  liée ; les créations de masse doivent passer par un service qui appelle
  `full_clean()`.
- `GalleryAdmin` expose `status`, `published_at`, `created_at` et `updated_at`
  en lecture seule ; le titre, le slug et la description restent modifiables.
- Ordre par défaut : `-created_at`.
- La suppression du photographe supprime ses galeries.
- L'admin affiche titre, photographe, slug, statut et date de création ; il
  filtre par statut, recherche par titre ou slug et expose les dates en lecture
  seule.

### Vérifications réellement exécutées

| Vérification | Résultat |
|--------------|----------|
| `pytest -q apps/galleries` | **24 passed** |
| `pytest -q` PostgreSQL (`--no-migrations`) | **301 passed** |
| `pytest -q -o addopts='' --create-db` avec migrations | **301 passed** |
| `DATABASE_URL='sqlite:///:memory:' pytest -q` | **301 passed** |
| `DATABASE_URL='sqlite:///:memory:' pytest -q -o addopts='' --create-db` | **301 passed** |
| `python manage.py check` | `System check identified no issues (0 silenced).` |
| `python manage.py makemigrations --check --dry-run` | `No changes detected` |
| `python -m pip check` | `No broken requirements found.` |
| `git diff --check` | Aucun problème |
| Migrations `galleries.0001_initial` et `0002_gallery_constraints` | Appliquées sur PostgreSQL de développement |
| Table `galleries_gallery` | Présente, contrainte unique `(photographer_id, slug)` et trois contraintes `CHECK` |
| Tests SQL directs | `save()`, `objects.create()` et `bulk_create()` refusent titre/slug vides et statut invalide |
| Tests du propriétaire | `full_clean()`, `save()` et `objects.create()` refusent un `platform_admin` |
| Données existantes | Compte admin et plan Free conservés ; 0 galerie |

### État de la base et Git

- PostgreSQL local `pixeo` : compte `admin@pixeo.test` conservé, plan Free
  actif, aucune galerie persistante.
- Les migrations A1–A6 n'ont pas été modifiées.
- A7 est implémenté, vérifié et validé ; commit `71dccd1`, poussé sur
  `origin/main`.
- `origin/main` pointe sur `71dccd1`.
- Les huit modifications frontend préexistantes restent intactes.

## 11. Lot A8 — API REST de gestion des galeries

### Livrables

| Élément | Chemin | État |
|---------|--------|------|
| Serializer API | `backend/apps/galleries/serializers.py` | Créé |
| Vue API | `backend/apps/galleries/views.py` | Créée |
| Enregistrement du routeur | `backend/apps/api/urls.py` | `GalleryViewSet` enregistré |
| Tests modèle et admin | `backend/apps/galleries/tests/test_models.py`, `test_admin.py` | 32 + 1 tests |
| Tests API | `backend/apps/galleries/tests/test_api.py` | 70 tests |
| Migration incrémentale | `backend/apps/galleries/migrations/0003_gallery_gallery_published_requires_published_at.py` | Contrainte de cohérence publication |
| Schémas OpenAPI | `backend/apps/galleries/serializers.py`, `backend/config/settings/base.py` | Tag Galeries, schémas camelCase, `status` absent des requêtes |
| Tests OpenAPI et racine API | `backend/apps/api/tests/test_documentation.py`, `backend/apps/api/tests/test_versioning.py` | Mis à jour |
| Documentation | `docs/API_DOCUMENTATION.md`, `docs/ARCHITECTURE.md`, `docs/DEVELOPMENT_PROGRESS.md` | Mise à jour |

A8 n'ajoute aucun modèle, upload, stockage, galerie publique, PIN, lien privé,
token de prépublication, paiement, abonnement ou modification frontend.
L'authentification A5, l'inscription A6, le modèle `Gallery` A7 et les
migrations A1–A7 restent inchangés. La correction ajoute uniquement la migration
incrémentale `galleries.0003` et le durcissement du CRUD.

### Endpoints et règles

- `POST /api/v1/galleries/` crée une galerie pour `request.user` et retourne
  `201` avec l'enveloppe de succès. La galerie est toujours créée en `draft`
  avec `publishedAt=null`.
- `GET /api/v1/galleries/` retourne uniquement les galeries de `request.user`,
  paginées et triées par `createdAt` décroissant.
- `GET /api/v1/galleries/{id}/` retourne une galerie du photographe.
- `PATCH /api/v1/galleries/{id}/` modifie partiellement `title`, `slug` et
  `description`. `PUT` n'est pas exposé.
- `DELETE /api/v1/galleries/{id}/` supprime une galerie du photographe et
  retourne `204` sans corps.
- `permission_classes = [IsPhotographer]` : compte actif, non suspendu, rôle
  `photographer`. Un `platform_admin` reçoit `403`.
- Le queryset de classe vaut `Gallery.objects.none()`. `get_queryset()` filtre
  systématiquement par `photographer=request.user` pour toutes les actions. Une
  galerie d'un autre photographe renvoie `404 NOT_FOUND`.
- `perform_create()` impose `photographer=request.user`, `status=draft` et
  `published_at=None`. Les champs `photographer`, `photographerId` et tout
  autre champ inconnu sont refusés avec `400 VALIDATION_ERROR`.
- Le serializer expose `id`, `title`, `slug`, `description`, `status`,
  `publishedAt`, `createdAt` et `updatedAt`. `status`, `publishedAt`, `id`,
  `createdAt` et `updatedAt` sont en lecture seule. Le propriétaire n'est jamais
  exposé.
- Fournir `status`, y compris `draft`, ou `publishedAt` dans `POST` ou `PATCH`
  renvoie `400 VALIDATION_ERROR`. Ces champs ne sont jamais ignorés
  silencieusement. Les transitions de statut seront réservées à un futur service
  métier.
- `title` et `slug` sont obligatoires et non vides ; `title` est limité à 150
  caractères, `slug` à 100. `description` est facultative.
- Le slug est unique par photographe ; le même slug reste autorisé pour deux
  photographes différents. Un doublon est refusé en validation. Seul le conflit
  d'unicité `unique_gallery_slug_per_photographer` est converti en
  `400 VALIDATION_ERROR` ; les autres erreurs d'intégrité sont journalisées et
  remontent en `500 INTERNAL_ERROR` générique, sans détail SQL.
- La liste accepte `page`, `page_size` et `?status=`. Le filtre de statut
  s'applique après l'isolation par propriétaire.
- Les erreurs utilisent l'enveloppe standard : `400 VALIDATION_ERROR`,
  `401 AUTHENTICATION_REQUIRED`, `403 PERMISSION_DENIED` /
  `CSRF_FAILED` / `ACCOUNT_DISABLED` / `ACCOUNT_SUSPENDED`, `404 NOT_FOUND`,
  `405 METHOD_NOT_ALLOWED` et `415 UNSUPPORTED_MEDIA_TYPE`.
- Une session Django est acceptée en plus du JWT. Une requête d'écriture sans
  jeton CSRF valide renvoie `403 CSRF_FAILED` ; CSRF n'est jamais désactivé.

### Vérifications réellement exécutées

| Vérification | Résultat |
|--------------|----------|
| `pytest -q apps/galleries` | **103 passed** (32 modèle + 1 admin + 70 API) |
| `pytest -q` PostgreSQL (`--no-migrations`) | **381 passed** |
| `pytest -q -o addopts='' --create-db` avec migrations PostgreSQL | **381 passed** |
| `DATABASE_URL='sqlite:///:memory:' pytest -q` | **381 passed** |
| `DATABASE_URL='sqlite:///:memory:' pytest -q -o addopts='' --create-db` | **381 passed** |
| `python manage.py check` | `System check identified no issues (0 silenced).` |
| `python manage.py makemigrations --check --dry-run` | `No changes detected` |
| `python manage.py spectacular --validate` | Schéma OpenAPI valide, aucune erreur ni avertissement |
| `python -m pip check` | `No broken requirements found.` |
| `git diff --check` | Aucun problème |
| Migration PostgreSQL `galleries.0003` | Appliquée ; contrainte `gallery_published_requires_published_at` présente |
| Migration SQLite avec données | Appliquée sur une base temporaire ; galerie conservée à l'identique |
| Tests d'authentification | Anonyme `401`, admin plateforme `403`, suspendu `403`, inactif `403` |
| Tests d'isolation | Liste, détail, `PATCH` et `DELETE` d'un autre photographe → `404` |
| Tests de création | Propriétaire `request.user`, injections refusées, `status`/`publishedAt` refusés, défauts, doublons et longueurs |
| Tests de transition | Toutes les valeurs de `status` refusées en `POST` et `PATCH`, depuis `draft`, `hidden` et `published` |
| Tests CSRF | Session sans jeton → `403 CSRF_FAILED` ; avec jeton → `POST`/`PATCH`/`DELETE` réussis |
| Tests `IntegrityError` | Conflit de slug → `400` ; autre erreur → `500` générique journalisée, sans SQL |
| Tests de liste | Pagination, filtre `status`, tri et total |
| Tests de validation | Enveloppe standard, champs inconnus, identifiant et propriétaire non modifiables |
| OpenAPI | Routes, paramètre `status`, schémas camelCase, `status` absent des requêtes, réponses `201` et `204` |
| Avertissements | 198, tous causés par `backend/staticfiles/` absent ; aucun échec |

### État de la base et Git

- PostgreSQL local `pixeo` : compte `admin@pixeo.test` conservé, plan Free
  actif, aucune galerie persistante. Les compteurs utilisateurs, administrateur
  et plans sont inchangés après migration.
- Les migrations A1–A7 n'ont pas été modifiées. A8 ajoute uniquement la
  migration incrémentale `galleries.0003_gallery_gallery_published_requires_published_at`.
- La migration a été appliquée après vérification : aucune galerie
  `published` sans `published_at` n'existait. Aucune donnée n'a été corrigée
  silencieusement.
- A8 est corrigé et vérifié dans le worktree, sans staging, commit, push,
  changement de branche, rebase ni reset.
- `HEAD` et `origin/main` pointent sur `71dccd1`.
- Les huit fichiers frontend protégés restent inchangés ; le hash du diff est
  `718a59ec6e47702024c7c4820b94b02f4c094788c1910e2563897966e56fd116`.

## 11 bis. Lot A9 — import et ordre des photos

### Livrables

| Élément | Chemin | État |
|---------|--------|------|
| Modèle `Photo` | `backend/apps/galleries/models.py` | Créé (UUID, FK `gallery`, métadonnées, SHA-256, position) |
| Migration | `backend/apps/galleries/migrations/0004_photo.py` | Créée et appliquée sur PostgreSQL local |
| Services métier | `backend/apps/galleries/services.py` | Créés (validation, import atomique, suppression, compaction, réorganisation) |
| Serializers / vues | `backend/apps/galleries/serializers.py`, `views.py` | `GalleryPhotoViewSet` |
| Routes | `backend/apps/api/urls.py` | `galleries/{id}/photos/`, `.../order/`, `.../{photoId}/` |
| Médias en développement | `backend/config/urls.py` | `MEDIA_URL` servi uniquement si `DEBUG` |
| Limites | `backend/config/settings/base.py`, `backend/.env.example` | `PIXEO_PHOTO_MAX_UPLOAD_SIZE`, `_MAX_BATCH_SIZE`, `_MAX_PIXELS` |
| Admin | `backend/apps/galleries/admin.py` | Photos consultables et supprimables, sans ajout ni édition |
| Tests | `backend/apps/galleries/tests/test_photo_api.py` | Créés |

### Règles

- Le format est détecté depuis le contenu (Pillow) : JPEG, PNG, WEBP. L'extension
  et le Content-Type client ne sont jamais utilisés pour décider.
- Protection contre les bombes de décompression, fichiers vides, tronqués ou
  trop grands. Un lot invalide n'écrit rien (ni base ni stockage).
- La clé de stockage est `galleries/{galleryId}/photos/{uuid}.{ext}` ; le nom
  d'origine n'est jamais utilisé comme chemin.
- Suppression : ligne supprimée et positions compactées dans une transaction ;
  le fichier est effacé après commit uniquement.
- Réorganisation : la liste complète des identifiants est exigée.
- Isolation : toute photo ou galerie d'un autre photographe renvoie 404.
- Décision V1 : **une photo appartient à une seule galerie**. La bibliothèque
  partagée entre collections est reportée en V1.1.

### Vérifications réellement exécutées

| Vérification | Résultat |
|--------------|----------|
| `pytest -q` | **421 passed** |
| `makemigrations --check --dry-run` | `No changes detected` |
| `spectacular --validate --fail-on-warn` | OK |
| `manage.py check` | `System check identified no issues (0 silenced).` |
| `migrate galleries` (PostgreSQL local) | `0004_photo` appliquée |

### Problèmes résolus pendant A9

- `test_import_rejects_unsupported_format` : l'aide de test `_mime_type` ne
  connaissait pas `GIF` (`KeyError`). Ajout de `image/gif`.
- `test_delete_rollback_keeps_database_row_and_file` : `Model.delete()` remet
  `pk` à `None` en mémoire même en cas de rollback ; le test capture désormais
  l'identifiant avant la suppression. Le comportement du service était correct.

## 12. Décisions structurantes

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
- L'API est versionnée par URL (`/api/v1/`) ; seule `v1` est autorisée en A8.
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
- L'inscription est publique, JSON-only et ne crée aucune session. Elle
  n'applique pas CSRF car elle ne lit aucun cookie et ne crée aucun état
  d'authentification ; JSON-only, CORS et le throttling dédié assurent la
  protection.
- Le rôle d'un compte inscrit est toujours `photographer`; tout champ `role`,
  `is_staff`, `is_superuser` ou de plan fourni par le client est refusé.
- L'inscription crée le `User`, la `Subscription` Free active, les
  `BrandingSettings` et les `HomepageSettings` dans une transaction unique.
- Le plan Free est seedé par migration ; les autres plans ne sont pas encore
  seedés. Un utilisateur ne peut avoir qu'un abonnement actif à la fois.
- Les modèles A6 sont placés dans `billing` et `studios`, conformément à la
  cible d'architecture ; `accounts.User` reste la seule source du
  `branding_username`.
- Aucune connexion automatique après inscription : le client appelle ensuite
  `/api/v1/auth/login/`.
- Le modèle A7 `Gallery` utilise le statut `pre_release` (underscore), un slug
  unique par photographe et une suppression en cascade avec le photographe.
- L'API A8 expose le CRUD des galeries sous `/api/v1/galleries/`. Le propriétaire
  est toujours `request.user`; aucun champ `photographer` ou `photographerId`
  fourni par le client n'est accepté. `PATCH` est la seule méthode de
  modification et `DELETE` retourne `204`.
- Le CRUD ne gère que `title`, `slug` et `description`. `status` et
  `publishedAt` sont en lecture seule : toute tentative d'écriture renvoie
  `400 VALIDATION_ERROR`, y compris `status=draft` ou `publishedAt=null`.
- Toute création commence en `draft` avec `publishedAt=null`. Les transitions
  de statut seront implémentées dans un futur service métier dédié.
- `publishedAt` représente la date de première publication. Il reste `null`
  avant la première publication, est renseigné par le futur service lors de
  cette première publication, puis conservé après une dépublication ou un
  masquage. Une prépublication ne le renseigne pas.
- Toute lecture, modification ou suppression de galerie est filtrée par
  `photographer=request.user`. Une galerie d'un autre photographe renvoie `404`
  pour ne pas révéler son existence.
- Le slug est unique par photographe. Un doublon est refusé en validation ; un
  conflit d'insertion concurrent sur `unique_gallery_slug_per_photographer` est
  converti en erreur API sans exposer l'exception SQL. Les autres erreurs
  d'intégrité remontent en `500 INTERNAL_ERROR` générique et sont journalisées.
- La liste des galeries est paginée, triée par `createdAt` décroissant et
  filtrable par `status`. Le filtre s'applique après l'isolation par
  propriétaire.
- A8 ajoute une migration incrémentale `galleries.0003` pour garantir au niveau
  SQL qu'une galerie `published` possède un `published_at` non nul.
- Les échecs CSRF des sessions Django sont normalisés en `403 CSRF_FAILED`
  pour tous les endpoints concernés ; CSRF reste actif.

## 13. Problèmes rencontrés et points d'attention

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

### Problèmes résolus pendant A6

- `--no-migrations` ne joue pas la migration de données du plan Free. Un fixture
  `free_plan` crée le plan dans les tests rapides ; la migration reste la source
  de vérité en PostgreSQL migré.
- Les tests de modèles avec migrations trouvaient déjà le plan Free seedé. Les
  fixtures utilisent `get_or_create` pour rester valides avec et sans migrations.
- DRF ignore par défaut les champs inconnus. Le serializer d'inscription les
  refuse explicitement, notamment `role`, `isStaff` et `isSuperuser`.
- Le schéma OpenAPI généré depuis les serializers runtime utilisait les noms
  snake_case internes. Des schémas publics dédiés en camelCase documentent le
  corps et la réponse d'inscription.
- Un conflit d'e-mail ou de nom public est signalé par une erreur non-field
  générique (`nonFieldErrors`). Cela reste une divulgation limitée de l'existence
  d'un compte ; une vérification d'e-mail asynchrone pourra réduire ce risque
  ultérieurement.
- Le plan Free est lu et verrouillé à l'intérieur de la transaction
  d'inscription. Un plan absent ou inactif renvoie `503 NOT_CONFIGURED` sans
  création partielle. Une course d'unicité à l'insertion renvoie `409 CONFLICT`.
- Les throttles A5/A6 utilisent `REMOTE_ADDR` par défaut et n'interprètent
  `X-Forwarded-For` que si `AUTH_TRUSTED_PROXY_COUNT` est explicitement
  configuré après vérification de la topologie du reverse proxy.

### Problèmes résolus pendant A7

- `save()` et `objects.create()` ne déclenchent pas `full_clean()` : des chaînes
  vides pouvaient être persistées. Des contraintes SQL `CHECK` couvrent
  désormais les écritures directes et les opérations de masse.
- Un statut hors énumération pouvait être inséré directement. La contrainte
  `gallery_status_valid` limite les valeurs au niveau PostgreSQL et SQLite.
- Un `platform_admin` pouvait être propriétaire d'une galerie. `Gallery.clean()`
  et `Gallery.save()` refusent ce rôle ; la règle inter-tables ne peut pas être
  une simple contrainte SQL. Les imports de masse devront passer par un service
  appelant `full_clean()`.
- Les tests distinguent la validation Django (`full_clean()`), les écritures
  `save()`/`objects.create()` et les contraintes réellement appliquées par la
  base.

### Problèmes résolus pendant A8

- L'ajout de la route galeries modifie la racine `/api/v1/` : le test A4 qui
  attendait une enveloppe vide a été mis à jour pour vérifier la découverte de
  `/api/v1/galleries/`.
- Le schéma OpenAPI généré depuis le `ModelSerializer` exposait les noms
  internes `published_at`, `created_at` et `updated_at`. Des schémas publics
  camelCase dédiés documentent désormais la requête et la réponse, comme pour
  l'inscription A6.
- La validation du slug couvre le doublon ordinaire. Une course entre la
  validation et l'insertion sur `unique_gallery_slug_per_photographer` est
  convertie en `400 VALIDATION_ERROR` via `IntegrityError`, dans une
  transaction, sans exposer SQL ni contrainte.
- Les autres `IntegrityError` ne sont plus masquées en erreurs de validation :
  elles sont journalisées et remontent en `500 INTERNAL_ERROR` générique, sans
  détail SQL.
- Un identifiant de galerie mal formé pouvait remonter comme erreur Django. La
  vue convertit `ValidationError`/`ValueError` en `404 NOT_FOUND` standard.
- DRF ignore par défaut les champs inconnus et les champs `read_only`. Le
  serializer refuse explicitement les champs inconnus, `photographer`,
  `photographerId`, `status`, `publishedAt`, `id`, `createdAt` et `updatedAt`.
  Fournir `status` ou `publishedAt` renvoie donc `400 VALIDATION_ERROR` au lieu
  d'être ignoré.
- Le CRUD ne pouvait pas garantir la cohérence du cycle de vie : `status` et
  `publishedAt` étaient modifiables. Ils sont désormais en lecture seule dans
  l'API et dans l'administration. La création force `draft`/`null` et les
  transitions sont réservées à un futur service métier.
- Le modèle et la base refusent une galerie `published` sans `published_at`.
  La contrainte SQL `gallery_published_requires_published_at` protège aussi les
  écritures de masse et les mises à jour directes.
- Le queryset de classe est désormais `Gallery.objects.none()` ; toutes les
  actions passent par `get_queryset()` filtré par photographe.
- Les échecs CSRF d'une session Django renvoyaient `PERMISSION_DENIED` au lieu
  de `CSRF_FAILED`. Le gestionnaire d'erreurs les normalise sans désactiver
  CSRF.
- `PUT` est désactivé au niveau de la vue ; seule la modification partielle
  `PATCH` est disponible.

### Points d'attention

- **Travail frontend antérieur non commité** : 8 fichiers modifiés (limites de
  galeries) ont été laissés intacts pendant A1 à A8. Ils devront être commités
  séparément après validation.
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

## 14. Plan de finition de la V1

Ordre des lots restants (un commit et un push par lot) :

| Phase | Lot | Contenu |
|-------|-----|---------|
| A | A10 | Clôture du socle : décision stockage et modèle de photo actée |
| C | C1 | Stockage objet S3-compatible (Cloudflare R2 recommandé), bucket privé, URLs signées |
| C | C2 | Quota de stockage du plan vérifié à l'import, usage exposé dans le profil |
| C | C3 | Miniatures et aperçus WebP générés par Celery |
| C | C4 | Publication / dépublication, photo de couverture |
| C | C5 | Accès public : homepage et galerie publiées |
| C | C6 | Téléchargement autorisé (URL signée, rate limiting) |
| C | C7 | Mot de passe de galerie (hashé, `unlock`, rate limiting) |
| B | B1–B4 | Plans publics, branding et filigrane, reset mot de passe et e-mails, changement de plan manuel par l'admin |
| D | D1–D7 | Client API frontend, auth réelle, collections, upload réel, galeries publiques, billing, retrait du `localStorage` |
| E | E1–E6 | Dockerfile, hébergement, domaine/TLS, CI, Sentry, pages légales, bêta fermée |

Reporté en V1.1 : bibliothèque partagée, sets, favoris/notes clients, PIN et
code client, liens pre-release, contacts et campagnes, paiement en ligne,
sous-domaines par photographe.

**Stockage** : TeraBox a été évalué et écarté comme stockage principal (aucune
API officielle pour applications tierces, risque de suspension et de rupture).
Le stockage cible reste S3-compatible, configurable via `STORAGE_BACKEND`.

## 15. Commandes utiles

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
pytest -q apps/galleries
pytest -q
pytest -q -o addopts='' --create-db
DATABASE_URL='sqlite:///:memory:' pytest -q

# API technique
curl -i http://localhost:8000/api/v1/health/
curl -s http://localhost:8000/api/v1/schema/?format=json | head
python manage.py spectacular --validate

# Inscription (JSON-only, sans session)
curl -i -X POST http://localhost:8000/api/v1/auth/register/ \
  -H 'Content-Type: application/json' \
  -d '{"email":"photographe@example.com","password":"MotDePasseSolide123!","passwordConfirmation":"MotDePasseSolide123!","brandingUsername":"studio-photo"}'

# Galeries (access token photographe requis)
curl -i http://localhost:8000/api/v1/galleries/ \
  -H 'Authorization: Bearer <accessToken>'
curl -i -X POST http://localhost:8000/api/v1/galleries/ \
  -H 'Authorization: Bearer <accessToken>' \
  -H 'Content-Type: application/json' \
  -d '{"title":"Mariage de Camille","slug":"mariage-camille"}'
# status et publishedAt sont refusés en écriture ; la galerie est créée en draft.
# Swagger UI : http://localhost:8000/api/v1/docs/
# ReDoc     : http://localhost:8000/api/v1/redoc/

# Frontend (existant)
pnpm dev
pnpm build

# État Git
git status --short
```
