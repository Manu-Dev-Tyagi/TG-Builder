import { useEffect, useRef } from "react";

export function useLifecycleLogger(componentName: string) {
  const mountTime = useRef(Date.now());

  useEffect(() => {
    console.group(`📌 [MOUNT] ${componentName}`);
    console.log(`Time: ${new Date().toLocaleTimeString()}`);
    console.groupEnd();

    return () => {
      const duration = Date.now() - mountTime.current;
      console.log("duration", duration);
      console.group(`🗑️ [UNMOUNT] ${componentName}`);
      console.log(`Duration active: ${duration}ms`);
      console.groupEnd();
    };
  }, [componentName]);

  const logEvent = (eventName: string, data?: any) => {
    console.group(`⚡ [EVENT] ${componentName} : ${eventName}`);
    if (data) console.log("Data:", data);
    console.groupEnd();
  };

  return { logEvent };
}
