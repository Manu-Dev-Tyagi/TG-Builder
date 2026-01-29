import React, { useEffect, useState } from "react";
import { api, type BrandInput } from "./api";
import { useNavigate } from "react-router-dom";
import { ConfirmGenerateModal } from "./components/ConfirmGenerateModal";
import {
  Sparkles,
  ChevronRight,
  Target,
  MapPin,
  DollarSign,
  Zap,
  Clock,
  Layers,
  Users,
} from "lucide-react";

import { useLifecycleLogger } from "./hooks/useLifecycleLogger";

export default function InputPage() {
  useLifecycleLogger("InputPage");
  // Strategy Input View
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [showConfirmModal, setShowConfirmModal] = useState(false);
  const [formData, setFormData] = useState<BrandInput>({
    brand_name: "",
    product_category: "",
    price_positioning: "Mid",
    geography: "",
    primary_usp: "",
    primary_objective: "Purchases",
    decision_speed: "Normal",
    platform_affinity: [],
    price_sensitivity: "Medium",
    strategy_depth: "full_funnel",
  });

  const [errors, setErrors] = useState<Record<string, string>>({});

  const handleChange = (
    e: React.ChangeEvent<
      HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement
    >,
  ) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));

    // Clear error when field is filled
    if (errors && errors[name]) {
      setErrors((prev) => ({ ...prev, [name]: "" }));
    }
  };

  const handlePlatformChange = (platform: string) => {
    setFormData((prev) => {
      const current = Array.isArray(prev.platform_affinity)
        ? prev.platform_affinity
        : [];
      const isSelected = current.includes(platform);

      const nextAffinity = isSelected
        ? current.filter((p) => p !== platform)
        : [...current, platform];

      return {
        ...prev,
        platform_affinity: nextAffinity,
      };
    });

    // Clear error if at least one selected
    setErrors((prev) => ({ ...prev, platform_affinity: "" }));
  };

  const validateForm = (): boolean => {
    const newErrors: Record<string, string> = {};

    if (!formData.brand_name.trim()) newErrors.brand_name = "Required";
    if (!formData.product_category.trim())
      newErrors.product_category = "Required";
    if (!formData.geography.trim()) newErrors.geography = "Required";
    if (!formData.primary_usp.trim()) newErrors.primary_usp = "Required";

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (validateForm()) {
      setShowConfirmModal(true);
    }
  };

  const handleConfirmGenerate = async () => {
    setLoading(true);
    try {
      const projectRes = await api.createProject(
        `Project ${formData.brand_name}`,
      );
      const pid = projectRes.project_id;
      localStorage.setItem("current_project_id", pid);
      await api.saveInputs(pid, formData);
      navigate("/generating");
    } catch (err: any) {
      console.error("Error starting project:", err);
      const errorMessage =
        err.response?.data?.detail || "Failed to start project. Check backend.";
      alert(errorMessage);
      setShowConfirmModal(false);
    } finally {
      setLoading(false);
    }
  };
  return (
    <div className="min-h-screen bg-slate-50 flex items-center justify-center p-6 relative overflow-hidden">
      {/* Decorative Background Elements - Reduced blur for better performance */}
      <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] bg-indigo-200/20 rounded-full blur-[80px] animate-float pointer-events-none" />
      <div
        className="absolute bottom-[-10%] right-[-10%] w-[40%] h-[40%] bg-purple-200/20 rounded-full blur-[80px] animate-float pointer-events-none"
        style={{ animationDelay: "2s" }}
      />

      <div className="max-w-5xl w-full grid grid-cols-1 lg:grid-cols-5 gap-8 relative z-10">
        {/* Left Side: Branding/Intro */}
        <div className="lg:col-span-2 flex flex-col justify-center text-left space-y-6">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-indigo-100 text-indigo-600 text-xs font-bold w-fit uppercase tracking-wider">
            <Zap size={14} /> Deterministic Strategy
          </div>
          <h1 className="text-5xl font-black text-slate-900 leading-[1.1] tracking-tight">
            Targeting <span className="text-indigo-600">Blueprint</span>
          </h1>
          <p className="text-lg text-slate-600 font-medium leading-relaxed">
            Build deterministic paid media strategies. No assumptions. No magic.
            Just compiled, auditable decisions.
          </p>
          <div className="space-y-4 pt-4">
            <StepItem
              icon={Target}
              text="Define brand & strategic constraints"
              active
            />
            <StepItem icon={Zap} text="Engine A locks campaign type" />
            <StepItem
              icon={Layers}
              text="Engine B compiles targeting clusters"
            />
            <StepItem icon={Sparkles} text="Review immutable playbook" />
          </div>
        </div>

        {/* Right Side: Form */}
        <div className="lg:col-span-3">
          <div className="glass-card rounded-3xl p-8 border border-white/50 shadow-2xl backdrop-blur-xl bg-white/80">
            <form onSubmit={handleSubmit} className="space-y-6">
              {/* Brand Fundamentals */}
              <div className="space-y-4">
                <h3 className="text-sm font-bold text-slate-400 uppercase tracking-widest">
                  Brand Fundamentals
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <InputGroup
                    label="Brand Name"
                    icon={Sparkles}
                    error={errors.brand_name}
                  >
                    <input
                      required
                      name="brand_name"
                      value={formData.brand_name}
                      onChange={handleChange}
                      className="form-input-premium"
                      placeholder="e.g. ZenWorkspace"
                    />
                  </InputGroup>
                  <InputGroup
                    label="Product Category"
                    icon={Target}
                    error={errors.product_category}
                  >
                    <input
                      required
                      name="product_category"
                      value={formData.product_category}
                      onChange={handleChange}
                      className="form-input-premium"
                      placeholder="e.g. Ergonomic Office Chairs"
                    />
                  </InputGroup>
                </div>
              </div>

              {/* Market Strategy */}
              <div className="space-y-4">
                <h3 className="text-sm font-bold text-slate-400 uppercase tracking-widest">
                  Commercial Reality
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <InputGroup label="Price Positioning" icon={DollarSign}>
                    <select
                      name="price_positioning"
                      value={formData.price_positioning}
                      onChange={handleChange}
                      className="form-input-premium appearance-none"
                    >
                      <option value="Low">Budget / Low</option>
                      <option value="Mid">Mid-Market</option>
                      <option value="Premium">Premium / Luxury</option>
                    </select>
                  </InputGroup>
                  <InputGroup label="Price Sensitivity" icon={Users}>
                    <select
                      name="price_sensitivity"
                      value={formData.price_sensitivity}
                      onChange={handleChange}
                      className="form-input-premium appearance-none"
                    >
                      <option value="High">High (Price-Driven)</option>
                      <option value="Medium">Medium (Value-Driven)</option>
                      <option value="Low">Low (Quality-Driven)</option>
                    </select>
                  </InputGroup>
                </div>
                <InputGroup
                  label="Geography"
                  icon={MapPin}
                  error={errors.geography}
                >
                  <input
                    required
                    name="geography"
                    value={formData.geography}
                    onChange={handleChange}
                    className="form-input-premium"
                    placeholder="e.g. Tier-1 India, USA, UK"
                  />
                </InputGroup>
              </div>

              {/* Strategic Constraints */}
              <div className="space-y-4">
                <h3 className="text-sm font-bold text-slate-400 uppercase tracking-widest">
                  Strategic Constraints
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <InputGroup label="Primary Objective" icon={Target}>
                    <select
                      name="primary_objective"
                      value={formData.primary_objective}
                      onChange={handleChange}
                      className="form-input-premium appearance-none"
                    >
                      <option value="Purchases">Purchases (Sales Focus)</option>
                      <option value="Leads">Leads (Form/Conversion)</option>
                      <option value="App Installs">
                        App Installs (Growth)
                      </option>
                    </select>
                  </InputGroup>
                  <InputGroup label="Decision Speed" icon={Clock}>
                    <select
                      name="decision_speed"
                      value={formData.decision_speed}
                      onChange={handleChange}
                      className="form-input-premium appearance-none"
                    >
                      <option value="Fast">Fast (Impulse Buy)</option>
                      <option value="Normal">Normal (Days)</option>
                      <option value="Slow">Slow (Weeks/Research)</option>
                    </select>
                  </InputGroup>
                </div>
              </div>

              {/* Core Value */}
              <div className="space-y-4">
                <h3 className="text-sm font-bold text-slate-400 uppercase tracking-widest">
                  Core Value Proposition
                </h3>
                <InputGroup label="Primary USP" error={errors.primary_usp}>
                  <textarea
                    required
                    name="primary_usp"
                    value={formData.primary_usp}
                    onChange={handleChange}
                    className="form-input-premium h-24 resize-none pt-3"
                    placeholder="Why do people buy this? e.g. 'Science-backed relief from chronic back pain'"
                  />
                </InputGroup>
              </div>

              {/* Strategy Depth Toggle */}
              <div className="bg-slate-50 rounded-xl p-4 border border-slate-200">
                <label className="flex items-center gap-3 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={formData.strategy_depth === "full_funnel"}
                    onChange={(e) =>
                      setFormData({
                        ...formData,
                        strategy_depth: e.target.checked
                          ? "full_funnel"
                          : "classification_only",
                      })
                    }
                    className="w-5 h-5 rounded border-slate-300 text-indigo-600 focus:ring-indigo-500"
                  />
                  <div>
                    <span className="font-bold text-slate-700">
                      Full Funnel Mode
                    </span>
                    <p className="text-xs text-slate-500">
                      Generate complete targeting clusters and keyword themes
                    </p>
                  </div>
                </label>
              </div>

              <button
                type="submit"
                disabled={loading}
                className="w-full premium-gradient hover:opacity-90 text-white font-bold py-4 px-6 rounded-2xl transition-all flex items-center justify-center gap-2 shadow-xl shadow-indigo-200 hover:shadow-indigo-300 transform active:scale-[0.98] mt-4"
              >
                {loading ? "INITIALIZING..." : "GENERATE BLUEPRINT"}
                {!loading && <ChevronRight size={20} />}
              </button>

              <p className="text-xs text-center text-slate-400 mt-2">
                This system does not assume missing intent. All fields are
                validated.
              </p>
            </form>
          </div>
        </div>
      </div>

      {/* Confirmation Modal */}
      <ConfirmGenerateModal
        isOpen={showConfirmModal}
        onConfirm={handleConfirmGenerate}
        onCancel={() => setShowConfirmModal(false)}
        isLoading={loading}
      />

      <style>{`
        .form-input-premium {
          width: 100%;
          padding: 0.75rem 1rem;
          background: #ffffff;
          border: 1.5px solid #e2e8f0;
          border-radius: 1rem;
          font-size: 0.875rem;
          color: #1e293b;
          transition: all 0.2s;
          outline: none;
        }
        .form-input-premium:focus {
          border-color: #6366f1;
          background: #ffffff;
          box-shadow: 0 0 0 4px rgba(99, 102, 241, 0.1);
        }
        .premium-gradient {
          background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
        }
        @keyframes float {
          0%, 100% { transform: translateY(0); }
          50% { transform: translateY(-20px); }
        }
        .animate-float { animation: float 6s ease-in-out infinite; }
      `}</style>
    </div>
  );
}

const StepItem = ({ icon: Icon, text, active }: any) => (
  <div
    className={`flex items-center gap-3 transition-all duration-500 ${active ? "opacity-100 translate-x-0" : "opacity-40 -translate-x-2"}`}
  >
    <div
      className={`p-2 rounded-xl ${active ? "bg-indigo-600 text-white shadow-lg" : "bg-slate-200 text-slate-500"}`}
    >
      <Icon size={18} />
    </div>
    <span className="text-sm font-bold tracking-tight text-slate-700">
      {text}
    </span>
  </div>
);

const InputGroup = ({ label, children, icon: Icon, error }: any) => (
  <div className="space-y-1.5 flex-1">
    <div className="flex items-center gap-2 mb-1 pl-1">
      {Icon && <Icon size={14} className="text-indigo-400" />}
      <label className="text-[11px] font-black uppercase tracking-widest text-slate-500">
        {label}
      </label>
      {error && (
        <span className="text-red-500 text-[10px] font-medium ml-auto">
          {error}
        </span>
      )}
    </div>
    {children}
  </div>
);
