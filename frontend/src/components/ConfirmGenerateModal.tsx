import React from "react";
import { AlertTriangle, Lock, X } from "lucide-react";

interface ConfirmGenerateModalProps {
  isOpen: boolean;
  onConfirm: () => void;
  onCancel: () => void;
  isLoading?: boolean;
}

export const ConfirmGenerateModal: React.FC<ConfirmGenerateModalProps> = ({
  isOpen,
  onConfirm,
  onCancel,
  isLoading = false,
}) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      {/* Backdrop */}
      <div
        className="absolute inset-0 bg-slate-900/60 backdrop-blur-sm"
        onClick={onCancel}
      />

      {/* Modal */}
      <div className="relative bg-white rounded-3xl shadow-2xl max-w-md w-full mx-4 overflow-hidden animate-in zoom-in-95 duration-200">
        {/* Header */}
        <div className="bg-amber-500 px-6 py-5 text-white">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-white/20 rounded-xl">
              <AlertTriangle size={24} />
            </div>
            <div>
              <h2 className="text-xl font-black">Confirm Generation</h2>
              <p className="text-amber-100 text-sm">
                This action is irreversible
              </p>
            </div>
          </div>
          <button
            onClick={onCancel}
            className="absolute top-4 right-4 p-2 hover:bg-white/20 rounded-full transition-colors"
            disabled={isLoading}
          >
            <X size={20} />
          </button>
        </div>

        {/* Body */}
        <div className="p-6">
          <div className="bg-amber-50 border border-amber-200 rounded-xl p-4 mb-6">
            <div className="flex gap-3">
              <Lock className="text-amber-600 flex-shrink-0 mt-0.5" size={20} />
              <div>
                <p className="text-sm font-bold text-amber-800 mb-1">
                  This will LOCK your strategy
                </p>
                <p className="text-xs text-amber-700 leading-relaxed">
                  Once generated, your inputs cannot be edited. The strategy
                  will be compiled and frozen. You'll need to create a new
                  project to try different inputs.
                </p>
              </div>
            </div>
          </div>

          <ul className="space-y-2 text-sm text-slate-600 mb-6">
            <li className="flex items-center gap-2">
              <div className="w-1.5 h-1.5 rounded-full bg-slate-400" />
              Personas will be generated and scored
            </li>
            <li className="flex items-center gap-2">
              <div className="w-1.5 h-1.5 rounded-full bg-slate-400" />
              Campaign structures will be compiled
            </li>
            <li className="flex items-center gap-2">
              <div className="w-1.5 h-1.5 rounded-full bg-slate-400" />
              Budget allocations will be finalized
            </li>
          </ul>

          {/* Actions */}
          <div className="flex gap-3">
            <button
              onClick={onCancel}
              disabled={isLoading}
              className="flex-1 px-4 py-3 border border-slate-200 text-slate-700 font-bold rounded-xl hover:bg-slate-50 transition-colors disabled:opacity-50"
            >
              Cancel
            </button>
            <button
              onClick={onConfirm}
              disabled={isLoading}
              className="flex-1 px-4 py-3 bg-indigo-600 text-white font-bold rounded-xl hover:bg-indigo-700 transition-colors disabled:opacity-50 flex items-center justify-center gap-2"
            >
              {isLoading ? (
                <>
                  <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                  Generating...
                </>
              ) : (
                <>
                  <Lock size={16} />
                  Confirm & Generate
                </>
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
