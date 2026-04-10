type ProgressDotsProps = {
  total: number;
  current: number;
};

export function ProgressDots({ total, current }: ProgressDotsProps) {
  return (
    <div className="flex justify-center gap-2">
      {Array.from({ length: total }).map((_, index) => {
        const filled = index < current;

        return (
          <span
            key={index}
            className={filled ? "h-2 w-2 rounded-full bg-primary" : "h-2 w-2 rounded-full bg-border"}
            role="presentation"
          />
        );
      })}
    </div>
  );
}
