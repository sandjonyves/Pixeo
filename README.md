# Pixeo

Galerie photo en ligne pour photographes — livraison client, galeries privées et abonnements.

## Stack

- Next.js (App Router)
- React + TypeScript
- Tailwind CSS

## Démarrage

```bash
pnpm install
pnpm dev
```

Ouvre [http://localhost:3000](http://localhost:3000).

### Comptes démo

| Rôle | Email | Mot de passe |
|------|-------|--------------|
| Photographe | `demo@pixeo.app` | `demo1234` |
| Admin plateforme | `admin@pixeo.app` | `admin1234` |

## Carte des routes

| Route | Description |
|-------|-------------|
| `/` | Landing Pixeo |
| `/pricing` | Tarifs et plans |
| `/login` | Connexion photographe |
| `/register` | Inscription |
| `/collections` | Dashboard — collections |
| `/library` | Dashboard — bibliothèque photos |
| `/starred` | Dashboard — favoris |
| `/homepage` | Dashboard — homepage publique |
| `/settings` | Dashboard — branding & préférences |
| `/billing` | Dashboard — plan et usage |
| `/account` | Compte utilisateur |
| `/site` | Homepage publique du photographe |
| `/c/[slug]` | Galerie client publique |
| `/admin` | Console admin Pixeo |
| `/api/health` | Health check API |

## Checklist de test manuel

### Auth & onboarding
- [ ] Landing `/` : CTA vers pricing et register
- [ ] Login avec `demo@pixeo.app` / `demo1234` → redirect collections
- [ ] Login admin `admin@pixeo.app` / `admin1234` → accès `/admin`
- [ ] Register avec plan free → watermark mentionné

### Dashboard photographe
- [ ] Sidebar : Collections, Library, Starred, Homepage, Settings, Billing (pas de Marketing)
- [ ] Créer / éditer collection, upload photos
- [ ] Publier galerie, copier lien `/c/[slug]`
- [ ] Billing : plan actuel, jauges storage/galleries, upgrade mock
- [ ] Account : nom du plan + lien billing

### Galeries publiques
- [ ] `/site` : liste des collections publiées
- [ ] `/c/yves` : galerie démo avec lightbox
- [ ] Téléchargement désactivé → bouton grisé + toast
- [ ] Favoris désactivés → cœur grisé + toast
- [ ] Footer « Powered by Pixeo » visible
- [ ] Plan free → bannière filigrane Pixeo

### Admin
- [ ] `/admin` : overview, photographes, plans, billing mock

### API
- [ ] `GET /api/health` → `{ "ok": true, "service": "pixeo" }`

## Scripts

- `pnpm dev` — serveur de développement
- `pnpm build` — build production
- `pnpm start` — démarrer le build

## Documentation

- [Architecture cible](docs/ARCHITECTURE.md)
- [Checklist launch](docs/LAUNCH.md)
- Variables d'environnement : `.env.example`
