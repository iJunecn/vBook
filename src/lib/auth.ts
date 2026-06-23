import { Lucia } from 'lucia';
import { DrizzlePostgreSQLAdapter } from '@lucia-auth/adapter-drizzle';
import { db } from './db';
import { sessions, users } from './schema';
import type { Campus } from './schema';

const adapter = new DrizzlePostgreSQLAdapter(db, sessions, users);

export const lucia = new Lucia(adapter, {
  sessionCookie: {
    attributes: { secure: import.meta.env.PROD },
  },
  // The drizzle adapter exposes the row using the schema's JS property
  // names (camelCase), so we read camelCase keys here.
  getUserAttributes: (attributes) => ({
    email: attributes.email,
    username: attributes.username,
    nickname: attributes.nickname,
    campus: attributes.campus,
    avatarUrl: attributes.avatarUrl,
  }),
});

declare module 'lucia' {
  interface Register {
    Lucia: typeof lucia;
    DatabaseUserAttributes: {
      email: string;
      username: string;
      nickname: string | null;
      campus: Campus | null;
      avatarUrl: string | null;
    };
  }
}
