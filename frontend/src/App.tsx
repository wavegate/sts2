import "./App.css";
import { useMutation } from "@tanstack/react-query";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import { Toaster } from "@/components/ui/sonner";
import { fetchHello } from "./services/helloService";

function App() {
  const { mutate, isPending } = useMutation({
    mutationFn: fetchHello,
    onSuccess: (data) => toast.success(JSON.stringify(data)),
    onError: () => toast.error("Failed to reach backend"),
  });

  return (
    <>
      <Toaster />
      <div className="flex h-screen items-center justify-center">
        <Button size="lg" className="h-16 px-12 text-xl" onClick={() => mutate()} disabled={isPending}>
          {isPending ? "Pinging..." : "Ping API"}
        </Button>
      </div>
    </>
  );
}

export default App;
