from flask import Flask, render_template, request, jsonify
from calculator import ConstructionCalculator
from ai_engine import AIEngine
from blueprint_gen import BlueprintGenerator

app = Flask(__name__)
ai_engine = AIEngine()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/plan', methods=['POST'])
def generate_plan():
    data = request.json
    area = float(data.get('area', 0))
    floors = int(data.get('floors', 1))
    timeline = data.get('timeline') # optional
    
    if area <= 0:
        return jsonify({"error": "Invalid area provided"}), 400

    # Initialize calculator
    calc = ConstructionCalculator(area, floors)
    
    # Perform calculations
    materials = calc.calculate_materials()
    labor = calc.calculate_labor(int(timeline) if timeline else None)
    costs = calc.calculate_costs()
    
    # Generate blueprint data
    bp_gen = BlueprintGenerator(area * 9) # convert sq yards to sq ft
    blueprint = bp_gen.generate_layout()
    
    # Get AI insights
    project_params = {
        "area": area,
        "floors": floors,
        "timeline": timeline,
        "estimated_days": labor["estimated_days"]
    }
    ai_insights = ai_engine.analyze_project(project_params)
    ai_schedule = ai_engine.generate_weekly_schedule(project_params)
    
    return jsonify({
        "materials": materials,
        "labor": labor,
        "costs": costs,
        "blueprint": blueprint,
        "ai_insights": ai_insights,
        "ai_schedule": ai_schedule
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
