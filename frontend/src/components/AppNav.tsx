import { NavLink } from "react-router";
import { Show, SignInButton, SignUpButton, UserButton } from "@clerk/react";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";

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
        <div className="ml-auto flex items-center gap-2">
          <Show when="signed-out">
            <SignInButton mode="modal">
              <Button variant="ghost" size="sm">
                Sign in
              </Button>
            </SignInButton>
            <SignUpButton mode="modal">
              <Button size="sm">
                Sign up
              </Button>
            </SignUpButton>
          </Show>
          <Show when="signed-in">
            <UserButton
              appearance={{
                elements: {
                  avatarBox: "h-8 w-8",
                },
              }}
            />
          </Show>
        </div>
      </div>
    </nav>
  );
}
