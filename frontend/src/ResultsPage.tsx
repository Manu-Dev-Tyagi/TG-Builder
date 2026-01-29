import React, { useEffect, useState } from "react";
import { api, type ResultsResponse, type Strategy } from "./api";
import { useNavigate, useLocation } from "react-router-dom";
import { StrategyLockCard } from "./components/StrategyLockCard";
import { RichPersonaCard } from "./components/RichPersonaCard";
import { MetaCampaignCard } from "./components/MetaCampaignCard";
import { GoogleCampaignCard } from "./components/GoogleCampaignCard";
import { PlatformDecisionGroup } from "./components/PlatformDecisionBadge";

import {
  User,
  Users,
  Layers,
  DollarSign,
  Download,
  ArrowLeft,
  AlertTriangle,
  FileText,
  ChevronDown,
  ChevronUp,
  Sparkles,
  Zap,
  Search,
  Key,
  Ban,
} from "lucide-react";
import clsx from "clsx";

import { useLifecycleLogger } from "./hooks/useLifecycleLogger";

export default function ResultsPage() {
  useLifecycleLogger("ResultsPage");
  const navigate = useNavigate();
  const location = useLocation();
  const runResult = location.state?.runResult;
  const [data, setData] = useState<ResultsResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<
    "personas" | "campaigns" | "budget" | "audit"
  >("personas");

  const pid = localStorage.getItem("current_project_id");
  const handleDownload = () => {
    if (!data) return;

    let content = `# TG BUILDER STRATEGY PLAYBOOK\n`;
    content += `Generated: ${new Date().toLocaleDateString()}\n\n`;

    content += `## EXECUTIVE SUMMARY\n`;
    content += `Strategy for: ${pid}\n`;
    content += `Total Personas: ${data.personas.length}\n`;
    content += `Platforms: Meta & Google\n\n`;

    content += `---\n\n`;
    content += `## SECTION 1: BUYER PERSONAS\n\n`;

    data.personas.forEach((p: any, i: number) => {
      content += `### ${i + 1}. ${p.name} (${p.funnel_role || "Primary"})\n`;
      content += `**Role**: ${p.role_in_portfolio}\n`;
      content += `**Demographics**: ${p.location}, ${p.age_range}, ${p.gender}, ${p.household_income}\n`;
      content += `**Profession**: ${p.profession}\n`;
      content += `**Key Pain Points**:\n`;
      p.pain_points.forEach((pain: string) => (content += `- ${pain}\n`));

      content += `\n**Psychographics**:\n`;
      if (p.psychographics) {
        content += `- Motivations: ${p.psychographics.motivations?.join(", ")}\n`;
        content += `- Values: ${p.psychographics.values?.join(", ")}\n`;
        content += `- Beliefs: ${p.psychographics.beliefs?.join(", ")}\n`;
      }

      if (p.buying_behavior) {
        content += `\n**Buying Behavior**:\n`;
        content += `- Triggers: ${p.buying_behavior.purchase_triggers?.join(", ")}\n`;
        content += `- Decision Speed: ${p.buying_behavior.decision_speed}\n`;
      }

      content += `\n**Content Strategy**:\n`;
      content += `- Formats: ${p.content_consumption?.join(", ")}\n`;
      content += `- Platforms: ${p.preferred_platforms?.join(", ")}\n\n`;
    });

    content += `---\n\n`;
    content += `## SECTION 2: META ADS STRATEGY\n\n`;

    data.blueprints.forEach((bp: any) => {
      const pName =
        data.personas.find((p: any) => p.id === bp.persona_id)?.name ||
        "Unknown Persona";
      content += `### Strategy for: ${pName}\n`;

      if (bp.targeting_data && bp.targeting_data.length > 0) {
        bp.targeting_data.forEach((adset: any) => {
          content += `#### Adset: ${adset.name?.split("|").pop()}\n`;
          content += `- Stage: ${adset.funnel_stage} (${adset.targeting_type})\n`;
          content += `- Placement: ${adset.placements || "Auto"}\n`;
          content += `- Interests: ${adset.interests?.join(", ")}\n`;
          if (adset.behaviors?.length > 0) {
            content += `- Behaviors: ${adset.behaviors.join(", ")}\n`;
          }
          if (
            adset.exclusions?.interests?.length > 0 ||
            adset.exclusions?.behaviors?.length > 0
          ) {
            content += `- Exclusions: ${[...(adset.exclusions?.interests || []), ...(adset.exclusions?.behaviors || [])].join(", ")}\n`;
          }
          content += `\n`;
        });
      } else {
        content += `No Meta adsets generated.\n`;
      }
      content += `\n`;
    });

    content += `---\n\n`;
    content += `## SECTION 3: GOOGLE ADS STRATEGY\n\n`;

    data.blueprints.forEach((bp: any) => {
      const pName =
        data.personas.find((p: any) => p.id === bp.persona_id)?.name ||
        "Unknown";

      if (bp.google_adgroups && bp.google_adgroups.length > 0) {
        content += `### Strategy for: ${pName}\n`;
        bp.google_adgroups.forEach((ag: any) => {
          content += `#### Ad Group: ${ag.name?.split("|").pop()}\n`;
          content += `- Type: ${ag.campaign_type}\n`;
          content += `- Intent: ${ag.intent}\n`;

          if (ag.campaign_type === "Search" && ag.keywords) {
            content += `- Keyword Themes:\n`;
            ag.keywords.forEach((kw: any) => {
              content += `  * ${kw.theme} (${kw.match_type}): ${kw.keywords.join(", ")}\n`;
            });
          }

          if (ag.audience_signals) {
            content += `- Audience Signals:\n`;
            if (ag.audience_signals.in_market?.length)
              content += `  * In-Market: ${ag.audience_signals.in_market.join(", ")}\n`;
            if (ag.audience_signals.affinity?.length)
              content += `  * Affinity: ${ag.audience_signals.affinity.join(", ")}\n`;
            if (ag.audience_signals.custom_segments?.length)
              content += `  * Custom: ${ag.audience_signals.custom_segments.join(", ")}\n`;
          }
          content += `\n`;
        });
      }
    });

    const blob = new Blob([content], { type: "text/markdown" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `TG_Builder_Strategy_${new Date().getTime()}.md`; // Changed to .md for better formatting viewing
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };
  useEffect(() => {
    const fetchResults = async () => {
      if (!pid) {
        navigate("/", { replace: true });
        return;
      }

      setLoading(true);
      try {
        // If we don't have results in navigation state (happens on refresh)
        // or if we want to ensure fresh data
        const res = await api.getResults(pid);
        setData(res);

        // Also try to find the runResult metadata if possible
        if (!location.state?.runResult) {
          console.log("Recovering from page refresh...");
          // NOTE: The runResult itself is not fetched here, only the main results.
          // If runResult needs to be recovered, an additional API call would be needed.
          // For now, this just logs the situation.
        }
      } catch (err: any) {
        console.error("Failed to load results:", err);
        setError(err.message || "Failed to load results");
      } finally {
        setLoading(false);
      }
    };

    fetchResults();
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-50 flex flex-col">
        {/* Skeleton Header */}
        <div className="bg-white border-b border-slate-200 px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <div className="w-10 h-10 bg-slate-200 rounded-full animate-pulse" />
            <div className="space-y-2">
              <div className="w-48 h-6 bg-slate-200 rounded animate-pulse" />
              <div className="w-32 h-4 bg-slate-100 rounded animate-pulse" />
            </div>
          </div>
          <div className="w-40 h-10 bg-slate-200 rounded-lg animate-pulse" />
        </div>

        <main className="max-w-7xl mx-auto p-6 w-full space-y-8">
          {/* Skeleton Strategy Card */}
          <div className="w-full h-48 bg-white border-2 border-slate-200 rounded-2xl animate-pulse" />

          <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
            <div className="lg:col-span-1 space-y-3">
              {[1, 2, 3, 4].map((i) => (
                <div
                  key={i}
                  className="w-full h-12 bg-white rounded-lg animate-pulse"
                />
              ))}
            </div>
            <div className="lg:col-span-3 grid grid-cols-1 md:grid-cols-2 gap-6">
              {[1, 2, 3, 4].map((i) => (
                <div
                  key={i}
                  className="w-full h-64 bg-white border border-slate-200 rounded-2xl animate-pulse"
                />
              ))}
            </div>
          </div>
        </main>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="min-h-screen bg-slate-50 flex items-center justify-center p-6">
        <div className="bg-white rounded-2xl shadow-xl p-8 max-w-md text-center">
          <AlertTriangle className="mx-auto text-red-500 mb-4" size={48} />
          <h2 className="text-xl font-bold text-slate-900 mb-2">
            Failed to Load Results
          </h2>
          <p className="text-slate-600 mb-6">{error || "No data found"}</p>
          <button
            onClick={() => navigate("/")}
            className="px-6 py-3 bg-indigo-600 text-white font-bold rounded-xl hover:bg-indigo-700"
          >
            Start New Project
          </button>
        </div>
      </div>
    );
  }

  const {
    strategy,
    personas = [],
    blueprints = [],
    budget = null,
  } = data || {};
  const projectId = localStorage.getItem("current_project_id");
  const isTofSuppressed = strategy?.funnel_policy === "NO_TOF";

  const handleDownloadPlaybook = () => {
    if (projectId) {
      window.open(api.getPlaybookUrl(projectId), "_blank");
    }
  };

  const getPersonaName = (id: string) => {
    return personas.find((p) => p.persona_id === id)?.name || "Persona";
  };

  // Budget calculations removed as feature is under upgrade
  // const funnelBudgets = getFunnelBudgets();
  // const platformTotals = getPlatformTotals();

  // return(<>hello</>)
  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 font-sans">
      {/* Header */}
      <header className="bg-white border-b border-slate-200 sticky top-0 z-10 px-6 py-4 flex items-center justify-between shadow-sm">
        <div className="flex items-center gap-4">
          <button
            onClick={() => navigate("/")}
            className="p-2 hover:bg-slate-100 rounded-full text-slate-500"
          >
            <ArrowLeft size={20} />
          </button>
          <div>
            <h1 className="text-xl font-bold text-slate-800">
              Strategy Playbook
            </h1>
            <p className="text-sm text-slate-500">
              Project: {projectId?.substring(0, 8)}...
            </p>
          </div>
          {runResult?.status && (
            <div
              className={clsx(
                "ml-4 px-3 py-1 rounded-full text-xs font-bold border",
                runResult.status === "SUCCESS"
                  ? "bg-green-100 text-green-700 border-green-200"
                  : runResult.status === "PARTIAL"
                    ? "bg-amber-100 text-amber-700 border-amber-200"
                    : "bg-red-100 text-red-700 border-red-200",
              )}
            >
              VERDICT: {runResult.status}
              {(runResult.blocking_errors?.length || 0) > 0 && (
                <span className="ml-2 opacity-75">
                  ({runResult.blocking_errors.length} Errors)
                </span>
              )}
            </div>
          )}
        </div>
        <button
          onClick={handleDownloadPlaybook}
          className="flex items-center gap-2 px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 text-sm font-medium shadow-md transition-all active:scale-95"
        >
          <Download size={16} /> Download Playbook
        </button>
      </header>

      {/* Main Layout */}
      <main className="max-w-7xl mx-auto p-6 space-y-8">
        {/* SECTION 1: Strategy Lock Card (ALWAYS FIRST) */}
        {strategy && <StrategyLockCard strategy={strategy} />}

        {/* Content Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
          {/* Sidebar Navigation */}
          <div className="lg:col-span-1 space-y-2">
            <NavButton
              active={activeTab === "personas"}
              onClick={() => setActiveTab("personas")}
              icon={User}
              label="Personas"
              count={personas?.length || 0}
            />
            <NavButton
              active={activeTab === "campaigns"}
              onClick={() => setActiveTab("campaigns")}
              icon={Layers}
              label="Campaign Structures"
            />
            <NavButton
              active={activeTab === "budget"}
              onClick={() => setActiveTab("budget")}
              icon={DollarSign}
              label="Budget & Funnel"
            />
            <NavButton
              active={activeTab === "audit"}
              onClick={() => setActiveTab("audit")}
              icon={FileText}
              label="Audit Trail"
            />
          </div>

          {/* Content Area */}
          <div className="lg:col-span-3">
            {/* PERSONAS TAB */}
            {activeTab === "personas" && (
              <div className="space-y-6 animate-in fade-in slide-in-from-bottom-2 duration-500">
                <h2 className="text-2xl font-bold mb-4">
                  Buyer Persona Portfolio
                </h2>
                <div className="flex flex-col gap-8">
                  {personas.map((p, idx) => (
                    <RichPersonaCard key={idx} data={p} index={idx} />
                  ))}
                </div>
              </div>
            )}

            {/* CAMPAIGNS TAB */}
            {activeTab === "campaigns" && (
              <div className="space-y-12 animate-in fade-in slide-in-from-bottom-2 duration-500">
                {/* Meta Section */}
                <section>
                  <div className="flex items-center gap-4 mb-8">
                    <div className="h-10 w-1 bg-[#1877F2] rounded-full" />
                    <div>
                      <h3 className="text-2xl font-black text-slate-800">
                        Meta Campaigns
                      </h3>
                      <p className="text-sm text-slate-500 font-medium">
                        Step-by-step Interest Stacks & Creative Angles
                      </p>
                    </div>
                  </div>

                  {blueprints.filter((c: any) => c.platform === "Meta").length >
                  0 ? (
                    <div className="space-y-8">
                      {blueprints
                        .filter((c: any) => c.platform === "Meta")
                        .map((blueprint: any, i: number) => {
                          const persona = personas.find(
                            (p: any) => p.persona_id === blueprint.persona_id,
                          );
                          const rationale =
                            persona?.platform_decisions?.["Meta"]?.reason;
                          return (
                            <MetaCampaignCard
                              key={i}
                              blueprint={blueprint}
                              personaName={persona?.name || "Unknown"}
                              rationale={rationale}
                            />
                          );
                        })}
                    </div>
                  ) : (
                    <PlatformBlockedCard platform="Meta" />
                  )}
                </section>

                <div className="border-t border-slate-200" />

                {/* Google Section */}
                <section>
                  <div className="flex items-center gap-4 mb-8">
                    <div className="h-10 w-1 bg-[#EA4335] rounded-full" />
                    <div>
                      <h3 className="text-2xl font-black text-slate-800">
                        Google Campaigns
                      </h3>
                      <p className="text-sm text-slate-500 font-medium">
                        Search Intent & Demand Generation Architecture
                      </p>
                    </div>
                  </div>

                  {blueprints.filter((c: any) => c.platform === "Google")
                    .length > 0 ? (
                    <div className="space-y-8">
                      {blueprints
                        .filter((c: any) => c.platform === "Google")
                        .map((blueprint: any, i: number) => {
                          const persona = personas.find(
                            (p: any) => p.persona_id === blueprint.persona_id,
                          );
                          const rationale =
                            persona?.platform_decisions?.["Google"]?.reason;

                          return (
                            <GoogleCampaignCard
                              key={i}
                              blueprint={blueprint}
                              personaName={persona?.name || "Unknown"}
                              rationale={rationale}
                            />
                          );
                        })}
                    </div>
                  ) : (
                    <PlatformBlockedCard platform="Google" />
                  )}
                </section>
              </div>
            )}

            {/* BUDGET TAB */}
            {activeTab === "budget" && (
              <div className="space-y-6 animate-in fade-in slide-in-from-bottom-2 duration-500">
                <div className="flex items-center justify-between mb-4">
                  <h2 className="text-2xl font-bold">
                    Budget & Funnel Architecture
                  </h2>
                </div>

                <div className="bg-white rounded-2xl border border-dashed border-slate-300 p-12 flex flex-col items-center justify-center text-center">
                  <div className="p-4 bg-indigo-50 rounded-full mb-4">
                    <Zap className="text-indigo-500" size={48} />
                  </div>
                  <h3 className="text-xl font-bold text-slate-900 mb-2">
                    Feature Under Development
                  </h3>
                  <p className="text-slate-500 max-w-md">
                    The AI Budget & Funnel Architect is currently being
                    upgraded. Check back soon for financial allocation matrices
                    and efficiency mapping.
                  </p>
                </div>
              </div>
            )}

            {/* AUDIT TAB */}
            {activeTab === "audit" && (
              <div className="space-y-6 animate-in fade-in slide-in-from-bottom-2 duration-500">
                <div className="flex items-center justify-between mb-4">
                  <h2 className="text-2xl font-bold">Project Audit Trail</h2>
                  <div className="text-xs bg-slate-900 text-white px-3 py-1 rounded-full font-mono uppercase">
                    Full Transparency Log
                  </div>
                </div>

                <div className="bg-white rounded-2xl border border-slate-200 p-8 shadow-sm">
                  {(() => {
                    const auditTrailLog = (runResult?.logs || []).find(
                      (l: string) => l.startsWith("AUDIT_TRAIL:"),
                    );
                    if (auditTrailLog) {
                      try {
                        const jsonStr = auditTrailLog
                          .substring("AUDIT_TRAIL:".length)
                          .trim();
                        // Handle potential double escaping if seen in earlier logs
                        const entries = JSON.parse(
                          jsonStr.replace(/\\'/g, "'"),
                        );

                        return (
                          <div className="relative border-l-2 border-slate-100 pl-8 space-y-12 ml-4 py-4">
                            {entries.map((entry: any, i: number) => (
                              <div key={i} className="relative">
                                {/* Dot */}
                                <div className="absolute -left-[41px] top-0 w-5 h-5 rounded-full bg-white border-4 border-indigo-500 shadow-md z-10" />

                                <div className="flex flex-col md:flex-row md:items-start gap-2 md:gap-8">
                                  <div className="min-w-[120px]">
                                    <span className="text-[10px] font-black text-indigo-400 uppercase tracking-widest block">
                                      {entry.timestamp
                                        ?.split("T")[1]
                                        ?.substring(0, 8)}
                                    </span>
                                    <span className="text-[10px] font-bold text-slate-400 uppercase">
                                      {entry.scope}
                                    </span>
                                  </div>
                                  <div className="flex-1">
                                    <h4 className="font-black text-slate-900 leading-tight mb-1">
                                      {entry.event}
                                    </h4>
                                    <p className="text-sm text-slate-500 leading-relaxed font-medium">
                                      {entry.detail}
                                    </p>
                                  </div>
                                </div>
                              </div>
                            ))}
                          </div>
                        );
                      } catch (e) {
                        console.error("Audit Parse Error:", e);
                      }
                    }

                    return (
                      <div className="space-y-4">
                        <div className="p-12 bg-slate-50 border border-dashed border-slate-200 rounded-2xl text-center">
                          <FileText
                            className="mx-auto text-slate-300 mb-4"
                            size={48}
                          />
                          <p className="text-slate-500 font-medium italic">
                            Detailed audit trail is available after a fresh
                            generation run.
                          </p>
                        </div>
                        <div className="space-y-2">
                          <p className="text-[10px] font-black text-slate-400 uppercase tracking-widest mb-2">
                            Technical Flow Output:
                          </p>
                          {(runResult?.logs || [])
                            .filter((l: string) => !l.startsWith("AUDIT"))
                            .map((log: string, i: number) => (
                              <div
                                key={i}
                                className="font-mono text-[10px] p-2 bg-slate-50 border border-slate-100 rounded text-slate-600"
                              >
                                {log}
                              </div>
                            ))}
                        </div>
                      </div>
                    );
                  })()}
                </div>
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}

// --- Subcomponents ---

const NavButton = ({ active, onClick, icon: Icon, label, count }: any) => (
  <button
    onClick={onClick}
    className={clsx(
      "w-full flex items-center justify-between px-4 py-3 rounded-xl text-sm font-medium transition-all group",
      active
        ? "bg-indigo-600 text-white shadow-lg shadow-indigo-200 translate-x-1"
        : "text-slate-600 hover:bg-white hover:text-indigo-600",
    )}
  >
    <div className="flex items-center gap-3">
      <Icon size={18} />
      {label}
    </div>
    {count !== undefined && (
      <span
        className={clsx(
          "px-2 py-0.5 rounded text-[10px] font-bold",
          active ? "bg-indigo-500 text-white" : "bg-slate-100 text-slate-500",
        )}
      >
        {count}
      </span>
    )}
  </button>
);

const PlatformBlockedCard = ({ platform }: { platform: string }) => (
  <div className="bg-slate-100 border-2 border-dashed border-slate-200 rounded-2xl p-8 text-center">
    <AlertTriangle className="mx-auto text-slate-300 mb-3" size={32} />
    <h4 className="font-bold text-slate-700 mb-1">
      {platform} Channel Deactivated
    </h4>
    <p className="text-sm text-slate-400 max-w-xs mx-auto">
      Locked Strategy has determined {platform} search intent or discovery
      volume is insufficient for this persona.
    </p>
  </div>
);

const PersonaCard = ({ data }: any) => {
  const [expanded, setExpanded] = useState(false);
  const behavior =
    data.buying_behavior || data.full_data?.buying_behavior || {};
  const psycho = data.psychographics || data.full_data?.psychographics || {};

  return (
    <div className="bg-white rounded-2xl border border-slate-200 shadow-sm hover:shadow-xl transition-all duration-300 overflow-hidden flex flex-col">
      {/* Top Header Section */}
      <div className="p-6 pb-4">
        <div className="flex justify-between items-start mb-6">
          <div className="flex items-center gap-2 flex-wrap">
            <span
              className={clsx(
                "px-2 py-1 rounded text-[10px] font-black uppercase tracking-widest",
                data.role_in_portfolio === "Anchor"
                  ? "bg-indigo-600 text-white"
                  : "bg-slate-100 text-slate-500",
              )}
            >
              {data.role_in_portfolio}
            </span>
            {/* New Funnel Role Badge */}
            {data.funnel_role && (
              <span className="px-2 py-1 bg-violet-100 text-violet-700 rounded text-[10px] font-black uppercase tracking-widest border border-violet-200">
                {data.funnel_role}
              </span>
            )}
            <span className="px-2 py-1 bg-amber-100 text-amber-700 rounded text-[10px] font-black uppercase tracking-widest border border-amber-200">
              {behavior.decision_speed || "NORMAL"}
            </span>
          </div>
          <span className="text-4xl font-black text-indigo-50/50 italic leading-none">
            0{data.rank}
          </span>
        </div>

        <h3 className="text-2xl font-black text-slate-900 leading-tight mb-2">
          {data.name}
        </h3>
        <p className="text-xs font-bold text-indigo-500 uppercase tracking-widest">
          {data.recommended_platforms?.join(" + ") || "DIGITAL MIX"}
        </p>
      </div>

      <div className="px-6 pb-6 space-y-5 flex-1">
        {/* Core Demographics Grid */}
        <div className="bg-slate-50 rounded-xl p-4 border border-slate-100 grid grid-cols-2 gap-y-3 gap-x-4">
          <div>
            <p className="text-[10px] text-slate-400 font-bold uppercase mb-0.5">
              Location
            </p>
            <p className="text-xs font-black text-slate-800">{data.location}</p>
          </div>
          <div>
            <p className="text-[10px] text-slate-400 font-bold uppercase mb-0.5">
              Age & Gender
            </p>
            <p className="text-xs font-black text-slate-800">
              {data.age_range}, {data.gender}
            </p>
          </div>
          <div>
            <p className="text-[10px] text-slate-400 font-bold uppercase mb-0.5">
              Profession
            </p>
            <p
              className="text-xs font-black text-slate-800 truncate"
              title={data.profession}
            >
              {data.profession}
            </p>
          </div>
          <div>
            <p className="text-[10px] text-slate-400 font-bold uppercase mb-0.5">
              Income
            </p>
            <p className="text-xs font-black text-slate-800">
              {data.household_income}
            </p>
          </div>
        </div>

        {/* Key Pain Points */}
        <div>
          <p className="text-[10px] font-black text-red-400 uppercase tracking-widest mb-2 flex items-center gap-1">
            <AlertTriangle size={12} /> Key Pains
          </p>
          <ul className="space-y-1">
            {(data.pain_points || [])
              .slice(0, 3)
              .map((pain: string, i: number) => (
                <li
                  key={i}
                  className="text-xs text-slate-700 font-medium flex items-start gap-1.5"
                >
                  <span className="mt-1.5 w-1 h-1 rounded-full bg-red-400 flex-shrink-0" />
                  {pain}
                </li>
              ))}
          </ul>
        </div>

        {/* Platforms & Content */}
        <div className="border-t border-slate-100 pt-3">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <p className="text-[10px] font-black text-slate-400 uppercase tracking-widest mb-1">
                Platforms
              </p>
              <div className="flex flex-wrap gap-1">
                {(data.preferred_platforms || []).map(
                  (p: string, i: number) => (
                    <span
                      key={i}
                      className="text-[10px] px-1.5 py-0.5 bg-slate-100 rounded text-slate-600 font-bold"
                    >
                      {p}
                    </span>
                  ),
                )}
              </div>
            </div>
            <div>
              <p className="text-[10px] font-black text-slate-400 uppercase tracking-widest mb-1">
                Content Formats
              </p>
              <p className="text-xs text-slate-600 font-medium leading-snug">
                {(data.content_consumption || []).slice(0, 3).join(", ")}
              </p>
            </div>
          </div>
        </div>

        {/* Expand/Collapse Toggle */}
        <button
          onClick={() => setExpanded(!expanded)}
          className="w-full flex items-center justify-center gap-2 py-2 border border-slate-100 rounded-lg text-[10px] font-black uppercase text-indigo-500 hover:bg-slate-50 transition-colors"
        >
          {expanded ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
          {expanded ? "Minimize Deep Dive" : "View Psychographics"}
        </button>

        {expanded && (
          <div className="pt-2 space-y-4 animate-in fade-in duration-300">
            {/* Motivations */}
            <div>
              <span className="text-[10px] font-black text-slate-400 uppercase tracking-widest block mb-2">
                Core Motivations
              </span>
              <div className="flex flex-wrap gap-1.5">
                {(psycho.motivations || []).map((m: string, i: number) => (
                  <span
                    key={i}
                    className="px-2 py-1 bg-green-50 border border-green-100 text-[10px] font-bold text-green-700 rounded shadow-sm"
                  >
                    {m}
                  </span>
                ))}
              </div>
            </div>
            {/* Values */}
            <div>
              <span className="text-[10px] font-black text-slate-400 uppercase tracking-widest block mb-2">
                Values & Beliefs
              </span>
              <div className="flex flex-wrap gap-1.5">
                {(psycho.values || []).map((v: string, i: number) => (
                  <span
                    key={i}
                    className="px-2 py-1 bg-slate-50 border border-slate-100 text-[10px] font-bold text-slate-600 rounded"
                  >
                    {v}
                  </span>
                ))}
              </div>
            </div>

            <div className="bg-slate-50 p-3 rounded-lg border border-slate-100">
              <span className="text-[9px] font-black text-slate-400 uppercase tracking-widest block mb-1">
                Buying Trigger
              </span>
              <p className="text-xs font-semibold text-slate-700 italic">
                "{behavior.purchase_triggers?.join(", ") || "Need based"}"
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
