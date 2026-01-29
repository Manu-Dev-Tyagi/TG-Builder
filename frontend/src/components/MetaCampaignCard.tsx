import React, { useState } from "react";
import {
  Copy,
  Check,
  Target,
  Layers,
  Filter,
  MousePointer2,
  Facebook,
  Instagram,
  Eye,
  TrendingUp,
  CreditCard,
} from "lucide-react";
import clsx from "clsx";
import { MetaAdset } from "../api";

interface MetaCampaignCardProps {
  blueprint: any; // Using any for flexibility with blueprint wrapper, but internal data is MetaAdset[]
  personaName: string;
  rationale?: string;
}

export const MetaCampaignCard: React.FC<MetaCampaignCardProps> = ({
  blueprint,
  personaName,
  rationale,
}) => {
  const adsets: MetaAdset[] = blueprint.targeting_data || [];

  if (adsets.length === 0) return null;

  return (
    <div className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden mb-8">
      {/* HEADER: Step 1 Platform Decision */}
      <div className="bg-[#1877F2]/5 border-b border-[#1877F2]/10 p-6">
        <div className="flex justify-between items-start mb-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-[#1877F2] rounded-xl flex items-center justify-center text-white shadow-lg shadow-blue-200">
              <Facebook size={24} fill="currentColor" className="stroke-none" />
            </div>
            <div>
              <h3 className="text-lg font-black text-slate-900 uppercase tracking-tight">
                Meta Ads Blueprint
              </h3>
              <p className="text-xs font-bold text-[#1877F2] uppercase tracking-widest">
                High-Fidelity Structure
              </p>
            </div>
          </div>
          <div className="bg-white px-3 py-1 rounded border border-slate-200 shadow-sm">
            <span className="text-xs font-bold text-slate-500 uppercase tracking-widest">
              Persona:{" "}
            </span>
            <span className="text-xs font-black text-slate-900">
              {personaName}
            </span>
          </div>
        </div>

        {/* Rationale Block */}
        <div className="bg-white rounded-xl p-4 border border-[#1877F2]/20 flex items-start gap-3">
          <div className="mt-1 min-w-[20px]">
            <Target size={18} className="text-[#1877F2]" />
          </div>
          <div>
            <p className="text-[10px] font-black text-slate-400 uppercase tracking-widest mb-1">
              Step 1: Platform Decision Logic
            </p>
            <p className="text-sm font-medium text-slate-700 italic">
              "
              {rationale ||
                "Selected based on high engagement with visual content and social discovery behavior."}
              "
            </p>
          </div>
        </div>
      </div>

      {/* BODY: Step 2 Adset Stack */}
      <div className="p-6 bg-slate-50/50">
        <div className="flex items-center gap-2 mb-6">
          <Layers className="text-slate-400" size={20} />
          <h4 className="text-sm font-black text-slate-500 uppercase tracking-widest">
            Step 2: Ad Set Architecture
          </h4>
        </div>

        <div className="space-y-6">
          {adsets.map((adset, idx) => (
            <AdsetRow key={idx} adset={adset} index={idx} />
          ))}
        </div>
      </div>
    </div>
  );
};

// --- Sub-component for individual Adset Row ---
const AdsetRow: React.FC<{ adset: MetaAdset; index: number }> = ({
  adset,
  index,
}) => {
  const getStageColor = (stage: string) => {
    if (stage?.includes("TOF"))
      return "bg-purple-100 text-purple-700 border-purple-200";
    if (stage?.includes("MOF"))
      return "bg-blue-100 text-blue-700 border-blue-200";
    if (stage?.includes("BOF"))
      return "bg-emerald-100 text-emerald-700 border-emerald-200";
    return "bg-slate-100 text-slate-600 border-slate-200";
  };

  const getStageIcon = (stage: string) => {
    if (stage?.includes("TOF")) return <Eye size={14} />;
    if (stage?.includes("MOF")) return <TrendingUp size={14} />;
    if (stage?.includes("BOF")) return <CreditCard size={14} />;
    return <Layers size={14} />;
  };

  return (
    <div className="bg-white rounded-xl border border-slate-200 shadow-sm hover:shadow-md transition-shadow duration-200 relative overflow-hidden group">
      {/* Left Color Bar */}
      <div
        className={clsx(
          "absolute top-0 bottom-0 left-0 w-1.5",
          getStageColor(adset.funnel_stage)
            .split(" ")[0]
            .replace("bg-", "bg-opacity-100 bg-"),
        )}
      />

      <div className="p-5 pl-7">
        {/* Header Row */}
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-4 border-b border-slate-100 pb-3">
          <div className="flex items-center gap-3">
            <span
              className={clsx(
                "px-2.5 py-1 rounded text-[10px] font-black uppercase tracking-widest border flex items-center gap-1.5",
                getStageColor(adset.funnel_stage),
              )}
            >
              {getStageIcon(adset.funnel_stage)}
              {adset.funnel_stage}
            </span>
            <h5 className="font-bold text-slate-900 text-sm">
              {adset.name.includes("|")
                ? adset.name.split("|").pop()?.trim()
                : adset.name}
            </h5>
          </div>
          {/* Placement Badge */}
          <div
            className={clsx(
              "px-3 py-1 rounded-full text-[10px] font-bold uppercase flex items-center gap-2 border",
              adset.placements.toLowerCase().includes("advantage")
                ? "bg-gradient-to-r from-pink-50 to-purple-50 border-purple-100 text-purple-700"
                : "bg-slate-100 border-slate-200 text-slate-600",
            )}
          >
            <MousePointer2 size={12} />
            {adset.placements}
          </div>
        </div>

        {/* Content Grid */}
        <div className="grid grid-cols-1 md:grid-cols-12 gap-6">
          {/* Demographics (Col 3) */}
          <div className="md:col-span-3 space-y-2">
            <p className="text-[10px] font-black text-slate-400 uppercase tracking-widest mb-1">
              Demographics
            </p>
            <div className="space-y-1">
              <div className="text-xs font-medium text-slate-700 flex justify-between border-b border-slate-50 pb-1">
                <span className="text-slate-500">Age:</span>
                <span>{adset.age_range}</span>
              </div>
              <div className="text-xs font-medium text-slate-700 flex justify-between border-b border-slate-50 pb-1">
                <span className="text-slate-500">Gender:</span>
                <span>{adset.gender}</span>
              </div>
              <div className="text-xs font-medium text-slate-700 flex justify-between">
                <span className="text-slate-500">Loc:</span>
                <span
                  className="truncate max-w-[100px]"
                  title={adset.locations}
                >
                  {adset.locations}
                </span>
              </div>
            </div>
          </div>

          {/* Targeting Stack (Col 5) */}
          <div className="md:col-span-5 space-y-3">
            <div>
              <div className="flex items-center justify-between mb-1.5">
                <p className="text-[10px] font-black text-slate-400 uppercase tracking-widest flex items-center gap-1">
                  <Target size={12} /> Include
                </p>
                <CopyButton
                  text={adset.interests.join(", ")}
                  label="Interests"
                />
              </div>
              <div className="bg-slate-50 rounded-lg p-3 border border-slate-100 text-xs font-medium text-slate-700 leading-relaxed">
                {adset.interests.length > 0 ? (
                  adset.interests.join(", ")
                ) : (
                  <span className="text-slate-400 italic">
                    Broad (No specific interests)
                  </span>
                )}
                {adset.behaviors && adset.behaviors.length > 0 && (
                  <div className="mt-2 pt-2 border-t border-slate-100 text-indigo-700">
                    <span className="font-bold text-[10px] uppercase block mb-1">
                      Behaviors:
                    </span>
                    {adset.behaviors.join(", ")}
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Exclusions (Col 4) */}
          <div className="md:col-span-4 space-y-3">
            <div>
              <div className="flex items-center justify-between mb-1.5">
                <p className="text-[10px] font-black text-red-300 uppercase tracking-widest flex items-center gap-1">
                  <Filter size={12} /> Exclude
                </p>
                {/* Combine exclusion lists for copy */}
                <CopyButton
                  text={[
                    ...(adset.exclusions?.interests || []),
                    ...(adset.exclusions?.behaviors || []),
                    ...(adset.exclusions?.custom_audiences || []),
                  ].join(", ")}
                  label="Exclusions"
                />
              </div>
              <div className="bg-red-50/50 rounded-lg p-3 border border-red-50 text-xs font-medium text-slate-700 leading-relaxed">
                {(() => {
                  // @ts-ignore - Handle blueprint wrapper weirdness if any
                  const ex = adset.exclusions || {};
                  const allExclusions = [
                    ...(ex.custom_audiences?.map((c) => `[CA] ${c}`) || []),
                    ...(ex.interests || []),
                    ...(ex.behaviors || []),
                  ];

                  if (allExclusions.length === 0)
                    return (
                      <span className="text-slate-400 italic">
                        No exclusions
                      </span>
                    );

                  return (
                    <ul className="list-disc list-inside space-y-0.5">
                      {allExclusions.map((item: string, i: number) => (
                        <li key={i} className="truncate" title={item}>
                          {item}
                        </li>
                      ))}
                    </ul>
                  );
                })()}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

// --- Helper Copy Button ---
const CopyButton = ({ text, label }: { text: string; label: string }) => {
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    if (!text) return;
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  if (!text) return null;

  return (
    <button
      onClick={handleCopy}
      className="flex items-center gap-1 text-[10px] font-bold text-indigo-600 hover:text-indigo-800 transition-colors uppercase"
      title={`Copy ${label}`}
    >
      {copied ? <Check size={12} /> : <Copy size={12} />}
      {copied ? "Copied" : "Copy"}
    </button>
  );
};
