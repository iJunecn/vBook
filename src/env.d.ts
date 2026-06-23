/// <reference path="../.astro/types.d.ts" />

interface ImportMetaEnv {
  readonly DATABASE_URL: string;
  readonly AGNES_API_KEY: string;
  readonly AGNES_BASE_URL: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}

declare namespace App {
  interface Locals {
    user: import('lucia').User | null;
    session: import('lucia').Session | null;
  }
}
