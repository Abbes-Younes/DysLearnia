"use client";

import { useState, useCallback, useRef, type DragEvent } from "react";
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
  type OnConnect,
  useReactFlow,
  ReactFlowProvider,
} from "@xyflow/react";
import "@xyflow/react/dist/style.css";
import { nodeTypes } from "./nodes";

const toolbox = [
  { type: "textInput", label: "Text Input", icon: "📄" },
  { type: "summarize", label: "Summarize", icon: "✂️" },
  { type: "tts", label: "Text to Speech", icon: "🔊" },
  { type: "spacing", label: "Add Spacing", icon: "↔️" },
  { type: "fontFlip", label: "Flip Font", icon: "🔤" },
  { type: "output", label: "Output", icon: "✅" },
] as const;

const initialNodes: Node[] = [
  {
    id: "input-1",
    type: "textInput",
    position: { x: 250, y: 50 },
    data: { label: "Text Input" },
  },
  {
    id: "summarize-1",
    type: "summarize",
    position: { x: 100, y: 250 },
    data: { label: "Summarize" },
  },
  {
    id: "spacing-1",
    type: "spacing",
    position: { x: 400, y: 250 },
    data: { label: "Add Spacing" },
  },
  {
    id: "output-1",
    type: "output",
    position: { x: 250, y: 450 },
    data: { label: "Output" },
  },
];

const initialEdges: Edge[] = [
  {
    id: "e-input-summarize",
    source: "input-1",
    target: "summarize-1",
    type: "smoothstep",
    markerEnd: { type: MarkerType.ArrowClosed },
  },
  {
    id: "e-input-spacing",
    source: "input-1",
    target: "spacing-1",
    type: "smoothstep",
    markerEnd: { type: MarkerType.ArrowClosed },
  },
  {
    id: "e-summarize-output",
    source: "summarize-1",
    target: "output-1",
    type: "smoothstep",
    markerEnd: { type: MarkerType.ArrowClosed },
  },
  {
    id: "e-spacing-output",
    source: "spacing-1",
    target: "output-1",
    type: "smoothstep",
    markerEnd: { type: MarkerType.ArrowClosed },
  },
];

let nodeId = 0;
function getNodeId() {
  return `node-${++nodeId}`;
}

function Flow() {
  const [nodes, setNodes] = useState<Node[]>(initialNodes);
  const [edges, setEdges] = useState<Edge[]>(initialEdges);
  const reactFlowWrapper = useRef<HTMLDivElement>(null);
  const { screenToFlowPosition } = useReactFlow();

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
          // Optionally show a warning or prevent the connection
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

  return (
    <div className="flex h-screen w-screen">
      {/* Sidebar toolbox */}
      <aside className="flex w-[240px] flex-col border-r border-border bg-card p-4">
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
              <span className="text-base">{tool.icon}</span>
              {tool.label}
            </div>
          ))}
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
          onDrop={onDrop}
          onDragOver={onDragOver}
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
          <Panel position="top-center">
            <div className="rounded-lg border border-border bg-card/90 px-4 py-2 text-sm font-semibold text-foreground shadow-md backdrop-blur-sm">
              DysLearnia — Learning Pipeline
            </div>
          </Panel>
        </ReactFlow>
      </div>
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

