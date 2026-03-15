/**
 * API client for communicating with the DysLearnia backend.
 */

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api";

// Common headers — ngrok returns an HTML interstitial page unless this is set
const COMMON_HEADERS: Record<string, string> = {
  "ngrok-skip-browser-warning": "true",
};

// ── Types matching backend schemas ──────────────────────────────────────────

export interface BlockParameter {
  name: string;
  type: string; // "slider" | "select" | "toggle" | "number" | "text"
  min?: number;
  max?: number;
  default?: unknown;
  options?: string[];
  label?: string;
}

export interface BlockDescription {
  name: string;
  display_name: string;
  group: "input" | "transform" | "output";
  input_types: string[];
  output_types: string[];
  parameters: BlockParameter[];
}

export interface NodeDef {
  id: string;
  type: string;
  data?: Record<string, unknown>;
}

export interface EdgeDef {
  source: string;
  target: string;
}

export interface PipelineRunRequest {
  nodes: NodeDef[];
  edges: EdgeDef[];
  params: Record<string, Record<string, unknown>>;
  initial_inputs: Record<string, Record<string, unknown>>;
  validate_only?: boolean;
}

export interface BlockDataOut {
  text: string | null;
  mime_type: string | null;
  metadata: Record<string, unknown>;
  source_chunks: string[];
  has_binary: boolean;
}

export interface PipelineRunResponse {
  run_id: string;
  outputs: Record<string, BlockDataOut[]>;
  validation_errors: string[];
}

// ── API functions ───────────────────────────────────────────────────────────

export async function fetchBlocks(): Promise<BlockDescription[]> {
  const res = await fetch(`${API_BASE}/blocks`, { headers: COMMON_HEADERS });
  if (!res.ok) throw new Error(`Failed to fetch blocks: ${res.status}`);
  return res.json();
}

export async function runPipeline(
  request: PipelineRunRequest
): Promise<PipelineRunResponse> {
  const res = await fetch(`${API_BASE}/pipeline/run`, {
    method: "POST",
    headers: { ...COMMON_HEADERS, "Content-Type": "application/json" },
    body: JSON.stringify(request),
  });
  if (!res.ok) {
    const detail = await res.json().catch(() => ({}));
    throw new Error(
      detail?.detail?.message || detail?.detail || `Pipeline failed: ${res.status}`
    );
  }
  return res.json();
}

export async function uploadDocument(file: File): Promise<{
  doc_id: string;
  chunk_count: number;
  full_text: string;
  preview_text: string;
}> {
  const formData = new FormData();
  formData.append("file", file);
  const res = await fetch(`${API_BASE}/documents/upload`, {
    method: "POST",
    headers: COMMON_HEADERS,
    body: formData,
  });
  if (!res.ok) throw new Error(`Upload failed: ${res.status}`);
  return res.json();
}

export function getBinaryOutputUrl(runId: string, nodeId: string): string {
  return `${API_BASE}/pipeline/${runId}/output/${nodeId}`;
}
