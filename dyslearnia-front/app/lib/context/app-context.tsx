"use client";

import React, { createContext, useContext, useState, useCallback, useEffect, ReactNode } from "react";
import { createClient } from "@/lib/supabase/client";
import * as queries from "@/lib/supabase/queries";

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
  updateUser: (updates: Partial<User>) => Promise<void>;
  refreshUser: () => Promise<void>;
  
  // Workflow actions
  setWorkflows: (workflows: Workflow[]) => void;
  addWorkflow: (workflow: Workflow) => Promise<void>;
  updateWorkflow: (id: string, updates: Partial<Workflow>) => Promise<void>;
  deleteWorkflow: (id: string) => Promise<void>;
  setCurrentWorkflow: (workflow: Workflow | null) => void;
  refreshWorkflows: () => Promise<void>;
  
  // Notification actions
  setNotifications: (notifications: Notification[]) => void;
  markAsRead: (id: string) => void;
  markAllAsRead: () => void;
  
  // Loading state
  setLoading: (loading: boolean) => void;
}

// Mock notifications
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

// Create the context
const AppContext = createContext<AppContextType | undefined>(undefined);

// Helper to convert DB workflow to app workflow
function dbWorkflowToWorkflow(dbWorkflow: {
  id: string;
  user_id: string;
  name: string;
  description: string | null;
  nodes: unknown;
  edges: unknown;
  created_at: string;
  updated_at: string;
}): Workflow {
  return {
    id: dbWorkflow.id,
    userId: dbWorkflow.user_id,
    name: dbWorkflow.name,
    description: dbWorkflow.description || undefined,
    nodes: (dbWorkflow.nodes as WorkflowNode[]) || [],
    edges: (dbWorkflow.edges as WorkflowEdge[]) || [],
    createdAt: new Date(dbWorkflow.created_at),
    updatedAt: new Date(dbWorkflow.updated_at),
  };
}

// Provider component
export function AppProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [workflows, setWorkflows] = useState<Workflow[]>([]);
  const [currentWorkflow, setCurrentWorkflow] = useState<Workflow | null>(null);
  const [notifications, setNotifications] = useState<Notification[]>(mockNotifications);
  const [isLoading, setLoading] = useState(true);

  // Initialize - check auth and load data
  useEffect(() => {
    async function init() {
      const supabase = createClient();
      
      try {
        const { data: { session } } = await supabase.auth.getSession();
        
        if (session?.user) {
          // User is logged in, fetch from database
          try {
            const dbUser = await queries.getUser(session.user.id);
            
            setUser({
              id: dbUser.id,
              email: dbUser.email,
              name: dbUser.name,
              avatarUrl: dbUser.avatar_url || undefined,
              createdAt: new Date(dbUser.created_at),
              xp: dbUser.xp,
              streak: dbUser.streak,
            });

            // Load workflows
            const dbWorkflows = await queries.getWorkflows(session.user.id);
            setWorkflows(dbWorkflows.map(dbWorkflowToWorkflow));
          } catch (dbError) {
            // User exists in Auth but not in database yet
            // Create them from auth data
            console.log("User not in database, creating profile...");
            try {
              const newUser = await queries.createUser(
                session.user.id,
                session.user.email || "",
                session.user.email?.split("@")[0] || "User"
              );
              
              setUser({
                id: newUser.id,
                email: newUser.email,
                name: newUser.name,
                avatarUrl: newUser.avatar_url || undefined,
                createdAt: new Date(newUser.created_at),
                xp: newUser.xp,
                streak: newUser.streak,
              });
            } catch (createError) {
              console.error("Error creating user:", createError);
            }
          }
        }
      } catch (error) {
        console.error("Error initializing:", error);
      } finally {
        setLoading(false);
      }
    }

    init();

    // Listen for auth changes
    const supabase = createClient();
    const { data: { subscription } } = supabase.auth.onAuthStateChange(async (event, session) => {
      if (session?.user) {
        try {
          const dbUser = await queries.getUser(session.user.id);
          
          setUser({
            id: dbUser.id,
            email: dbUser.email,
            name: dbUser.name,
            avatarUrl: dbUser.avatar_url || undefined,
            createdAt: new Date(dbUser.created_at),
            xp: dbUser.xp,
            streak: dbUser.streak,
          });

          // Reload workflows
          const dbWorkflows = await queries.getWorkflows(session.user.id);
          setWorkflows(dbWorkflows.map(dbWorkflowToWorkflow));
        } catch (error) {
          console.error("Error fetching user:", error);
        }
      } else {
        setUser(null);
        setWorkflows([]);
      }
    });

    return () => {
      subscription.unsubscribe();
    };
  }, []);

  const updateUser = useCallback(async (updates: Partial<User>) => {
    if (!user) return;
    
    try {
      await queries.updateUser(user.id, {
        name: updates.name,
        avatar_url: updates.avatarUrl,
        xp: updates.xp,
        streak: updates.streak,
      });
      
      setUser((prev) => prev ? { ...prev, ...updates } : null);
    } catch (error) {
      console.error("Error updating user:", error);
      throw error;
    }
  }, [user]);

  const refreshUser = useCallback(async () => {
    if (!user) return;
    
    try {
      const dbUser = await queries.getUser(user.id);
      setUser({
        id: dbUser.id,
        email: dbUser.email,
        name: dbUser.name,
        avatarUrl: dbUser.avatar_url || undefined,
        createdAt: new Date(dbUser.created_at),
        xp: dbUser.xp,
        streak: dbUser.streak,
      });
    } catch (error) {
      console.error("Error refreshing user:", error);
    }
  }, [user]);

  const addWorkflow = useCallback(async (workflow: Workflow) => {
    if (!user) return;
    
    try {
      const dbWorkflow = await queries.createWorkflow(user.id, {
        name: workflow.name,
        description: workflow.description,
        nodes: workflow.nodes,
        edges: workflow.edges,
      });
      
      setWorkflows((prev) => [dbWorkflowToWorkflow(dbWorkflow), ...prev]);
    } catch (error) {
      console.error("Error adding workflow:", error);
      throw error;
    }
  }, [user]);

  const updateWorkflow = useCallback(async (id: string, updates: Partial<Workflow>) => {
    try {
      const dbWorkflow = await queries.updateWorkflow(id, {
        name: updates.name,
        description: updates.description,
        nodes: updates.nodes,
        edges: updates.edges,
        is_public: updates.description !== undefined ? undefined : undefined,
      });
      
      setWorkflows((prev) =>
        prev.map((w) => (w.id === id ? dbWorkflowToWorkflow(dbWorkflow) : w))
      );
      
      if (currentWorkflow?.id === id) {
        setCurrentWorkflow(dbWorkflowToWorkflow(dbWorkflow));
      }
    } catch (error) {
      console.error("Error updating workflow:", error);
      throw error;
    }
  }, [currentWorkflow]);

  const deleteWorkflow = useCallback(async (id: string) => {
    try {
      await queries.deleteWorkflow(id);
      setWorkflows((prev) => prev.filter((w) => w.id !== id));
      
      if (currentWorkflow?.id === id) {
        setCurrentWorkflow(null);
      }
    } catch (error) {
      console.error("Error deleting workflow:", error);
      throw error;
    }
  }, [currentWorkflow]);

  const refreshWorkflows = useCallback(async () => {
    if (!user) return;
    
    try {
      const dbWorkflows = await queries.getWorkflows(user.id);
      setWorkflows(dbWorkflows.map(dbWorkflowToWorkflow));
    } catch (error) {
      console.error("Error refreshing workflows:", error);
    }
  }, [user]);

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
    refreshUser,
    setWorkflows,
    addWorkflow,
    updateWorkflow,
    deleteWorkflow,
    setCurrentWorkflow,
    refreshWorkflows,
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
