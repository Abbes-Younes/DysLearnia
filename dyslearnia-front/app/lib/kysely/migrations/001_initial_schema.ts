// Migration: 001_initial_schema
// Description: Create initial database schema for DysLearnia
// Created: 2026-03-15

import { Kysely, SqliteAdapter, SqliteIntrospector, SqliteDriver } from "kysely";

export async function up(db: Kysely<unknown>): Promise<void> {
  // Create users table
  await db.schema
    .createTable("users")
    .addColumn("id", "text", (col) => col.primaryKey())
    .addColumn("email", "text", (col) => col.notNull().unique())
    .addColumn("name", "text", (col) => col.notNull())
    .addColumn("password_hash", "text", (col) => col.notNull())
    .addColumn("avatar_url", "text", (col) => col)
    .addColumn("xp", "integer", (col) => col.notNull().defaultTo(0))
    .addColumn("streak", "integer", (col) => col.notNull().defaultTo(0))
    .addColumn("created_at", "datetime", (col) => col.notNull().defaultTo(new Date().toISOString()))
    .addColumn("updated_at", "datetime", (col) => col.notNull().defaultTo(new Date().toISOString()))
    .execute();

  // Create workflows table
  await db.schema
    .createTable("workflows")
    .addColumn("id", "text", (col) => col.primaryKey())
    .addColumn("user_id", "text", (col) => col.notNull().references("users.id").onDelete("cascade"))
    .addColumn("name", "text", (col) => col.notNull())
    .addColumn("description", "text", (col) => col)
    .addColumn("nodes", "text", (col) => col.notNull().defaultTo("[]")) // JSON array
    .addColumn("edges", "text", (col) => col.notNull().defaultTo("[]")) // JSON array
    .addColumn("is_public", "integer", (col) => col.notNull().defaultTo(0)) // boolean as integer
    .addColumn("created_at", "datetime", (col) => col.notNull().defaultTo(new Date().toISOString()))
    .addColumn("updated_at", "datetime", (col) => col.notNull().defaultTo(new Date().toISOString()))
    .execute();

  // Create nodes table
  await db.schema
    .createTable("nodes")
    .addColumn("id", "text", (col) => col.primaryKey())
    .addColumn("workflow_id", "text", (col) => col.notNull().references("workflows.id").onDelete("cascade"))
    .addColumn("type", "text", (col) => col.notNull())
    .addColumn("position_x", "real", (col) => col.notNull().defaultTo(0))
    .addColumn("position_y", "real", (col) => col.notNull().defaultTo(0))
    .addColumn("data", "text", (col) => col.notNull().defaultTo("{}")) // JSON object
    .addColumn("created_at", "datetime", (col) => col.notNull().defaultTo(new Date().toISOString()))
    .addColumn("updated_at", "datetime", (col) => col.notNull().defaultTo(new Date().toISOString()))
    .execute();

  // Create edges table
  await db.schema
    .createTable("edges")
    .addColumn("id", "text", (col) => col.primaryKey())
    .addColumn("workflow_id", "text", (col) => col.notNull().references("workflows.id").onDelete("cascade"))
    .addColumn("source_node_id", "text", (col) => col.notNull())
    .addColumn("target_node_id", "text", (col) => col.notNull())
    .addColumn("source_handle", "text", (col) => col)
    .addColumn("target_handle", "text", (col) => col)
    .addColumn("created_at", "datetime", (col) => col.notNull().defaultTo(new Date().toISOString()))
    .addColumn("updated_at", "datetime", (col) => col.notNull().defaultTo(new Date().toISOString()))
    .execute();

  // Create indexes for better query performance
  await db.schema
    .createIndex("idx_workflows_user_id")
    .on("workflows")
    .column("user_id")
    .execute();

  await db.schema
    .createIndex("idx_nodes_workflow_id")
    .on("nodes")
    .column("workflow_id")
    .execute();

  await db.schema
    .createIndex("idx_edges_workflow_id")
    .on("edges")
    .column("workflow_id")
    .execute();

  // Create migrations table to track applied migrations
  await db.schema
    .createTable("_migrations")
    .addColumn("id", "integer", (col) => col.autoIncrement().primaryKey())
    .addColumn("name", "text", (col) => col.notNull().unique())
    .addColumn("applied_at", "datetime", (col) => col.notNull().defaultTo(new Date().toISOString()))
    .execute();

  console.log("Migration 001_initial_schema completed successfully");
}

export async function down(db: Kysely<unknown>): Promise<void> {
  // Drop tables in reverse order (respecting foreign key constraints)
  await db.schema.dropTableIfExists("edges").execute();
  await db.schema.dropTableIfExists("nodes").execute();
  await db.schema.dropTableIfExists("workflows").execute();
  await db.schema.dropTableIfExists("users").execute();
  await db.schema.dropTableIfExists("_migrations").execute();

  console.log("Migration 001_initial_schema reverted successfully");
}
