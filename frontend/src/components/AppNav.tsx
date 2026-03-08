import { NavLink } from "react-router";
import { cn } from "@/lib/utils";

const navItems = [
  { to: "/runs", label: "Home" },
  { to: "/cards", label: "Cards" },
  { to: "/runs", label: "Runs" },
] as const;

export function AppNav() {
  return (
    <nav className="border-b border-border bg-background">
      <div className="container mx-auto flex h-12 items-center gap-6 px-4">
        {navItems.map(({ to, label }) => (
          <NavLink
            key={to + label}
            to={to}
            end={to === "/runs" && label === "Home"}
            className={({ isActive }) =>
              cn(
                "text-sm font-medium transition-colors hover:text-foreground",
                isActive ? "text-foreground" : "text-muted-foreground"
              )
            }
          >
            {label}
          </NavLink>
        ))}
      </div>
    </nav>
  );
}
