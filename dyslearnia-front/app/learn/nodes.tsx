"use client";

import {
  Handle,
  Position,
  useReactFlow,
  type NodeProps,
} from "@xyflow/react";
import {
  Trash2,
  Plus,
  FileText,
  Scissors,
  Volume2,
  Type,
  CheckCircle2,
  Brain,
  HelpCircle,
  Lightbulb,
  BookOpen,
  Network,
  Gamepad2,
  Image,
  FileDown,
  Presentation,
  Music,
  Video,
  Search,
  type LucideIcon,
} from "lucide-react";

// ── Icon & color mapping for known block types ──────────────────────────────

const BLOCK_ICONS: Record<string, LucideIcon> = {
  course_input: FileText,
  summarizer: Scissors,
  simplified_text: BookOpen,
  quiz_builder: HelpCircle,
  key_concepts: Lightbulb,
  knowledge_graph: Network,
  flashcards: Brain,
  gap_detector: Search,
  gamification: Gamepad2,
  dyslexia_font: Type,
  infographic: Image,
  tts: Volume2,
  pdf_unifier: FileDown,
  pptx_unifier: Presentation,
  audio_unifier: Music,
  video_unifier: Video,
};

const GROUP_COLORS: Record<string, string> = {
  input: "#4a9b8e",
  transform: "#e8a838",
  output: "#22c55e",
};

const BLOCK_COLORS: Record<string, string> = {
  course_input: "#4a9b8e",
  summarizer: "#e8a838",
  simplified_text: "#f59e0b",
  quiz_builder: "#ef4444",
  key_concepts: "#eab308",
  knowledge_graph: "#06b6d4",
  flashcards: "#8b5cf6",
  gap_detector: "#f97316",
  gamification: "#ec4899",
  dyslexia_font: "#6366f1",
  infographic: "#14b8a6",
  tts: "#6366f1",
  pdf_unifier: "#22c55e",
  pptx_unifier: "#10b981",
  audio_unifier: "#059669",
  video_unifier: "#047857",
};

export function getBlockIcon(blockName: string): LucideIcon {
  return BLOCK_ICONS[blockName] || CheckCircle2;
}

export function getBlockColor(blockName: string, group?: string): string {
  return BLOCK_COLORS[blockName] || GROUP_COLORS[group || "transform"] || "#6b7280";
}

// ── Node Shell (shared visual wrapper) ──────────────────────────────────────

function NodeShell({
  id,
  label,
  icon: Icon,
  color,
  hasSource = true,
  hasTarget = true,
  status,
}: {
  id: string;
  label: string;
  icon: LucideIcon;
  color: string;
  hasSource?: boolean;
  hasTarget?: boolean;
  status?: "idle" | "running" | "done" | "error";
}) {
  const { deleteElements } = useReactFlow();

  const statusRing =
    status === "running"
      ? "ring-2 ring-blue-400 animate-pulse"
      : status === "done"
        ? "ring-2 ring-green-400"
        : status === "error"
          ? "ring-2 ring-red-400"
          : "";

  return (
    <div className="group/node flex flex-col items-center gap-2">
      <div className="relative flex items-center">
        {hasTarget && (
          <Handle
            type="target"
            position={Position.Left}
            className="!w-2.5 !h-2.5 !bg-gray-400 !-left-2"
          />
        )}
        <button
          onClick={() => deleteElements({ nodes: [{ id }] })}
          className="absolute -top-2 -right-2 z-10 hidden h-5 w-5 items-center justify-center rounded-full bg-error text-white shadow-md transition-transform hover:scale-110 group-hover/node:flex"
        >
          <Trash2 size={10} />
        </button>
        <div
          className={`flex h-12 w-12 items-center justify-center rounded-lg border-2 shadow-md ${statusRing}`}
          style={{ borderColor: color, backgroundColor: `${color}15` }}
        >
          <Icon size={22} style={{ color }} />
        </div>
        {hasSource && (
          <Handle
            type="source"
            position={Position.Right}
            className="!w-2.5 !h-2.5 !bg-gray-400 !-right-2"
          />
        )}
      </div>
      <span className="relative z-10 text-xs font-medium text-foreground max-w-[80px] text-center leading-tight">
        {label}
      </span>
    </div>
  );
}

// ── Dynamic Node (renders any block from backend metadata) ──────────────────

export function DynamicNode({ id, data }: NodeProps) {
  const blockName = data.blockName as string || "";
  const group = data.group as string || "transform";
  const label = (data.label as string) || blockName;
  const status = data.status as "idle" | "running" | "done" | "error" | undefined;

  const Icon = getBlockIcon(blockName);
  const color = getBlockColor(blockName, group);

  return (
    <NodeShell
      id={id}
      label={label}
      icon={Icon}
      color={color}
      hasTarget={group !== "input"}
      hasSource={group !== "output"}
      status={status}
    />
  );
}

// ── Placeholder Node ────────────────────────────────────────────────────────

export function PlaceholderNode() {
  return (
    <div className="flex flex-col items-center gap-2">
      <div className="flex h-12 w-12 items-center justify-center rounded-lg border-2 border-dashed border-accent/40 bg-accent/5">
        <Plus size={20} className="text-accent/60" />
      </div>
      <span className="text-xs font-medium text-text-secondary max-w-[80px] text-center leading-tight">
        Add first step
      </span>
    </div>
  );
}

// ── Node type registry for React Flow ───────────────────────────────────────

export const nodeTypes = {
  dynamic: DynamicNode,
  placeholder: PlaceholderNode,
};
