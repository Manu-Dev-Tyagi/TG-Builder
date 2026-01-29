import { useEffect } from "react";

export const ConsoleLogger = () => {
  useEffect(() => {
    const handleError = (event: ErrorEvent) => {
      console.group("⚠️ [GLOBAL ERROR CAUGHT]");
      console.error("Message:", event.message);
      console.error("Source:", event.filename);
      console.error("Line:", event.lineno, "Col:", event.colno);
      console.error("Error Object:", event.error);
      console.groupEnd();
    };

    const handleRejection = (event: PromiseRejectionEvent) => {
      console.group("⚠️ [UNHANDLED PROMISE REJECTION]");
      console.error("Reason:", event.reason);
      console.groupEnd();
    };

    window.addEventListener("error", handleError);
    window.addEventListener("unhandledrejection", handleRejection);

    return () => {
      window.removeEventListener("error", handleError);
      window.removeEventListener("unhandledrejection", handleRejection);
    };
  }, []);

  return null;
};
