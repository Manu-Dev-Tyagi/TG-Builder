import axios from "axios";

const API_URL = "http://localhost:8000";

export interface BrandInput {
  brand_name: string;
  product_category: string;
  price_positioning: "Low" | "Mid" | "Premium";
  geography: string;
  primary_usp: string;
  primary_objective: "Purchases" | "Leads" | "App Installs";
  // New fields for deterministic gating
  decision_speed: "Fast" | "Normal" | "Slow";
  platform_affinity: string[];
  budget_range?: string;
  price_sensitivity: "High" | "Medium" | "Low";
  // Optional fields
  age_ranges?: string[];
  cities?: string[];
  professions?: string[];
  known_audience_insights?: string;
  strategy_depth?: "classification_only" | "full_funnel";
}

export interface PlatformDecision {
  allowed: boolean;
  reason: string;
}

export interface Strategy {
  campaign_type: string;
  decision_speed: string;
  funnel_policy: "NO_TOF" | "FULL_FUNNEL";
  status: "LOCKED" | "NA_REJECTION" | "PENDING";
  notes: string;
}

export interface Persona {
  id: string;
  persona_id: string;
  project_id: string;
  name: string;
  rank: number;
  role_in_portfolio: string;
  funnel_stage: string;
  recommended_platforms: string[];
  platform_decisions: Record<string, PlatformDecision>;
  notes: string;
  campaign_type: string;
  // Demographics
  location: string;
  age_range: string;
  gender: string;
  profession: string;
  household_income: string;
  // Behavior
  psychographics: Record<string, unknown>;
  buying_behavior: Record<string, unknown>;
  // Rich fields
  archetype?: string;
  needs?: string[];
  frustrations?: string[];
  value_drivers?: string[];
  delights?: string[];
  
  digital_index?: {
    research_orientation: number;
    digital_comfort: number;
    category_maturity: number;
    shopping_intent: number;
    device_usage: string[];
    content_consumption: string[];
  };

  pain_points: string[];
  interests: string[];
  hobbies: string[];
  created_at: string;
}

export interface MetaAdset {
  name: string;
  funnel_stage: string;
  targeting_type: string;
  age_range: string;
  gender: string;
  locations: string;
  interests: string[];
  exclusions: string[];
  placements: string;
}

export interface GoogleKeyword {
  theme: string;
  match_type: "Exact" | "Phrase" | "Broad";
  keywords: string[];
}

export interface GoogleAudienceSignals {
  in_market: string[];
  affinity: string[];
  custom_segments: string[];
  demographics?: string;
}

export interface GoogleAdGroup {
  name: string;
  campaign_type: "Search" | "Performance Max" | "Demand Gen" | "Video" | "Display";
  intent: "Awareness" | "Consideration" | "Conversion";
  keywords?: GoogleKeyword[];
  audience_signals?: GoogleAudienceSignals;
}

export interface CampaignBlueprint {
  id: string;
  project_id: string;
  persona_id: string;
  platform: string;
  funnel_stage: string;
  targeting_data: MetaAdset[];
  google_adgroups?: GoogleAdGroup[];
  created_at: string;
}

export interface FunnelSplit {
  funnel_stage: string;
  daily_budget: number;
  structure_type: string;
  name: string;
  alloc_percentage: number;
}

export interface BudgetPlan {
  id: string;
  project_id: string;
  persona_id: string;
  platform: string;
  funnel_stage: string;
  targeting_data: {
    total: number;
    meta: number;
    google: number;
    splits: FunnelSplit[];
    rules: Array<{
      name: string;
      condition: string;
      action: string;
      trigger_type: string;
    }>;
    rationale?: string;
  };
  created_at: string;
}

export interface GenerationResponse {
  status: "SUCCESS" | "PARTIAL" | "FAILED";
  project_id: string;
  personas_selected: number;
  artifacts: Array<{
    name: string;
    required: boolean;
    status: "GENERATED" | "SKIPPED" | "FAILED";
    error: string | null;
  }>;
  blocking_errors: string[];
  logs: string[];
}

export interface ResultsResponse {
  strategy: Strategy;
  personas: Persona[];
  blueprints: CampaignBlueprint[];
  budget: BudgetPlan[] | null;
}

// ============================================================================
// API Client
// ============================================================================

export const api = {
  createProject: async (name: string) => {
    const res = await axios.post(`${API_URL}/projects`, { name });
    return res.data as { project_id: string };
  },

  saveInputs: async (projectId: string, inputs: BrandInput) => {
    const res = await axios.post(`${API_URL}/inputs`, {
      project_id: projectId,
      brand_input: inputs,
    });
    return res.data;
  },

  triggerGeneration: async (projectId: string): Promise<GenerationResponse> => {
    const res = await axios.post(`${API_URL}/generate`, {
      project_id: projectId,
    });
    return res.data;
  },

  getResults: async (projectId: string): Promise<ResultsResponse> => {
    const res = await axios.get(`${API_URL}/projects/${projectId}/results`);
    return res.data;
  },

  getPlaybookUrl: (projectId: string) => {
    return `${API_URL}/projects/${projectId}/playbook`;
  },
};
