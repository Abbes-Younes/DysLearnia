import { Kysely, sql } from 'kysely'

export async function up(db: Kysely<unknown>): Promise<void> {
  await db.schema
    .createTable('nodes')
    .ifNotExists()
    .addColumn('id', 'uuid', (col) =>
      col.primaryKey().defaultTo(sql`gen_random_uuid()`)
    )
    .addColumn('workflow_id', 'uuid', (col) =>
      col.references('workflows.id').onDelete('cascade').notNull()
    )
    .addColumn('type', 'varchar(100)', (col) => col.notNull())
    .addColumn('position_x', 'double precision', (col) => col.notNull())
    .addColumn('position_y', 'double precision', (col) => col.notNull())
    .addColumn('data', 'jsonb', (col) => col.defaultTo('{}').notNull())
    .addColumn('created_at', 'timestamptz', (col) =>
      col.defaultTo(sql`now()`).notNull()
    )
    .addColumn('updated_at', 'timestamptz', (col) =>
      col.defaultTo(sql`now()`).notNull()
    )
    .execute()

  // Create index for faster workflow node queries
  await db.schema
    .createIndex('nodes_workflow_id_idx')
    .ifNotExists()
    .on('nodes')
    .column('workflow_id')
    .execute()
}

export async function down(db: Kysely<unknown>): Promise<void> {
  await db.schema.dropIndex('nodes_workflow_id_idx').ifExists().execute()
  await db.schema.dropTable('nodes').ifExists().execute()
}
