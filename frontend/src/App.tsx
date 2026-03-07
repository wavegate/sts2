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
      <Button onClick={() => mutate()} disabled={isPending}>
        {isPending ? "Pinging..." : "Ping API"}
      </Button>
    </>
  );
}

export default App;
