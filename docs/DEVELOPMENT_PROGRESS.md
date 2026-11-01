# Pixeo — Développement backend

> Dernière mise à jour : 2026-11-01
> Lot en cours : **A3 — PostgreSQL, migrations initiales et Django Admin** (réalisé, en attente de validation)

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
| A | **A3** | PostgreSQL, migration initiale, superutilisateur, Django Admin, health DB | **Réalisé — en attente de validation** |
| B | — | Authentification, JWT, cookies, CSRF, permissions | Non démarré |
| C | — | Studio, branding, homepage, plans/abonnements | Non démarré |
| D | — | Collections, photos, stockage, accès publics, favoris/notes | Non démarré |
| E | — | Intégration frontend et retrait du `localStorage` | Non démarré |

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

## 7. Décisions structurantes

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

## 8. Problèmes rencontrés et points d'attention

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
- Le niveau `DEBUG` de `backend/.env` rend les logs SQL très verbeux ; cela
  n'affecte pas les résultats et peut être réduit avec `DJANGO_LOG_LEVEL=INFO`.

### Points d'attention

- **Travail frontend antérieur non commité** : 8 fichiers modifiés (limites de
  galeries) ont été laissés intacts pendant A1, A2 et A3. Ils devront être
  commités séparément après validation.
- Les migrations `accounts.0001_initial` et les fichiers Compose/Admin/tests A3
  sont prêts à être commités, mais **aucun commit A3 n'a été créé**.
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

## 9. Prochain lot

**A4 — périmètre à valider** (non démarré) :

- Attendre la validation explicite du rapport A3.
- Ne pas démarrer A4, les modèles métier, l'authentification JWT ou les endpoints
  métier avant cette validation.
- Les lots B/C restent non démarrés.

## 10. Commandes utiles

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

# Frontend (existant)
pnpm dev
pnpm build

# État Git
git status --short
```
