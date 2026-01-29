import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import "./index.css";
import { App } from "./App";
import { GlobalErrorBoundary } from "./components/GlobalErrorBoundary";
import { ConsoleLogger } from "./components/ConsoleLogger";

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    {/* <>skjagdajgdajsgd</> */}
    <GlobalErrorBoundary>
      <ConsoleLogger />
      <App />
    </GlobalErrorBoundary>
  </StrictMode>,
);
