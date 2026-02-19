import requests
import json

class AIEngine:
    def __init__(self, model="granite:3.3-2b", base_url="http://localhost:11434/api/generate"):
        self.model = model
        self.base_url = base_url

    def analyze_project(self, project_data):
        """Use IBM Granite to provide AI-powered construction insights."""
        prompt = f"""
        Analyze the following construction project parameters and provide professional advice:
        - Built-up Area: {project_data['area']} sq yards
        - Number of Floors: {project_data['floors']}
        - Target Timeline: {project_data.get('timeline', 'Not specified')} days
        
        Provide a concise analysis including:
        1. Potential construction challenges for this scale.
        2. Recommendations for material quality.
        3. Tips for optimizing the construction schedule.
        4. Resource intensity assessment.
        
        Keep the response professional and structured.
        """
        
        try:
            response = requests.post(
                self.base_url,
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False
                },
                timeout=30
            )

            if response.status_code == 200:
                raw = response.json().get("response", "")
                # Normalize to a list of bullet points if possible
                lines = [ln.strip(' •\n') for ln in raw.splitlines() if ln.strip()]
                if len(lines) == 0 and raw:
                    # try splitting by sentences
                    lines = [s.strip() for s in raw.split('.') if s.strip()]
                return {"ok": True, "insights": lines, "raw": raw}
            else:
                return {"ok": False, "error": "Error connecting to local AI model. Please ensure Ollama is running."}
        except Exception as e:
            return {"ok": False, "error": f"AI Integration Error: {str(e)}"}

    def generate_weekly_schedule(self, project_data):
        """Generate a high-level weekly schedule using AI."""
        prompt = f"""
        Create a week-by-week construction schedule for a {project_data['area']} sq yard, {project_data['floors']}-floor building.
        Total estimated duration: {project_data.get('estimated_days', 90)} days.
        
        List key activities for each week from site preparation to final finishing.
        Format as a simple list.
        """
        
        try:
            response = requests.post(
                self.base_url,
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False
                },
                timeout=30
            )

            if response.status_code == 200:
                raw = response.json().get("response", "")
                # Attempt to parse simple week-by-week lines
                weeks = []
                for line in raw.splitlines():
                    if not line.strip():
                        continue
                    # Expect formats like: "Week 1: Site prep - activities"
                    parts = line.split(':', 1)
                    if len(parts) == 2 and parts[0].strip().lower().startswith('week'):
                        week_label = parts[0].strip()
                        phase_activities = parts[1].strip()
                        # split phase and activities if hyphenated
                        if ' - ' in phase_activities:
                            phase, acts = phase_activities.split(' - ', 1)
                            activities = [a.strip() for a in acts.split(',') if a.strip()]
                        else:
                            phase = phase_activities
                            activities = []
                        try:
                            week_num = int(''.join(filter(str.isdigit, week_label)))
                        except Exception:
                            week_num = None
                        weeks.append({"week": week_num, "phase": phase.strip(), "activities": activities})
                return {"ok": True, "weeks": weeks, "raw": raw}
            else:
                return {"ok": False, "error": "Error connecting to AI model."}
        except Exception as e:
            return {"ok": False, "error": f"Failed to generate schedule via AI: {e}"}
