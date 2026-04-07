export default function Home() {
  return (
    <main className="flex min-h-screen items-center justify-center px-6 py-16">
      <div className="w-full max-w-2xl rounded-3xl border border-border bg-card p-10 shadow-sm">
        <p className="text-sm font-medium uppercase tracking-[0.24em] text-muted-foreground">
          Patty Frontend v2
        </p>
        <h1 className="mt-4 text-4xl font-semibold tracking-tight text-foreground">
          Fresh frontend scaffold in place.
        </h1>
        <p className="mt-4 max-w-xl text-base leading-7 text-muted-foreground">
          This starter page replaces the default Vercel intro so the project now
          has an app-specific baseline while we build out the real routes and UI.
        </p>
      </div>
    </main>
  );
}
