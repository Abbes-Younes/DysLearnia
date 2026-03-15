import { Kysely, sql } from 'kysely'

export async function up(db: Kysely<unknown>): Promise<void> {
  await db.schema
    .createTable('lectures')
    .ifNotExists()
    .addColumn('id', 'uuid', (col) =>
      col.primaryKey().defaultTo(sql`gen_random_uuid()`)
    )
    .addColumn('created_at', 'timestamptz', (col) =>
      col.defaultTo(sql`now()`).notNull()
    )
    .addColumn('user_id', 'uuid', (col) => col.references('auth.users.id'))
    .addColumn('file_name', 'text')
    .addColumn('file_url', 'text')
    .addColumn('raw_text', 'text')
    .addColumn('simplified_text', 'text')
    .addColumn('summary', 'text')
    .addColumn('status', 'text', (col) => col.defaultTo('pending'))
    .execute()
}

export async function down(db: Kysely<unknown>): Promise<void> {
  await db.schema.dropTable('lectures').ifExists().execute()
}
