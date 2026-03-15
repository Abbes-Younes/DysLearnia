"use client";

import type { LucideIcon } from "lucide-react";
import {
  Handle,
  Position,
  useReactFlow,
  type NodeProps,
} from "@xyflow/react";
import {
  Trash2,
  Plus,
  PenLine,
  Scissors,
  Volume2,
  MoveHorizontal,
  Type,
  CheckCircle2,
} from "lucide-react";

function NodeShell({
  id,
  label,
  icon: Icon,
  color,
  hasSource = true,
  hasTarget = true,
}: {
  id: string;
  label: string;
  icon: LucideIcon;
  color: string;
  hasSource?: boolean;
  hasTarget?: boolean;
}) {
  const { deleteElements } = useReactFlow();

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
          className="flex h-12 w-12 items-center justify-center rounded-lg border-2 shadow-md"
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
      <span className="text-xs font-medium text-foreground max-w-[80px] text-center leading-tight">
        {label}
      </span>
    </div>
  );
}

export function TextInputNode({ id, data }: NodeProps) {
  return (
    <NodeShell
      id={id}
      label={data.label as string}
      icon={PenLine}
      color="#4a9b8e"
      hasTarget={false}
    />
  );
}

export function SummarizeNode({ id, data }: NodeProps) {
  return (
    <NodeShell
      id={id}
      label={data.label as string}
      icon={Scissors}
      color="#e8a838"
    />
  );
}

export function TTSNode({ id, data }: NodeProps) {
  return (
    <NodeShell
      id={id}
      label={data.label as string}
      icon={Volume2}
      color="#6366f1"
    />
  );
}

export function SpacingNode({ id, data }: NodeProps) {
  return (
    <NodeShell
      id={id}
      label={data.label as string}
      icon={MoveHorizontal}
      color="#d4806b"
    />
  );
}

export function FontFlipNode({ id, data }: NodeProps) {
  return (
    <NodeShell
      id={id}
      label={data.label as string}
      icon={Type}
      color="#8b5cf6"
    />
  );
}

export function OutputNode({ id, data }: NodeProps) {
  return (
    <NodeShell
      id={id}
      label={data.label as string}
      icon={CheckCircle2}
      color="#22c55e"
      hasSource={false}
    />
  );
}

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

export const nodeTypes = {
  textInput: TextInputNode,
  summarize: SummarizeNode,
  tts: TTSNode,
  spacing: SpacingNode,
  fontFlip: FontFlipNode,
  result: OutputNode,
  placeholder: PlaceholderNode,
};
