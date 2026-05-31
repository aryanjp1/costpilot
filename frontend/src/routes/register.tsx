import { useState } from "react";
import { Link, useNavigate } from "@tanstack/react-router";
import { Button, Card, Input, Label } from "@/components/ui";
import { apiError } from "@/lib/api";
import { useLogin, useRegister } from "@/hooks/useAuth";

export function RegisterPage() {
  const navigate = useNavigate();
  const register = useRegister();
  const login = useLogin();
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const onSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    await register.mutateAsync({
      email,
      password,
      full_name: fullName || undefined,
    });
    await login.mutateAsync({ email, password });
    navigate({ to: "/projects" });
  };

  const error = register.error ?? login.error;

  return (
    <div className="flex min-h-screen items-center justify-center p-4">
      <Card className="w-full max-w-sm">
        <div className="mb-6 text-center">
          <h1 className="text-2xl font-bold">💰 CostPilot</h1>
          <p className="mt-1 text-sm text-slate-500">Create your account</p>
        </div>
        <form onSubmit={onSubmit} className="space-y-4">
          <div>
            <Label>Full name</Label>
            <Input
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
            />
          </div>
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
              minLength={8}
              required
            />
            <p className="mt-1 text-xs text-slate-400">At least 8 characters.</p>
          </div>
          {error && <p className="text-sm text-red-600">{apiError(error)}</p>}
          <Button
            type="submit"
            className="w-full"
            disabled={register.isPending || login.isPending}
          >
            Create account
          </Button>
        </form>
        <p className="mt-4 text-center text-sm text-slate-500">
          Already have an account?{" "}
          <Link to="/login" className="font-medium text-indigo-600">
            Sign in
          </Link>
        </p>
      </Card>
    </div>
  );
}
