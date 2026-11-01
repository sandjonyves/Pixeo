# Pixeo — Contrat API

> **Statut : document de conception, lot A3.**
> Seuls les endpoints techniques `health`, `schema` et `docs` sont implémentés.
> La migration initiale, PostgreSQL et Django Admin sont en place ; aucun endpoint
> métier ni authentification JWT n'est encore exposé. Les chemins métier
> ci-dessous constituent la cible validée et seront ajustés, le cas échéant, lors
> des lots backend.

## 1. Conventions générales

| Élément | Convention |
|---------|------------|
| Préfixe | `/api/v1/` |
| Format | JSON UTF-8 |
| Champs | `camelCase` dans les réponses et requêtes |
| Dates | ISO 8601 UTC |
| Identifiants | UUID |
| Authentification | `Authorization: Bearer <accessToken>` |
| Refresh | Cookie HttpOnly `pixeo_refresh` (jamais accessible en JS) |
| CSRF | `X-CSRFToken` sur les requêtes mutantes |
| Pagination | `page`, `pageSize` ; réponse `items`, `total`, `page`, `pageSize` |
| Documentation | OpenAPI via `drf-spectacular` (prévu) |

### Enveloppe de succès

```json
{
  "ok": true,
  "data": {}
}
```

### Enveloppe d'erreur

```json
{
  "ok": false,
  "error": "Message lisible",
  "code": "validation_error",
  "details": {
    "field": ["Message"]
  }
}
```

Codes d'erreur prévus : `validation_error`, `authentication_required`,
`permission_denied`, `not_found`, `conflict`, `rate_limited`,
`gallery_locked`, `invalid_password`, `invalid_pin`, `expired`,
`quota_exceeded`, `not_configured`, `server_error`.

### Codes HTTP

| Code | Usage |
|------|-------|
| 200 | Lecture / mise à jour |
| 201 | Création |
| 204 | Suppression |
| 400 | Requête invalide |
| 401 | Authentification absente ou invalide |
| 403 | Droits insuffisants / accès refusé |
| 404 | Ressource inexistante ou hors tenant |
| 409 | Conflit (slug, état) |
| 410 | Lien ou galerie expiré |
| 422 | Validation métier |
| 429 | Rate limit |
| 503 | Base indisponible ou fonctionnalité non configurée |

## 2. Authentification

| Méthode | Route | Description |
|---------|-------|-------------|
| POST | `/api/v1/auth/register/` | Inscription photographe + Free + branding + homepage (transaction) |
| POST | `/api/v1/auth/login/` | Connexion ; access en réponse, refresh en cookie |
| POST | `/api/v1/auth/refresh/` | Rotation du refresh token |
| POST | `/api/v1/auth/logout/` | Blacklist du refresh + suppression cookie |
| GET | `/api/v1/auth/me/` | Profil courant (sans secret) |
| PATCH | `/api/v1/auth/me/` | Mise à jour du profil |
| POST | `/api/v1/auth/password/change/` | Changement de mot de passe |
| POST | `/api/v1/auth/password/reset/request/` | Demande de réinitialisation (V1 : journalisée) |
| POST | `/api/v1/auth/password/reset/confirm/` | Confirmation par token |

Règles :

- L'identifiant de connexion est l'e-mail (`User.USERNAME_FIELD = "email"`) ; le
  modèle `User` n'a pas de champ `username`.
- L'access token n'est jamais stocké dans `localStorage`.
- Le refresh token est `HttpOnly`, `Secure` en production, avec rotation.
- Le login et la réinitialisation sont rate-limités.
- Un compte `suspended` ne peut pas se connecter.
- Au lot C5, l'authentification JWT vérifiera `is_suspended` à **chaque requête**
  (et pas seulement au login) : un access token encore valide ne donnera plus
  accès à l'API dès la suspension. `is_active` reste réservé à la désactivation
  Django ; la suspension métier est portée par `is_suspended`.

## 3. Studio (photographe authentifié)

| Méthode | Route | Description |
|---------|-------|-------------|
| GET/PATCH | `/api/v1/studio/branding/` | Logo, favicon, filigrane, username |
| GET/PATCH | `/api/v1/studio/homepage/` | Activation, bio, nom de marque |
| POST | `/api/v1/studio/homepage/password/` | Définir le mot de passe (hashé) |
| POST | `/api/v1/studio/homepage/password/reset/` | Réinitialiser (hashé) |
| GET | `/api/v1/studio/subscription/` | Plan actif depuis `Subscription` |
| GET | `/api/v1/studio/usage/` | Stockage utilisé / quota |

Le changement de plan self-service est **désactivé en V1** ; seul l'admin peut le
faire.

## 4. Collections / galeries (photographe authentifié)

> Le frontend appelle « collection » ce que l'API nomme « gallery ».

| Méthode | Route | Description |
|---------|-------|-------------|
| GET | `/api/v1/galleries/` | Liste filtrée par tenant |
| POST | `/api/v1/galleries/` | Créer (aucune limite de nombre) |
| GET | `/api/v1/galleries/{id}/` | Détail |
| PATCH | `/api/v1/galleries/{id}/` | Mise à jour |
| DELETE | `/api/v1/galleries/{id}/` | Supprimer la collection (pas les photos) |
| POST | `/api/v1/galleries/{id}/publish/` | Publier |
| POST | `/api/v1/galleries/{id}/unpublish/` | Repasser en brouillon |
| POST | `/api/v1/galleries/{id}/password/` | Définir le mot de passe (hashé) |
| POST | `/api/v1/galleries/{id}/password/reset/` | Réinitialiser |
| POST | `/api/v1/galleries/{id}/client-access-code/` | Générer/réinitialiser le code exclusif |
| POST | `/api/v1/galleries/{id}/download-pin/` | Définir/réinitialiser le PIN (hashé) |
| POST | `/api/v1/galleries/{id}/share-link/` | Créer/renouveler le lien pre-release |
| GET | `/api/v1/galleries/{id}/activity/` | Journal d'activité |

### Sets

| Méthode | Route | Description |
|---------|-------|-------------|
| GET/POST | `/api/v1/galleries/{id}/sets/` | Lister / créer |
| PATCH/DELETE | `/api/v1/galleries/{id}/sets/{setId}/` | Modifier / supprimer |
| PATCH | `/api/v1/galleries/{id}/sets/reorder/` | Réordonner |

### Photos dans une collection

| Méthode | Route | Description |
|---------|-------|-------------|
| GET | `/api/v1/galleries/{id}/photos/` | Photos rattachées |
| POST | `/api/v1/galleries/{id}/photos/` | Rattacher des photos de la bibliothèque |
| DELETE | `/api/v1/galleries/{id}/photos/{photoId}/` | Détacher (ne supprime pas le fichier) |
| PATCH | `/api/v1/galleries/{id}/photos/reorder/` | Réordonner |

## 5. Bibliothèque de photos

| Méthode | Route | Description |
|---------|-------|-------------|
| GET | `/api/v1/photos/` | Liste paginée, filtrée par tenant |
| POST | `/api/v1/photos/` | Upload multipart (dev) / URL signée (prod) |
| GET | `/api/v1/photos/{id}/` | Détail |
| PATCH | `/api/v1/photos/{id}/` | Renommer, favori |
| DELETE | `/api/v1/photos/{id}/` | Supprimer de la bibliothèque si non référencée |
| POST | `/api/v1/photos/{id}/star/` | Basculer le favori |

Règles :

- Le quota de stockage est vérifié avant l'upload.
- Une photo peut appartenir à plusieurs collections.
- La suppression d'une liaison ne supprime jamais le fichier.

## 6. Accès public aux galeries

Le username est explicite dans le chemin pour éviter toute ambiguïté de tenant.

| Méthode | Route | Description |
|---------|-------|-------------|
| GET | `/api/v1/public/{username}/` | Homepage publique du photographe |
| GET | `/api/v1/public/{username}/galleries/{slug}/` | Galerie publique |
| POST | `/api/v1/public/{username}/galleries/{slug}/unlock/` | Mot de passe de galerie |
| POST | `/api/v1/public/{username}/galleries/{slug}/client-access/` | Code client exclusif |
| POST | `/api/v1/public/{username}/galleries/{slug}/download-pin/` | PIN de téléchargement |
| POST | `/api/v1/public/{username}/galleries/{slug}/favorites/` | Favori (activité) |
| POST | `/api/v1/public/{username}/galleries/{slug}/notes/` | Note (activité) |
| GET | `/api/v1/public/{username}/galleries/{slug}/downloads/{photoId}/` | Téléchargement autorisé |
| GET | `/api/v1/public/pre-release/{shareToken}/` | Lien privé pre-release |

Règles :

- Les galeries `pre-release` ne sont jamais listées sur la homepage.
- Le lien pre-release vérifie `share_token` **et** l'expiration côté serveur.
- Les mots de passe, codes et PIN sont vérifiés côté serveur, jamais renvoyés.
- Les tentatives sont rate-limitées (429 + `Retry-After`).
- Les favoris et notes V1 alimentent `GalleryActivity` avec un identifiant
  visiteur persistant ; ils ne modifient pas la bibliothèque.
- `?preview=1` ne contourne aucun contrôle ; la prévisualisation owner exige un
  JWT photographe et la propriété de la collection.

## 7. Contacts, partages et marketing

| Méthode | Route | Description |
|---------|-------|-------------|
| GET/POST | `/api/v1/contacts/` | Lister / créer |
| PATCH/DELETE | `/api/v1/contacts/{id}/` | Modifier / supprimer |
| GET/POST | `/api/v1/galleries/{id}/shares/` | Historique / créer un partage |
| GET/POST | `/api/v1/campaigns/` | Campagnes (V1 : brouillon) |
| PATCH/DELETE | `/api/v1/campaigns/{id}/` | Modifier / supprimer |

En V1, aucun email réel n'est envoyé. Les partages sont journalisés ; une
tentative d'envoi réel renvoie `not_configured` si le backend email n'est pas
configuré.

## 8. Administration plateforme

| Méthode | Route | Description |
|---------|-------|-------------|
| GET | `/api/v1/admin/overview/` | Statistiques globales |
| GET | `/api/v1/admin/users/` | Photographes |
| PATCH | `/api/v1/admin/users/{id}/` | Statut, rôle, plan (admin uniquement) |
| GET/POST | `/api/v1/admin/plans/` | Catalogue des plans |
| PATCH/DELETE | `/api/v1/admin/plans/{id}/` | Modifier / désactiver |
| GET | `/api/v1/admin/subscriptions/` | Abonnements |
| PATCH | `/api/v1/admin/subscriptions/{id}/` | Changer le plan |
| GET | `/api/v1/admin/billing-events/` | Historique |
| GET/PATCH | `/api/v1/admin/settings/` | Paramètres plateforme |

Toutes les routes admin exigent `role = platform_admin` et sont auditées.

## 9. Santé et schéma

| Méthode | Route | Description |
|---------|-------|-------------|
| GET | `/api/v1/health/` | Vérifie Django et PostgreSQL (`SELECT 1`) |
| GET | `/api/v1/schema/` | OpenAPI (prévu) |
| GET | `/api/v1/docs/` | Documentation interactive (prévu) |

Health check disponible (HTTP 200) :

```json
{
  "ok": true,
  "service": "pixeo",
  "database": "available"
}
```

Health check avec base indisponible (HTTP 503) :

```json
{
  "ok": false,
  "service": "pixeo",
  "database": "unavailable"
}
```

La réponse ne contient ni identifiants, ni hôte, ni détail d'exception.

## 10. Règles transverses

- Toute requête authentifiée est filtrée par `request.user`.
- Un objet d'un autre tenant renvoie `404`, pas `403`, pour ne pas divulguer son
  existence.
- Les serializers n'exposent jamais un hash, un token de reset ou un secret.
- Les écritures sensibles sont atomiques.
- Les listes sont paginées ; les exports massifs seront ajoutés ultérieurement.
- Les champs inconnus sont refusés en écriture.
