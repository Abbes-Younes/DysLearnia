"use client";

import { useEffect, useState, useMemo } from "react";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";
import { 
  ArrowLeft, 
  Save, 
  Share2, 
  Play
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { 
  useApp, 
  Workflow as WorkflowType,
  WorkflowNode,
  WorkflowEdge 
} from "@/lib/context/app-context";

export default function WorkflowDetailPage() {
  const params = useParams();
  const router = useRouter();
  const { workflows, setCurrentWorkflow, currentWorkflow } = useApp();
  const [isLoading, setIsLoading] = useState(true);

  const workflowId = params.id as string;

  // Find workflow - using useMemo to avoid recreating on each render
  const workflow = useMemo(() => {
    return workflows.find((w) => w.id === workflowId);
  }, [workflows, workflowId]);

  useEffect(() => {
    if (workflow) {
      setCurrentWorkflow(workflow);
    } else {
      // For demo, create a sample workflow if not found
      const sampleWorkflow: WorkflowType = {
        id: workflowId,
        userId: "user-1",
        name: "Sample Workflow",
        description: "A sample workflow for demonstration",
        nodes: [
          {
            id: "node-1",
            type: "input",
            position: { x: 100, y: 200 },
            data: { label: "Start" }
          },
          {
            id: "node-2",
            type: "process",
            position: { x: 400, y: 200 },
            data: { label: "Process" }
          },
          {
            id: "node-3",
            type: "output",
            position: { x: 700, y: 200 },
            data: { label: "Output" }
          }
        ],
        edges: [
          { id: "edge-1", source: "node-1", target: "node-2" },
          { id: "edge-2", source: "node-2", target: "node-3" }
        ],
        createdAt: new Date(),
        updatedAt: new Date()
      };
      setCurrentWorkflow(sampleWorkflow);
    }
    
    // Use setTimeout to defer the loading state update
    const timer = setTimeout(() => {
      setIsLoading(false);
    }, 0);
    
    return () => clearTimeout(timer);
  }, [workflowId, workflow, setCurrentWorkflow]);

  if (isLoading) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
        </div>
      </div>
    );
  }

  if (!currentWorkflow) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="text-center py-16">
          <h2 className="text-2xl font-bold text-foreground mb-4">
            Workflow not found
          </h2>
          <p className="text-muted-foreground mb-6">
            The workflow you are looking for does not exist or has been deleted.
          </p>
          <Link href="/workflows">
            <Button>
              <ArrowLeft className="size-4 mr-2" />
              Back to Workflows
            </Button>
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8 max-w-6xl">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 mb-8">
        <div className="flex items-center gap-4">
          <Link href="/workflows">
            <Button variant="ghost" size="icon">
              <ArrowLeft className="size-5" />
            </Button>
          </Link>
          <div>
            <h1 className="text-2xl font-bold text-foreground">
              {currentWorkflow.name}
            </h1>
            {currentWorkflow.description && (
              <p className="text-muted-foreground mt-1">
                {currentWorkflow.description}
              </p>
            )}
          </div>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="outline" className="gap-2">
            <Play className="size-4" />
            Run
          </Button>
          <Button variant="outline" className="gap-2">
            <Share2 className="size-4" />
            Share
          </Button>
          <Button className="gap-2">
            <Save className="size-4" />
            Save
          </Button>
        </div>
      </div>

      {/* Workflow Canvas / Details */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main Canvas Area */}
        <div className="lg:col-span-2">
          <Card className="min-h-125">
            <CardHeader>
              <CardTitle>Workflow Canvas</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="relative w-full h-100 bg-muted/30 rounded-lg border-2 border-dashed border-muted-foreground/20 overflow-auto">
                {/* Nodes visualization */}
                <div className="absolute inset-0 p-8">
                  {currentWorkflow.nodes.map((node) => (
                    <NodeVisual
                      key={node.id}
                      node={node}
                      edges={currentWorkflow.edges}
                      nodes={currentWorkflow.nodes}
                    />
                  ))}
                  
                  {currentWorkflow.nodes.length === 0 && (
                    <div className="flex items-center justify-center h-full">
                      <div className="text-center">
                        <p className="text-muted-foreground mb-4">
                          No nodes in this workflow yet
                        </p>
                        <Link href="/learn">
                          <Button>Add Nodes in Editor</Button>
                        </Link>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Sidebar - Node List & Details */}
        <div className="space-y-4">
          {/* Nodes List */}
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Nodes ({currentWorkflow.nodes.length})</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2">
              {currentWorkflow.nodes.length === 0 ? (
                <p className="text-sm text-muted-foreground text-center py-4">
                  No nodes yet
                </p>
              ) : (
                currentWorkflow.nodes.map((node) => (
                  <div
                    key={node.id}
                    className="flex items-center gap-3 p-2 rounded-lg hover:bg-muted/50 cursor-pointer transition-colors"
                  >
                    <div className={getNodeColorClass(node.type)} />
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium truncate">
                        {(node.data?.label as string) || node.type}
                      </p>
                      <p className="text-xs text-muted-foreground">
                        {node.type}
                      </p>
                    </div>
                  </div>
                ))
              )}
            </CardContent>
          </Card>

          {/* Edges List */}
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Connections ({currentWorkflow.edges.length})</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2">
              {currentWorkflow.edges.length === 0 ? (
                <p className="text-sm text-muted-foreground text-center py-4">
                  No connections yet
                </p>
              ) : (
                currentWorkflow.edges.map((edge) => {
                  const sourceNode = currentWorkflow.nodes.find(n => n.id === edge.source);
                  const targetNode = currentWorkflow.nodes.find(n => n.id === edge.target);
                  return (
                    <div
                      key={edge.id}
                      className="flex items-center gap-2 p-2 rounded-lg text-sm"
                    >
                      <span className="truncate">
                        {(sourceNode?.data?.label as string) || edge.source}
                      </span>
                      <span className="text-muted-foreground">→</span>
                      <span className="truncate">
                        {(targetNode?.data?.label as string) || edge.target}
                      </span>
                    </div>
                  );
                })
              )}
            </CardContent>
          </Card>

          {/* Workflow Info */}
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Info</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3 text-sm">
              <div className="flex justify-between">
                <span className="text-muted-foreground">Created</span>
                <span>{formatDate(currentWorkflow.createdAt)}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Updated</span>
                <span>{formatDate(currentWorkflow.updatedAt)}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Status</span>
                <span className="text-success">Active</span>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}

function NodeVisual({
  node,
  edges,
}: {
  node: WorkflowNode;
  edges: WorkflowEdge[];
  nodes: WorkflowNode[];
}) {
  const outgoingEdges = edges.filter((e) => e.source === node.id);
  const incomingEdges = edges.filter((e) => e.target === node.id);

  return (
    <div
      className={`absolute p-3 rounded-lg border-2 min-w-30 text-center ${
        node.type === "input"
          ? "bg-green-50 border-green-300"
          : node.type === "output"
          ? "bg-blue-50 border-blue-300"
          : "bg-yellow-50 border-yellow-300"
      }`}
      style={{
        left: node.position.x,
        top: node.position.y,
        transform: "translate(-50%, -50%)",
      }}
    >
      <p className="text-sm font-medium">
        {(node.data?.label as string) || node.type}
      </p>
      <p className="text-xs text-muted-foreground mt-1">{node.type}</p>
      
      {/* Connection indicators */}
      {incomingEdges.length > 0 && (
        <div className="absolute -left-3 top-1/2 -translate-y-1/2 w-3 h-3 rounded-full bg-primary" />
      )}
      {outgoingEdges.length > 0 && (
        <div className="absolute -right-3 top-1/2 -translate-y-1/2 w-3 h-3 rounded-full bg-primary" />
      )}
    </div>
  );
}

function getNodeColorClass(type: string): string {
  switch (type) {
    case "input":
      return "w-3 h-3 rounded-full bg-green-400";
    case "output":
      return "w-3 h-3 rounded-full bg-blue-400";
    default:
      return "w-3 h-3 rounded-full bg-yellow-400";
  }
}

function formatDate(date: Date): string {
  return new Date(date).toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
  });
}
