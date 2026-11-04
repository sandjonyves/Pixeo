# Pixeo — Contrat API

> **Statut : fondation API A4 et authentification A5.**
> Les endpoints techniques `health`, `schema`, `docs` et `redoc` sont implémentés,
> ainsi que le versionnement `/api/v1/`, les enveloppes de réponse, la gestion
> centralisée des erreurs, la pagination, les permissions de base et la conversion
> `camelCase`. Le lot A5 ajoute la connexion JWT, le cookie de refresh, sa
> rotation et sa révocation, le profil courant et la protection CSRF/CORS.
> La migration initiale, PostgreSQL et Django Admin restent en place.
> Les endpoints métier ci-dessous restent une cible : aucun endpoint
> d'inscription, de galerie, de photo, d'abonnement ou de paiement n'est exposé.

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
| Pagination | entrée `page`, `page_size` ; réponse `items`, `total`, `page`, `pageSize` |
| Documentation | OpenAPI via `drf-spectacular` ; Swagger UI et ReDoc |

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
  "error": "Les données fournies sont invalides.",
  "code": "VALIDATION_ERROR",
  "details": {
    "fieldName": ["Message"]
  }
}
```

Les codes sont stables et en majuscules. Codes transverses implémentés en A4 :
`VALIDATION_ERROR`, `INVALID_REQUEST`, `AUTHENTICATION_REQUIRED`,
`AUTHENTICATION_FAILED`, `PERMISSION_DENIED`, `NOT_FOUND`,
`METHOD_NOT_ALLOWED`, `UNSUPPORTED_MEDIA_TYPE`, `RATE_LIMITED`,
`INTERNAL_ERROR` et `API_ERROR`. Le lot A5 ajoute `INVALID_CREDENTIALS`,
`TOKEN_EXPIRED`, `TOKEN_INVALID`, `TOKEN_REVOKED`, `ACCOUNT_SUSPENDED`,
`ACCOUNT_DISABLED` et `CSRF_FAILED`. Les codes métier prévus (`CONFLICT`,
`GALLERY_LOCKED`, `INVALID_PASSWORD`, `INVALID_PIN`, `EXPIRED`,
`QUOTA_EXCEEDED`, `NOT_CONFIGURED`) seront ajoutés avec leurs endpoints.

Les détails de validation conservent les champs et les messages utiles, avec des
clés en `camelCase`, y compris pour les structures imbriquées. Les erreurs
internes ne renvoient jamais de trace Python, de secret ni de détail base de
données.

### Pagination

Les listes paginées acceptent `page` (numéro de page, à partir de 1) et
`page_size` (20 par défaut, 100 maximum). La réponse respecte le format :

```json
{
  "ok": true,
  "data": {
    "items": [],
    "total": 0,
    "page": 1,
    "pageSize": 20
  }
}
```

### camelCase

Les modèles et les serializers Django restent en `snake_case`. Les serializers
Pixeo convertissent les clés en `camelCase` à l'entrée et à la sortie, y compris
pour les structures imbriquées et les erreurs de validation. Les nouveaux
serializers doivent hériter de `PixeoSerializer` ou `PixeoModelSerializer`.

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
| 500 | Erreur interne générique, sans détail sensible |
| 503 | Base indisponible ou fonctionnalité non configurée |

## 2. Authentification

### 2.1 Endpoints implémentés en A5

| Méthode | Route | Authentification | Description |
|---------|-------|------------------|-------------|
| POST | `/api/v1/auth/login/` | CSRF | Vérifie e-mail + mot de passe ; retourne l'access token et pose le cookie de refresh |
| POST | `/api/v1/auth/refresh/` | Cookie de refresh + CSRF | Effectue la rotation, blackliste l'ancien refresh et retourne un nouvel access token |
| POST | `/api/v1/auth/logout/` | Cookie de refresh + CSRF | Blackliste le refresh s'il est valide et supprime le cookie |
| GET | `/api/v1/auth/me/` | Bearer ou session Django | Retourne le profil courant, sans secret |
| GET | `/api/v1/auth/csrf/` | Aucune | Pose le cookie CSRF et retourne le jeton à envoyer dans `X-CSRFToken` |

Les endpoints d'inscription, de mise à jour du profil, de changement ou de
réinitialisation de mot de passe ne sont **pas** implémentés en A5. Ils restent
dans la cible des lots ultérieurs.

### 2.2 Tokens et cookies

- L'identifiant de connexion est l'e-mail (`User.USERNAME_FIELD = "email"`) ; le
  modèle `User` n'a pas de champ `username`.
- L'access token est un JWT signé, de courte durée (10 minutes par défaut,
  configurable via `AUTH_ACCESS_TOKEN_LIFETIME_MINUTES`). Il est retourné dans
  `data.accessToken` et doit être envoyé avec `Authorization: Bearer <token>`.
- L'access token reste en mémoire côté frontend ; il ne doit pas être stocké dans
  `localStorage` ou `sessionStorage`.
- Le refresh token est **uniquement** dans un cookie `HttpOnly`, `SameSite=Lax`,
  `Secure` en production, host-only par défaut (aucun `Domain` global). Son
  chemin est `/api/v1/auth/`. Il n'apparaît jamais dans le JSON.
- La durée de vie du refresh est de 7 jours par défaut
  (`AUTH_REFRESH_TOKEN_LIFETIME_DAYS`). Chaque refresh effectue une rotation :
  l'ancien jeton R1 est blacklisté et ne peut plus être réutilisé.
- La réutilisation de R1 est détectée et refusée avec `401 TOKEN_REVOKED`.
  SimpleJWT blackliste le jeton individuel, pas toute sa famille : dans la
  politique A5, le refresh suivant R2 reste valide après la détection du rejeu
  de R1. Une révocation de famille n'est pas implémentée.
- La déconnexion blackliste le refresh courant et supprime le cookie. L'access
  token déjà émis reste valide jusqu'à son expiration : il n'existe pas de
  révocation immédiate d'un access token JWT dans ce lot.

Exemple de réponse de connexion :

```json
{
  "ok": true,
  "data": {
    "accessToken": "<jwt>",
    "user": {
      "id": "00000000-0000-0000-0000-000000000000",
      "email": "photographer@example.com",
      "firstName": "Jean",
      "lastName": "Dupont",
      "role": "photographer",
      "brandingUsername": "jean-dupont",
      "isActive": true,
      "isSuspended": false,
      "dateJoined": "2026-11-03T00:00:00Z"
    }
  }
}
```

Le cookie est posé dans l'en-tête `Set-Cookie` et n'est pas répété dans
`data`. La réponse de refresh ne contient que `data.accessToken`.

### 2.3 CSRF et CORS

- `GET /api/v1/auth/csrf/` retourne `data.csrfToken` et pose le cookie CSRF
  Django. Le frontend envoie ce jeton dans `X-CSRFToken` pour `POST
  /api/v1/auth/login/`, `POST /api/v1/auth/refresh/` et `POST
  /api/v1/auth/logout/`.
- Le login exige aussi un jeton CSRF : il crée un état d'authentification et
  dépose un cookie de refresh. Sans jeton, il retourne `403 CSRF_FAILED` sans
  créer de session.
- Le login n'accepte que `Content-Type: application/json`. Une soumission HTML
  classique (`application/x-www-form-urlencoded` ou `multipart/form-data`) ou un
  corps `text/plain` ne peut pas créer de session : le refus est un `403` sans
  CSRF, ou un `400`/`415` avec un jeton CSRF valide.
- La vérification CSRF n'est pas désactivée globalement. Un échec retourne
  `403` avec le code `CSRF_FAILED`.
- CORS n'autorise que les origines explicitement déclarées, avec
  `CORS_ALLOW_CREDENTIALS=True`. Aucun wildcard global n'est activé en
  production. Une requête JSON cross-origin déclenche un preflight ; une origine
  non autorisée ne reçoit pas `Access-Control-Allow-Origin` et le navigateur
  n'envoie pas la requête réelle. CORS est une défense complémentaire, pas un
  remplacement du CSRF.
- Le frontend et l'API doivent rester **same-site** pour que le cookie
  `SameSite=Lax` soit envoyé ; le frontend utilise `credentials: "include"`.
- Le cookie CSRF et le cookie de refresh restent host-only. Le frontend lit le
  jeton CSRF dans la réponse JSON, pas via `document.cookie`.

### 2.4 Statut du compte et permissions

- Un compte `is_active=False` est refusé avec `ACCOUNT_DISABLED`.
- Un compte `is_suspended=True` est refusé avec `ACCOUNT_SUSPENDED`.
- Ces contrôles sont effectués à la connexion, au refresh et à **chaque requête
  authentifiée** : un ancien access token ou un ancien refresh token ne permet
  pas de contourner une suspension ou une désactivation.
- `IsPhotographer` et `IsPlatformAdmin` vérifient également le rôle et le statut
  courant. La permission par défaut des vues privées reste `IsAuthenticated`.
- Un e-mail inconnu et un mot de passe incorrect renvoient la même réponse
  `401 INVALID_CREDENTIALS`, sans indiquer lequel est faux.

### 2.5 Throttling

- Connexion : 5 tentatives par minute et par identité réseau par défaut
  (`AUTH_LOGIN_RATE`).
- Refresh : 30 renouvellements par minute et par identité réseau par défaut
  (`AUTH_REFRESH_RATE`).
- Le dépassement retourne `429 RATE_LIMITED`. Le throttling DRF est une
  protection complémentaire, pas une solution anti-brute-force complète ; en
  production derrière un proxy, configurer correctement la confiance dans
  `X-Forwarded-For`.

### 2.6 Erreurs d'authentification

| Code | HTTP | Sens |
|------|------|------|
| `INVALID_CREDENTIALS` | 401 | E-mail inconnu ou mot de passe incorrect |
| `AUTHENTICATION_REQUIRED` | 401 | Aucun token ou aucune session |
| `TOKEN_EXPIRED` | 401 | Access ou refresh expiré |
| `TOKEN_INVALID` | 401 | Jeton malformé, mauvais type ou compte introuvable |
| `TOKEN_REVOKED` | 401 | Refresh blacklisté ou déjà utilisé |
| `ACCOUNT_SUSPENDED` | 403 | Compte suspendu |
| `ACCOUNT_DISABLED` | 403 | Compte désactivé |
| `CSRF_FAILED` | 403 | Jeton CSRF absent, invalide ou origine refusée |
| `RATE_LIMITED` | 429 | Quota de tentatives dépassé |

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

## 9. Santé, versionnement et documentation

| Méthode | Route | Description |
|---------|-------|-------------|
| GET | `/api/v1/` | Racine versionnée ; enveloppe de succès |
| GET | `/api/v1/health/` | Vérifie Django et PostgreSQL (`SELECT 1`) |
| GET | `/api/v1/schema/` | Schéma OpenAPI (JSON avec `?format=json`) |
| GET | `/api/v1/docs/` | Swagger UI |
| GET | `/api/v1/redoc/` | ReDoc |

Le préfixe public est `/api/<version>/`. Seule la version `v1` est autorisée en
A5 ; une version inconnue est rejetée avec l'enveloppe d'erreur standard. Le
endpoint de santé est conservé hors routeur pour préserver exactement son
contrat historique.

La documentation OpenAPI est librement accessible en développement. En
production, elle est réservée aux administrateurs authentifiés via la session
Django. Les routes métier ne sont pas documentées tant qu'elles n'existent pas.

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
- Les erreurs DRF passent toutes par le gestionnaire central et utilisent
  l'enveloppe standard ; aucune trace Python n'est exposée.
- Les serializers métier héritent de `PixeoSerializer` ou
  `PixeoModelSerializer` pour garantir le camelCase.
