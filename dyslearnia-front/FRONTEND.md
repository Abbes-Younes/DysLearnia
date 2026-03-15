# DysLearnia Frontend Documentation

> Context document for AI assistants working on this codebase.

## Overview

DysLearnia is a dyslexia-friendly learning platform built with **Next.js 16**, **React 19**, **Tailwind CSS v4**, and **React Flow v12**. Users build visual learning pipelines by dragging processing blocks onto a canvas, connecting them, and executing the pipeline against a Python backend.

**Active route:** `/learn` — the pipeline builder.
**Legacy routes (do not modify):** `/dashboard`, `/lectures/*`

---

## Directory Structure

```
dyslearnia-front/
├── app/
│   ├── auth/callback/route.ts        # OAuth code → session exchange
│   ├── components/
│   │   ├── ui/
│   │   │   ├── button.tsx             # CVA button (variants: default/outline/ghost/destructive/link)
│   │   │   └── card.tsx               # Card, CardHeader, CardTitle, CardContent, CardFooter
│   │   ├── app-header.tsx             # Top bar: branding, XP/streak badges, avatar
│   │   ├── course-card.tsx            # Dashboard course tile with progress ring
│   │   ├── progress-ring.tsx          # SVG circular progress indicator
│   │   └── upload-zone.tsx            # Drag-and-drop file zone (PDF only, incomplete)
│   ├── learn/                         # ★ CORE ROUTE
│   │   ├── page.tsx                   # React Flow canvas + sidebar + results panel
│   │   ├── nodes.tsx                  # Node components, icons, colors
│   │   └── course-input-modal.tsx     # Upload/paste modal for course_input nodes
│   ├── lib/
│   │   ├── api.ts                     # Backend HTTP client (fetch wrappers)
│   │   ├── utils.ts                   # cn() — clsx + tailwind-merge
│   │   └── supabase/
│   │       ├── client.ts              # Browser Supabase client
│   │       └── server.ts              # Server Supabase client (cookie-based)
│   ├── login/page.tsx                 # Email/password login
│   ├── signup/page.tsx                # Email/password signup
│   ├── dashboard/page.tsx             # LEGACY — server component, course list
│   ├── lectures/[id]/page.tsx         # LEGACY — empty
│   ├── page.tsx                       # Root "/" — Next.js placeholder
│   ├── layout.tsx                     # Root layout: Inter font, metadata
│   └── globals.css                    # Design tokens, Tailwind v4 theme
├── middleware.ts                       # Auth guard: redirect to /login if no session
├── components.json                     # shadcn/ui config
├── next.config.ts
├── tsconfig.json
└── package.json
```

---

## Tech Stack

| Layer | Tech | Version |
|-------|------|---------|
| Framework | Next.js | 16.1.6 |
| UI | React | 19.2.3 |
| Styling | Tailwind CSS | v4 |
| Visual pipeline | @xyflow/react (React Flow) | 12.10.1 |
| Icons | lucide-react | 0.577+ |
| Auth | @supabase/ssr + @supabase/supabase-js | 0.9 / 2.99 |
| UI primitives | @base-ui/react + shadcn | 1.3 / 4.0 |
| Utilities | clsx, tailwind-merge, class-variance-authority, uuid | — |

---

## Design System (globals.css)

All colors/radii/shadows live as CSS custom properties on `:root`.

| Token | Value | Usage |
|-------|-------|-------|
| `--background` | `#fdf6e3` | Warm cream page bg |
| `--foreground` | `#2c2c2c` | Primary text |
| `--accent` / `--primary` | `#4a9b8e` | Teal accent (buttons, links, rings) |
| `--gold` | `#e8a838` | Highlights, transform group |
| `--error` / `--destructive` | `#d4806b` | Error states |
| `--background-secondary` | `#f0f4ef` | Light sage cards/sections |

**Dyslexia-friendly defaults:**
- `line-height: 1.8`
- `letter-spacing: 0.05em`
- `max-width: 70ch` on text blocks
- Inter font via Google Fonts

---

## Environment Variables

| Name | Required | Default |
|------|----------|---------|
| `NEXT_PUBLIC_API_URL` | No | `http://localhost:8000/api` |
| `NEXT_PUBLIC_SUPABASE_URL` | Yes | — |
| `NEXT_PUBLIC_SUPABASE_ANON_KEY` | Yes | — |

---

## Authentication Flow

1. **middleware.ts** intercepts every request (except `/login`, `/signup`, static assets).
2. Checks Supabase session via `@supabase/ssr` cookie management.
3. Redirects to `/login` if no valid session.
4. `/auth/callback/route.ts` handles OAuth code exchange → sets cookies → redirects.

Client pages use `createClient()` from `lib/supabase/client.ts`.
Server pages use `createClient()` from `lib/supabase/server.ts`.

---

## Backend API Client (`lib/api.ts`)

Base URL: `NEXT_PUBLIC_API_URL` (default `http://localhost:8000/api`).

All requests include header `"ngrok-skip-browser-warning": "true"`.

### Types

```typescript
interface BlockParameter {
  name: string;
  type: "slider" | "select" | "toggle" | "number" | "text";
  min?: number; max?: number; default?: unknown;
  options?: string[]; label?: string;
}

interface BlockDescription {
  name: string;                    // e.g. "course_input"
  display_name: string;            // e.g. "Course Input"
  group: "input" | "transform" | "output";
  input_types: string[];
  output_types: string[];
  parameters: BlockParameter[];
}

interface PipelineRunRequest {
  nodes: { id: string; type: string; data?: Record<string, unknown> }[];
  edges: { source: string; target: string }[];
  params: Record<string, Record<string, unknown>>;
  initial_inputs: Record<string, Record<string, unknown>>;
  validate_only?: boolean;
}

interface BlockDataOut {
  text: string | null;
  mime_type: string | null;
  metadata: Record<string, unknown>;
  source_chunks: string[];
  has_binary: boolean;
}

interface PipelineRunResponse {
  run_id: string;
  outputs: Record<string, BlockDataOut[]>;
  validation_errors: string[];
}
```

### Functions

| Function | Method | Endpoint | Purpose |
|----------|--------|----------|---------|
| `fetchBlocks()` | GET | `/api/blocks` | List all registered pipeline blocks |
| `runPipeline(req)` | POST | `/api/pipeline/run` | Execute a pipeline |
| `uploadDocument(file)` | POST | `/api/documents/upload` | Upload + extract text from file |
| `getBinaryOutputUrl(runId, nodeId)` | — | `/api/pipeline/{runId}/output/{nodeId}` | URL builder for binary downloads |

**Do NOT use legacy endpoints** (`/api/simplify`, `/api/quiz`, etc.). Always use the block/pipeline system.

---

## The /learn Route (Pipeline Builder)

### page.tsx — Main Page

**State:**
- `nodes`, `edges` — React Flow graph state
- `blocks` — block registry from backend (`fetchBlocks()` on mount)
- `blocksLoading`, `blocksError` — fetch status
- `pipelineRunning`, `pipelineError`, `pipelineResult` — execution state
- `courseInputNodeId` — which node's modal is open (null = closed)

**Layout (3 sections):**

1. **Sidebar (260px, left)** — Block toolbox
   - Blocks fetched from `/api/blocks` and grouped by `group` field
   - Groups: Input → Transform → Output (each with icon + color)
   - Each block is draggable (`onDragStart` sets transfer data)
   - "Execute Pipeline" button at bottom (disabled during cycles or no nodes)

2. **Canvas (center)** — React Flow workspace
   - Grid background, Controls, MiniMap
   - Drop handler creates new `dynamic` nodes at drop position
   - Click handler opens `CourseInputModal` for `course_input` nodes
   - Cycle detection on connect

3. **Results Panel (right overlay)** — Pipeline output
   - Shows per-node outputs after execution
   - Text results in formatted boxes
   - Binary download links
   - Source chunk attribution

**Key behaviors:**
- Drag block from sidebar → drop on canvas → creates node with UUID
- Placeholder node shown when canvas empty, removed on first real node
- `onNodeClick`: opens `CourseInputModal` only for `course_input` blocks
- `executePipeline()`: builds `PipelineRunRequest` from graph, seeds source nodes with `inputText`, POSTs to backend
- Cycle detection via DFS in `hasCycle()` — prevents connecting and executing cyclic graphs

### nodes.tsx — Node Components

**nodeTypes registry:**
```typescript
{ dynamic: DynamicNode, placeholder: PlaceholderNode }
```

**DynamicNode** — renders any block:
- Reads `blockName`, `group`, `label` from `data`
- Looks up icon from `BLOCK_ICONS` map, color from `BLOCK_COLORS` map
- Input nodes: no target handle. Output nodes: no source handle.
- Wrapped in `NodeShell`

**NodeShell** — shared visual wrapper:
- Rounded icon box with colored border
- Input/output handles (configurable via `hasSource`/`hasTarget`)
- Delete button (trash icon) on hover — uses `e.stopPropagation()` to avoid triggering node click
- Status ring: idle (gray), running (pulse animation), done (green), error (red)
- Label below icon

**Block icon map** (`BLOCK_ICONS`):
```
course_input → FileText, summarizer → Scissors, simplified_text → BookOpen,
quiz_builder → HelpCircle, key_concepts → Lightbulb, knowledge_graph → Network,
flashcards → Brain, gap_detector → Search, gamification → Gamepad2,
dyslexia_font → Type, infographic → Image, tts → Volume2,
pdf_unifier → FileDown, pptx_unifier → Presentation,
audio_unifier → Music, video_unifier → Video
```

**Block color map** (`BLOCK_COLORS`): per-block hex colors. Falls back to group colors (`input: #4a9b8e`, `transform: #e8a838`, `output: #22c55e`).

**PlaceholderNode** — dashed border, "Add first step" prompt.

### course-input-modal.tsx — Course Input Modal

**Props:**
```typescript
{
  nodeId: string;
  initialText?: string;
  initialFileName?: string;
  onSave: (nodeId: string, text: string, fileName?: string) => void;
  onClose: () => void;
}
```

**Two tabs:**
1. **Upload File** — drag-and-drop or click-to-browse. Accepts: `.pdf`, `.pptx`, `.mp4`, `.mov`, `.mkv`, `.webm`. Calls `uploadDocument(file)` → stores returned `full_text`.
2. **Paste Text** — textarea with character count.

Saves text (+ optional filename) back to node via `onSave` callback.

---

## Node Data Shape

```typescript
{
  id: string;                        // UUID v4
  type: "dynamic" | "placeholder";
  position: { x: number; y: number };
  data: {
    blockName: string;               // Backend block name
    label: string;                   // Display name
    group: "input" | "transform" | "output";
    inputText?: string;              // Text content (course_input nodes)
    inputFileName?: string;          // Original filename
    status?: "idle" | "running" | "done" | "error";
  };
}
```

**Edge shape:**
```typescript
{
  source: string; target: string;
  type: "smoothstep";
  markerEnd: { type: MarkerType.ArrowClosed };
}
```

---

## Shared Components

| Component | File | Purpose |
|-----------|------|---------|
| `AppHeader` | `components/app-header.tsx` | Top bar with branding, XP/streak badges, avatar |
| `CourseCard` | `components/course-card.tsx` | Dashboard course tile (title, doc count, progress ring) |
| `ProgressRing` | `components/progress-ring.tsx` | SVG circular progress (percentage, size, strokeWidth) |
| `UploadZone` | `components/upload-zone.tsx` | Drag-and-drop file zone (PDF, incomplete handler) |
| `Button` | `components/ui/button.tsx` | CVA button with variants/sizes |
| `Card` | `components/ui/card.tsx` | Card layout components |

---

## State Management

No global store. All state is local React hooks (`useState`, `useCallback`, `useMemo`, `useRef`).
React Flow state managed via its built-in hooks (`useReactFlow`, `useNodesState`, `useEdgesState`).
Auth state managed by Supabase SSR cookies.

---

## Data Flow Summary

```
Page Load → GET /api/blocks → populate sidebar

Drag block → drop on canvas → create node (UUID)

Click course_input node → open modal → upload file (POST /api/documents/upload) or paste text → save to node.data.inputText

Connect nodes → cycle check → create edge

Execute Pipeline → build PipelineRunRequest from graph → POST /api/pipeline/run → display results overlay
```
