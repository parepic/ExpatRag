import { Button } from "@/components/ui/button";

type YesNoToggleProps = {
  value: boolean | null;
  onChange: (value: boolean) => void;
};

export function YesNoToggle({ value, onChange }: YesNoToggleProps) {
  return (
    <div className="grid grid-cols-2 gap-3">
      <Button
        type="button"
        variant={value === true ? "default" : "outline"}
        size="default"
        className="rounded-full"
        onClick={() => onChange(true)}
      >
        Yes
      </Button>
      <Button
        type="button"
        variant={value === false ? "default" : "outline"}
        size="default"
        className="rounded-full"
        onClick={() => onChange(false)}
      >
        No
      </Button>
    </div>
  );
}
