import { Button } from "@/components/ui/button";

interface ChipSelectProps {
  options: readonly string[];
  value: string | null;
  onChange: (value: string) => void;
}

export function ChipSelect({ options, value, onChange }: ChipSelectProps) {
  return (
    <div className="flex flex-wrap gap-2">
      {options.map((option) => (
        <Button
          key={option}
          type="button"
          variant={option === value ? "default" : "outline"}
          size="sm"
          data-selected={option === value ? true : undefined}
          onClick={() => onChange(option)}
          className="rounded-full px-4"
        >
          {option}
        </Button>
      ))}
    </div>
  );
}
