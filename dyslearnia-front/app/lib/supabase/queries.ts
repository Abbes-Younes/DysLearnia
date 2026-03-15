import { createClient } from "./client";

// Inline types for Supabase tables
interface DbUser {
  id: string;
  email: string;
  name: string;
  password_hash: string;
  avatar_url: string | null;
  xp: number;
  streak: number;
  created_at: string;
  updated_at: string;
}

interface DbWorkflow {
  id: string;
  user_id: string;
  name: string;
  description: string | null;
  nodes: unknown;
  edges: unknown;
  is_public: boolean;
  created_at: string;
  updated_at: string;
}

interface DbNode {
  id: string;
  workflow_id: string;
  type: string;
  position_x: number;
  position_y: number;
  data: unknown;
  created_at: string;
  updated_at: string;
}

interface DbEdge {
  id: string;
  workflow_id: string;
  source_node_id: string;
  target_node_id: string;
  source_handle: string | null;
  target_handle: string | null;
  created_at: string;
  updated_at: string;
}

// User functions

export async function createUser(id: string, email: string, name: string): Promise<DbUser> {
  const supabase = createClient();
  const { data, error } = await supabase
    .from("users")
    .insert({
      id,
      email,
      name,
      password_hash: "", // Will be updated when they set a password
      xp: 0,
      streak: 0,
    })
    .select()
    .single();

  if (error) throw error;
  return data as DbUser;
}

export async function getUser(userId: string): Promise<DbUser> {
  const supabase = createClient();
  const { data, error } = await supabase
    .from("users")
    .select("*")
    .eq("id", userId)
    .single();

  if (error) throw error;
  return data as DbUser;
}

export async function updateUser(userId: string, updates: Partial<DbUser>): Promise<DbUser> {
  const supabase = createClient();
  const { data, error } = await supabase
    .from("users")
    .update(updates)
    .eq("id", userId)
    .select()
    .single();

  if (error) throw error;
  return data as DbUser;
}

export async function uploadAvatar(userId: string, file: File): Promise<string> {
  const supabase = createClient();
  
  // Upload file to avatars bucket
  const fileName = `${userId}/${Date.now()}-${file.name}`;
  const { error: uploadError } = await supabase.storage
    .from("avatars")
    .upload(fileName, file, { upsert: true });

  if (uploadError) throw uploadError;

  // Get public URL
  const { data: { publicUrl } } = supabase.storage
    .from("avatars")
    .getPublicUrl(fileName);

  // Update user avatar_url
  await updateUser(userId, { avatar_url: publicUrl });

  return publicUrl;
}

// Workflow functions
export async function getWorkflows(userId: string): Promise<DbWorkflow[]> {
  const supabase = createClient();
  const { data, error } = await supabase
    .from("workflows")
    .select("*")
    .eq("user_id", userId)
    .order("updated_at", { ascending: false });

  if (error) throw error;
  return data as DbWorkflow[];
}

export async function getWorkflow(workflowId: string): Promise<DbWorkflow> {
  const supabase = createClient();
  const { data, error } = await supabase
    .from("workflows")
    .select("*")
    .eq("id", workflowId)
    .single();

  if (error) throw error;
  return data as DbWorkflow;
}

export async function createWorkflow(userId: string, workflow: Partial<DbWorkflow>): Promise<DbWorkflow> {
  const supabase = createClient();
  const { data, error } = await supabase
    .from("workflows")
    .insert({
      user_id: userId,
      name: workflow.name,
      description: workflow.description,
      nodes: workflow.nodes || [],
      edges: workflow.edges || [],
      is_public: workflow.is_public || false,
    })
    .select()
    .single();

  if (error) throw error;
  return data as DbWorkflow;
}

export async function updateWorkflow(workflowId: string, updates: Partial<DbWorkflow>): Promise<DbWorkflow> {
  const supabase = createClient();
  const { data, error } = await supabase
    .from("workflows")
    .update({
      ...updates,
      updated_at: new Date().toISOString(),
    })
    .eq("id", workflowId)
    .select()
    .single();

  if (error) throw error;
  return data as DbWorkflow;
}

export async function deleteWorkflow(workflowId: string): Promise<void> {
  const supabase = createClient();
  const { error } = await supabase
    .from("workflows")
    .delete()
    .eq("id", workflowId);

  if (error) throw error;
}

// Node functions
export async function getNodes(workflowId: string): Promise<DbNode[]> {
  const supabase = createClient();
  const { data, error } = await supabase
    .from("nodes")
    .select("*")
    .eq("workflow_id", workflowId);

  if (error) throw error;
  return data as DbNode[];
}

export async function createNode(workflowId: string, node: Partial<DbNode>): Promise<DbNode> {
  const supabase = createClient();
  const { data, error } = await supabase
    .from("nodes")
    .insert({
      workflow_id: workflowId,
      type: node.type,
      position_x: node.position_x,
      position_y: node.position_y,
      data: node.data || {},
    })
    .select()
    .single();

  if (error) throw error;
  return data as DbNode;
}

export async function updateNode(nodeId: string, updates: Partial<DbNode>): Promise<DbNode> {
  const supabase = createClient();
  const { data, error } = await supabase
    .from("nodes")
    .update({
      ...updates,
      updated_at: new Date().toISOString(),
    })
    .eq("id", nodeId)
    .select()
    .single();

  if (error) throw error;
  return data as DbNode;
}

export async function deleteNode(nodeId: string): Promise<void> {
  const supabase = createClient();
  const { error } = await supabase
    .from("nodes")
    .delete()
    .eq("id", nodeId);

  if (error) throw error;
}

// Edge functions
export async function getEdges(workflowId: string): Promise<DbEdge[]> {
  const supabase = createClient();
  const { data, error } = await supabase
    .from("edges")
    .select("*")
    .eq("workflow_id", workflowId);

  if (error) throw error;
  return data as DbEdge[];
}

export async function createEdge(workflowId: string, edge: Partial<DbEdge>): Promise<DbEdge> {
  const supabase = createClient();
  const { data, error } = await supabase
    .from("edges")
    .insert({
      workflow_id: workflowId,
      source_node_id: edge.source_node_id,
      target_node_id: edge.target_node_id,
      source_handle: edge.source_handle,
      target_handle: edge.target_handle,
    })
    .select()
    .single();

  if (error) throw error;
  return data as DbEdge;
}

export async function deleteEdge(edgeId: string): Promise<void> {
  const supabase = createClient();
  const { error } = await supabase
    .from("edges")
    .delete()
    .eq("id", edgeId);

  if (error) throw error;
}
