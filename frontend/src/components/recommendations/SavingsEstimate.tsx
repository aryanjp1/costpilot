import { Badge } from "@/components/ui";
import { formatCurrency } from "@/lib/utils";

export function SavingsEstimate({ amount }: { amount: number }) {
  if (amount <= 0) return null;
  return (
    <Badge color="green">~{formatCurrency(amount)}/mo saved</Badge>
  );
}
