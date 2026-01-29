import React from "react";
import { Check, X, Info } from "lucide-react";
import type { PlatformDecision } from "../api";

interface PlatformDecisionBadgeProps {
  platform: string;
  decision: PlatformDecision;
}

export const PlatformDecisionBadge: React.FC<PlatformDecisionBadgeProps> = ({
  platform,
  decision,
}) => {
  const [showTooltip, setShowTooltip] = React.useState(false);

  const platformIcons: Record<string, string> = {
    Meta: "📘",
    Google: "🔍",
  };

  return (
    <div className="relative inline-block">
      <div
        className={`
          inline-flex items-center gap-2 px-3 py-1.5 rounded-lg text-sm font-medium border transition-all cursor-help
          ${
            decision.allowed
              ? "bg-emerald-50 text-emerald-700 border-emerald-200 hover:bg-emerald-100"
              : "bg-red-50 text-red-700 border-red-200 hover:bg-red-100"
          }
        `}
        onMouseEnter={() => setShowTooltip(true)}
        onMouseLeave={() => setShowTooltip(false)}
      >
        <span>{platformIcons[platform] || "📱"}</span>
        <span className="font-bold">{platform}</span>
        {decision.allowed ? (
          <Check size={14} className="text-emerald-600" />
        ) : (
          <X size={14} className="text-red-600" />
        )}
        <Info size={12} className="opacity-50" />
      </div>

      {/* Tooltip */}
      {showTooltip && (
        <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 z-50 w-64">
          <div
            className={`
              px-3 py-2 rounded-lg shadow-xl text-xs font-medium border
              ${
                decision.allowed
                  ? "bg-emerald-900 text-emerald-100 border-emerald-700"
                  : "bg-red-900 text-red-100 border-red-700"
              }
            `}
          >
            <div className="font-bold mb-1">
              {decision.allowed ? "✅ Allowed" : "❌ Blocked"}
            </div>
            <p className="opacity-90 leading-relaxed">{decision.reason}</p>
          </div>
          {/* Arrow */}
          <div
            className={`
              w-3 h-3 rotate-45 absolute left-1/2 -translate-x-1/2 -bottom-1.5
              ${decision.allowed ? "bg-emerald-900" : "bg-red-900"}
            `}
          />
        </div>
      )}
    </div>
  );
};

interface PlatformDecisionGroupProps {
  decisions: Record<string, PlatformDecision>;
}

export const PlatformDecisionGroup: React.FC<PlatformDecisionGroupProps> = ({
  decisions,
}) => {
  if (!decisions || Object.keys(decisions).length === 0) {
    return (
      <div className="text-xs text-slate-400 italic">
        No platform decisions available
      </div>
    );
  }

  return (
    <div className="flex flex-wrap gap-2">
      {Object.entries(decisions).map(([platform, decision]) => (
        <PlatformDecisionBadge
          key={platform}
          platform={platform}
          decision={decision}
        />
      ))}
    </div>
  );
};
