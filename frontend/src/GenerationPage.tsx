import React, { useEffect, useState } from "react";
import { api } from "./api";
import { useNavigate } from "react-router-dom";
import {
  Sparkles,
  Cpu,
  Search,
  Layers,
  ShieldCheck,
  AlertTriangle,
} from "lucide-react";
import clsx from "clsx";

import { useLifecycleLogger } from "./hooks/useLifecycleLogger";

export const GenerationPage: React.FC = () => {
  useLifecycleLogger("GenerationPage");
  const navigate = useNavigate();
  const [status, setStatus] = useState("Initializing Engine...");
  const [progress, setProgress] = useState(0);
  const [error, setError] = useState<string | null>(null);

  const hasStarted = React.useRef(false);

  useEffect(() => {
    if (hasStarted.current) return;
    hasStarted.current = true;

    const run = async () => {
      const pid = localStorage.getItem("current_project_id");
      if (!pid) {
        navigate("/");
        return;
      }

      try {
        setError(null);
        setStatus("Analyzing Market Data...");
        setProgress(15);

        setStatus("Synthesizing Personas (AI)...");
        setProgress(40);
        const result = await api.triggerGeneration(pid);

        // If the result has blocking errors but technically 'succeeded' in the API sense
        if (result.status === "FAILED") {
          throw new Error(
            result.blocking_errors.join(", ") ||
              "Generation failed at orchestrator level.",
          );
        }

        setStatus("Optimizing Cluster Strategies...");
        setProgress(75);

        setStatus("Drafting Strategy Playbook...");
        setProgress(95);

        setProgress(100);
        setTimeout(() => {
          navigate("/results", { state: { runResult: result } });
        }, 300);
      } catch (e: any) {
        console.error(e);
        const msg = e.response?.data?.detail
          ? typeof e.response.data.detail === "string"
            ? e.response.data.detail
            : JSON.stringify(e.response.data.detail)
          : e.message;
        setError(msg || "Generation Failed. Check backend connection.");
        setStatus("Engine Halted");
      }
    };

    run();
  }, []);

  return (
    <div className="min-h-screen bg-slate-900 flex flex-col items-center justify-center p-6 text-white text-center relative overflow-hidden">
      {/* Immersive Background */}
      <div className="absolute top-[-20%] left-[-10%] w-[60%] h-[60%] bg-indigo-600/10 rounded-full blur-[150px] animate-pulse" />
      <div
        className="absolute bottom-[-20%] right-[-10%] w-[60%] h-[60%] bg-purple-600/10 rounded-full blur-[150px] animate-pulse"
        style={{ animationDelay: "2s" }}
      />

      <div className="relative z-10 max-w-lg w-full scale-110">
        <div className="mb-10 relative inline-flex items-center justify-center">
          <div className="absolute inset-0 bg-indigo-500/20 blur-3xl animate-pulse rounded-full" />
          <div className="relative bg-slate-800 p-6 rounded-[2.5rem] border border-slate-700 shadow-2xl">
            <Cpu
              size={48}
              className={clsx("text-indigo-400", !error && "animate-pulse")}
            />
          </div>
        </div>

        <h2 className="text-4xl font-black mb-4 tracking-tight leading-tight">
          Architecting Your <br />
          <span className="text-indigo-400">Targeting Blueprint</span>
        </h2>

        {error ? (
          <div className="mt-8 animate-in fade-in zoom-in duration-300">
            <div className="bg-red-500/10 border border-red-500/30 rounded-2xl p-6 mb-8 text-left">
              <h3 className="text-red-400 font-bold mb-2 flex items-center gap-2 text-sm uppercase tracking-widest">
                <AlertTriangle size={18} /> Engine Error Detected
              </h3>
              <p className="text-slate-300 text-sm font-mono break-words leading-relaxed">
                {error}
              </p>
            </div>
            <button
              onClick={() => navigate("/")}
              className="w-full py-4 bg-white text-slate-900 font-black rounded-xl hover:bg-slate-200 transition-all active:scale-95 shadow-xl"
            >
              BACK TO INPUTS
            </button>
          </div>
        ) : (
          <>
            <p className="text-slate-400 text-lg font-medium tracking-wide mb-12 h-8">
              {status}
            </p>

            {/* Custom Progress Bar */}
            <div className="w-full bg-slate-800/50 h-2.5 rounded-full overflow-hidden border border-slate-700 p-0.5">
              <div
                className="h-full bg-gradient-to-r from-indigo-500 to-purple-500 rounded-full transition-all duration-1000 ease-out shadow-[0_0_20px_rgba(99,102,241,0.5)]"
                style={{ width: `${progress}%` }}
              />
            </div>
          </>
        )}

        {/* Feature Icons Grid */}
        <div className="grid grid-cols-4 gap-4 mt-16 opacity-30 group">
          <StatusIcon icon={Search} label="Search" active={progress > 20} />
          <StatusIcon icon={Layers} label="Clusters" active={progress > 50} />
          <StatusIcon
            icon={ShieldCheck}
            label="Validate"
            active={progress > 80}
          />
          <StatusIcon
            icon={Sparkles}
            label="Complete"
            active={progress === 100}
          />
        </div>
      </div>
    </div>
  );
};

const StatusIcon = ({ icon: Icon, label, active }: any) => (
  <div
    className={`flex flex-col items-center gap-2 transition-all duration-700 ${active ? "opacity-100 scale-110 text-indigo-400 font-bold" : "opacity-40 grayscale"}`}
  >
    <div
      className={`p-3 rounded-2xl border ${active ? "border-indigo-500/50 bg-indigo-500/10" : "border-slate-700"}`}
    >
      <Icon size={20} />
    </div>
    <span className="text-[10px] uppercase tracking-widest">{label}</span>
  </div>
);
