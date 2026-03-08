import { Outlet } from "react-router";
import { AppNav } from "@/src/components/AppNav";

export function AppLayout() {
  return (
    <>
      <AppNav />
      <main>
        <Outlet />
      </main>
    </>
  );
}
