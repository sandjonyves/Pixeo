# Pixeo — Développement backend

> Dernière mise à jour : 2026-11-01
> Lot en cours : **A2 — Configuration Django et utilisateur custom** (réalisé, en attente de validation)

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
| A | **A2** | Projet Django, settings, configuration, utilisateur custom | **Réalisé — en attente de validation** |
| A | A3 | Modèles, migrations initiales, admin | Non démarré |
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

## 6. Décisions structurantes

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

## 7. Problèmes rencontrés et points d'attention

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

### Points d'attention

- **Travail frontend antérieur non commité** : 8 fichiers modifiés (limites de
  galeries) ont été laissés intacts pendant A1 et A2. Ils devront être commités
  séparément après validation.
- `README.md` racine reste modifié par le travail frontend antérieur ; le guide
  backend est dans `backend/README.md` pour ne pas mélanger les deux.
- `pixeo.com`, le DNS wildcard et les certificats TLS ne sont pas vérifiés.
- `docs/LAUNCH.md` mentionne encore Supabase ; il sera actualisé en Phase E.
- Les dépendances de test (pytest, pytest-django) sont maintenant dans
  `backend/requirements-dev.txt`.

## 8. Prochain lot

**A3 — Modèles, migrations initiales et admin** (non démarré) :

- Générer la migration initiale de `accounts` après validation du modèle custom.
- Enregistrer l'utilisateur dans l'admin Django avec les champs Pixeo.
- Poursuivre les modèles prévus pour A3 selon la validation explicite.
- Ne pas démarrer les endpoints métier ni l'authentification avant les lots B/C.

## 9. Commandes utiles

```bash
# Backend
cd backend
source .venv/bin/activate
python --version
pip install -r requirements.txt
pip install -r requirements-dev.txt
pip check
python manage.py check
pytest

# Frontend (existant)
pnpm dev
pnpm build

# État Git
git status --short
```
