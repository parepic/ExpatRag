import { Button } from "@/components/ui/button";

type ChipSelectProps = {
  options: readonly string[];
  value: string | null;
  onChange: (value: string) => void;
};

export function ChipSelect({
  options,
  value,
  onChange,
}: ChipSelectProps) {
  return (
    <div className="flex flex-wrap gap-3">
      {options.map((option) => {
        const isSelected = option === value;

        return (
          <Button
            key={option}
            type="button"
            variant={isSelected ? "default" : "outline"}
            size="sm"
            onClick={() => onChange(option)}
            className="rounded-full px-4"
          >
            {option}
          </Button>
        );
      })}
    </div>
  );
}
