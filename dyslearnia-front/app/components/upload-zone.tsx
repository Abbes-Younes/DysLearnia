"use client";

import { useCallback, useRef, useState } from "react";
import { Upload } from "lucide-react";
import { Button } from "@/components/ui/button";

export function UploadZone() {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [isDragging, setIsDragging] = useState(false);

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    // TODO: handle dropped files
  }, []);

  return (
    <section className="flex flex-col">
      <div
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={() => fileInputRef.current?.click()}
        className={`flex flex-col items-center gap-8 rounded-xl border-4 border-dashed px-6 py-20 transition-all cursor-pointer ${
          isDragging
            ? "border-primary bg-primary/15"
            : "border-primary/30 bg-primary/5 hover:border-primary/50 hover:bg-primary/10"
        }`}
      >
        <div className="bg-primary/20 p-6 rounded-full">
          <Upload className="size-12 text-primary" />
        </div>
        <div className="flex flex-col items-center gap-2">
          <p className="text-foreground text-2xl font-bold tracking-tight text-center">
            Upload Study Materials
          </p>
          <p className="text-text-secondary text-base font-normal max-w-[400px] text-center">
            Drag and drop your PDFs here, or browse your local files to get
            started.
          </p>
        </div>
        <Button
          size="lg"
          className="min-w-[180px] h-12 px-6 text-base font-bold rounded-xl shadow-lg shadow-primary/20 transition-transform hover:scale-105 active:scale-95"
          onClick={(e) => {
            e.stopPropagation();
            fileInputRef.current?.click();
          }}
        >
          Browse Files
        </Button>
        <input
          ref={fileInputRef}
          type="file"
          accept=".pdf"
          multiple
          className="hidden"
        />
      </div>
    </section>
  );
}
