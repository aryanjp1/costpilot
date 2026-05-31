import {
  createRootRoute,
  createRoute,
  createRouter,
  redirect,
} from "@tanstack/react-router";
import { isAuthenticated } from "@/lib/auth";
import { AppLayout } from "@/components/layout/AppLayout";
import { LoginPage } from "@/routes/login";
import { RegisterPage } from "@/routes/register";
import { ProjectsPage } from "@/routes/projects/index";
import { NewProjectPage } from "@/routes/projects/new";
import { ProjectDashboard } from "@/routes/projects/project/index";
import { ModelsPage } from "@/routes/projects/project/models";
import { FeaturesPage } from "@/routes/projects/project/features";
import { MembersPage } from "@/routes/projects/project/members";
import { BudgetsPage } from "@/routes/projects/project/budgets";
import { AlertsPage } from "@/routes/projects/project/alerts";
import { RecommendationsPage } from "@/routes/projects/project/recommendations";
import { LogsPage } from "@/routes/projects/project/logs";
import { SettingsPage } from "@/routes/projects/project/settings";

const rootRoute = createRootRoute();

function requireAuth() {
  if (!isAuthenticated()) {
    throw redirect({ to: "/login" });
  }
}

const loginRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: "/login",
  component: LoginPage,
});

const registerRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: "/register",
  component: RegisterPage,
});

const indexRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: "/",
  beforeLoad: () => {
    throw redirect({ to: isAuthenticated() ? "/projects" : "/login" });
  },
});

const appRoute = createRoute({
  getParentRoute: () => rootRoute,
  id: "app",
  beforeLoad: requireAuth,
  component: AppLayout,
});

const projectsRoute = createRoute({
  getParentRoute: () => appRoute,
  path: "/projects",
  component: ProjectsPage,
});

const newProjectRoute = createRoute({
  getParentRoute: () => appRoute,
  path: "/projects/new",
  component: NewProjectPage,
});

const projectRoute = createRoute({
  getParentRoute: () => appRoute,
  path: "/projects/$projectId",
  component: ProjectDashboard,
});

function projectChild(path: string, component: () => JSX.Element) {
  return createRoute({
    getParentRoute: () => appRoute,
    path: `/projects/$projectId/${path}`,
    component,
  });
}

const modelsRoute = projectChild("models", ModelsPage);
const featuresRoute = projectChild("features", FeaturesPage);
const membersRoute = projectChild("members", MembersPage);
const budgetsRoute = projectChild("budgets", BudgetsPage);
const alertsRoute = projectChild("alerts", AlertsPage);
const recommendationsRoute = projectChild(
  "recommendations",
  RecommendationsPage,
);
const logsRoute = projectChild("logs", LogsPage);
const settingsRoute = projectChild("settings", SettingsPage);

const routeTree = rootRoute.addChildren([
  loginRoute,
  registerRoute,
  indexRoute,
  appRoute.addChildren([
    projectsRoute,
    newProjectRoute,
    projectRoute,
    modelsRoute,
    featuresRoute,
    membersRoute,
    budgetsRoute,
    alertsRoute,
    recommendationsRoute,
    logsRoute,
    settingsRoute,
  ]),
]);

export const router = createRouter({ routeTree });

declare module "@tanstack/react-router" {
  interface Register {
    router: typeof router;
  }
}
