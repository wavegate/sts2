import "./App.css";
import { Routes, Route, Navigate } from "react-router";
import { Toaster } from "@/components/ui/sonner";
import CardsPage from "@/src/pages/Cards";

function App() {
  return (
    <>
      <Toaster />
      <Routes>
        <Route path="/" element={<Navigate to="/cards" replace />} />
        <Route path="/cards" element={<CardsPage />} />
      </Routes>
    </>
  );
}

export default App;
