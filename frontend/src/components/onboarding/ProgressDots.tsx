interface ProgressDotsProps {
  total: number;
  current: number; // number of completed steps
}

export function ProgressDots({ total, current }: ProgressDotsProps) {
  return (
    <div className="flex gap-2 justify-center">
      {Array.from({ length: total }).map((_, i) => (
        <span
          key={i}
          role="presentation"
          data-filled={i < current ? "true" : "false"}
          className={`
            w-2 h-2 rounded-full transition-colors
            ${i < current ? "bg-primary" : "bg-border"}
          `}
        />
      ))}
    </div>
  );
}
