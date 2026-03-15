"use client";

import {
  useState,
  useCallback,
  useMemo,
  useRef,
  useEffect,
  type DragEvent,
} from "react";
import {
  ReactFlow,
  applyNodeChanges,
  applyEdgeChanges,
  addEdge,
  Background,
  Controls,
  MiniMap,
  getOutgoers,
  MarkerType,
  type Node,
  type Edge,
  type OnNodesChange,
  type OnEdgesChange,
  type OnEdgesDelete,
  type OnNodesDelete,
  type OnConnect,
  useReactFlow,
  ReactFlowProvider,
} from "@xyflow/react";
import "@xyflow/react/dist/style.css";
import { v4 as uuidv4 } from "uuid";
import { nodeTypes, getBlockIcon, getBlockColor } from "./nodes";
import {
  fetchBlocks,
  runPipeline,
  getBinaryOutputUrl,
  type BlockDescription,
  type PipelineRunResponse,
} from "../lib/api";
import { Loader2, AlertCircle, Download, X } from "lucide-react";
import { CourseInputModal } from "./course-input-modal";

// ── Placeholder node shown on empty canvas ──────────────────────────────────

const placeholderNode: Node = {
  id: "placeholder",
  type: "placeholder",
  position: { x: 250, y: 200 },
  data: {},
  selectable: false,
  draggable: false,
};

function getNodeId() {
  return uuidv4();
}

// ── Results Panel ───────────────────────────────────────────────────────────

function ResultsPanel({
  response,
  onClose,
}: {
  response: PipelineRunResponse;
  onClose: () => void;
}) {
  return (
    <div className="absolute right-4 top-4 z-50 w-[400px] max-h-[80vh] overflow-auto rounded-xl border border-border bg-card shadow-xl">
      <div className="flex items-center justify-between border-b border-border px-4 py-3">
        <h3 className="text-sm font-bold text-foreground">Pipeline Results</h3>
        <button onClick={onClose} className="text-text-secondary hover:text-foreground">
          <X size={16} />
        </button>
      </div>
      <div className="flex flex-col gap-3 p-4">
        {Object.entries(response.outputs).map(([nodeId, outputs]) => (
          <div key={nodeId} className="rounded-lg border border-border bg-background p-3">
            <p className="mb-1 text-xs font-semibold text-accent">{nodeId}</p>
            {outputs.map((out, i) => (
              <div key={i} className="text-xs text-foreground">
                {out.text && (
                  <pre className="mt-1 max-h-48 overflow-auto whitespace-pre-wrap rounded bg-card p-2 text-xs">
                    {out.text}
                  </pre>
                )}
                {out.has_binary && (
                  <a
                    href={getBinaryOutputUrl(response.run_id, nodeId)}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="mt-2 inline-flex items-center gap-1 rounded bg-accent px-2 py-1 text-xs font-medium text-accent-foreground hover:bg-accent-hover"
                  >
                    <Download size={12} />
                    Download {out.mime_type || "file"}
                  </a>
                )}
                {out.source_chunks.length > 0 && (
                  <details className="mt-2">
                    <summary className="cursor-pointer text-xs text-text-secondary">
                      {out.source_chunks.length} source chunks
                    </summary>
                    <ul className="mt-1 list-disc pl-4 text-xs text-text-secondary">
                      {out.source_chunks.map((chunk, j) => (
                        <li key={j} className="mb-1">{chunk.slice(0, 200)}...</li>
                      ))}
                    </ul>
                  </details>
                )}
              </div>
            ))}
          </div>
        ))}
        {Object.keys(response.outputs).length === 0 && (
          <p className="text-xs text-text-secondary">No outputs produced.</p>
        )}
      </div>
    </div>
  );
}

// ── Main Flow Component ─────────────────────────────────────────────────────

function Flow() {
  const [nodes, setNodes] = useState<Node[]>([placeholderNode]);
  const [edges, setEdges] = useState<Edge[]>([]);
  const reactFlowWrapper = useRef<HTMLDivElement>(null);
  const { screenToFlowPosition } = useReactFlow();

  // Block registry from backend
  const [blocks, setBlocks] = useState<BlockDescription[]>([]);
  const [blocksLoading, setBlocksLoading] = useState(true);
  const [blocksError, setBlocksError] = useState<string | null>(null);

  // Course input modal state
  const [courseInputNodeId, setCourseInputNodeId] = useState<string | null>(null);

  // Pipeline execution state
  const [pipelineRunning, setPipelineRunning] = useState(false);
  const [pipelineError, setPipelineError] = useState<string | null>(null);
  const [pipelineResult, setPipelineResult] = useState<PipelineRunResponse | null>(null);

  // Fetch blocks from backend on mount
  useEffect(() => {
    fetchBlocks()
      .then((data) => {
        setBlocks(data);
        setBlocksError(null);
      })
      .catch((err) => setBlocksError(err.message))
      .finally(() => setBlocksLoading(false));
  }, []);

  // Group blocks by category for sidebar
  const groupedBlocks = useMemo(() => {
    const groups: Record<string, BlockDescription[]> = {
      input: [],
      transform: [],
      output: [],
    };
    for (const block of blocks) {
      const g = groups[block.group] || groups.transform;
      g.push(block);
    }
    return groups;
  }, [blocks]);

  const onNodesChange: OnNodesChange = useCallback(
    (changes) =>
      setNodes((nds) => {
        const updated = applyNodeChanges(changes, nds);
        // Restore placeholder if all real nodes are gone
        const hasReal = updated.some((n) => n.type !== "placeholder");
        if (!hasReal) return [placeholderNode];
        return updated;
      }),
    [],
  );

  const onEdgesChange: OnEdgesChange = useCallback(
    (changes) => setEdges((eds) => applyEdgeChanges(changes, eds)),
    [],
  );

  const hasCycle = useCallback(
    (sourceNode: Node, targetNode: Node, existingEdges: Edge[]): boolean => {
      const visited = new Set<string>();
      const checkCycle = (node: Node): boolean => {
        if (visited.has(node.id)) return false;
        visited.add(node.id);
        if (node.id === targetNode.id) return true;
        const outgoers = getOutgoers(node, nodes, existingEdges);
        return outgoers.some((outgoer) => checkCycle(outgoer));
      };
      return checkCycle(sourceNode);
    },
    [nodes],
  );

  const handleConnect = useCallback(
    (params: Parameters<OnConnect>[0]) => {
      const sourceNode = nodes.find((n) => n.id === params.source);
      const targetNode = nodes.find((n) => n.id === params.target);

      if (sourceNode && targetNode) {
        if (hasCycle(sourceNode, targetNode, edges)) {
          console.warn("Adding this edge would create a cycle");
          return;
        }
      }

      setEdges((eds) =>
        addEdge(
          {
            ...params,
            type: "smoothstep",
            markerEnd: { type: MarkerType.ArrowClosed },
          },
          eds,
        ),
      );
    },
    [nodes, edges, hasCycle],
  );

  const onNodesDelete: OnNodesDelete = useCallback(
    (deleted) => {
      const deletedIds = new Set(deleted.map((n) => n.id));
      setEdges((eds) =>
        eds.filter((e) => !deletedIds.has(e.source) && !deletedIds.has(e.target)),
      );
    },
    [],
  );

  const onEdgesDelete: OnEdgesDelete = useCallback(
    (deleted) => {
      const deletedIds = new Set(deleted.map((e) => e.id));
      setEdges((eds) => eds.filter((e) => !deletedIds.has(e.id)));
    },
    [],
  );

  // Detect cycles in the entire graph
  const graphHasCycle = useMemo(() => {
    const adj = new Map<string, string[]>();
    for (const node of nodes) adj.set(node.id, []);
    for (const edge of edges) adj.get(edge.source)?.push(edge.target);

    const visited = new Set<string>();
    const inStack = new Set<string>();

    const dfs = (id: string): boolean => {
      visited.add(id);
      inStack.add(id);
      for (const neighbor of adj.get(id) ?? []) {
        if (inStack.has(neighbor)) return true;
        if (!visited.has(neighbor) && dfs(neighbor)) return true;
      }
      inStack.delete(id);
      return false;
    };

    for (const node of nodes) {
      if (!visited.has(node.id) && dfs(node.id)) return true;
    }
    return false;
  }, [nodes, edges]);

  // Check if we have real nodes (not just placeholder)
  const hasRealNodes = useMemo(
    () => nodes.some((n) => n.type !== "placeholder"),
    [nodes],
  );

  const onDragOver = useCallback((event: DragEvent) => {
    event.preventDefault();
    event.dataTransfer.dropEffect = "move";
  }, []);

  const onDrop = useCallback(
    (event: DragEvent) => {
      event.preventDefault();

      const blockName = event.dataTransfer.getData("application/reactflow-block");
      const label = event.dataTransfer.getData("application/reactflow-label");
      const group = event.dataTransfer.getData("application/reactflow-group");

      if (!blockName) return;

      const position = screenToFlowPosition({
        x: event.clientX,
        y: event.clientY,
      });

      const newNode: Node = {
        id: getNodeId(),
        type: "dynamic",
        position,
        data: { label, blockName, group },
      };

      // Remove placeholder if it exists
      setNodes((nds) => [
        ...nds.filter((n) => n.id !== "placeholder"),
        newNode,
      ]);
    },
    [screenToFlowPosition],
  );

  // Open modal when clicking a course_input node
  const onNodeClick = useCallback(
    (_event: React.MouseEvent, node: Node) => {
      if (node.data.blockName === "course_input") {
        setCourseInputNodeId(node.id);
      }
    },
    [],
  );

  // Save course input data into the node
  const onCourseInputSave = useCallback(
    (nodeId: string, text: string, fileName?: string) => {
      setNodes((nds) =>
        nds.map((n) =>
          n.id === nodeId
            ? {
                ...n,
                data: {
                  ...n.data,
                  inputText: text,
                  inputFileName: fileName,
                },
              }
            : n,
        ),
      );
      setCourseInputNodeId(null);
    },
    [],
  );

  const onDragStart = (
    event: DragEvent,
    block: BlockDescription,
  ) => {
    event.dataTransfer.setData("application/reactflow-block", block.name);
    event.dataTransfer.setData("application/reactflow-label", block.display_name);
    event.dataTransfer.setData("application/reactflow-group", block.group);
    event.dataTransfer.effectAllowed = "move";
  };

  // ── Execute Pipeline ────────────────────────────────────────────────────

  const executePipeline = useCallback(async () => {
    setPipelineError(null);
    setPipelineResult(null);
    setPipelineRunning(true);

    // Mark all real nodes as "running"
    setNodes((nds) =>
      nds.map((n) =>
        n.type === "dynamic"
          ? { ...n, data: { ...n.data, status: "running" } }
          : n,
      ),
    );

    try {
      // Build request from React Flow state
      const realNodes = nodes.filter((n) => n.type === "dynamic");
      const request = {
        nodes: realNodes.map((n) => ({
          id: n.id,
          type: n.data.blockName as string,
          data: {},
        })),
        edges: edges.map((e) => ({ source: e.source, target: e.target })),
        params: {} as Record<string, Record<string, unknown>>,
        initial_inputs: {} as Record<string, Record<string, unknown>>,
      };

      // Seed source nodes with their stored input text
      for (const n of realNodes) {
        const blockName = n.data.blockName as string;
        const hasIncoming = edges.some((e) => e.target === n.id);
        if (!hasIncoming) {
          const text = (n.data.inputText as string) || "";
          if (blockName === "course_input" && text) {
            // Pre-seeded text from upload or paste — skip binary extraction
            request.initial_inputs[n.id] = { text };
          } else if (blockName !== "course_input") {
            request.initial_inputs[n.id] = { text };
          }
        }
      }

      const result = await runPipeline(request);

      // Mark all nodes as "done"
      setNodes((nds) =>
        nds.map((n) =>
          n.type === "dynamic"
            ? { ...n, data: { ...n.data, status: "done" } }
            : n,
        ),
      );

      setPipelineResult(result);
    } catch (err) {
      // Mark all nodes as "error"
      setNodes((nds) =>
        nds.map((n) =>
          n.type === "dynamic"
            ? { ...n, data: { ...n.data, status: "error" } }
            : n,
        ),
      );
      setPipelineError(err instanceof Error ? err.message : String(err));
    } finally {
      setPipelineRunning(false);
    }
  }, [nodes, edges]);

  // ── Render ──────────────────────────────────────────────────────────────

  const GROUP_LABELS: Record<string, string> = {
    input: "Input",
    transform: "Transform",
    output: "Output",
  };

  return (
    <div className="flex h-screen w-screen">
      {/* Sidebar toolbox */}
      <aside className="flex w-[260px] flex-col border-r border-border bg-card">
        <div className="p-4 pb-2">
          <h2 className="mb-1 text-lg font-bold text-foreground">
            Learning Tools
          </h2>
          <p className="mb-2 text-sm text-text-secondary">
            Drag blocks onto the canvas to build your pipeline
          </p>
        </div>

        <div className="flex-1 overflow-y-auto px-4 pb-4">
          {blocksLoading && (
            <div className="flex items-center gap-2 py-8 text-sm text-text-secondary">
              <Loader2 size={14} className="animate-spin" />
              Loading blocks...
            </div>
          )}

          {blocksError && (
            <div className="flex items-start gap-2 rounded-lg border border-error/30 bg-error/5 p-3 text-sm text-error">
              <AlertCircle size={14} className="mt-0.5 shrink-0" />
              <div>
                <p className="font-medium">Failed to load blocks</p>
                <p className="mt-1 opacity-80">{blocksError}</p>
                <button
                  onClick={() => {
                    setBlocksLoading(true);
                    setBlocksError(null);
                    fetchBlocks()
                      .then(setBlocks)
                      .catch((e) => setBlocksError(e.message))
                      .finally(() => setBlocksLoading(false));
                  }}
                  className="mt-2 underline hover:no-underline"
                >
                  Retry
                </button>
              </div>
            </div>
          )}

          {!blocksLoading &&
            !blocksError &&
            (["input", "transform", "output"] as const).map((group) =>
              groupedBlocks[group]?.length ? (
                <div key={group} className="mb-4">
                  <p className="mb-2 text-xs font-bold uppercase tracking-wider text-text-secondary">
                    {GROUP_LABELS[group]}
                  </p>
                  <div className="flex flex-col gap-1.5">
                    {groupedBlocks[group].map((block) => {
                      const Icon = getBlockIcon(block.name);
                      const color = getBlockColor(block.name, block.group);
                      return (
                        <div
                          key={block.name}
                          draggable
                          onDragStart={(e) => onDragStart(e, block)}
                          className="flex cursor-grab items-center gap-2 rounded-lg border border-border bg-background px-3 py-2 text-base font-medium text-foreground transition-colors hover:border-accent hover:bg-accent/10 active:cursor-grabbing"
                          title={`${block.display_name}\nIn: ${block.input_types.join(", ")}\nOut: ${block.output_types.join(", ")}`}
                        >
                          <div
                            className="flex h-7 w-7 shrink-0 items-center justify-center rounded-md border"
                            style={{
                              borderColor: color,
                              backgroundColor: `${color}15`,
                            }}
                          >
                            <Icon size={14} style={{ color }} />
                          </div>
                          <span className="truncate">{block.display_name}</span>
                        </div>
                      );
                    })}
                  </div>
                </div>
              ) : null,
            )}
        </div>

        <div className="border-t border-border p-4">
          {graphHasCycle && (
            <p className="mb-2 text-xs font-medium text-error">
              Cycle detected — remove a connection to continue
            </p>
          )}
          {pipelineError && (
            <p className="mb-2 text-xs font-medium text-error">
              {pipelineError}
            </p>
          )}
          <button
            disabled={graphHasCycle || !hasRealNodes || pipelineRunning}
            onClick={executePipeline}
            className="flex w-full items-center justify-center gap-2 rounded-lg bg-accent px-4 py-2 text-sm font-semibold text-accent-foreground transition-colors hover:bg-accent-hover disabled:cursor-not-allowed disabled:opacity-50"
          >
            {pipelineRunning && <Loader2 size={14} className="animate-spin" />}
            {pipelineRunning ? "Running..." : "Execute Pipeline"}
          </button>
        </div>
      </aside>

      {/* Canvas */}
      <div ref={reactFlowWrapper} className="relative flex-1">
        <ReactFlow
          nodes={nodes}
          edges={edges}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          onConnect={handleConnect}
          onNodesDelete={onNodesDelete}
          onEdgesDelete={onEdgesDelete}
          onDrop={onDrop}
          onDragOver={onDragOver}
          onNodeClick={onNodeClick}
          deleteKeyCode={["Backspace", "Delete"]}
          nodeTypes={nodeTypes}
          fitView
          className="bg-background"
        >
          <Background gap={20} size={1} />
          <Controls />
          <MiniMap
            nodeStrokeWidth={3}
            className="!bg-card !border-border"
          />
        </ReactFlow>

        {/* Results overlay */}
        {pipelineResult && (
          <ResultsPanel
            response={pipelineResult}
            onClose={() => setPipelineResult(null)}
          />
        )}
      </div>

      {/* Course input modal */}
      {courseInputNodeId && (
        <CourseInputModal
          nodeId={courseInputNodeId}
          initialText={
            (nodes.find((n) => n.id === courseInputNodeId)?.data
              .inputText as string) || ""
          }
          initialFileName={
            (nodes.find((n) => n.id === courseInputNodeId)?.data
              .inputFileName as string) || undefined
          }
          onSave={onCourseInputSave}
          onClose={() => setCourseInputNodeId(null)}
        />
      )}
    </div>
  );
}

export default function LearnPage() {
  return (
    <ReactFlowProvider>
      <Flow />
    </ReactFlowProvider>
  );
}
