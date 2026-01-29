import React, { useState } from "react";
import {
  Copy,
  Check,
  Search as SearchIcon,
  Globe,
  Hash,
  Users,
  Target,
  BarChart2,
  List,
} from "lucide-react";
import clsx from "clsx";
import { GoogleAdGroup, GoogleKeyword } from "../api";

interface GoogleCampaignCardProps {
  blueprint: any;
  personaName: string;
  rationale?: string;
}

export const GoogleCampaignCard: React.FC<GoogleCampaignCardProps> = ({
  blueprint,
  personaName,
  rationale,
}) => {
  const adgroups: GoogleAdGroup[] = blueprint.google_adgroups || [];

  if (adgroups.length === 0) return null;

  return (
    <div className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden mb-8">
      {/* HEADER: Step 1 Platform Decision */}
      <div className="bg-[#EA4335]/5 border-b border-[#EA4335]/10 p-6">
        <div className="flex justify-between items-start mb-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-white border border-[#EA4335]/20 rounded-xl flex items-center justify-center text-[#EA4335] shadow-sm">
              <Globe size={24} className="stroke-current" />
            </div>
            <div>
              <h3 className="text-lg font-black text-slate-900 uppercase tracking-tight">
                Google Ads Blueprint
              </h3>
              <p className="text-xs font-bold text-[#EA4335] uppercase tracking-widest">
                Architectural Structure
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
        <div className="bg-white rounded-xl p-4 border border-[#EA4335]/20 flex items-start gap-3">
          <div className="mt-1 min-w-[20px]">
            <Target size={18} className="text-[#EA4335]" />
          </div>
          <div>
            <p className="text-[10px] font-black text-slate-400 uppercase tracking-widest mb-1">
              Step 1: Platform Decision Logic
            </p>
            <p className="text-sm font-medium text-slate-700 italic">
              "
              {rationale ||
                "Selected based on high intent search behavior and research orientation."}
              "
            </p>
          </div>
        </div>
      </div>

      {/* BODY: Step 2 Ad Group Structure */}
      <div className="p-6 bg-slate-50/50">
        <div className="flex items-center gap-2 mb-6">
          <List className="text-slate-400" size={20} />
          <h4 className="text-sm font-black text-slate-500 uppercase tracking-widest">
            Step 2: Ad Group Architecture
          </h4>
        </div>

        <div className="space-y-8">
          {adgroups.map((ag, idx) => (
            <AdGroupSection key={idx} adgroup={ag} index={idx} />
          ))}
        </div>
      </div>
    </div>
  );
};

// --- Sub-component for Ad Group (Splits handling for Search vs Other) ---
const AdGroupSection: React.FC<{ adgroup: GoogleAdGroup; index: number }> = ({
  adgroup,
  index,
}) => {
  const isSearch = adgroup.campaign_type === "Search";
  const typeLabel = isSearch
    ? "Search Campaign"
    : `${adgroup.campaign_type} (Audience First)`;

  // Icon logic
  const Icon = isSearch ? SearchIcon : BarChart2;
  const colorClass = isSearch
    ? "text-blue-600 bg-blue-50 border-blue-100"
    : "text-amber-600 bg-amber-50 border-amber-100";

  return (
    <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
      <div className="px-5 py-4 border-b border-slate-100 flex items-center justify-between bg-slate-50/50">
        <div className="flex items-center gap-3">
          <div className={clsx("p-2 rounded-lg border", colorClass)}>
            <Icon size={16} />
          </div>
          <div>
            <h5 className="font-bold text-slate-900 text-sm">
              {adgroup.name.split("|").pop()}
            </h5>
            <p className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">
              {typeLabel}
            </p>
          </div>
        </div>
        <span className="px-2 py-1 rounded text-[10px] font-black uppercase tracking-widest bg-slate-200 text-slate-600">
          {adgroup.intent}
        </span>
      </div>

      <div className="p-5">
        {isSearch && adgroup.keywords ? (
          <KeywordTable groups={adgroup.keywords} />
        ) : adgroup.audience_signals ? (
          <AudienceSignalsVisuals signals={adgroup.audience_signals as any} />
        ) : (
          <p className="text-sm text-slate-400 italic">
            No targeting data available.
          </p>
        )}
      </div>
    </div>
  );
};

// --- Search: Keyword Table ---
// The models might pass keywords as a wrapper object or list of objects
const KeywordTable = ({ groups }: { groups: GoogleKeyword[] }) => {
  return (
    <div className="overflow-x-auto">
      <table className="w-full text-left text-xs border-collapse">
        <thead>
          <tr className="border-b border-slate-200">
            <th className="py-2 pl-2 font-black text-slate-400 uppercase tracking-widest w-1/4">
              Check
            </th>
            <th className="py-2 font-black text-slate-400 uppercase tracking-widest w-1/2">
              Keywords
            </th>
            <th className="py-2 font-black text-slate-400 uppercase tracking-widest w-1/4">
              Match Type
            </th>
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-100">
          {groups.map((grp, i) => (
            <tr key={i} className="group hover:bg-slate-50 transition-colors">
              <td className="py-3 pl-2 align-top">
                <div className="w-4 h-4 border-2 border-slate-300 rounded flex items-center justify-center">
                  {/* Mock check UI */}
                </div>
              </td>
              <td className="py-3 align-top font-medium text-slate-700">
                <div className="space-y-1">
                  {grp.keywords.map((k, j) => (
                    <div key={j} className="flex items-center gap-2">
                      <span className="w-1.5 h-1.5 rounded-full bg-slate-300"></span>
                      {k}
                    </div>
                  ))}
                </div>
              </td>
              <td className="py-3 align-top">
                <span
                  className={clsx(
                    "px-2 py-1 rounded text-[10px] font-bold uppercase border",
                    grp.match_type === "Exact"
                      ? "bg-red-50 text-red-700 border-red-200"
                      : grp.match_type === "Phrase"
                        ? "bg-amber-50 text-amber-700 border-amber-200"
                        : "bg-blue-50 text-blue-700 border-blue-200",
                  )}
                >
                  {grp.match_type}
                </span>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

// --- PMax: Audience Signals ---
const AudienceSignalsVisuals = ({ signals }: { signals: any }) => {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
      <div>
        <p className="text-[10px] font-black text-slate-400 uppercase tracking-widest mb-3 flex items-center gap-2">
          <Users size={14} /> In-Market & Affinity
        </p>
        <div className="flex flex-wrap gap-2">
          {[...(signals.in_market || []), ...(signals.affinity || [])].map(
            (item: string, i: number) => (
              <span
                key={i}
                className="px-2.5 py-1.5 bg-indigo-50 text-indigo-700 border border-indigo-100 rounded-lg text-xs font-bold shadow-sm"
              >
                {item}
              </span>
            ),
          )}
          {!signals.in_market && !signals.affinity && (
            <span className="text-slate-400 italic text-xs">
              No signals found
            </span>
          )}
        </div>
      </div>

      <div>
        <p className="text-[10px] font-black text-slate-400 uppercase tracking-widest mb-3 flex items-center gap-2">
          <Hash size={14} /> Custom Segments (Search/URL)
        </p>
        <div className="space-y-2">
          {signals.custom_segments?.length > 0 ? (
            signals.custom_segments.map((item: string, i: number) => (
              <div
                key={i}
                className="flex items-center gap-2 text-xs font-medium text-slate-600 bg-slate-50 p-2 rounded border border-slate-100"
              >
                <SearchIcon size={12} className="text-slate-400" />
                {item}
              </div>
            ))
          ) : (
            <span className="text-slate-400 italic text-xs">
              No custom segments
            </span>
          )}
        </div>
      </div>
    </div>
  );
};
