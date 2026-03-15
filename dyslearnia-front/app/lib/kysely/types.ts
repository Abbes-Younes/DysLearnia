import { Generated, Insertable, Selectable, Updateable } from 'kysely'

// Add a table interface for each table in your DB
export interface LectureTable {
  id: Generated<string>
  created_at: Generated<string>
  file_name: string | null
  file_url: string | null
  raw_text: string | null
  simplified_text: string | null
  summary: string | null
  status: string | null
  user_id: string | null
}

// User table
export interface UserTable {
  id: string
  email: string
  name: string
  password_hash: string
  avatar_url: string | null
  xp: number
  streak: number
  created_at: Date
  updated_at: Date
}

// Workflow table
export interface WorkflowTable {
  id: string
  user_id: string
  name: string
  description: string | null
  nodes: unknown
  edges: unknown
  is_public: boolean
  created_at: Date
  updated_at: Date
}

// Node table
export interface NodeTable {
  id: string
  workflow_id: string
  type: string
  position_x: number
  position_y: number
  data: unknown
  created_at: Date
  updated_at: Date
}

// Edge table
export interface EdgeTable {
  id: string
  workflow_id: string
  source_node_id: string
  target_node_id: string
  source_handle: string | null
  target_handle: string | null
  created_at: Date
  updated_at: Date
}

// Database interface — add every table here
export interface Database {
  lectures: LectureTable
  users: UserTable
  workflows: WorkflowTable
  nodes: NodeTable
  edges: EdgeTable
}

// Handy type helpers
export type Lecture = Selectable<LectureTable>
export type NewLecture = Insertable<LectureTable>
export type UpdateLecture = Updateable<LectureTable>

export type User = Selectable<UserTable>
export type NewUser = Insertable<UserTable>
export type UpdateUser = Updateable<UserTable>

export type Workflow = Selectable<WorkflowTable>
export type NewWorkflow = Insertable<WorkflowTable>
export type UpdateWorkflow = Updateable<WorkflowTable>

export type Node = Selectable<NodeTable>
export type NewNode = Insertable<NodeTable>
export type UpdateNode = Updateable<NodeTable>

export type Edge = Selectable<EdgeTable>
export type NewEdge = Insertable<EdgeTable>
export type UpdateEdge = Updateable<EdgeTable>
