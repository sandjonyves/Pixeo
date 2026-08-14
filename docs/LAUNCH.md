# Pixeo — Checklist soft launch

Checklist pour un lancement initial (démo → bêta fermée) avant intégration Stripe et stockage cloud réel.

## Avant le déploiement

- [ ] Variables d'environnement renseignées (voir `.env.example`)
- [ ] `pnpm build` passe sans erreur bloquante
- [ ] `GET /api/health` retourne `{ ok: true, service: "pixeo" }`
- [ ] Comptes démo fonctionnels (`demo@pixeo.app`, `admin@pixeo.app`)
- [ ] Page `/pricing` et `/billing` cohérentes avec `lib/plans.ts`
- [ ] Filigrane « Powered by Pixeo » visible sur galeries publiques (plan Free)
- [ ] README à jour (routes, tests manuels)

## Hébergement (Vercel recommandé)

Next.js 16 se déploie sans configuration spéciale :

```bash
pnpm build
pnpm start
```

Aucun `vercel.json` requis pour un déploiement standard App Router.  
Configurer sur Vercel :

- Framework preset : **Next.js**
- Build : `pnpm build`
- Root : répertoire du projet
- Env : `NEXT_PUBLIC_APP_URL` = URL de production

## Stripe (phase ultérieure)

- [ ] Créer produits / prix alignés sur les plans FCFA
- [ ] Webhook `checkout.session.completed` → upsert `subscriptions`
- [ ] Portail client Stripe pour annulation / factures
- [ ] Remplacer `changePlan()` mock dans `gallery-context` par API + Stripe
- [ ] Page billing : statut abonnement réel, pas seulement boutons « Upgrade »

## Plan Free & filigrane

- Plan **Free** : filigrane Pixeo sur galeries publiques (`Powered by Pixeo` + bannière optionnelle).
- Plans payants (Starter+) : pas de filigrane Pixeo par défaut.
- Mention explicite sur `/billing` et `/pricing` pour le plan Free.
- Option photographe : `branding.watermarkEnabled` pour filigrane personnalisé (Pro+).

## Sécurité & conformité (bêta)

- [ ] Mots de passe hashés (Supabase Auth) — **ne pas** shipper les mots de passe en clair comme la démo
- [ ] RLS activé sur toutes les tables
- [ ] URLs signées courtes durée pour téléchargements
- [ ] Rate limiting sur login et upload
- [ ] Politique de confidentialité + CGU (pages statiques)

## Communication launch

- [ ] Landing `/` : proposition de valeur claire
- [ ] Lien `/register?plan=free` pour onboarding
- [ ] Email de bienvenue (template Settings → Email Templates, backend)
- [ ] Support : chat mock → outil réel (Crisp, Intercom, etc.)

## Métriques post-launch

- Inscriptions / jour
- Galeries publiées
- Taux conversion Free → Starter
- Erreurs 5xx sur `/api/*`
- Temps de chargement galerie publique (LCP)

## Rollback

- Tag git par release
- Vercel : promote previous deployment
- Migrations DB : toujours réversibles ou additive-only en bêta
