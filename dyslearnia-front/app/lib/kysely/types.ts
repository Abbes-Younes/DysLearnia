// Database types for Kysely
// This file contains all the TypeScript interfaces for our database tables

export interface Database {
  // Tables
  users: User;
  workflows: Workflow;
  nodes: Node;
  edges: Edge;
  _migrations: Migration;
  
  // Row types
  User: User;
  Workflow: Workflow;
  Node: Node;
  Edge: Edge;
  Migration: Migration;
}

// User table
export interface User {
  id: string;
  email: string;
  name: string;
  password_hash: string;
  avatar_url: string | null;
  xp: number;
  streak: number;
  created_at: Date;
  updated_at: Date;
}

// Workflow table
export interface Workflow {
  id: string;
  user_id: string;
  name: string;
  description: string | null;
  nodes: unknown; // JSON array of nodes
  edges: unknown; // JSON array of edges
  is_public: boolean;
  created_at: Date;
  updated_at: Date;
}

// Node table
export interface Node {
  id: string;
  workflow_id: string;
  type: string;
  position_x: number;
  position_y: number;
  data: unknown; // JSON object for node data
  created_at: Date;
  updated_at: Date;
}

// Edge table
export interface Edge {
  id: string;
  workflow_id: string;
  source_node_id: string;
  target_node_id: string;
  source_handle: string | null;
  target_handle: string | null;
  created_at: Date;
  updated_at: Date;
}

// Migration table
export interface Migration {
  id: number;
  name: string;
  applied_at: Date;
}

// Helper types for inserting data
export type InsertUser = Omit<User, "id" | "created_at" | "updated_at">;
export type InsertWorkflow = Omit<Workflow, "id" | "created_at" | "updated_at">;
export type InsertNode = Omit<Node, "id" | "created_at" | "updated_at">;
export type InsertEdge = Omit<Edge, "id" | "created_at" | "updated_at">;

// Helper types for updating data
export type UpdateUser = Partial<Omit<User, "id" | "created_at">>;
export type UpdateWorkflow = Partial<Omit<Workflow, "id" | "created_at">>;
export type UpdateNode = Partial<Omit<Node, "id" | "created_at">>;
export type UpdateEdge = Partial<Omit<Edge, "id" | "created_at">>;
