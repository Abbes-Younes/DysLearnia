"use client";

import Link from "next/link";
import { useState } from "react";
import { 
  Plus, 
  Workflow, 
  Clock, 
  MoreVertical, 
  Trash2, 
  Edit,
  Search,
  Filter
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { useApp, Workflow as WorkflowType } from "@/lib/context/app-context";

export default function WorkflowsPage() {
  const { workflows, deleteWorkflow } = useApp();
  const [searchQuery, setSearchQuery] = useState("");
  const [sortBy, setSortBy] = useState<"recent" | "name">("recent");

  // Filter and sort workflows
  const filteredWorkflows = (workflows || [])
    .filter((w) =>
      w.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      w.description?.toLowerCase().includes(searchQuery.toLowerCase())
    )
    .sort((a, b) => {
      if (sortBy === "recent") {
        return new Date(b.updatedAt).getTime() - new Date(a.updatedAt).getTime();
      }
      return a.name.localeCompare(b.name);
    });

  return (
    <div className="container mx-auto px-4 py-8 max-w-6xl">
      {/* Page Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 mb-8">
        <div>
          <h1 className="text-3xl font-bold text-foreground">My Workflows</h1>
          <p className="text-muted-foreground mt-1">
            Create and manage your learning workflows
          </p>
        </div>
        <Link href="/learn">
          <Button className="gap-2">
            <Plus className="size-4" />
            Create New Workflow
          </Button>
        </Link>
      </div>

      {/* Search and Filter */}
      <div className="flex flex-col sm:flex-row gap-4 mb-6">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 size-4 text-muted-foreground" />
          <input
            type="text"
            placeholder="Search workflows..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-10 pr-4 py-2 rounded-lg border border-input bg-background focus:outline-none focus:ring-2 focus:ring-ring"
          />
        </div>
        <div className="flex items-center gap-2">
          <Filter className="size-4 text-muted-foreground" />
          <select
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value as "recent" | "name")}
            className="px-3 py-2 rounded-lg border border-input bg-background focus:outline-none focus:ring-2 focus:ring-ring"
            aria-label="Sort workflows"
          >
            <option value="recent">Most Recent</option>
            <option value="name">Name</option>
          </select>
        </div>
      </div>

      {/* Workflows Grid */}
      {filteredWorkflows.length === 0 ? (
        <div className="text-center py-16">
          <div className="inline-flex items-center justify-center size-16 rounded-full bg-primary/10 mb-4">
            <Workflow className="size-8 text-primary" />
          </div>
          <h3 className="text-lg font-semibold text-foreground mb-2">
            {searchQuery ? "No workflows found" : "No workflows yet"}
          </h3>
          <p className="text-muted-foreground mb-6 max-w-md mx-auto">
            {searchQuery
              ? "Try adjusting your search query"
              : "Start creating your first workflow to organize your learning content"}
          </p>
          {!searchQuery && (
            <Link href="/learn">
              <Button>
                <Plus className="size-4 mr-2" />
                Create Your First Workflow
              </Button>
            </Link>
          )}
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filteredWorkflows.map((workflow) => (
            <WorkflowCard
              key={workflow.id}
              workflow={workflow}
              onDelete={deleteWorkflow}
            />
          ))}
        </div>
      )}
    </div>
  );
}

function WorkflowCard({
  workflow,
  onDelete,
}: {
  workflow: WorkflowType;
  onDelete: (id: string) => void;
}) {
  const [showMenu, setShowMenu] = useState(false);

  return (
    <Card className="group hover:shadow-lg transition-all duration-200">
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-primary/10">
              <Workflow className="size-5 text-primary" />
            </div>
            <CardTitle className="text-lg font-semibold">
              {workflow.name}
            </CardTitle>
          </div>
          <div className="relative">
            <Button
              variant="ghost"
              size="icon-xs"
              className="opacity-0 group-hover:opacity-100 transition-opacity"
              onClick={() => setShowMenu(!showMenu)}
            >
              <MoreVertical className="size-4" />
            </Button>
            {showMenu && (
              <div className="absolute right-0 top-full mt-1 w-36 bg-popover border border-border rounded-lg shadow-lg overflow-hidden z-10">
                <Link
                  href={`/workflows/${workflow.id}`}
                  className="flex items-center gap-2 px-3 py-2 text-sm hover:bg-muted/50"
                  onClick={() => setShowMenu(false)}
                >
                  <Edit className="size-4" />
                  Edit
                </Link>
                <button
                  className="flex items-center gap-2 px-3 py-2 text-sm text-destructive hover:bg-destructive/10 w-full"
                  onClick={() => {
                    onDelete(workflow.id);
                    setShowMenu(false);
                  }}
                >
                  <Trash2 className="size-4" />
                  Delete
                </button>
              </div>
            )}
          </div>
        </div>
      </CardHeader>
      <CardContent>
        {workflow.description && (
          <p className="text-sm text-muted-foreground mb-4 line-clamp-2">
            {workflow.description}
          </p>
        )}
        <div className="flex items-center justify-between text-xs text-muted-foreground">
          <div className="flex items-center gap-1">
            <Clock className="size-3" />
            {formatDate(workflow.updatedAt)}
          </div>
          <div className="flex items-center gap-2">
            <span>{workflow.nodes.length} nodes</span>
            <span>•</span>
            <span>{workflow.edges.length} edges</span>
          </div>
        </div>
        <Link href={`/workflows/${workflow.id}`}>
          <Button variant="outline" className="w-full mt-4">
            Open Workflow
          </Button>
        </Link>
      </CardContent>
    </Card>
  );
}

function formatDate(date: Date): string {
  const now = new Date();
  const d = new Date(date);
  const diff = now.getTime() - d.getTime();
  const days = Math.floor(diff / (1000 * 60 * 60 * 24));

  if (days === 0) return "Today";
  if (days === 1) return "Yesterday";
  if (days < 7) return `${days} days ago`;
  return d.toLocaleDateString("en-US", { month: "short", day: "numeric" });
}
