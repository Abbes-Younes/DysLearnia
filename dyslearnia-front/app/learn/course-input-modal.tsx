"use client";

import { useCallback, useRef, useState } from "react";
import {
  Upload,
  Loader2,
  CheckCircle2,
  AlertCircle,
  X,
  FileText,
  FileSpreadsheet,
  Video,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { uploadDocument } from "@/lib/api";

const ACCEPTED_FORMATS = [
  { ext: ".pdf", label: "PDF", icon: FileText },
  { ext: ".pptx", label: "PowerPoint", icon: FileSpreadsheet },
  { ext: ".mp4", label: "MP4", icon: Video },
  { ext: ".mov", label: "MOV", icon: Video },
  { ext: ".mkv", label: "MKV", icon: Video },
  { ext: ".webm", label: "WebM", icon: Video },
];

const ACCEPT_STRING = ACCEPTED_FORMATS.map((f) => f.ext).join(",");

type InputMode = "upload" | "text";

interface CourseInputModalProps {
  nodeId: string;
  initialText?: string;
  initialFileName?: string;
  onSave: (nodeId: string, text: string, fileName?: string) => void;
  onClose: () => void;
}

export function CourseInputModal({
  nodeId,
  initialText = "",
  initialFileName,
  onSave,
  onClose,
}: CourseInputModalProps) {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [mode, setMode] = useState<InputMode>(
    initialFileName ? "upload" : initialText ? "text" : "upload",
  );

  // Upload state
  const [isDragging, setIsDragging] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [uploadedText, setUploadedText] = useState(
    initialFileName ? initialText : "",
  );
  const [uploadedFileName, setUploadedFileName] = useState(
    initialFileName || "",
  );
  const [uploadError, setUploadError] = useState<string | null>(null);

  // Text state
  const [pastedText, setPastedText] = useState(
    initialFileName ? "" : initialText,
  );

  const handleFiles = useCallback(async (files: FileList | null) => {
    if (!files || files.length === 0) return;

    setUploading(true);
    setUploadError(null);
    setUploadedText("");
    setUploadedFileName("");

    try {
      const file = files[0];
      const res = await uploadDocument(file);
      setUploadedText(res.full_text);
      setUploadedFileName(file.name);
    } catch (err) {
      setUploadError(err instanceof Error ? err.message : "Upload failed");
    } finally {
      setUploading(false);
    }
  }, []);

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  }, []);

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      setIsDragging(false);
      handleFiles(e.dataTransfer.files);
    },
    [handleFiles],
  );

  const handleSave = () => {
    if (mode === "upload" && uploadedText) {
      onSave(nodeId, uploadedText, uploadedFileName);
    } else if (mode === "text" && pastedText.trim()) {
      onSave(nodeId, pastedText.trim());
    }
  };

  const hasContent =
    (mode === "upload" && !!uploadedText) ||
    (mode === "text" && !!pastedText.trim());

  return (
    <div className="fixed inset-0 z-[100] flex items-center justify-center">
      {/* Backdrop */}
      <div
        className="absolute inset-0 bg-black/40 backdrop-blur-sm"
        onClick={onClose}
      />

      {/* Modal */}
      <div className="relative z-10 flex w-full max-w-lg flex-col rounded-2xl border border-border bg-card shadow-2xl">
        {/* Header */}
        <div className="flex items-center justify-between border-b border-border px-5 py-4">
          <h2 className="text-lg font-bold text-foreground">Course Input</h2>
          <button
            onClick={onClose}
            className="rounded-lg p-1 text-text-secondary transition-colors hover:bg-muted hover:text-foreground"
          >
            <X size={18} />
          </button>
        </div>

        {/* Mode tabs */}
        <div className="flex border-b border-border">
          <button
            onClick={() => setMode("upload")}
            className={`flex-1 px-4 py-2.5 text-sm font-medium transition-colors ${
              mode === "upload"
                ? "border-b-2 border-accent text-accent"
                : "text-text-secondary hover:text-foreground"
            }`}
          >
            Upload File
          </button>
          <button
            onClick={() => setMode("text")}
            className={`flex-1 px-4 py-2.5 text-sm font-medium transition-colors ${
              mode === "text"
                ? "border-b-2 border-accent text-accent"
                : "text-text-secondary hover:text-foreground"
            }`}
          >
            Paste Text
          </button>
        </div>

        {/* Body */}
        <div className="p-5">
          {mode === "upload" ? (
            <div className="flex flex-col gap-4">
              {/* Drop zone */}
              <div
                onDragOver={handleDragOver}
                onDragLeave={handleDragLeave}
                onDrop={handleDrop}
                onClick={() => fileInputRef.current?.click()}
                className={`flex cursor-pointer flex-col items-center gap-3 rounded-xl border-2 border-dashed px-4 py-8 transition-all ${
                  isDragging
                    ? "border-accent bg-accent/10"
                    : "border-border bg-background hover:border-accent/50 hover:bg-accent/5"
                }`}
              >
                {uploading ? (
                  <Loader2 className="size-8 animate-spin text-accent" />
                ) : uploadedFileName ? (
                  <CheckCircle2 className="size-8 text-green-500" />
                ) : (
                  <Upload className="size-8 text-accent/70" />
                )}

                {uploadedFileName ? (
                  <div className="text-center">
                    <p className="text-sm font-medium text-foreground">
                      {uploadedFileName}
                    </p>
                    <p className="mt-0.5 text-xs text-text-secondary">
                      Click or drop to replace
                    </p>
                  </div>
                ) : uploading ? (
                  <p className="text-sm text-text-secondary">Uploading...</p>
                ) : (
                  <div className="text-center">
                    <p className="text-sm font-medium text-foreground">
                      Drop your file here or click to browse
                    </p>
                  </div>
                )}
              </div>

              {/* Supported formats */}
              <div className="flex flex-wrap items-center gap-2">
                <span className="text-xs text-text-secondary">Supported:</span>
                {ACCEPTED_FORMATS.map(({ ext, label, icon: FormatIcon }) => (
                  <span
                    key={ext}
                    className="inline-flex items-center gap-1 rounded-md bg-muted px-2 py-0.5 text-xs text-text-secondary"
                  >
                    <FormatIcon size={10} />
                    {label}
                  </span>
                ))}
              </div>

              {uploadError && (
                <div className="flex items-center gap-1.5 text-sm text-error">
                  <AlertCircle size={14} />
                  {uploadError}
                </div>
              )}

              <input
                ref={fileInputRef}
                type="file"
                accept={ACCEPT_STRING}
                className="hidden"
                onChange={(e) => handleFiles(e.target.files)}
              />
            </div>
          ) : (
            <div className="flex flex-col gap-3">
              <textarea
                value={pastedText}
                onChange={(e) => setPastedText(e.target.value)}
                placeholder="Paste your course material here..."
                className="h-48 w-full resize-none rounded-xl border border-border bg-background px-4 py-3 text-sm text-foreground placeholder:text-text-secondary/50 focus:border-accent focus:outline-none focus:ring-1 focus:ring-accent"
              />
              <p className="text-xs text-text-secondary">
                {pastedText.length > 0
                  ? `${pastedText.length} characters`
                  : "Paste or type your course content directly"}
              </p>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="flex items-center justify-end gap-2 border-t border-border px-5 py-4">
          <Button variant="outline" onClick={onClose}>
            Cancel
          </Button>
          <Button disabled={!hasContent || uploading} onClick={handleSave}>
            Save Input
          </Button>
        </div>
      </div>
    </div>
  );
}
