import React from "react";
import { AlertTriangle } from "lucide-react";

interface FunnelChartProps {
  tof: number;
  mof: number;
  bof: number;
  isSuppressed?: boolean;
}

export function FunnelChart({
  tof,
  mof,
  bof,
  isSuppressed = false,
}: FunnelChartProps) {
  const total = tof + mof + bof || 1; // Prevent division by zero

  const stages = [
    {
      label: "TOF",
      fullLabel: "Awareness & Discovery",
      description: "Driving reach and brand recall among new audiences.",
      value: tof,
      percent: (tof / total) * 100,
      color: isSuppressed ? "bg-slate-300" : "bg-blue-500",
      suppressed: isSuppressed && tof === 0,
    },
    {
      label: "MOF",
      fullLabel: "Consideration & Intent",
      description: "Engaging prospects who are actively researching solutions.",
      value: mof,
      percent: (mof / total) * 100,
      color: "bg-indigo-500",
      suppressed: false,
    },
    {
      label: "BOF",
      fullLabel: "Conversion & Action",
      description: "Capturing high-intent users ready to purchase/sign up.",
      value: bof,
      percent: (bof / total) * 100,
      color: "bg-purple-500",
      suppressed: false,
    },
  ];

  return (
    <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-sm font-bold text-slate-400 uppercase tracking-widest">
          Funnel Budget Distribution
        </h3>
        <span className="text-[10px] font-bold text-indigo-500 bg-indigo-50 px-2 py-1 rounded-md">
          ALGORITHMIC STRATEGY
        </span>
      </div>

      {/* Warning if TOF suppressed */}
      {isSuppressed && (
        <div className="mb-4 p-3 bg-amber-50 border border-amber-200 rounded-xl flex items-start gap-2">
          <AlertTriangle
            size={16}
            className="text-amber-600 flex-shrink-0 mt-0.5"
          />
          <p className="text-xs text-amber-700">
            <strong>TOF Suppressed:</strong> Budget reallocated to MOF/BOF to
            prioritize immediate ROAS for Growth Jockey objectives.
          </p>
        </div>
      )}

      {/* Visual Bar */}
      <div className="h-12 rounded-xl overflow-hidden flex bg-slate-100 mb-6">
        {stages.map((stage) => (
          <div
            key={stage.label}
            className={`
              ${stage.color} 
              transition-all duration-700 ease-out 
              flex items-center justify-center
              ${stage.percent > 0 ? "min-w-[60px]" : ""}
            `}
            style={{ width: `${stage.percent}%` }}
          >
            {stage.percent > 10 && (
              <span className="text-white text-xs font-bold">
                {stage.label}
              </span>
            )}
          </div>
        ))}
      </div>

      {/* Legend */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {stages.map((stage) => (
          <div
            key={stage.label}
            className={`
              text-left p-4 rounded-xl border transition-all
              ${stage.suppressed ? "bg-slate-50 border-slate-200 opacity-50" : "bg-white border-slate-100 shadow-sm hover:border-indigo-200"}
            `}
          >
            <div className="flex items-center gap-2 mb-2">
              <div className={`w-3 h-3 rounded-full ${stage.color}`} />
              <span className="text-xs font-bold text-slate-500 uppercase tracking-wider">
                {stage.label}
              </span>
              {stage.suppressed && (
                <span className="text-[10px] bg-red-100 text-red-600 px-1.5 py-0.5 rounded font-bold">
                  SKIPPED
                </span>
              )}
            </div>
            <p className="text-2xl font-black text-slate-800">
              ₹{stage.value.toLocaleString("en-IN")}
            </p>
            <div className="mt-2">
              <p className="text-[11px] font-bold text-slate-700 leading-tight">
                {stage.fullLabel}
              </p>
              <p className="text-[10px] text-slate-400 mt-1 leading-relaxed">
                {stage.description}
              </p>
            </div>
            <p className="text-[10px] font-bold text-indigo-500 mt-3 pt-3 border-t border-slate-50">
              {stage.percent.toFixed(0)}% Allocation
            </p>
          </div>
        ))}
      </div>

      {/* Total */}
      <div className="mt-6 pt-4 border-t border-slate-100 flex items-center justify-between">
        <div>
          <span className="text-sm font-bold text-slate-800">
            Total Daily Budget
          </span>
          <p className="text-[10px] text-slate-400">
            Targeting spend across all digital touchpoints
          </p>
        </div>
        <span className="text-2xl font-black text-indigo-600">
          ₹{total.toLocaleString("en-IN", { maximumFractionDigits: 0 })}
        </span>
      </div>
    </div>
  );
};

