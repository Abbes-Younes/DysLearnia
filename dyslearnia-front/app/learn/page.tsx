"use client";

import { useState, useCallback, useMemo, useRef, type DragEvent } from "react";
import {
  ReactFlow,
  applyNodeChanges,
  applyEdgeChanges,
  addEdge,
  Background,
  Controls,
  MiniMap,
  Panel,
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
import { nodeTypes } from "./nodes";
import type { LucideIcon } from "lucide-react";
import {
  PenLine,
  Scissors,
  Volume2,
  MoveHorizontal,
  Type,
  CheckCircle2,
  Save,
  Loader2,
  X,
} from "lucide-react";
import { useApp, WorkflowNode, WorkflowEdge } from "@/lib/context/app-context";

const toolbox: { type: string; label: string; icon: LucideIcon; color: string }[] = [
  { type: "textInput", label: "Text Input", icon: PenLine, color: "#4a9b8e" },
  { type: "summarize", label: "Summarize", icon: Scissors, color: "#e8a838" },
  { type: "tts", label: "Text to Speech", icon: Volume2, color: "#6366f1" },
  { type: "spacing", label: "Add Spacing", icon: MoveHorizontal, color: "#d4806b" },
  { type: "fontFlip", label: "Flip Font", icon: Type, color: "#8b5cf6" },
  { type: "result", label: "Output", icon: CheckCircle2, color: "#22c55e" },
];

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

// Save Workflow Dialog
function SaveWorkflowDialog({ 
  isOpen, 
  onClose, 
  onSave 
}: { 
  isOpen: boolean; 
  onClose: () => void; 
  onSave: (name: string) => void 
}) {
  const [name, setName] = useState("");
  const [isSaving, setIsSaving] = useState(false);

  if (!isOpen) return null;

  const handleSave = async () => {
    if (!name.trim()) return;
    setIsSaving(true);
    await onSave(name.trim());
    setIsSaving(false);
    setName("");
    onClose();
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
      <div className="w-full max-w-md rounded-lg bg-card p-6 shadow-lg">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold">Save Workflow</h3>
          <button onClick={onClose} className="text-muted-foreground hover:text-foreground">
            <X className="size-5" />
          </button>
        </div>
        <div className="space-y-4">
          <div>
            <label className="text-sm font-medium">Workflow Name</label>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="Enter workflow name..."
              className="mt-1 w-full rounded-lg border border-input bg-background px-3 py-2 focus:outline-none focus:ring-2 focus:ring-ring"
              autoFocus
            />
          </div>
          <div className="flex gap-2 justify-end">
            <button
              onClick={onClose}
              className="px-4 py-2 text-sm font-medium text-muted-foreground hover:text-foreground"
            >
              Cancel
            </button>
            <button
              onClick={handleSave}
              disabled={!name.trim() || isSaving}
              className="flex items-center gap-2 rounded-lg bg-primary px-4 py-2 text-sm font-medium text-primary-foreground hover:bg-primary/90 disabled:opacity-50"
            >
              {isSaving ? (
                <>
                  <Loader2 className="size-4 animate-spin" />
                  Saving...
                </>
              ) : (
                <>
                  <Save className="size-4" />
                  Save
                </>
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

function Flow() {
  const [nodes, setNodes] = useState<Node[]>([placeholderNode]);
  const [edges, setEdges] = useState<Edge[]>([]);
  const [showSaveDialog, setShowSaveDialog] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const reactFlowWrapper = useRef<HTMLDivElement>(null);
  const { screenToFlowPosition } = useReactFlow();
  const { addWorkflow, user } = useApp();

  const onNodesChange: OnNodesChange = useCallback(
    (changes) => setNodes((nds) => applyNodeChanges(changes, nds)),
    [],
  );

  const onEdgesChange: OnEdgesChange = useCallback(
    (changes) => setEdges((eds) => applyEdgeChanges(changes, eds)),
    [],
  );

  // Check if adding an edge would create a cycle
  const hasCycle = useCallback(
    (sourceNode: Node, targetNode: Node, existingEdges: Edge[]): boolean => {
      const visited = new Set<string>();

      const checkCycle = (node: Node): boolean => {
        if (visited.has(node.id)) return false;
        visited.add(node.id);

        // If we reach the target node, a cycle would be created
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
      // Find source and target nodes
      const sourceNode = nodes.find((n) => n.id === params.source);
      const targetNode = nodes.find((n) => n.id === params.target);

      if (sourceNode && targetNode) {
        // Check if adding this edge would create a cycle
        if (hasCycle(sourceNode, targetNode, edges)) {
          console.warn("Adding this edge would create a cycle");
          return;
        }
      }

      // Add edge with arrow marker
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
      // Remove edges connected to deleted nodes
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

  // Detect cycles in the entire graph (not DAG-safe)
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

  const onDragOver = useCallback((event: DragEvent) => {
    event.preventDefault();
    event.dataTransfer.dropEffect = "move";
  }, []);

  const onDrop = useCallback(
    (event: DragEvent) => {
      event.preventDefault();

      const type = event.dataTransfer.getData("application/reactflow-type");
      const label = event.dataTransfer.getData("application/reactflow-label");

      if (!type) return;

      const position = screenToFlowPosition({
        x: event.clientX,
        y: event.clientY,
      });

      const newNode: Node = {
        id: getNodeId(),
        type,
        position,
        data: { label },
      };

      setNodes((nds) => [...nds, newNode]);
    },
    [screenToFlowPosition],
  );

  const onDragStart = (
    event: DragEvent,
    nodeType: string,
    label: string,
  ) => {
    event.dataTransfer.setData("application/reactflow-type", nodeType);
    event.dataTransfer.setData("application/reactflow-label", label);
    event.dataTransfer.effectAllowed = "move";
  };

  // Convert ReactFlow nodes/edges to our workflow format
  const convertToWorkflowFormat = useCallback((): { nodes: WorkflowNode[]; edges: WorkflowEdge[] } => {
    const workflowNodes: WorkflowNode[] = nodes
      .filter(n => n.type !== "placeholder")
      .map((node) => ({
        id: node.id,
        type: node.type || "custom",
        position: node.position,
        data: node.data || {},
      }));

    const workflowEdges: WorkflowEdge[] = edges.map((edge) => ({
      id: edge.id,
      source: edge.source,
      target: edge.target,
      sourceHandle: edge.sourceHandle || undefined,
      targetHandle: edge.targetHandle || undefined,
    }));

    return { nodes: workflowNodes, edges: workflowEdges };
  }, [nodes, edges]);

  // Handle save workflow
  const handleSaveWorkflow = useCallback(async (name: string) => {
    if (!user) {
      // Redirect to login if not authenticated
      window.location.href = '/login';
      return;
    }

    // Remove placeholder node before saving
    const actualNodes = nodes.filter(n => n.type !== "placeholder");
    if (actualNodes.length === 0) {
      alert("Please add at least one node to your workflow");
      return;
    }

    setIsSaving(true);
    try {
      const { nodes: workflowNodes, edges: workflowEdges } = convertToWorkflowFormat();
      
      await addWorkflow({
        id: "", // Will be generated by DB
        userId: user.id,
        name,
        description: "",
        nodes: workflowNodes,
        edges: workflowEdges,
        createdAt: new Date(),
        updatedAt: new Date(),
      });

      alert("Workflow saved successfully!");
      
      // Reset the canvas
      setNodes([placeholderNode]);
      setEdges([]);
    } catch (error) {
      console.error("Error saving workflow:", error);
      alert("Failed to save workflow. Please try again.");
    } finally {
      setIsSaving(false);
    }
  }, [user, nodes, edges, addWorkflow, convertToWorkflowFormat]);

  return (
    <>
      <div className="flex h-screen w-screen">
        {/* Sidebar toolbox */}
        <aside className="flex w-60 flex-col border-r border-border bg-card p-4">
          <h2 className="mb-1 text-lg font-bold text-foreground">
            Learning Tools
          </h2>
          <p className="mb-4 text-xs text-text-secondary">
            Drag nodes onto the canvas to build your learning pipeline
          </p>
          <div className="flex flex-col gap-2">
            {toolbox.map((tool) => (
              <div
                key={tool.type}
                draggable
                onDragStart={(e) => onDragStart(e, tool.type, tool.label)}
                className="flex cursor-grab items-center gap-2 rounded-lg border border-border bg-background px-3 py-2 text-sm font-medium text-foreground transition-colors hover:border-accent hover:bg-accent/10 active:cursor-grabbing"
              >
                <div
                  className="flex h-7 w-7 shrink-0 items-center justify-center rounded-md border"
                  style={{ borderColor: tool.color, backgroundColor: `${tool.color}15` }}
                >
                  <tool.icon size={14} style={{ color: tool.color }} />
                </div>
                {tool.label}
              </div>
            ))}
          </div>

          <div className="mt-auto pt-4 space-y-2">
            {graphHasCycle && (
              <p className="mb-2 text-xs text-error font-medium">
                Cycle detected — remove a connection to continue
              </p>
            )}
            {!user && (
              <p className="mb-2 text-xs text-muted-foreground">
                Sign in to save your workflow
              </p>
            )}
            <button
              onClick={() => user ? setShowSaveDialog(true) : (window.location.href = '/login')}
              disabled={graphHasCycle || nodes.length <= 1 || !user}
              className="w-full flex items-center justify-center gap-2 rounded-lg bg-primary px-4 py-2 text-sm font-semibold text-primary-foreground transition-colors hover:bg-primary/90 disabled:cursor-not-allowed disabled:opacity-50"
            >
              <Save className="size-4" />
              {user ? 'Save Workflow' : 'Sign in to Save'}
            </button>
            <button
              disabled={graphHasCycle}
              className="w-full rounded-lg bg-accent px-4 py-2 text-sm font-semibold text-accent-foreground transition-colors hover:bg-accent-hover disabled:cursor-not-allowed disabled:opacity-50"
            >
              Execute Pipeline
            </button>
          </div>
        </aside>

        {/* Canvas */}
        <div ref={reactFlowWrapper} className="flex-1">
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
        </div>
      </div>

      <SaveWorkflowDialog
        isOpen={showSaveDialog}
        onClose={() => setShowSaveDialog(false)}
        onSave={handleSaveWorkflow}
      />
    </>
  );
}

export default function LearnPage() {
  return (
    <ReactFlowProvider>
      <Flow />
    </ReactFlowProvider>
  );
}
