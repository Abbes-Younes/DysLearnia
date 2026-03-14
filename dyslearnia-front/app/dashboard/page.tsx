import { createClient } from "@/lib/supabase/server";
import { redirect } from "next/navigation";
import { Brain, BookOpen, Microscope, ArrowRight } from "lucide-react";
import { AppHeader } from "@/components/app-header";
import { UploadZone } from "@/components/upload-zone";
import { CourseCard } from "@/components/course-card";
import { Button } from "@/components/ui/button";

const courses = [
  {
    title: "Intro to Psychology",
    documents: 12,
    summaries: 4,
    progress: 45,
    icon: Brain,
    iconBgClass: "bg-blue-100",
    iconTextClass: "text-blue-600",
  },
  {
    title: "Modern History",
    documents: 8,
    summaries: 6,
    progress: 80,
    icon: BookOpen,
    iconBgClass: "bg-amber-100",
    iconTextClass: "text-amber-600",
  },
  {
    title: "Microbiology",
    documents: 15,
    summaries: 1,
    progress: 12,
    icon: Microscope,
    iconBgClass: "bg-emerald-100",
    iconTextClass: "text-emerald-600",
  },
];

export default async function DashboardPage() {
  const supabase = await createClient();
  const {
    data: { user },
  } = await supabase.auth.getUser();

  if (!user) redirect("/login");

  const displayName =
    user.user_metadata?.full_name?.split(" ")[0] ||
    user.email?.split("@")[0] ||
    "there";

  return (
    <div className="relative flex min-h-screen w-full flex-col overflow-x-hidden">
      <AppHeader />

      <main className="flex flex-1 justify-center py-10 px-6">
        <div className="flex flex-col max-w-[960px] flex-1 gap-12">
          {/* Welcome Section */}
          <section className="text-center space-y-2">
            <h1 className="text-4xl font-bold text-foreground tracking-tight">
              Welcome back, {displayName}.
            </h1>
            <p className="text-text-secondary text-lg">
              Ready to transform your study materials into clear paths?
            </p>
          </section>

          {/* Upload Zone */}
          <UploadZone />

          {/* My Courses Section */}
          <section className="flex flex-col gap-6">
            <div className="flex items-center justify-between">
              <h2 className="text-foreground text-2xl font-bold tracking-tight">
                My Courses
              </h2>
              <Button variant="link" className="text-primary font-semibold">
                View all
                <ArrowRight className="size-4" />
              </Button>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {courses.map((course) => (
                <CourseCard key={course.title} {...course} />
              ))}
            </div>
          </section>
        </div>
      </main>

      {/* Footer */}
      <footer className="px-6 md:px-20 py-8 border-t border-primary/5 flex justify-center opacity-50">
        <div className="flex items-center gap-6 text-xs font-medium text-foreground">
          <a href="#" className="hover:text-primary transition-colors">
            Support
          </a>
          <a href="#" className="hover:text-primary transition-colors">
            Privacy
          </a>
          <a href="#" className="hover:text-primary transition-colors">
            Accessibility Settings
          </a>
          <p>&copy; 2024 DysLearnia</p>
        </div>
      </footer>
    </div>
  );
}
