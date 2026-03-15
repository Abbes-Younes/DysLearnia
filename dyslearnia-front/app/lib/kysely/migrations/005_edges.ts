import { Kysely, sql } from 'kysely'

export async function up(db: Kysely<unknown>): Promise<void> {
  await db.schema
    .createTable('edges')
    .ifNotExists()
    .addColumn('id', 'uuid', (col) =>
      col.primaryKey().defaultTo(sql`gen_random_uuid()`)
    )
    .addColumn('workflow_id', 'uuid', (col) =>
      col.references('workflows.id').onDelete('cascade').notNull()
    )
    .addColumn('source_node_id', 'uuid', (col) =>
      col.references('nodes.id').onDelete('cascade').notNull()
    )
    .addColumn('target_node_id', 'uuid', (col) =>
      col.references('nodes.id').onDelete('cascade').notNull()
    )
    .addColumn('source_handle', 'varchar(100)')
    .addColumn('target_handle', 'varchar(100)')
    .addColumn('created_at', 'timestamptz', (col) =>
      col.defaultTo(sql`now()`).notNull()
    )
    .addColumn('updated_at', 'timestamptz', (col) =>
      col.defaultTo(sql`now()`).notNull()
    )
    .execute()

  // Create indexes for faster workflow edge queries
  await db.schema
    .createIndex('edges_workflow_id_idx')
    .ifNotExists()
    .on('edges')
    .column('workflow_id')
    .execute()

  await db.schema
    .createIndex('edges_source_node_id_idx')
    .ifNotExists()
    .on('edges')
    .column('source_node_id')
    .execute()

  await db.schema
    .createIndex('edges_target_node_id_idx')
    .ifNotExists()
    .on('edges')
    .column('target_node_id')
    .execute()
}

export async function down(db: Kysely<unknown>): Promise<void> {
  await db.schema.dropIndex('edges_target_node_id_idx').ifExists().execute()
  await db.schema.dropIndex('edges_source_node_id_idx').ifExists().execute()
  await db.schema.dropIndex('edges_workflow_id_idx').ifExists().execute()
  await db.schema.dropTable('edges').ifExists().execute()
}
