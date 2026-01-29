import React, { useState } from "react";
import {
  ChevronDown,
  ChevronUp,
  Smartphone,
  Monitor,
  Tablet,
  Target,
  Zap,
  Heart,
  AlertOctagon,
  Search,
  Wifi,
  BookOpen,
  ShoppingCart,
  Instagram,
  Linkedin,
  Facebook,
  Twitter,
  Youtube,
  Globe,
  MapPin,
  Briefcase,
  Users,
  DollarSign,
} from "lucide-react";
import clsx from "clsx";
import { type Persona } from "../api";

interface RichPersonaCardProps {
  data: Persona;
  index: number;
}

export const RichPersonaCard: React.FC<RichPersonaCardProps> = ({
  data,
  index,
}) => {
  const [expanded, setExpanded] = useState(false);

  // Fallback for missing new fields (backward compatibility)
  const archetype = (data as any).archetype || "Persona Archetype";
  const needs = (data as any).needs || [];
  const frustrations = (data as any).frustrations || data.pain_points || [];
  const valueDrivers = (data as any).value_drivers || [];
  const delights = (data as any).delights || [];

  // Sliders map
  const di = (data as any).digital_index || {};
  const sliders = [
    {
      label: "Research Orientation",
      value:
        di.research_orientation || (data as any).research_orientation || 50,
      icon: Search,
      color: "bg-blue-500",
    },
    {
      label: "Digital Comfort",
      value: di.digital_comfort || (data as any).digital_comfort || 50,
      icon: Wifi,
      color: "bg-indigo-500",
    },
    {
      label: "Medical/Category Literacy",
      value: di.category_maturity || (data as any).category_maturity || 50,
      icon: BookOpen,
      color: "bg-purple-500",
    },
    {
      label: "Shopping Intent",
      value: di.shopping_intent || (data as any).shopping_intent || 50,
      icon: ShoppingCart,
      color: "bg-green-500",
    },
  ];

  const devices = di.device_usage || (data as any).device_usage || ["Mobile"];
  const contentConsumption =
    di.content_consumption || (data as any).content_consumption || [];
  const platforms = (data as any).preferred_platforms || [];

  return (
    <div className="bg-white rounded-3xl border border-slate-200 shadow-xl flex flex-col hover:shadow-2xl transition-all duration-300">
      {/* Header Bar */}
      <div className="bg-slate-900 text-white px-6 py-4 flex flex-wrap justify-between items-center gap-4 rounded-t-3xl">
        <div>
          <div className="flex items-center gap-3 mb-1">
            <span className="w-6 h-6 rounded-full bg-indigo-500 flex items-center justify-center font-bold text-xs">
              {index + 1}
            </span>
            <h3 className="text-xl font-bold font-mono text-white">
              {data.name}
            </h3>
          </div>
          <div className="flex items-center gap-4 text-xs font-medium text-slate-400">
            <span className="flex items-center gap-1">
              <MapPin size={12} /> {data.location}
            </span>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <span
            className={`px-3 py-1 rounded-lg text-xs font-bold uppercase tracking-widest border border-white/10 ${getRoleBadgeColor(data.role_in_portfolio)}`}
          >
            {data.role_in_portfolio || (data as any).funnel_role || "Persona"}
          </span>
        </div>
      </div>

      <div className="p-8 grid grid-cols-1 lg:grid-cols-5 gap-8">
        {/* Left Column: Psychology (3/5 width) */}
        <div className="lg:col-span-3 flex flex-col gap-6">
          {/* Demographics Block */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 p-4 bg-slate-50 rounded-xl border border-slate-100">
            <DemographicItem icon={Users} label="Age" value={data.age_range} />
            <DemographicItem icon={Users} label="Gender" value={data.gender} />
            <DemographicItem
              icon={Briefcase}
              label="Profession"
              value={data.profession}
            />
            <DemographicItem
              icon={DollarSign}
              label="Income"
              value={data.household_income}
            />
          </div>

          {/* 2x2 Grid for Attributes */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Needs */}
            <SectionBlock
              title="Needs"
              items={needs}
              icon={Target}
              color="text-indigo-600"
              bulletColor="bg-indigo-600"
            />

            {/* Frustrations */}
            <SectionBlock
              title="Frustrations"
              items={frustrations}
              icon={AlertOctagon}
              color="text-red-500"
              bulletColor="bg-red-500"
            />

            {/* Value Drivers */}
            <SectionBlock
              title="Value Drivers"
              items={valueDrivers}
              icon={Zap}
              color="text-amber-500"
              bulletColor="bg-amber-500"
            />

            {/* Delights */}
            <SectionBlock
              title="Delights"
              items={delights}
              icon={Heart}
              color="text-pink-500"
              bulletColor="bg-pink-500"
            />
          </div>
        </div>

        {/* Right Column: Archetype & Stats (2/5 width) */}
        <div className="lg:col-span-2 flex flex-col gap-6">
          <div className="bg-slate-50 p-6 rounded-2xl border border-slate-100 h-full flex flex-col gap-6">
            {/* Archetype Showcase */}
            <div>
              <p className="text-xs font-black text-slate-400 uppercase tracking-widest mb-1">
                PERSONA ARCHETYPE
              </p>
              <h2 className="text-3xl font-black text-slate-800 leading-tight">
                {archetype}
              </h2>
              <div className="h-1 w-20 bg-indigo-500 mt-4 mb-2" />
            </div>

            {/* Platform Icons (New) */}
            <div>
              <p className="text-xs font-bold text-slate-400 uppercase tracking-widest mb-3">
                PREFERRED PLATFORMS
              </p>
              <div className="flex gap-3 flex-wrap">
                {platforms.map((p: string) => (
                  <PlatformIcon key={p} name={p} />
                ))}
              </div>
            </div>

            {/* Sliders */}
            <div className="space-y-5 pt-4 border-t border-slate-200">
              {sliders.map((s) => (
                <div key={s.label}>
                  <div className="flex justify-between items-center mb-1">
                    <span className="text-xs font-bold text-slate-600 flex items-center gap-2">
                      <s.icon size={12} className="opacity-50" /> {s.label}
                    </span>
                  </div>
                  <div className="h-2 w-full bg-slate-200 rounded-full overflow-hidden">
                    <div
                      className={`h-full ${s.color} transition-all duration-1000 ease-out`}
                      style={{ width: `${s.value}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Footer / Expandable Deep Dive */}
      <div className="bg-slate-50 px-6 py-3 border-t border-slate-200 rounded-b-3xl">
        <button
          onClick={() => setExpanded(!expanded)}
          className="w-full flex items-center justify-center gap-2 text-xs font-bold text-slate-500 uppercase hover:text-indigo-600 transition-colors"
        >
          {expanded ? "Hide Deep Dive" : "View Buying Behavior & Content"}
          {expanded ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
        </button>

        {expanded && (
          <div className="mt-6 grid grid-cols-2 gap-6 pb-4 animate-in fade-in slide-in-from-top-2">
            <div>
              <h4 className="font-black text-slate-900 mb-2">Psychographics</h4>
              <p className="text-sm text-slate-600">
                <span className="font-bold">Values:</span>{" "}
                {data.psychographics?.values?.join(", ")}
              </p>
              <p className="text-sm text-slate-600 mt-2">
                <span className="font-bold">Motivations:</span>{" "}
                {data.psychographics?.motivations?.join(", ")}
              </p>
            </div>
            <div>
              <h4 className="font-black text-slate-900 mb-2">
                Content Strategy
              </h4>
              <p className="text-sm text-slate-600">
                <span className="font-bold">Formats:</span>{" "}
                {contentConsumption?.join(", ")}
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

// --- Subcomponents ---

const getRoleBadgeColor = (role: string) => {
  const r = (role || "").toLowerCase();
  if (r.includes("primary")) return "bg-green-500 text-white border-green-400";
  if (r.includes("influencer"))
    return "bg-purple-500 text-white border-purple-400";
  if (r.includes("decision")) return "bg-blue-600 text-white border-blue-500";
  if (r.includes("end user"))
    return "bg-orange-500 text-white border-orange-400";
  return "bg-slate-700 text-slate-200 border-slate-600";
};

const SectionBlock = ({
  title,
  items,
  icon: Icon,
  color,
  bulletColor,
}: any) => (
  <div className="p-4 rounded-xl hover:bg-slate-50 transition-colors duration-300">
    <h4
      className={`text-base font-bold mb-3 flex items-center gap-2 ${color} uppercase tracking-wider text-xs`}
    >
      <Icon size={14} />
      {title}
    </h4>
    <ul className="space-y-2">
      {items.map((item: string, i: number) => (
        <li
          key={i}
          className="flex items-start gap-2 text-slate-600 font-medium text-sm leading-relaxed hover:text-slate-900 transition-colors"
        >
          <span
            className={`mt-1.5 w-1.5 h-1.5 rounded-full ${bulletColor} flex-shrink-0 opacity-60`}
          />
          {item}
        </li>
      ))}
    </ul>
  </div>
);

const PlatformIcon = ({ name }: { name: string }) => {
  // Simple mapping
  const n = name.toLowerCase();
  let Icon = Globe;
  let color = "text-slate-400";

  if (n.includes("instagram")) {
    Icon = Instagram;
    color = "text-pink-600";
  } else if (n.includes("facebook")) {
    Icon = Facebook;
    color = "text-blue-600";
  } else if (n.includes("linkedin")) {
    Icon = Linkedin;
    color = "text-blue-700";
  } else if (n.includes("twitter") || n.includes("x")) {
    Icon = Twitter;
    color = "text-slate-900";
  } else if (n.includes("youtube")) {
    Icon = Youtube;
    color = "text-red-600";
  }

  return (
    <div
      className="p-2 bg-white rounded-lg border border-slate-100 shadow-sm flex items-center justify-center group relative cursor-help"
      title={name}
    >
      <Icon size={20} className={color} />
      <Tooltip text={name} />
    </div>
  );
};

const Tooltip = ({ text }: { text: string }) => (
  <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 px-3 py-1.5 bg-slate-900 text-white text-xs font-semibold rounded-lg shadow-xl opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap pointer-events-none z-50">
    {text}
    <div className="absolute top-full left-1/2 -translate-x-1/2 border-4 border-transparent border-t-slate-900" />
  </div>
);

const DemographicItem = ({ icon: Icon, label, value }: any) => (
  <div className="flex flex-col group relative cursor-help">
    <span className="text-[10px] uppercase font-bold text-slate-400 flex items-center gap-1 mb-1">
      <Icon size={10} /> {label}
    </span>
    <span className="text-sm font-bold text-slate-800 truncate">{value}</span>
    {/* Custom Tooltip */}
    <Tooltip text={value} />
  </div>
);
