import { Kysely, sql } from 'kysely'

export async function up(db: Kysely<unknown>): Promise<void> {
  await db.schema
    .createTable('workflows')
    .ifNotExists()
    .addColumn('id', 'uuid', (col) =>
      col.primaryKey().defaultTo(sql`gen_random_uuid()`)
    )
    .addColumn('user_id', 'uuid', (col) =>
      col.references('users.id').onDelete('cascade').notNull()
    )
    .addColumn('name', 'varchar(255)', (col) => col.notNull())
    .addColumn('description', 'text')
    .addColumn('nodes', 'jsonb', (col) => col.defaultTo('[]').notNull())
    .addColumn('edges', 'jsonb', (col) => col.defaultTo('[]').notNull())
    .addColumn('is_public', 'boolean', (col) => col.defaultTo(false).notNull())
    .addColumn('created_at', 'timestamptz', (col) =>
      col.defaultTo(sql`now()`).notNull()
    )
    .addColumn('updated_at', 'timestamptz', (col) =>
      col.defaultTo(sql`now()`).notNull()
    )
    .execute()

  // Create index for faster user workflow queries
  await db.schema
    .createIndex('workflows_user_id_idx')
    .ifNotExists()
    .on('workflows')
    .column('user_id')
    .execute()
}

export async function down(db: Kysely<unknown>): Promise<void> {
  await db.schema.dropIndex('workflows_user_id_idx').ifExists().execute()
  await db.schema.dropTable('workflows').ifExists().execute()
}
