from typing import List, Dict, Any
from src.db import get_db
from src.services_read_results import ResultsReadService
from fpdf import FPDF
import os

class PlaybookAssemblerService:
    @staticmethod
    def assemble_playbook(project_id: str) -> str:
        """
        Assembles all project data into a clean, readable Markdown playbook.
        """
        data = ResultsReadService.get_final_personas(project_id)
        blueprints = ResultsReadService.get_campaign_blueprints(project_id)
        budget = ResultsReadService.get_budget_plan(project_id)
        
        # 1. Header
        playbook = f"# TG BUILDER - STRATEGY PLAYBOOK\n"
        playbook += f"Project ID: {project_id}\n\n"
        playbook += "---\n\n"
        
        # 2. Personas
        playbook += "## 👤 TARGET PERSONAS\n\n"
        for p in data:
            playbook += f"### {p['name']} (Rank #{p['rank']})\n"
            playbook += f"**Role**: {p['role_in_portfolio']}\n"
            playbook += f"**Funnel Stage**: {p['funnel_stage']}\n"
            playbook += f"**Strategy**: {p.get('campaign_type', 'N/A')}\n"
            playbook += f"**Bio**: {p['full_data'].get('profession', 'N/A')} from {p['full_data'].get('location', 'N/A')}\n\n"
            
            playbook += "#### 🎯 Targeting Clusters\n"
            # Find blueprints for this persona
            persona_blueprints = [b for b in blueprints if b['persona_id'] == p['persona_id']]
            
            for b in persona_blueprints:
                playbook += f"**Platform**: {b['platform']}\n"
                for targeting in b['targeting_data']:
                    playbook += f"- **Adset/Ad Group**: {targeting['name']}\n"
                    playbook += f"  - Funnel: {targeting['funnel_stage']}\n"
                    playbook += f"  - Placement: {targeting.get('placements', 'Auto')}\n"
                    if targeting.get('interests'):
                        playbook += f"  - Interests: {', '.join(targeting['interests'])}\n"
                    if targeting.get('keywords'):
                        playbook += f"  - Keywords: {', '.join([k['theme'] for k in targeting['keywords']])}\n"
                    if targeting.get('audience_signals'):
                        sig = targeting['audience_signals']
                        playbook += f"  - Audience Signals: {len(sig.get('in_market', []))} In-market, {len(sig.get('affinity', []))} Affinity\n"
                playbook += "\n"
                
        # 3. Budget
        if budget:
            playbook += "## 💰 BUDGET ALLOCATION\n\n"
            playbook += f"**Total Daily Budget**: ${budget['targeting_data'].get('total', 0)}\n\n"
            playbook += "| Platform | Funnel Stage | Allocation |\n"
            playbook += "| --- | --- | --- |\n"
            for split in budget['targeting_data'].get('splits', []):
                 playbook += f"| {split['structure_type']} | {split['funnel_stage']} | ${split['daily_budget']} |\n"
                 
    @staticmethod
    def generate_pdf(project_id: str) -> str:
        """
        Generates a professional PDF playbook for Growth Jockey.
        Returns the path to the temporary PDF file.
        """
        data = ResultsReadService.get_final_personas(project_id)
        blueprints = ResultsReadService.get_campaign_blueprints(project_id)
        budget = ResultsReadService.get_budget_plan(project_id)
        strategy = ResultsReadService.get_locked_strategy(project_id)
        
        pdf = FPDF()
        pdf.add_page()
        
        # --- PDF STYLE CONFIG ---
        pdf.set_font("Helvetica", "B", 24)
        pdf.set_text_color(30, 41, 59) # Slate 800
        
        # --- HEADER ---
        pdf.cell(0, 20, "AUDITABLE STRATEGY PLAYBOOK", ln=True, align="C")
        pdf.set_font("Helvetica", "", 12)
        pdf.set_text_color(100, 116, 139) # Slate 500
        pdf.cell(0, 10, f"Project: {project_id}", ln=True, align="C")
        pdf.cell(0, 10, "Targeting & Acquisition Strategy", ln=True, align="C")
        pdf.line(10, 55, 200, 55)
        pdf.ln(15)
        
        # --- STRATEGY SUMMARY ---
        pdf.set_font("Helvetica", "B", 16)
        pdf.set_text_color(79, 70, 229) # Indigo 600
        pdf.cell(0, 10, "1. Executive Strategy Lock", ln=True)
        pdf.set_font("Helvetica", "", 11)
        pdf.set_text_color(30, 41, 59)
        pdf.multi_cell(0, 8, f"Campaign Type: {strategy.get('campaign_type')}\nFunnel Depth: {strategy.get('funnel_policy')}\nStatus: {strategy.get('status')}")
        pdf.ln(5)
        
        # --- PERSONAS ---
        pdf.set_font("Helvetica", "B", 16)
        pdf.set_text_color(79, 70, 229)
        pdf.cell(0, 10, "2. Target Personas & Portfolio Role", ln=True)
        pdf.ln(5)
        
        for p in data:
            pdf.set_font("Helvetica", "B", 13)
            pdf.set_text_color(15, 23, 42)
            pdf.cell(0, 8, f"{p['name']} - Rank #{p['rank']}", ln=True)
            pdf.set_font("Helvetica", "I", 10)
            pdf.set_text_color(100, 116, 139)
            pdf.cell(0, 6, f"Role: {p['role_in_portfolio']} | Stage: {p['funnel_stage']}", ln=True)
            
            pdf.set_font("Helvetica", "", 10)
            pdf.set_text_color(30, 41, 59)
            bio = f"Demographics: {p.get('age_range', 'N/A')}, {p.get('location', 'N/A')}, {p.get('profession', 'N/A')}"
            pdf.multi_cell(0, 6, bio)
            
            # Targeting Clusters
            persona_blueprints = [b for b in blueprints if b['persona_id'] == p['persona_id']]
            if persona_blueprints:
                pdf.set_font("Helvetica", "B", 10)
                pdf.cell(0, 8, "Targeting Blueprint:", ln=True)
                pdf.set_font("Helvetica", "", 9)
                for b in persona_blueprints:
                    plat_text = f" Platform: {b['platform']}"
                    pdf.cell(0, 6, plat_text, ln=True)
                    for targeting in b['targeting_data']:
                        pdf.set_text_color(71, 85, 105)
                        pdf.cell(5) # Indent
                        
                        # Robust Access: Google uses 'intent', Meta uses 'funnel_stage'
                        stage_val = targeting.get('funnel_stage') or targeting.get('intent') or "N/A"
                        
                        pdf.cell(0, 5, f"- {targeting['name']} ({stage_val})", ln=True)
                        if targeting.get('interests'):
                            pdf.cell(10)
                            pdf.set_font("Helvetica", "I", 8)
                            pdf.multi_cell(0, 4, f"Interests: {', '.join(targeting['interests'][:10])}...")
                            pdf.set_font("Helvetica", "", 9)
            pdf.ln(5)

        # --- BUDGET ---
        if budget:
            pdf.add_page()
            pdf.set_font("Helvetica", "B", 16)
            pdf.set_text_color(79, 70, 229)
            pdf.cell(0, 10, "3. Financial Allocation Plan", ln=True)
            pdf.ln(5)
            
            total_val = budget['targeting_data'].get('total', 0)
            pdf.set_font("Helvetica", "B", 12)
            pdf.set_text_color(30, 41, 59)
            pdf.cell(0, 10, f"Total Daily Budget: Rs. {total_val:,.0f}", ln=True)
            
            # Table Header
            pdf.set_fill_color(241, 245, 249)
            pdf.set_font("Helvetica", "B", 10)
            pdf.cell(60, 10, "Stage", 1, 0, "C", True)
            pdf.cell(60, 10, "Platform", 1, 0, "C", True)
            pdf.cell(60, 10, "Daily Budget", 1, 1, "C", True)
            
            # Table Rows
            pdf.set_font("Helvetica", "", 10)
            for split in budget['targeting_data'].get('splits', []):
                pdf.cell(60, 10, str(split['funnel_stage']), 1, 0, "C")
                pdf.cell(60, 10, str(split['structure_type']), 1, 0, "C")
                pdf.cell(60, 10, f"Rs. {split['daily_budget']:,.0f}", 1, 1, "C")
            
            # Rationale
            if budget['targeting_data'].get('rationale'):
                pdf.ln(10)
                pdf.set_font("Helvetica", "B", 11)
                pdf.cell(0, 10, "Strategic Reasoning:", ln=True)
                pdf.set_font("Helvetica", "I", 10)
                pdf.set_text_color(71, 85, 105)
                # Sanitize Unicode symbols for Helvetica
                clean_rationale = budget['targeting_data']['rationale'].replace('₹', 'Rs.')
                pdf.multi_cell(0, 6, f"\"{clean_rationale}\"")

        # Save to temp file
        file_path = f"/tmp/playbook_{project_id}.pdf"
        pdf.output(file_path)
        return file_path
