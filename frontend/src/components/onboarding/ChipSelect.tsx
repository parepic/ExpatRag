interface ChipSelectProps {
  options: readonly string[];
  value: string | null;
  onChange: (value: string) => void;
}

export function ChipSelect({ options, value, onChange }: ChipSelectProps) {
  return (
    <div className="flex flex-wrap gap-2">
      {options.map((option) => (
        <button
          key={option}
          data-selected={option === value ? true : undefined}
          onClick={() => onChange(option)}
          className={`
            px-4 py-2 rounded-full border text-sm font-medium transition-colors
            ${option === value
              ? "border-[--color-accent] bg-[--color-accent] text-white"
              : "border-[--color-border] bg-white text-[--color-text] hover:border-[--color-accent]"
            }
          `}
        >
          {option}
        </button>
      ))}
    </div>
  );
}
