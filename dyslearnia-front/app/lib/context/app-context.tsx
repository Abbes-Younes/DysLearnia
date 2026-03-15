"use client";

import React, { createContext, useContext, useState, useCallback, ReactNode } from "react";

// Types for our data models
export interface User {
  id: string;
  email: string;
  name: string;
  avatarUrl?: string;
  createdAt: Date;
  xp: number;
  streak: number;
}

export interface Workflow {
  id: string;
  userId: string;
  name: string;
  description?: string;
  nodes: WorkflowNode[];
  edges: WorkflowEdge[];
  createdAt: Date;
  updatedAt: Date;
}

export interface WorkflowNode {
  id: string;
  type: string;
  position: { x: number; y: number };
  data: Record<string, unknown>;
}

export interface WorkflowEdge {
  id: string;
  source: string;
  target: string;
  sourceHandle?: string;
  targetHandle?: string;
}

export interface Notification {
  id: string;
  title: string;
  message: string;
  read: boolean;
  createdAt: Date;
}

// Context state interface
interface AppState {
  // User state
  user: User | null;
  isAuthenticated: boolean;
  
  // Workflows state
  workflows: Workflow[];
  currentWorkflow: Workflow | null;
  
  // Notifications
  notifications: Notification[];
  unreadCount: number;
  
  // Loading states
  isLoading: boolean;
}

// Context actions interface
interface AppContextType extends AppState {
  // User actions
  setUser: (user: User | null) => void;
  updateUser: (updates: Partial<User>) => void;
  
  // Workflow actions
  setWorkflows: (workflows: Workflow[]) => void;
  addWorkflow: (workflow: Workflow) => void;
  updateWorkflow: (id: string, updates: Partial<Workflow>) => void;
  deleteWorkflow: (id: string) => void;
  setCurrentWorkflow: (workflow: Workflow | null) => void;
  
  // Notification actions
  setNotifications: (notifications: Notification[]) => void;
  markAsRead: (id: string) => void;
  markAllAsRead: () => void;
  
  // Loading state
  setLoading: (loading: boolean) => void;
}

// Default mock user for development
const mockUser: User = {
  id: "user-1",
  email: "alex@example.com",
  name: "Alex Thompson",
  avatarUrl: undefined,
  createdAt: new Date("2024-01-15"),
  xp: 1250,
  streak: 7,
};

const mockNotifications: Notification[] = [
  {
    id: "notif-1",
    title: "New Achievement",
    message: "You've earned the 'Quick Learner' badge!",
    read: false,
    createdAt: new Date(),
  },
  {
    id: "notif-2",
    title: "Workflow Saved",
    message: "Your workflow 'Math Basics' was saved successfully.",
    read: true,
    createdAt: new Date(Date.now() - 86400000),
  },
];

// Only use mock user in development mode
const initialUser: User | null = process.env.NODE_ENV === "development" ? mockUser : null;

// Create the context
const AppContext = createContext<AppContextType | undefined>(undefined);

// Provider component
export function AppProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(initialUser);
  const [workflows, setWorkflows] = useState<Workflow[]>([]);
  const [currentWorkflow, setCurrentWorkflow] = useState<Workflow | null>(null);
  const [notifications, setNotifications] = useState<Notification[]>(mockNotifications);
  const [isLoading, setLoading] = useState(false);

  const updateUser = useCallback((updates: Partial<User>) => {
    setUser((prev) => (prev ? { ...prev, ...updates } : null));
  }, []);

  const addWorkflow = useCallback((workflow: Workflow) => {
    setWorkflows((prev) => [...prev, workflow]);
  }, []);

  const updateWorkflow = useCallback((id: string, updates: Partial<Workflow>) => {
    setWorkflows((prev) =>
      prev.map((w) => (w.id === id ? { ...w, ...updates } : w))
    );
  }, []);

  const deleteWorkflow = useCallback((id: string) => {
    setWorkflows((prev) => prev.filter((w) => w.id !== id));
  }, []);

  const markAsRead = useCallback((id: string) => {
    setNotifications((prev) =>
      prev.map((n) => (n.id === id ? { ...n, read: true } : n))
    );
  }, []);

  const markAllAsRead = useCallback(() => {
    setNotifications((prev) => prev.map((n) => ({ ...n, read: true })));
  }, []);

  const unreadCount = notifications.filter((n) => !n.read).length;

  const value: AppContextType = {
    user,
    isAuthenticated: !!user,
    workflows,
    currentWorkflow,
    notifications,
    unreadCount,
    isLoading,
    setUser,
    updateUser,
    setWorkflows,
    addWorkflow,
    updateWorkflow,
    deleteWorkflow,
    setCurrentWorkflow,
    setNotifications,
    markAsRead,
    markAllAsRead,
    setLoading,
  };

  return <AppContext.Provider value={value}>{children}</AppContext.Provider>;
}

// Custom hook to use the context
export function useApp() {
  const context = useContext(AppContext);
  if (context === undefined) {
    throw new Error("useApp must be used within an AppProvider");
  }
  return context;
}
