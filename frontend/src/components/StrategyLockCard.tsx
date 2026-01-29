import React from "react";
import {
  Lock,
  AlertTriangle,
  XCircle,
  ChevronDown,
  ChevronUp,
  Zap,
  Target,
  Layers,
} from "lucide-react";
import type { Strategy } from "../api";

interface StrategyLockCardProps {
  strategy: Strategy;
}

export const StrategyLockCard: React.FC<StrategyLockCardProps> = ({
  strategy,
}) => {
  const [expanded, setExpanded] = React.useState(false);

  const getStatusConfig = () => {
    switch (strategy.status) {
      case "LOCKED":
        return {
          icon: Lock,
          color: "bg-emerald-500",
          bgColor: "bg-emerald-50",
          borderColor: "border-emerald-200",
          textColor: "text-emerald-700",
          label: "LOCKED",
        };
      case "NA_REJECTION":
        return {
          icon: XCircle,
          color: "bg-red-500",
          bgColor: "bg-red-50",
          borderColor: "border-red-200",
          textColor: "text-red-700",
          label: "REJECTED",
        };
      default:
        return {
          icon: AlertTriangle,
          color: "bg-amber-500",
          bgColor: "bg-amber-50",
          borderColor: "border-amber-200",
          textColor: "text-amber-700",
          label: "PENDING",
        };
    }
  };

  const statusConfig = getStatusConfig();
  const StatusIcon = statusConfig.icon;

  const getFunnelPolicyBadge = () => {
    if (strategy.funnel_policy === "NO_TOF") {
      return (
        <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold bg-amber-100 text-amber-700 border border-amber-200">
          <AlertTriangle size={12} />
          TOF SUPPRESSED
        </span>
      );
    }
    return (
      <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold bg-emerald-100 text-emerald-700 border border-emerald-200">
        <Layers size={12} />
        FULL FUNNEL
      </span>
    );
  };

  return (
    <div
      className={`rounded-2xl border-2 ${statusConfig.borderColor} ${statusConfig.bgColor} overflow-hidden shadow-lg`}
    >
      {/* Header */}
      <div className="p-6">
        <div className="flex items-start justify-between">
          <div className="flex items-center gap-4">
            <div
              className={`p-3 rounded-xl ${statusConfig.color} text-white shadow-lg`}
            >
              <StatusIcon size={24} />
            </div>
            <div>
              <h2 className="text-2xl font-black text-slate-900 tracking-tight">
                {strategy.campaign_type || "Strategy Pending"}
              </h2>
              <p className="text-sm text-slate-500 mt-1">
                Locked Campaign Strategy
              </p>
            </div>
          </div>
          <div
            className={`px-4 py-2 rounded-full ${statusConfig.color} text-white text-xs font-black uppercase tracking-wider shadow-md`}
          >
            {statusConfig.label}
          </div>
        </div>

        {/* Key Metrics */}
        <div className="grid grid-cols-3 gap-4 mt-6">
          <div className="bg-white/60 rounded-xl p-4 border border-white/80">
            <div className="flex items-center gap-2 text-slate-500 text-xs font-bold uppercase tracking-wider mb-1">
              <Target size={12} />
              Campaign Type
            </div>
            <p className="text-lg font-bold text-slate-800">
              {strategy.campaign_type || "—"}
            </p>
          </div>
          <div className="bg-white/60 rounded-xl p-4 border border-white/80">
            <div className="flex items-center gap-2 text-slate-500 text-xs font-bold uppercase tracking-wider mb-1">
              <Zap size={12} />
              Decision Speed
            </div>
            <p className="text-lg font-bold text-slate-800">
              {strategy.decision_speed || "—"}
            </p>
          </div>
          <div className="bg-white/60 rounded-xl p-4 border border-white/80">
            <div className="flex items-center gap-2 text-slate-500 text-xs font-bold uppercase tracking-wider mb-1">
              <Layers size={12} />
              Funnel Policy
            </div>
            <div className="mt-1">{getFunnelPolicyBadge()}</div>
          </div>
        </div>

        {/* NO_TOF Warning Banner */}
        {strategy.funnel_policy === "NO_TOF" && (
          <div className="mt-4 p-4 bg-amber-100 border border-amber-300 rounded-xl flex items-start gap-3">
            <AlertTriangle
              className="text-amber-600 flex-shrink-0 mt-0.5"
              size={18}
            />
            <div>
              <p className="text-sm font-bold text-amber-800">
                Awareness Stage Suppressed
              </p>
              <p className="text-xs text-amber-700 mt-1">
                Top-of-funnel (TOF) assets are disabled due to Fast Decision
                Speed. Budget has been reallocated to MOF/BOF stages.
              </p>
            </div>
          </div>
        )}
      </div>

      {/* Expandable Notes Section */}
      {strategy.notes && (
        <div className="border-t border-slate-200/50">
          <button
            onClick={() => setExpanded(!expanded)}
            className="w-full px-6 py-3 flex items-center justify-between hover:bg-white/30 transition-colors"
          >
            <span className="text-sm font-bold text-slate-600">
              Strategy Rationale
            </span>
            {expanded ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
          </button>
          {expanded && (
            <div className="px-6 pb-4">
              <div className="bg-white/80 rounded-xl p-4 text-sm text-slate-600 font-mono whitespace-pre-wrap border border-slate-200">
                {strategy.notes}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
