import { Bell, Sparkles, Zap } from "lucide-react";
import { Button } from "@/components/ui/button";

export function AppHeader() {
  return (
    <header className="flex items-center justify-between whitespace-nowrap border-b border-primary/10 px-6 md:px-20 py-4 bg-background/80 backdrop-blur-md sticky top-0 z-50">
      <div className="flex items-center gap-4 text-primary">
        <h2 className="text-foreground text-xl font-bold leading-tight tracking-tight">
          DysLearnia
        </h2>
      </div>

      <div className="flex items-center gap-4">
        {/* Gamification Badges */}
        <div className="hidden sm:flex items-center gap-2 px-3 py-1.5 bg-primary/10 rounded-full border border-primary/20">
          <Zap className="size-4 text-primary fill-primary" />
          <span className="text-xs font-bold text-primary">7 DAY STREAK</span>
        </div>
        <div className="hidden sm:flex items-center gap-2 px-3 py-1.5 bg-gold/20 rounded-full border border-gold/30">
          <Sparkles className="size-4 text-gold fill-gold" />
          <span className="text-xs font-bold text-gold">1,250 XP</span>
        </div>

        <div className="flex gap-2 border-l border-primary/10 pl-4 ml-2">
          <Button
            variant="ghost"
            size="icon"
            className="rounded-xl bg-primary/5 text-foreground hover:bg-primary/10"
          >
            <Bell className="size-5" />
          </Button>
          <div className="bg-primary/20 rounded-full size-10 border-2 border-primary/20 flex items-center justify-center text-primary font-bold text-sm">
            A
          </div>
        </div>
      </div>
    </header>
  );
}
