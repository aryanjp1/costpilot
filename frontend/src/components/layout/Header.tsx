import { LogOut } from "lucide-react";
import { logout, useCurrentUser } from "@/hooks/useAuth";
import { Button } from "@/components/ui";
import { ProjectSwitcher } from "./ProjectSwitcher";

export function Header() {
  const { data: user } = useCurrentUser();

  return (
    <header className="flex h-14 items-center justify-between border-b border-slate-200 bg-white px-6">
      <ProjectSwitcher />
      <div className="flex items-center gap-4">
        {user && (
          <span className="text-sm text-slate-600">{user.email}</span>
        )}
        <Button variant="ghost" size="sm" onClick={logout}>
          <LogOut className="h-4 w-4" /> Sign out
        </Button>
      </div>
    </header>
  );
}
