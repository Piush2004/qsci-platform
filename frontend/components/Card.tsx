/** The one card surface used throughout the app -- replaces the repeated
 * `rounded-lg border border-border bg-surface p-4/p-5` markup that was
 * previously duplicated in WhyPanel, DecisionChain, and every page. */
export function Card({
  children,
  className = "",
  padded = true,
}: {
  children: React.ReactNode;
  className?: string;
  padded?: boolean;
}) {
  return (
    <div className={`rounded-lg border border-border bg-surface ${padded ? "p-5" : ""} ${className}`}>
      {children}
    </div>
  );
}
