import { pgTable, uuid, text, numeric, timestamp, pgEnum } from 'drizzle-orm/pg-core';

export const campusEnum = pgEnum('campus', ['main', 'north', 'south', 'east']);
export const bookStatusEnum = pgEnum('book_status', ['available', 'sold', 'removed']);

export const users = pgTable('users', {
  id: uuid('id').primaryKey().defaultRandom(),
  email: text('email').notNull().unique(),
  username: text('username').notNull().unique(),
  passwordHash: text('password_hash').notNull(),
  nickname: text('nickname'),
  campus: campusEnum('campus'),
  avatarUrl: text('avatar_url'),
  createdAt: timestamp('created_at').defaultNow().notNull(),
});

export const sessions = pgTable('sessions', {
  id: text('id').primaryKey(),
  userId: uuid('user_id')
    .notNull()
    .references(() => users.id),
  expiresAt: timestamp('expires_at', { withTimezone: true }).notNull(),
});

export const listings = pgTable('listings', {
  id: uuid('id').primaryKey().defaultRandom(),
  sellerId: uuid('seller_id')
    .notNull()
    .references(() => users.id),
  createdAt: timestamp('created_at').defaultNow().notNull(),
});

export const books = pgTable('books', {
  id: uuid('id').primaryKey().defaultRandom(),
  listingId: uuid('listing_id')
    .notNull()
    .references(() => listings.id),
  title: text('title').notNull(),
  author: text('author'),
  publisher: text('publisher'),
  isbn: text('isbn'),
  edition: text('edition'),
  price: numeric('price', { precision: 10, scale: 2 }).notNull(),
  status: bookStatusEnum('status').default('available').notNull(),
  createdAt: timestamp('created_at').defaultNow().notNull(),
});

export const orders = pgTable('orders', {
  id: uuid('id').primaryKey().defaultRandom(),
  bookId: uuid('book_id')
    .notNull()
    .references(() => books.id)
    .unique(),
  buyerId: uuid('buyer_id')
    .notNull()
    .references(() => users.id),
  createdAt: timestamp('created_at').defaultNow().notNull(),
});

export type User = typeof users.$inferSelect;
export type Listing = typeof listings.$inferSelect;
export type Book = typeof books.$inferSelect;
export type Order = typeof orders.$inferSelect;
export type Campus = (typeof campusEnum.enumValues)[number];
export type BookStatus = (typeof bookStatusEnum.enumValues)[number];
