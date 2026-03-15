"use client";

import { useState, useRef } from "react";
import { 
  User, 
  Mail, 
  Lock, 
  Bell, 
  Shield, 
  Trash2, 
  Save,
  Camera,
  Eye,
  EyeOff,
  Zap,
  Sparkles,
  BookOpen,
  Award,
  Loader2
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { useApp } from "@/lib/context/app-context";
import { uploadAvatar } from "@/lib/supabase/queries";

export default function ProfilePage() {
  const { user, updateUser } = useApp();
  const [isEditingName, setIsEditingName] = useState(false);
  const [name, setName] = useState(user?.name || "");
  const [showPasswordChange, setShowPasswordChange] = useState(false);
  const [currentPassword, setCurrentPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [showCurrentPassword, setShowCurrentPassword] = useState(false);
  const [showNewPassword, setShowNewPassword] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [isUploadingAvatar, setIsUploadingAvatar] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Notification settings
  const [emailNotifications, setEmailNotifications] = useState(true);
  const [pushNotifications, setPushNotifications] = useState(true);
  const [achievementNotifications, setAchievementNotifications] = useState(true);
  const [workflowUpdates, setWorkflowUpdates] = useState(true);

  const handleSaveName = async () => {
    if (name.trim() && name !== user?.name) {
      try {
        await updateUser({ name: name.trim() });
      } catch (error) {
        alert("Failed to update name");
        return;
      }
    }
    setIsEditingName(false);
  };

  const handleAvatarUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file || !user) return;

    // Validate file
    if (!file.type.startsWith("image/")) {
      alert("Please select an image file");
      return;
    }

    if (file.size > 5 * 1024 * 1024) {
      alert("File size must be less than 5MB");
      return;
    }

    setIsUploadingAvatar(true);
    try {
      const avatarUrl = await uploadAvatar(user.id, file);
      await updateUser({ avatarUrl });
    } catch (error) {
      console.error("Error uploading avatar:", error);
      alert("Failed to upload avatar");
    } finally {
      setIsUploadingAvatar(false);
    }
  };

  const handlePasswordChange = () => {
    if (newPassword !== confirmPassword) {
      alert("Passwords don't match");
      return;
    }
    if (newPassword.length < 8) {
      alert("Password must be at least 8 characters");
      return;
    }
    
    // Mock password change
    setIsSaving(true);
    setTimeout(() => {
      setIsSaving(false);
      setShowPasswordChange(false);
      setCurrentPassword("");
      setNewPassword("");
      setConfirmPassword("");
      alert("Password changed successfully!");
    }, 1000);
  };

  const getInitials = (name: string) => {
    return name
      .split(" ")
      .map((n) => n[0])
      .join("")
      .toUpperCase()
      .slice(0, 2);
  };

  return (
    <div className="container mx-auto px-4 py-8 max-w-4xl">
      <h1 className="text-3xl font-bold text-foreground mb-8">Profile Settings</h1>

      {/* Profile Card */}
      <Card className="mb-6">
        <CardHeader>
          <CardTitle>Account Information</CardTitle>
          <CardDescription>Manage your personal information</CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Avatar */}
          <div className="flex items-center gap-6">
            <div className="relative">
              {user?.avatarUrl ? (
                <img
                  src={user.avatarUrl}
                  alt={user.name}
                  className="size-24 rounded-full object-cover border-4 border-primary/20"
                />
              ) : (
                <div className="size-24 rounded-full bg-primary/20 border-4 border-primary/20 flex items-center justify-center text-primary font-bold text-3xl">
                  {user ? getInitials(user.name) : "?"}
                </div>
              )}
              <button
                className="absolute bottom-0 right-0 p-2 bg-primary text-primary-foreground rounded-full hover:bg-primary/90 transition-colors disabled:opacity-50"
                aria-label="Change profile picture"
                onClick={() => fileInputRef.current?.click()}
                disabled={isUploadingAvatar}
              >
                {isUploadingAvatar ? (
                  <Loader2 className="size-4 animate-spin" />
                ) : (
                  <Camera className="size-4" />
                )}
              </button>
              <input
                ref={fileInputRef}
                type="file"
                accept="image/*"
                onChange={handleAvatarUpload}
                className="hidden"
                aria-label="Upload profile picture"
              />
            </div>
            <div>
              <h3 className="text-lg font-semibold">{user?.name}</h3>
              <p className="text-muted-foreground">Member since {user?.createdAt.toLocaleDateString()}</p>
            </div>
          </div>

          {/* Name */}
          <div className="space-y-2">
            <label className="text-sm font-medium flex items-center gap-2">
              <User className="size-4" />
              Full Name
            </label>
            {isEditingName ? (
              <div className="flex gap-2">
                <input
                  type="text"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  placeholder="Enter your full name"
                  className="flex-1 px-3 py-2 rounded-lg border border-input bg-background focus:outline-none focus:ring-2 focus:ring-ring"
                />
                <Button onClick={handleSaveName}>Save</Button>
                <Button variant="ghost" onClick={() => setIsEditingName(false)}>Cancel</Button>
              </div>
            ) : (
              <div className="flex items-center gap-2">
                <p className="flex-1 px-3 py-2 rounded-lg bg-muted/30">{user?.name}</p>
                <Button variant="outline" onClick={() => {
                  setName(user?.name || "");
                  setIsEditingName(true);
                }}>
                  Edit
                </Button>
              </div>
            )}
          </div>

          {/* Email */}
          <div className="space-y-2">
            <label className="text-sm font-medium flex items-center gap-2">
              <Mail className="size-4" />
              Email Address
            </label>
            <div className="flex items-center gap-2">
              <p className="flex-1 px-3 py-2 rounded-lg bg-muted/30">{user?.email}</p>
              <Button variant="outline" disabled>Change</Button>
            </div>
            <p className="text-xs text-muted-foreground">Contact support to change your email address</p>
          </div>
        </CardContent>
      </Card>

      {/* Password Change */}
      <Card className="mb-6">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Lock className="size-5" />
            Change Password
          </CardTitle>
          <CardDescription>Update your password to keep your account secure</CardDescription>
        </CardHeader>
        <CardContent>
          {showPasswordChange ? (
            <div className="space-y-4">
              <div className="space-y-2">
                <label className="text-sm font-medium">Current Password</label>
                <div className="relative">
                  <input
                    type={showCurrentPassword ? "text" : "password"}
                    value={currentPassword}
                    onChange={(e) => setCurrentPassword(e.target.value)}
                    placeholder="Enter current password"
                    className="w-full px-3 py-2 pr-10 rounded-lg border border-input bg-background focus:outline-none focus:ring-2 focus:ring-ring"
                    aria-label="Current password"
                  />
                  <button
                    type="button"
                    onClick={() => setShowCurrentPassword(!showCurrentPassword)}
                    className="absolute right-2 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground"
                  >
                    {showCurrentPassword ? <EyeOff className="size-4" /> : <Eye className="size-4" />}
                  </button>
                </div>
              </div>
              <div className="space-y-2">
                <label className="text-sm font-medium">New Password</label>
                <div className="relative">
                  <input
                    type={showNewPassword ? "text" : "password"}
                    value={newPassword}
                    onChange={(e) => setNewPassword(e.target.value)}
                    placeholder="Enter new password"
                    className="w-full px-3 py-2 pr-10 rounded-lg border border-input bg-background focus:outline-none focus:ring-2 focus:ring-ring"
                    aria-label="New password"
                  />
                  <button
                    type="button"
                    onClick={() => setShowNewPassword(!showNewPassword)}
                    className="absolute right-2 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground"
                  >
                    {showNewPassword ? <EyeOff className="size-4" /> : <Eye className="size-4" />}
                  </button>
                </div>
              </div>
              <div className="space-y-2">
                <label className="text-sm font-medium">Confirm New Password</label>
                <input
                  type="password"
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  placeholder="Confirm new password"
                  className="w-full px-3 py-2 rounded-lg border border-input bg-background focus:outline-none focus:ring-2 focus:ring-ring"
                  aria-label="Confirm new password"
                />
              </div>
              <div className="flex gap-2">
                <Button onClick={handlePasswordChange} disabled={isSaving}>
                  <Save className="size-4 mr-2" />
                  {isSaving ? "Saving..." : "Update Password"}
                </Button>
                <Button variant="ghost" onClick={() => setShowPasswordChange(false)}>Cancel</Button>
              </div>
            </div>
          ) : (
            <Button variant="outline" onClick={() => setShowPasswordChange(true)}>
              <Lock className="size-4 mr-2" />
              Change Password
            </Button>
          )}
        </CardContent>
      </Card>

      {/* Notification Settings */}
      <Card className="mb-6">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Bell className="size-5" />
            Notification Preferences
          </CardTitle>
          <CardDescription>Choose how you want to be notified</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="font-medium">Email Notifications</p>
              <p className="text-sm text-muted-foreground">Receive notifications via email</p>
            </div>
            <button
              onClick={() => setEmailNotifications(!emailNotifications)}
              className={`relative w-12 h-6 rounded-full transition-colors ${
                emailNotifications ? "bg-primary" : "bg-muted"
              }`}
              aria-label={emailNotifications ? "Disable email notifications" : "Enable email notifications"}
              role="switch"
              aria-checked={emailNotifications ? "true" : "false"}
            >
              <span
                className={`absolute top-1 w-4 h-4 rounded-full bg-white transition-transform ${
                  emailNotifications ? "translate-x-7" : "translate-x-1"
                }`}
              />
            </button>
          </div>
          
          <div className="flex items-center justify-between">
            <div>
              <p className="font-medium">Push Notifications</p>
              <p className="text-sm text-muted-foreground">Receive push notifications in browser</p>
            </div>
            <button
              onClick={() => setPushNotifications(!pushNotifications)}
              className={`relative w-12 h-6 rounded-full transition-colors ${
                pushNotifications ? "bg-primary" : "bg-muted"
              }`}
              aria-label={pushNotifications ? "Disable push notifications" : "Enable push notifications"}
              role="switch"
              aria-checked={pushNotifications ? "true" : "false"}
            >
              <span
                className={`absolute top-1 w-4 h-4 rounded-full bg-white transition-transform ${
                  pushNotifications ? "translate-x-7" : "translate-x-1"
                }`}
              />
            </button>
          </div>

          <div className="flex items-center justify-between">
            <div>
              <p className="font-medium">Achievement Alerts</p>
              <p className="text-sm text-muted-foreground">Get notified when you earn badges</p>
            </div>
            <button
              onClick={() => setAchievementNotifications(!achievementNotifications)}
              className={`relative w-12 h-6 rounded-full transition-colors ${
                achievementNotifications ? "bg-primary" : "bg-muted"
              }`}
              aria-label={achievementNotifications ? "Disable achievement notifications" : "Enable achievement notifications"}
              role="switch"
              aria-checked={achievementNotifications ? "true" : "false"}
            >
              <span
                className={`absolute top-1 w-4 h-4 rounded-full bg-white transition-transform ${
                  achievementNotifications ? "translate-x-7" : "translate-x-1"
                }`}
              />
            </button>
          </div>

          <div className="flex items-center justify-between">
            <div>
              <p className="font-medium">Workflow Updates</p>
              <p className="text-sm text-muted-foreground">Get notified about workflow changes</p>
            </div>
            <button
              onClick={() => setWorkflowUpdates(!workflowUpdates)}
              className={`relative w-12 h-6 rounded-full transition-colors ${
                workflowUpdates ? "bg-primary" : "bg-muted"
              }`}
              aria-label={workflowUpdates ? "Disable workflow updates" : "Enable workflow updates"}
              role="switch"
              aria-checked={workflowUpdates ? "true" : "false"}
            >
              <span
                className={`absolute top-1 w-4 h-4 rounded-full bg-white transition-transform ${
                  workflowUpdates ? "translate-x-7" : "translate-x-1"
                }`}
              />
            </button>
          </div>
        </CardContent>
      </Card>

      {/* Stats */}
      <Card className="mb-6">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Award className="size-5" />
            Your Stats
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="p-4 rounded-lg bg-primary/10 text-center">
              <Zap className="size-6 text-primary mx-auto mb-2" />
              <p className="text-2xl font-bold">{user?.streak}</p>
              <p className="text-xs text-muted-foreground">Day Streak</p>
            </div>
            <div className="p-4 rounded-lg bg-gold/10 text-center">
              <Sparkles className="size-6 text-gold mx-auto mb-2" />
              <p className="text-2xl font-bold">{user?.xp.toLocaleString()}</p>
              <p className="text-xs text-muted-foreground">Total XP</p>
            </div>
            <div className="p-4 rounded-lg bg-accent/10 text-center">
              <BookOpen className="size-6 text-accent mx-auto mb-2" />
              <p className="text-2xl font-bold">12</p>
              <p className="text-xs text-muted-foreground">Courses</p>
            </div>
            <div className="p-4 rounded-lg bg-secondary text-center">
              <Award className="size-6 mx-auto mb-2" />
              <p className="text-2xl font-bold">5</p>
              <p className="text-xs text-muted-foreground">Badges</p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Danger Zone */}
      <Card className="border-destructive/20">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-destructive">
            <Shield className="size-5" />
            Danger Zone
          </CardTitle>
          <CardDescription>Irreversible actions for your account</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-between">
            <div>
              <p className="font-medium">Delete Account</p>
              <p className="text-sm text-muted-foreground">Permanently delete your account and all data</p>
            </div>
            <Button 
              variant="destructive"
              onClick={() => {
                if (confirm("Are you sure you want to delete your account? This action cannot be undone.")) {
                  // Handle account deletion
                  alert("Account deletion is not implemented yet.");
                }
              }}
            >
              <Trash2 className="size-4 mr-2" />
              Delete Account
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
