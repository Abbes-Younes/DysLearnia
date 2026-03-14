import type { LucideIcon } from "lucide-react";
import { ProgressRing } from "@/components/progress-ring";

interface CourseCardProps {
  title: string;
  documents: number;
  summaries: number;
  progress: number;
  icon: LucideIcon;
  iconBgClass: string;
  iconTextClass: string;
}

export function CourseCard({
  title,
  documents,
  summaries,
  progress,
  icon: Icon,
  iconBgClass,
  iconTextClass,
}: CourseCardProps) {
  return (
    <div className="bg-background/50 border border-primary/10 rounded-xl p-6 hover:shadow-xl hover:shadow-primary/5 transition-all group cursor-pointer">
      <div className="flex justify-between items-start mb-6">
        <div className={`p-3 rounded-lg ${iconBgClass} ${iconTextClass}`}>
          <Icon className="size-6" />
        </div>
        <ProgressRing percentage={progress} />
      </div>
      <h3 className="text-foreground text-lg font-bold mb-1">{title}</h3>
      <p className="text-primary/60 text-sm font-medium">
        {documents} documents · {summaries}{" "}
        {summaries === 1 ? "summary" : "summaries"}
      </p>
    </div>
  );
}
