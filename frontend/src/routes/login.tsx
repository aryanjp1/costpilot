import { useState } from "react";
import { Link, useNavigate } from "@tanstack/react-router";
import { Button, Card, Input, Label } from "@/components/ui";
import { apiError } from "@/lib/api";
import { useLogin } from "@/hooks/useAuth";

export function LoginPage() {
  const navigate = useNavigate();
  const login = useLogin();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const onSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    await login.mutateAsync({ email, password });
    navigate({ to: "/projects" });
  };

  return (
    <div className="flex min-h-screen items-center justify-center p-4">
      <Card className="w-full max-w-sm">
        <div className="mb-6 text-center">
          <h1 className="text-2xl font-bold">💰 CostPilot</h1>
          <p className="mt-1 text-sm text-slate-500">
            Sign in to your dashboard
          </p>
        </div>
        <form onSubmit={onSubmit} className="space-y-4">
          <div>
            <Label>Email</Label>
            <Input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
          </div>
          <div>
            <Label>Password</Label>
            <Input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </div>
          {login.isError && (
            <p className="text-sm text-red-600">{apiError(login.error)}</p>
          )}
          <Button type="submit" className="w-full" disabled={login.isPending}>
            Sign in
          </Button>
        </form>
        <p className="mt-4 text-center text-sm text-slate-500">
          No account?{" "}
          <Link to="/register" className="font-medium text-indigo-600">
            Create one
          </Link>
        </p>
      </Card>
    </div>
  );
}
