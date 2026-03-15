-- DysLearnia Database Schema
-- This file contains the SQL schema for the database
-- You can run this directly against your database or use the Kysely migration runner

-- ============================================================================
-- USERS TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS users (
    id TEXT PRIMARY KEY,
    email TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    password_hash TEXT NOT NULL,
    avatar_url TEXT,
    xp INTEGER NOT NULL DEFAULT 0,
    streak INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);

-- ============================================================================
-- WORKFLOWS TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS workflows (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    nodes TEXT NOT NULL DEFAULT '[]',
    edges TEXT NOT NULL DEFAULT '[]',
    is_public INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- ============================================================================
-- NODES TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS nodes (
    id TEXT PRIMARY KEY,
    workflow_id TEXT NOT NULL,
    type TEXT NOT NULL,
    position_x REAL NOT NULL DEFAULT 0,
    position_y REAL NOT NULL DEFAULT 0,
    data TEXT NOT NULL DEFAULT '{}',
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (workflow_id) REFERENCES workflows(id) ON DELETE CASCADE
);

-- ============================================================================
-- EDGES TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS edges (
    id TEXT PRIMARY KEY,
    workflow_id TEXT NOT NULL,
    source_node_id TEXT NOT NULL,
    target_node_id TEXT NOT NULL,
    source_handle TEXT,
    target_handle TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (workflow_id) REFERENCES workflows(id) ON DELETE CASCADE
);

-- ============================================================================
-- MIGRATIONS TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS _migrations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    applied_at TEXT NOT NULL DEFAULT (datetime('now'))
);

-- ============================================================================
-- INDEXES
-- ============================================================================
CREATE INDEX IF NOT EXISTS idx_workflows_user_id ON workflows(user_id);
CREATE INDEX IF NOT EXISTS idx_nodes_workflow_id ON nodes(workflow_id);
CREATE INDEX IF NOT EXISTS idx_edges_workflow_id ON edges(workflow_id);

-- ============================================================================
-- RELATIONSHIPS SUMMARY
-- ============================================================================
-- 
-- users (1) ----< (0..many) workflows
--   - A user can have 0 or many workflows
--   - Each workflow belongs to exactly one user
--
-- workflows (1) ----< (1..many) edges
--   - A workflow has 1 or many edges
--   - Each edge belongs to exactly one workflow
--
-- edges connects exactly 2 nodes:
--   - edges.source_node_id REFERENCES nodes.id
--   - edges.target_node_id REFERENCES nodes.id
--
-- nodes (1) ----< (0..many) edges (as source)
-- nodes (1) ----< (0..many) edges (as target)
--   - A node can be connected to many edges (both as source and target)
--   - Each edge always links exactly 2 nodes

-- ============================================================================
-- SAMPLE DATA (for testing)
-- ============================================================================

-- Insert a sample user
-- INSERT INTO users (id, email, name, password_hash, xp, streak)
-- VALUES ('user-1', 'alex@example.com', 'Alex Thompson', '$2b$10$samplehash', 1250, 7);

-- Insert a sample workflow
-- INSERT INTO workflows (id, user_id, name, description)
-- VALUES ('wf-1', 'user-1', 'My First Workflow', 'A sample workflow for learning');

-- Insert sample nodes
-- INSERT INTO nodes (id, workflow_id, type, position_x, position_y, data)
-- VALUES 
--     ('node-1', 'wf-1', 'input', 100, 200, '{"label": "Start"}'),
--     ('node-2', 'wf-1', 'process', 400, 200, '{"label": "Process"}'),
--     ('node-3', 'wf-1', 'output', 700, 200, '{"label": "Output"}');

-- Insert sample edges (linking nodes)
-- INSERT INTO edges (id, workflow_id, source_node_id, target_node_id)
-- VALUES 
--     ('edge-1', 'wf-1', 'node-1', 'node-2'),
--     ('edge-2', 'wf-1', 'node-2', 'node-3');
