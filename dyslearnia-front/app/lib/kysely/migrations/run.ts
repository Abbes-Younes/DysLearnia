// Migration runner for Kysely
// Usage: npx tsx app/lib/kysely/migrations/run.ts [up|down] [migration-name]

import { Kysely } from "kysely";
import { readdirSync } from "fs";
import { join } from "path";
import Database from "better-sqlite3";

import type { Database as DatabaseType } from "../types";

// Database configuration - update this for your setup
const DATABASE_PATH = process.env.DATABASE_PATH || "./dyslearnia.db";

interface Migration {
  name: string;
  up: (db: Kysely<DatabaseType>) => Promise<void>;
  down: (db: Kysely<DatabaseType>) => Promise<void>;
}

// Dynamic import for ES modules
async function loadMigrations(): Promise<Migration[]> {
  const migrationsDir = join(__dirname);
  const files = readdirSync(migrationsDir).filter(f => f.endsWith(".ts") && f !== "run.ts");
  
  const migrations: Migration[] = [];
  
  for (const file of files) {
    const migration = await import(join(migrationsDir, file));
    migrations.push({
      name: file.replace(".ts", ""),
      up: migration.up,
      down: migration.down
    });
  }
  
  return migrations.sort((a, b) => a.name.localeCompare(b.name));
}

// Using type assertion to work around Kysely type issues with better-sqlite3
function createKysely() {
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  return new Kysely<DatabaseType>({
    // @ts-expect-error - Using better-sqlite3 directly
    db: new Database(DATABASE_PATH)
  }) as Kysely<DatabaseType> & { db: Database.Database };
}

export async function runMigrations(direction: "up" | "down", specificMigration?: string): Promise<void> {
  const db = createKysely();

  try {
    // Ensure migrations table exists using raw SQL
    db.db.exec(`
      CREATE TABLE IF NOT EXISTS _migrations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE,
        applied_at TEXT NOT NULL
      )
    `);

    const migrations = await loadMigrations();
    
    // Get applied migrations using raw SQL
    const appliedRows = db.db.prepare("SELECT name FROM _migrations ORDER BY id ASC").all() as { name: string }[];
    const applied = appliedRows.map(row => row.name);

    console.log(`Current database: ${DATABASE_PATH}`);
    console.log(`Found ${migrations.length} migration files`);
    console.log(`Applied migrations: ${applied.length}`);

    if (direction === "up") {
      const pending = migrations.filter(m => !applied.includes(m.name));
      
      if (specificMigration) {
        const target = migrations.find(m => m.name === specificMigration);
        if (!target) {
          console.error(`Migration ${specificMigration} not found`);
          process.exit(1);
        }
        
        if (applied.includes(specificMigration)) {
          console.log(`Migration ${specificMigration} already applied`);
          return;
        }
        
        console.log(`Applying migration: ${specificMigration}`);
        await target.up(db);
        
        // Mark as applied using raw SQL
        db.db.prepare("INSERT INTO _migrations (name, applied_at) VALUES (?, ?)").run(specificMigration, new Date().toISOString());
        
        console.log(`Migration ${specificMigration} applied successfully`);
      } else {
        console.log(`\nApplying ${pending.length} pending migrations...\n`);
        
        for (const migration of pending) {
          console.log(`Applying: ${migration.name}`);
          await migration.up(db);
          
          // Mark as applied using raw SQL
          db.db.prepare("INSERT INTO _migrations (name, applied_at) VALUES (?, ?)").run(migration.name, new Date().toISOString());
          
          console.log(`✓ ${migration.name} applied`);
        }
        
        console.log(`\n${pending.length} migrations applied successfully`);
      }
    } else {
      // Down migrations
      const toRevert = specificMigration
        ? [migrations.find(m => m.name === specificMigration)].filter(Boolean) as Migration[]
        : [...applied].reverse().map(name => migrations.find(m => m.name === name)).filter(Boolean) as Migration[];
      
      if (toRevert.length === 0 || toRevert[0] === undefined) {
        console.log("No migrations to revert");
        return;
      }

      console.log(`\nReverting ${toRevert.length} migration(s)...\n`);
      
      for (const migration of toRevert) {
        if (!migration) continue;
        
        console.log(`Reverting: ${migration.name}`);
        await migration.down(db);
        
        // Mark as reverted using raw SQL
        db.db.prepare("DELETE FROM _migrations WHERE name = ?").run(migration.name);
        
        console.log(`✓ ${migration.name} reverted`);
      }
      
      console.log(`\n${toRevert.length} migrations reverted successfully`);
    }
  } catch (error) {
    console.error("Migration failed:", error);
    process.exit(1);
  } finally {
    db.db.close();
  }
}

// CLI handler
if (require.main === module) {
  const args = process.argv.slice(2);
  const direction = args[0] as "up" | "down";
  const migrationName = args[1];

  if (!direction || !["up", "down"].includes(direction)) {
    console.log("Usage: npx tsx app/lib/kysely/migrations/run.ts [up|down] [migration-name]");
    console.log("Examples:");
    console.log("  npx tsx app/lib/kysely/migrations/run.ts up          # Run all pending migrations");
    console.log("  npx tsx app/lib/kysely/migrations/run.ts up 001_initial_schema  # Run specific migration");
    console.log("  npx tsx app/lib/kysely/migrations/run.ts down        # Revert all migrations");
    console.log("  npx tsx app/lib/kysely/migrations/run.ts down 001_initial_schema  # Revert specific migration");
    process.exit(1);
  }

  runMigrations(direction, migrationName);
}
