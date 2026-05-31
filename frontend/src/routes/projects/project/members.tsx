import { useState } from "react";
import { useProjectId } from "@/hooks/useProjectId";
import { Trash2, UserPlus } from "lucide-react";
import { Badge, Button, Card, Input, Select } from "@/components/ui";
import { Loading, PageHeader } from "@/components/common";
import { PeriodSelector } from "@/components/dashboard/PeriodSelector";
import { MemberBreakdown } from "@/components/dashboard/MemberBreakdown";
import { apiError } from "@/lib/api";
import { useMemberBreakdown } from "@/hooks/useAnalytics";
import {
  useInviteMember,
  useMembers,
  useRemoveMember,
} from "@/hooks/useProjects";
import type { Period } from "@/types";

export function MembersPage() {
  const projectId = useProjectId();
  const [period, setPeriod] = useState<Period>("7d");
  const [email, setEmail] = useState("");
  const [role, setRole] = useState("member");

  const members = useMembers(projectId);
  const breakdown = useMemberBreakdown(projectId, period);
  const invite = useInviteMember(projectId);
  const remove = useRemoveMember(projectId);

  const onInvite = async (e: React.FormEvent) => {
    e.preventDefault();
    await invite.mutateAsync({ email, role });
    setEmail("");
  };

  return (
    <div className="space-y-6">
      <PageHeader title="Members">
        <PeriodSelector value={period} onChange={setPeriod} />
      </PageHeader>

      {breakdown.data && <MemberBreakdown data={breakdown.data} />}

      <Card>
        <h3 className="mb-4 text-sm font-semibold text-slate-700">
          Invite a member
        </h3>
        <form onSubmit={onInvite} className="flex flex-wrap items-end gap-3">
          <div className="flex-1">
            <Input
              type="email"
              placeholder="teammate@example.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
          </div>
          <Select
            value={role}
            onChange={(e) => setRole(e.target.value)}
            className="w-32"
          >
            <option value="member">Member</option>
            <option value="admin">Admin</option>
          </Select>
          <Button type="submit" disabled={invite.isPending}>
            <UserPlus className="h-4 w-4" /> Invite
          </Button>
        </form>
        {invite.isError && (
          <p className="mt-2 text-sm text-red-600">{apiError(invite.error)}</p>
        )}
      </Card>

      <Card>
        <h3 className="mb-2 text-sm font-semibold text-slate-700">Team</h3>
        {members.isLoading || !members.data ? (
          <Loading />
        ) : (
          <div className="divide-y divide-slate-100">
            {members.data.map((member) => (
              <div
                key={member.id}
                className="flex items-center justify-between py-3"
              >
                <div>
                  <p className="font-medium text-slate-800">
                    {member.full_name ?? member.email}
                  </p>
                  <p className="text-xs text-slate-400">{member.email}</p>
                </div>
                <div className="flex items-center gap-3">
                  <Badge color={member.role === "owner" ? "indigo" : "slate"}>
                    {member.role}
                  </Badge>
                  {member.role !== "owner" && (
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => remove.mutate(member.id)}
                    >
                      <Trash2 className="h-4 w-4 text-red-500" />
                    </Button>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </Card>
    </div>
  );
}
