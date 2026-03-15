"use client";

import { useState, useRef, useEffect } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { 
  Bell, 
  Sparkles, 
  Zap, 
  Plus, 
  Workflow, 
  User, 
  Settings, 
  LogOut,
  ChevronDown,
  Menu
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { useApp } from "@/lib/context/app-context";
import { cn } from "@/lib/utils";
import { useRouter } from "next/navigation";

export function Navbar() {
  const pathname = usePathname();
  const router = useRouter();
  const { user, notifications, unreadCount, markAsRead, markAllAsRead, setUser } = useApp();
  const [showNotifications, setShowNotifications] = useState(false);
  const [showUserMenu, setShowUserMenu] = useState(false);
  const notifRef = useRef<HTMLDivElement>(null);
  const userMenuRef = useRef<HTMLDivElement>(null);

  // Close dropdowns when clicking outside
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (notifRef.current && !notifRef.current.contains(event.target as Node)) {
        setShowNotifications(false);
      }
      if (userMenuRef.current && !userMenuRef.current.contains(event.target as Node)) {
        setShowUserMenu(false);
      }
    }

    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const getInitials = (name: string) => {
    if (!name) return "?";
    return name
      .split(" ")
      .filter((n) => n.length > 0)
      .map((n) => n[0])
      .join("")
      .toUpperCase()
      .slice(0, 2) || "?";
  };

  return (
    <header className="flex items-center justify-between whitespace-nowrap border-b border-primary/10 px-4 md:px-8 py-3 bg-background/95 backdrop-blur-md sticky top-0 z-50">
      {/* Logo */}
      <div className="flex items-center gap-4">
        <Link href="/" className="flex items-center gap-2">
          <h2 className="text-foreground text-xl font-bold leading-tight tracking-tight">
            DysLearnia
          </h2>
        </Link>

        {/* Navigation Links */}
        <nav className="hidden md:flex items-center gap-1 ml-8">
          <Link href="/learn">
            <Button
              variant={pathname === "/learn" ? "secondary" : "ghost"}
              size="sm"
              className="gap-2"
            >
              <Plus className="size-4" />
              New Workflow
            </Button>
          </Link>
          <Link href="/workflows">
            <Button
              variant={pathname.startsWith("/workflows") ? "secondary" : "ghost"}
              size="sm"
              className="gap-2"
            >
              <Workflow className="size-4" />
              My Workflows
            </Button>
          </Link>
        </nav>
      </div>

      {/* Right side - Stats, Notifications, User */}
      <div className="flex items-center gap-2">
        {/* Gamification Stats */}
        <div className="hidden sm:flex items-center gap-2 px-3 py-1.5 bg-primary/10 rounded-full border border-primary/20">
          <Zap className="size-4 text-primary fill-primary" />
          <span className="text-xs font-bold text-primary">{user?.streak} DAY STREAK</span>
        </div>
        <div className="hidden sm:flex items-center gap-2 px-3 py-1.5 bg-gold/20 rounded-full border border-gold/30">
          <Sparkles className="size-4 text-gold fill-gold" />
          <span className="text-xs font-bold text-gold">{user?.xp.toLocaleString()} XP</span>
        </div>

        {/* Notifications */}
        <div className="relative" ref={notifRef}>
          <Button
            variant="ghost"
            size="icon"
            className="rounded-xl bg-primary/5 text-foreground hover:bg-primary/10 relative"
            onClick={() => setShowNotifications(!showNotifications)}
          >
            <Bell className="size-5" />
            {unreadCount > 0 && (
              <span className="absolute -top-1 -right-1 size-4 bg-destructive text-destructive-foreground text-[10px] font-bold rounded-full flex items-center justify-center">
                {unreadCount}
              </span>
            )}
          </Button>

          {/* Notifications Dropdown */}
          {showNotifications && (
            <div className="absolute right-0 top-full mt-2 w-80 bg-popover border border-border rounded-lg shadow-lg overflow-hidden">
              <div className="flex items-center justify-between px-4 py-3 border-b border-border">
                <h3 className="font-semibold text-sm">Notifications</h3>
                {unreadCount > 0 && (
                  <button
                    onClick={markAllAsRead}
                    className="text-xs text-primary hover:underline"
                  >
                    Mark all as read
                  </button>
                )}
              </div>
              <div className="max-h-80 overflow-y-auto">
                {notifications.length === 0 ? (
                  <div className="px-4 py-8 text-center text-muted-foreground text-sm">
                    No notifications yet
                  </div>
                ) : (
                  notifications.map((notif) => (
                    <div
                      key={notif.id}
                      className={cn(
                        "px-4 py-3 border-b border-border last:border-0 cursor-pointer hover:bg-muted/50 transition-colors",
                        !notif.read && "bg-primary/5"
                      )}
                      onClick={() => markAsRead(notif.id)}
                    >
                      <div className="flex items-start gap-3">
                        {!notif.read && (
                          <span className="w-2 h-2 rounded-full bg-primary mt-1.5 shrink-0" />
                        )}
                        <div className={cn(!notif.read && "ml-2")}>
                          <p className="font-medium text-sm">{notif.title}</p>
                          <p className="text-xs text-muted-foreground mt-0.5">
                            {notif.message}
                          </p>
                          <p className="text-xs text-muted-foreground mt-1">
                            {formatTimeAgo(notif.createdAt)}
                          </p>
                        </div>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>
          )}
        </div>

        {/* User Menu */}
        <div className="relative" ref={userMenuRef}>
          <Button
            variant="ghost"
            className="gap-2 px-2 h-auto hover:bg-primary/5"
            onClick={() => setShowUserMenu(!showUserMenu)}
          >
            {user?.avatarUrl ? (
              <img
                src={user.avatarUrl}
                alt={user.name}
                className="size-8 rounded-full object-cover border-2 border-primary/20"
              />
            ) : (
              <div className="bg-primary/20 rounded-full size-8 border-2 border-primary/20 flex items-center justify-center text-primary font-bold text-sm">
                {user ? getInitials(user.name) : "?"}
              </div>
            )}
            <ChevronDown className="size-4 text-muted-foreground hidden sm:block" />
          </Button>

          {/* User Dropdown */}
          {showUserMenu && (
            <div className="absolute right-0 top-full mt-2 w-56 bg-popover border border-border rounded-lg shadow-lg overflow-hidden">
              <div className="px-4 py-3 border-b border-border">
                <p className="font-medium text-sm">{user?.name}</p>
                <p className="text-xs text-muted-foreground">{user?.email}</p>
              </div>
              <div className="py-1">
                <Link
                  href="/profile"
                  className="flex items-center gap-3 px-4 py-2 text-sm hover:bg-muted/50 transition-colors"
                  onClick={() => setShowUserMenu(false)}
                >
                  <User className="size-4" />
                  Profile
                </Link>
                <Link
                  href="/profile"
                  className="flex items-center gap-3 px-4 py-2 text-sm hover:bg-muted/50 transition-colors"
                  onClick={() => setShowUserMenu(false)}
                >
                  <Settings className="size-4" />
                  Settings
                </Link>
                <div className="border-t border-border my-1" />
                <button
                  className="flex items-center gap-3 px-4 py-2 text-sm text-destructive hover:bg-destructive/10 w-full transition-colors"
                  onClick={() => {
                    setShowUserMenu(false);
                    setUser(null);
                    router.push("/login");
                  }}
                >
                  <LogOut className="size-4" />
                  Sign out
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </header>
  );
}

function formatTimeAgo(date: Date): string {
  const now = new Date();
  const diff = now.getTime() - new Date(date).getTime();
  const minutes = Math.floor(diff / 60000);
  const hours = Math.floor(minutes / 60);
  const days = Math.floor(hours / 24);

  if (days > 0) return `${days}d ago`;
  if (hours > 0) return `${hours}h ago`;
  if (minutes > 0) return `${minutes}m ago`;
  return "Just now";
}
