"use client";

import { Handle, Position, type NodeProps } from "@xyflow/react";

function NodeShell({
  children,
  label,
  icon,
  color,
}: {
  children?: React.ReactNode;
  label: string;
  icon: string;
  color: string;
}) {
  return (
    <div
      className="rounded-xl border-2 bg-card shadow-md min-w-[180px] max-w-[240px] relative"
      style={{ borderColor: color }}
    >
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

export function TextInputNode({ data }: NodeProps) {
  return (
    <>
      <NodeShell label={data.label as string} icon="📄" color="#4a9b8e">
        <p>Upload or paste your text content here</p>
      </NodeShell>
      {/* Exits Right */}
      <Handle type="source" position={Position.Right} className="w-3 h-3 !bg-gray-400" />
    </>
  );
}

export function SummarizeNode({ data }: NodeProps) {
  return (
    <>
      {/* Enters Left */}
      <Handle type="target" position={Position.Left} className="w-3 h-3 !bg-gray-400" />
      <NodeShell label={data.label as string} icon="✂️" color="#e8a838">
        <p>Summarize text into key points</p>
      </NodeShell>
      {/* Exits Right */}
      <Handle type="source" position={Position.Right} className="w-3 h-3 !bg-gray-400" />
    </>
  );
}

export function TTSNode({ data }: NodeProps) {
  return (
    <>
      <Handle type="target" position={Position.Left} className="w-3 h-3 !bg-gray-400" />
      <NodeShell label={data.label as string} icon="🔊" color="#6366f1">
        <p>Read text aloud with text-to-speech</p>
      </NodeShell>
      <Handle type="source" position={Position.Right} className="w-3 h-3 !bg-gray-400" />
    </>
  );
}

export function SpacingNode({ data }: NodeProps) {
  return (
    <>
      <Handle type="target" position={Position.Left} className="w-3 h-3 !bg-gray-400" />
      <NodeShell label={data.label as string} icon="↔️" color="#d4806b">
        <p>Increase letter &amp; line spacing</p>
      </NodeShell>
      <Handle type="source" position={Position.Right} className="w-3 h-3 !bg-gray-400" />
    </>
  );
}

export function FontFlipNode({ data }: NodeProps) {
  return (
    <>
      <Handle type="target" position={Position.Left} className="w-3 h-3 !bg-gray-400" />
      <NodeShell label={data.label as string} icon="🔤" color="#8b5cf6">
        <p>Switch to OpenDyslexic font</p>
      </NodeShell>
      <Handle type="source" position={Position.Right} className="w-3 h-3 !bg-gray-400" />
    </>
  );
}

export function OutputNode({ data }: NodeProps) {
  return (
    <>
      {/* Enters Left, No Exit */}
      <Handle type="target" position={Position.Left} className="w-3 h-3 !bg-gray-400" />
      <NodeShell label={data.label as string} icon="✅" color="#22c55e">
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