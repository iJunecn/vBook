import { drizzle } from 'drizzle-orm/postgres-js';
import postgres from 'postgres';
import * as schema from './schema';

// Read at runtime via process.env (NOT import.meta.env, which Vite statically
// inlines at build time) so the same built image is configured per-environment
// by injected env vars — required for the k8s deploy.
const connectionString = process.env.DATABASE_URL;

if (!connectionString) {
  throw new Error('DATABASE_URL is not set');
}

// Reuse a single client across hot-reloads / requests.
const client = postgres(connectionString);

export const db = drizzle(client, { schema });
