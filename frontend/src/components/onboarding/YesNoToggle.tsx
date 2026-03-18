import { Button } from "@/components/ui/button";

interface YesNoToggleProps {
  value: "yes" | "no" | null;
  onChange: (value: "yes" | "no") => void;
}

export function YesNoToggle({ value, onChange }: YesNoToggleProps) {
  return (
    <div className="flex gap-3">
      {(["yes", "no"] as const).map((opt) => (
        <Button
          key={opt}
          type="button"
          variant={opt === value ? "default" : "outline"}
          data-selected={opt === value ? true : undefined}
          onClick={() => onChange(opt)}
          className="rounded-full px-8 capitalize"
        >
          {opt === "yes" ? "Yes" : "No"}
        </Button>
      ))}
    </div>
  );
}
