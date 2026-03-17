interface YesNoToggleProps {
  value: "yes" | "no" | null;
  onChange: (value: "yes" | "no") => void;
}

export function YesNoToggle({ value, onChange }: YesNoToggleProps) {
  return (
    <div className="flex gap-3">
      {(["yes", "no"] as const).map((opt) => (
        <button
          key={opt}
          data-selected={opt === value ? true : undefined}
          onClick={() => onChange(opt)}
          className={`
            px-8 py-3 rounded-full border text-sm font-medium capitalize transition-colors
            ${opt === value
              ? "border-[--color-accent] bg-[--color-accent] text-white"
              : "border-[--color-border] bg-white text-[--color-text] hover:border-[--color-accent]"
            }
          `}
        >
          {opt === "yes" ? "Yes" : "No"}
        </button>
      ))}
    </div>
  );
}
