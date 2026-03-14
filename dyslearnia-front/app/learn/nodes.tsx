"use client";

import {
  Handle,
  Position,
  useReactFlow,
  type NodeProps,
} from "@xyflow/react";
import { Trash2 } from "lucide-react";

function NodeShell({
  id,
  children,
  label,
  icon,
  color,
}: {
  id: string;
  children?: React.ReactNode;
  label: string;
  icon: string;
  color: string;
}) {
  const { deleteElements } = useReactFlow();

  return (
    <div
      className="group/node rounded-xl border-2 bg-card shadow-md min-w-[180px] max-w-[240px] relative"
      style={{ borderColor: color }}
    >
      <button
        onClick={() => deleteElements({ nodes: [{ id }] })}
        className="absolute -top-3 -right-3 z-10 hidden h-6 w-6 items-center justify-center rounded-full bg-error text-white shadow-md transition-transform hover:scale-110 group-hover/node:flex"
      >
        <Trash2 size={12} />
      </button>
      <div
        className="flex items-center gap-2 rounded-t-[10px] px-3 py-2 text-sm font-semibold text-white"
        style={{ backgroundColor: color }}
      >
        <span className="text-base">{icon}</span>
        <span>{label}</span>
      </div>
      {children && (
        <div className="px-3 py-2 text-xs text-text-secondary">{children}</div>
      )}
    </div>
  );
}

export function TextInputNode({ id, data }: NodeProps) {
  return (
    <>
      <NodeShell id={id} label={data.label as string} icon="📄" color="#4a9b8e">
        <p>Upload or paste your text content here</p>
      </NodeShell>
      {/* Exits Right */}
      <Handle type="source" position={Position.Right} className="w-3 h-3 !bg-gray-400" />
    </>
  );
}

export function SummarizeNode({ id, data }: NodeProps) {
  return (
    <>
      {/* Enters Left */}
      <Handle type="target" position={Position.Left} className="w-3 h-3 !bg-gray-400" />
      <NodeShell id={id} label={data.label as string} icon="✂️" color="#e8a838">
        <p>Summarize text into key points</p>
      </NodeShell>
      {/* Exits Right */}
      <Handle type="source" position={Position.Right} className="w-3 h-3 !bg-gray-400" />
    </>
  );
}

export function TTSNode({ id, data }: NodeProps) {
  return (
    <>
      <Handle type="target" position={Position.Left} className="w-3 h-3 !bg-gray-400" />
      <NodeShell id={id} label={data.label as string} icon="🔊" color="#6366f1">
        <p>Read text aloud with text-to-speech</p>
      </NodeShell>
      <Handle type="source" position={Position.Right} className="w-3 h-3 !bg-gray-400" />
    </>
  );
}

export function SpacingNode({ id, data }: NodeProps) {
  return (
    <>
      <Handle type="target" position={Position.Left} className="w-3 h-3 !bg-gray-400" />
      <NodeShell id={id} label={data.label as string} icon="↔️" color="#d4806b">
        <p>Increase letter &amp; line spacing</p>
      </NodeShell>
      <Handle type="source" position={Position.Right} className="w-3 h-3 !bg-gray-400" />
    </>
  );
}

export function FontFlipNode({ id, data }: NodeProps) {
  return (
    <>
      <Handle type="target" position={Position.Left} className="w-3 h-3 !bg-gray-400" />
      <NodeShell id={id} label={data.label as string} icon="🔤" color="#8b5cf6">
        <p>Switch to OpenDyslexic font</p>
      </NodeShell>
      <Handle type="source" position={Position.Right} className="w-3 h-3 !bg-gray-400" />
    </>
  );
}

export function OutputNode({ id, data }: NodeProps) {
  return (
    <>
      {/* Enters Left, No Exit */}
      <Handle type="target" position={Position.Left} className="w-3 h-3 !bg-gray-400" />
      <NodeShell id={id} label={data.label as string} icon="✅" color="#22c55e">
        <p>Final processed output</p>
      </NodeShell>
    </>
  );
}

export const nodeTypes = {
  textInput: TextInputNode,
  summarize: SummarizeNode,
  tts: TTSNode,
  spacing: SpacingNode,
  fontFlip: FontFlipNode,
  result: OutputNode,
};