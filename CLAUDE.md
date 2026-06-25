# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

vBook (贝壳易书) — a campus second-hand book trading platform. Sellers photograph book spines → AI identifies the books → seller confirms and lists them; buyers browse, filter by campus, and buy. The UI copy is Simplified Chinese.

## Commands

```bash
npm run dev          # Astro dev server
npm run build        # Production build (esbuild transform; does NOT type-check)
npm run preview      # Serve the built Node standalone output
npx astro check      # Full TypeScript + .astro/.vue type check — the real "lint"
npx astro sync       # Regenerate .astro/types.d.ts after schema/env changes

npm run db:generate  # Generate SQL migration from src/lib/schema.ts into drizzle/
npm run db:migrate   # Apply migrations to DATABASE_URL
npm run db:push      # Push schema directly (dev shortcut, skips migration files)
npm run db:studio    # Drizzle Studio
```

There is no test suite. Treat `npx astro check` (must report 0 errors) as the gate before considering work done — `npm run build` will silently pass code with type errors because the Vite/esbuild transform strips types without checking them.

Drizzle commands read `DATABASE_URL` from `.env` automatically (drizzle-kit auto-loads it).

## Environment

Requires `.env` (copy from `.env.example`): `DATABASE_URL` (PostgreSQL), `AGNES_API_KEY`, `AGNES_BASE_URL` (OpenAI-compatible endpoint, should end in `/v1`). These are typed in [src/env.d.ts](src/env.d.ts) and read via `import.meta.env.*`, not `process.env`.

## Architecture

Single Astro 5 app in SSR mode (`output: 'server'`, Node standalone adapter) — frontend and backend live together. There is no separate API server.

- **Rendering model**: `.astro` pages run server-side per request (most declare `export const prerender = false`), query the DB directly in their frontmatter, and hydrate Vue components as islands (`client:load`). Server-rendered DB rows are passed into islands as props.
- **Vue islands** ([src/components/vue/](src/components/vue/)) are separate mini-apps and cannot share reactive state across island boundaries. When multiple widgets must coordinate, they are composed inside one parent island rather than placed side-by-side — e.g. `BookGrid.vue` owns the search/campus state and embeds `SearchBar`/`CampusFilter`/`BookCard`; `SellFlow.vue` orchestrates `ImageUploader` → `/api/recognize` → `RecognitionTable` → `/api/listings`.
- **Two client→server patterns**: forms that need a redirect (login/register/logout/profile) use plain `<form method="post">` so the browser follows the API's 302; everything else (recognize, list, buy, status change) uses `fetch` with JSON from inside a Vue island.

### Auth (Lucia v3 + session cookies)

[src/middleware.ts](src/middleware.ts) runs on every request, validates the session cookie, refreshes/clears it, and sets `Astro.locals.user` / `Astro.locals.session` (typed in [src/env.d.ts](src/env.d.ts)). Pages guard with `if (!Astro.locals.user) return Astro.redirect('/auth/login')`; API routes return JSON 401. Passwords are hashed with `bcryptjs`.

Gotcha: the Drizzle adapter exposes user rows by their **schema JS property names (camelCase)**, so `getUserAttributes` in [src/lib/auth.ts](src/lib/auth.ts) reads `attributes.avatarUrl`, not `avatar_url`. Keep `DatabaseUserAttributes` and `getUserAttributes` in sync with the `users` table when adding fields.

### Data layer

[src/lib/schema.ts](src/lib/schema.ts) is the single source of truth (Drizzle). Domain shape: a `listing` (one seller, one upload session) owns many `books`; an `order` references exactly one `book` (unique constraint) and a buyer. A book's seller is reached via `books → listings.sellerId`, so ownership/seller queries always join through `listings`.

Mutations that must stay atomic use `db.transaction()`: listing creation (insert listing + books), and order placement. **Order placement locks the book row with `.for('update')`** before checking `status === 'available'` to prevent oversell — preserve this pattern for any new purchase-like flow.

`price` is a Postgres `numeric` and surfaces as a **string** throughout TS — keep it a string in props/JSON and parse only when doing math.

### Enums

`campusEnum` (`main`/`north`/`south`/`east`) and `bookStatusEnum` (`available`/`sold`/`removed`) are DB enums. Human labels for campus live in [src/components/vue/types.ts](src/components/vue/types.ts) (`CAMPUS_LABELS`) and in the page-level option lists — update both, plus regenerate a migration, when changing enum values.

### AI recognition

[src/lib/ai.ts](src/lib/ai.ts) calls the agnes model via the OpenAI SDK with an image + text prompt and expects a raw JSON array of `RecognizedBook`. The model is unreliable about format, so parsing falls back to regex-extracting the first `[...]` and returns `[]` on total failure rather than throwing — callers treat an empty result as "nothing recognized," not an error.
