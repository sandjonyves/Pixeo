# Pixeo — Développement backend

> Dernière mise à jour : 2026-10-31
> Lot en cours : **A1 — Initialisation et socle** (réalisé, en attente de validation)

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
| A | **A1** | Squelette `backend/`, venv, dépendances, `.env.example`, `.gitignore`, documentation, stratégie sous-domaines, audit nommage | **Réalisé — en attente de validation** |
| A | A2 | Projet Django, settings, configuration, utilisateur custom | Non démarré |
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

## 5. Décisions structurantes

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

## 6. Problèmes rencontrés et points d'attention

### Problème résolu pendant A1

- Première installation : `redis==8.1.0` entrait en conflit avec `kombu[redis]`
  (contrainte `redis < 6.5`) utilisé par Celery. La version a été ramenée à
  `redis==6.4.0`, puis l'installation et `pip check` ont réussi.
- Le miroir PyPI utilisé était lent ; aucune incidence sur le résultat final.

### Points d'attention

- **Travail frontend antérieur non commité** : 8 fichiers modifiés (limites de
  galeries) ont été laissés intacts pendant A1. Ils devront être commités
  séparément après validation.
- `README.md` n'a pas été modifié pendant A1 pour ne pas mélanger ce travail avec
  les modifications frontend en attente. Les liens documentaires pourront y être
  ajoutés après le commit frontend.
- `pixeo.com`, le DNS wildcard et les certificats TLS ne sont pas vérifiés.
- `docs/LAUNCH.md` mentionne encore Supabase ; il sera actualisé en Phase E.
- Les dépendances de développement/test (pytest, ruff, etc.) seront ajoutées en A2.

## 7. Prochain lot

**A2 — Projet Django et configuration** (non démarré) :

- Créer le projet Django dans `backend/`.
- Configurer les settings par environnement.
- Brancher `django-environ`, `dj-database-url`, CORS, DRF, spectacular.
- Créer l'utilisateur custom **avant** la première migration.
- Aucun endpoint métier.

## 8. Commandes utiles

```bash
# Backend
cd backend
source .venv/bin/activate
python --version
pip check

# Frontend (existant)
pnpm dev
pnpm build

# État Git
git status --short
```
