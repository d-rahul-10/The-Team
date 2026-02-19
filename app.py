from flask import Flask, render_template, request, jsonify
import requests
import time
import math
from ai_engine import AIEngine
from calculator import ConstructionCalculator

app = Flask(__name__)

# ================= CONFIGURATION =================
# ⚠️ IMPORTANT: Run 'ollama list' in terminal and match this name exactly
# Common names: "granite3.3:2b" or "granite:3.3-2b"
MODEL_ID = "granite3.3:2b" 
OLLAMA_API_URL = "http://localhost:11434/api/generate"

print("="*70)
print("Construction Planning System")
print(f" Model: {MODEL_ID}")
print(" Running locally via Ollama")
print("="*70)

# Initialize AI engine (used as primary AI interface)
AI_ENGINE = AIEngine(model=MODEL_ID, base_url=OLLAMA_API_URL)

# Using unified ConstructionCalculator from calculator.py

# ================= AI INTEGRATION (OLLAMA) =================
def get_ai_insight(project_data):
    """Call the `AIEngine` and provide a safe fallback if the model is unreachable.

    The `AIEngine` expects keys like `area` and `floors` — map the project_data
    coming from the API to that shape and use the engine. If the engine reports
    an error or returns an empty response, return the canned recommendations.
    """
    # Map to ai_engine expected keys
    ai_payload = {
        "area": project_data.get("built_up_area"),
        "floors": project_data.get("floors"),
        "timeline": project_data.get("duration_days") or project_data.get("duration_weeks")
    }

    try:
        insight = AI_ENGINE.analyze_project(ai_payload)
        # Expect structured dict: {ok: bool, insights: [...], raw: '...'}
        if isinstance(insight, dict) and insight.get("ok"):
            return insight
        else:
            raise RuntimeError(insight.get('error') if isinstance(insight, dict) else 'AI returned invalid response')
    except Exception as e:
        print(f"⚠️ AI Engine fallback activated: {e}")

    # Fallback canned recommendations
    return (
        "• 🛡️ Risk: Monitor weather forecasts before concrete pouring to avoid curing issues.\n"
        "• 💰 Cost: Lock in material prices early to mitigate market fluctuation risks.\n"
        "• ⏱️ Timeline: Add a 5-day buffer for regulatory inspections and approvals.\n"
        "(AI Model Offline - Showing Standard Recommendations)"
    )

# ================= ROUTES =================
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/calculate", methods=["POST"])
def api_calculate():
    try:
        data = request.json
        calculator = ConstructionCalculator(
            built_up_area=data.get("built_up_area", 1000),
            floors=data.get("floors", "G+2"),
            daily_wage=data.get("daily_wage"),
            cost_per_sq_yard=data.get("cost_per_sq_yard")
        )
        
        workers = calculator.calculate_workers()
        costs = calculator.calculate_costs(workers)
        
        # Prepare data for AI
        ai_input = {
            "built_up_area": data.get("built_up_area"),
            "floors": data.get("floors"),
            "total_cost": costs['total_cost'],
            "duration_weeks": costs['duration_weeks']
        }
        
        # Get AI Insight (with fallback)
        ai_insight = get_ai_insight(ai_input)
        # Try AI-generated weekly schedule, fallback to algorithmic schedule
        try:
            ai_schedule_payload = {
                "area": data.get("built_up_area"),
                "floors": data.get("floors"),
                "estimated_days": costs.get('duration_days')
            }
            ai_schedule_resp = AI_ENGINE.generate_weekly_schedule(ai_schedule_payload)
            if isinstance(ai_schedule_resp, dict) and ai_schedule_resp.get('ok') and ai_schedule_resp.get('weeks'):
                schedule = ai_schedule_resp.get('weeks')
            else:
                schedule = calculator.generate_schedule()
        except Exception:
            schedule = calculator.generate_schedule()

        result = {
            "workers": workers,
            "total_workers": sum(workers.values()),
            "materials": calculator.calculate_materials(),
            "costs": costs,
            "blueprint": calculator.generate_blueprint(room_options=data.get('room_options')), 
            "schedule": schedule,
            "ai_insight": ai_insight,
            "assumptions": {
                "location": "India",
                "cost_per_sq_yard": calculator.COST_PER_SQ_YARD,
                "overhead_percentage": calculator.OVERHEAD_PERCENTAGE
            }
        }
        return jsonify(result), 200
    except Exception as e:
        print(f"❌ Backend Error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/health")
def health():
    return jsonify({"status": "healthy", "system": "Construction Planning System", "timestamp": time.time()})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
