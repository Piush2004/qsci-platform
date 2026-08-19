/** Every page in the app shell uses this for its title block instead of a
 * hand-rolled <header> -- keeps title/description typography identical
 * across /dashboard, /demand, /inventory, /research, and every future page. */
export function PageHeader({
  title,
  description,
  action,
}: {
  title: string;
  description?: string;
  action?: React.ReactNode;
}) {
  return (
    <header className="motion-rise-in mb-6 flex flex-wrap items-start justify-between gap-4">
      <div>
        <h1 className="text-h1">{title}</h1>
        {description && <p className="mt-1 text-supporting">{description}</p>}
      </div>
      {action}
    </header>
  );
}
