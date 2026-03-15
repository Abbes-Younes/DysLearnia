import { Kysely, Migrator, FileMigrationProvider, PostgresDialect } from 'kysely'
import { Pool } from 'pg'
import { promises as fs } from 'fs'
import path from 'path'
import { Database } from '../types'
import * as dotenv from 'dotenv'

// Load .env.local
dotenv.config({ path: '.env.local' })
dotenv.config({ path: '.env' }) // fallbac

async function migrateToLatest() {
  const db = new Kysely<Database>({
    dialect: new PostgresDialect({
      pool: new Pool({
        connectionString: process.env.DATABASE_URL,
      }),
    }),
  })

  const migrator = new Migrator({
    db,
    provider: new FileMigrationProvider({
      fs,
      path,
      migrationFolder: path.join(process.cwd(), 'app/lib/kysely/migrations'),
    }),
  })

  const { error, results } = await migrator.migrateToLatest()

  results?.forEach((result) => {
    if (result.status === 'Success') {
      console.log(`✅ migration "${result.migrationName}" applied successfully`)
    } else if (result.status === 'Error') {
      console.error(`❌ migration "${result.migrationName}" failed`)
    }
  })

  if (error) {
    console.error('Migration failed:', error)
    process.exit(1)
  }

  console.log('\nAll migrations applied!')
  await db.destroy()
}

migrateToLatest()
