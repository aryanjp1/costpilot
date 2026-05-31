import { Link, useParams } from "@tanstack/react-router";
import {
  AlertTriangle,
  BarChart3,
  FolderKanban,
  Gauge,
  Lightbulb,
  ListOrdered,
  Settings,
  Tags,
  Users,
  Wallet,
} from "lucide-react";
import { cn } from "@/lib/utils";

const projectLinks = [
  { to: "/projects/$projectId", label: "Overview", icon: Gauge, exact: true },
  { to: "/projects/$projectId/models", label: "Models", icon: BarChart3 },
  { to: "/projects/$projectId/features", label: "Features", icon: Tags },
  { to: "/projects/$projectId/members", label: "Members", icon: Users },
  { to: "/projects/$projectId/budgets", label: "Budgets", icon: Wallet },
  { to: "/projects/$projectId/alerts", label: "Alerts", icon: AlertTriangle },
  {
    to: "/projects/$projectId/recommendations",
    label: "Recommendations",
    icon: Lightbulb,
  },
  { to: "/projects/$projectId/logs", label: "Logs", icon: ListOrdered },
  { to: "/projects/$projectId/settings", label: "Settings", icon: Settings },
];

export function Sidebar() {
  const params = useParams({ strict: false }) as { projectId?: string };
  const projectId = params.projectId;

  return (
    <aside className="flex w-60 flex-col border-r border-slate-200 bg-white">
      <div className="flex h-14 items-center gap-2 border-b border-slate-200 px-5 text-lg font-bold">
        <span>💰</span> CostPilot
      </div>
      <nav className="flex-1 space-y-1 p-3">
        <Link
          to="/projects"
          className="flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium text-slate-600 hover:bg-slate-100"
        >
          <FolderKanban className="h-4 w-4" /> All Projects
        </Link>

        {projectId && (
          <div className="pt-2">
            <p className="px-3 pb-1 text-xs font-semibold uppercase text-slate-400">
              Project
            </p>
            {projectLinks.map((link) => {
              const Icon = link.icon;
              return (
                <Link
                  key={link.label}
                  to={link.to}
                  params={{ projectId }}
                  activeOptions={{ exact: link.exact ?? false }}
                  className="flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium text-slate-600 hover:bg-slate-100"
                  activeProps={{
                    className: cn("bg-indigo-50 text-indigo-700"),
                  }}
                >
                  <Icon className="h-4 w-4" /> {link.label}
                </Link>
              );
            })}
          </div>
        )}
      </nav>
    </aside>
  );
}
