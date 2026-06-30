# frontend

The `waapi-unof` dashboard — a Next.js (App Router) application. **UI only**: it
talks exclusively to the Django API over HTTPS (JWT) and listens to Server-Sent
Events for realtime (QR codes, device status).

> Implemented in **Phase 6** (core) and **Phase 15** (full dashboard). This README
> documents the intended layout; the app is scaffolded in those phases.

## Stack

- Next.js (latest stable, App Router) + TypeScript
- TailwindCSS + shadcn/ui
- TanStack React Query (server state) + Axios (HTTP client)

## Principles

- **Server Components by default**; Client Components only when interactivity
  requires them.
- Feature-first organization under `src/features/`.
- All API access goes through a typed client in `src/lib/api/`.
- Responsive, minimal, modern — inspired by Stripe / Vercel / Supabase / Railway.

## Structure

```
src/
├── app/
│   ├── (auth)/         # login, register
│   └── (dashboard)/    # devices, messages, webhooks, scheduler,
│                       # automation, api-keys, analytics, settings
├── components/ui/      # shadcn/ui primitives
├── features/           # feature-scoped components + hooks
├── lib/                # api (axios), auth, react-query, utils
├── hooks/              # shared hooks
├── types/              # shared TypeScript types
└── styles/             # global styles / Tailwind layers
```

## Develop

```bash
npm install
npm run dev     # http://localhost:3000
npm run lint
npm run build   # type-checks + production build
```

Set `NEXT_PUBLIC_API_BASE_URL` to the running API. See
[`../docs/development.md`](../docs/development.md).
