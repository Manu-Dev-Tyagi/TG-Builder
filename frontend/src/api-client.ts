/**
 * TG Builder API Client
 * Drop-in TypeScript client for frontend integration
 */

const API_BASE_URL = "http://localhost:8000";

// ============================================================================
// Type Definitions
// ============================================================================

export interface BrandInput {
  brand_name: string;
  product_category: string;
  price_positioning: "Low" | "Mid" | "Premium";
  geography: string;
  primary_usp: string;
  primary_objective: "Purchase" | "Leads" | "Awareness" | "App Install";
  age_ranges?: string[];
  cities?: string[];
  professions?: string[];
  known_audience_insights?: string;
}

export interface ProjectResponse {
  project_id: string;
}

export interface GenerationResponse {
  status: string;
  project_id: string;
  personas_selected: number;
  artifacts: Array<{
    name: string;
    required: boolean;
    status: string;
    error: string | null;
  }>;
  blocking_errors: string[];
  logs: string[];
}

export interface Persona {
  id: string;
  persona_id: string;
  project_id: string;
  rank: number;
  role_in_portfolio: string;
  funnel_stage: string;
  recommended_platforms: string[];
  notes: string;
  reason: string;
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

export interface Campaign {
  id: string;
  project_id: string;
  persona_id: string;
  platform: string;
  funnel_stage: string;
  targeting_data: MetaAdset[];
  created_at: string;
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
    splits: Array<{
      structure_type: string;
      name: string;
      funnel_stage: string;
      alloc_percentage: number;
      daily_budget: number;
    }>;
    rules: Array<{
      name: string;
      condition: string;
      action: string;
      trigger_type: string;
    }>;
  };
  created_at: string;
}

export interface ResultsResponse {
  personas: Persona[];
  campaigns: Campaign[];
  budget: BudgetPlan | null;
}

// ============================================================================
// API Client
// ============================================================================

class TGBuilderAPI {
  private baseUrl: string;

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl;
  }

  /**
   * Generic fetch wrapper with error handling
   */
  private async request<T>(
    endpoint: string,
    options: RequestInit = {},
  ): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;

    try {
      const response = await fetch(url, {
        ...options,
        headers: {
          "Content-Type": "application/json",
          ...options.headers,
        },
      });

      if (!response.ok) {
        const error = await response
          .json()
          .catch(() => ({ detail: "Request failed" }));
        throw new Error(error.detail || `HTTP ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error(`API Error [${endpoint}]:`, error);
      throw error;
    }
  }

  /**
   * Health check
   */
  async healthCheck(): Promise<{ status: string; version: string }> {
    return this.request("/");
  }

  /**
   * Create a new project
   */
  async createProject(name: string): Promise<ProjectResponse> {
    return this.request("/projects", {
      method: "POST",
      body: JSON.stringify({ name }),
    });
  }

  /**
   * Save brand inputs for a project
   */
  async saveInputs(
    projectId: string,
    brandInput: BrandInput,
  ): Promise<ProjectResponse> {
    return this.request("/inputs", {
      method: "POST",
      body: JSON.stringify({
        project_id: projectId,
        brand_input: brandInput,
      }),
    });
  }

  /**
   * Generate targeting blueprint (long-running: 5-15 seconds)
   */
  async generate(projectId: string): Promise<GenerationResponse> {
    return this.request("/generate", {
      method: "POST",
      body: JSON.stringify({ project_id: projectId }),
    });
  }

  /**
   * Get all results for a project
   */
  async getResults(projectId: string): Promise<ResultsResponse> {
    return this.request(`/projects/${projectId}/results`);
  }

  /**
   * Complete flow: Create → Save Inputs → Generate
   *
   * Usage:
   *   const result = await api.runCompleteFlow("My Project", brandInput);
   *   navigate(`/results/${result.project_id}`);
   */
  async runCompleteFlow(
    projectName: string,
    brandInput: BrandInput,
  ): Promise<GenerationResponse> {
    // Step 1: Create project
    const { project_id } = await this.createProject(projectName);

    // Step 2: Save inputs
    await this.saveInputs(project_id, brandInput);

    // Step 3: Generate
    const result = await this.generate(project_id);

    return result;
  }
}

// ============================================================================
// Singleton Instance (import this)
// ============================================================================

export const tgBuilderAPI = new TGBuilderAPI();
