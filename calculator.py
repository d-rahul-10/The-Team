import math
from blueprint_gen import generate_floor_layouts


class ConstructionCalculator:
    """Unified construction calculator.

    Inputs are given in square yards (built_up_area). Internally the class
    converts to square feet for layout/blueprint calculations but keeps
    thumb-rule rates per sq yard where appropriate.
    """

    # Defaults / constants
    DAILY_WAGE_PER_WORKER = 500
    COST_PER_SQ_YARD = 1500
    OVERHEAD_PERCENTAGE = 10

    # Thumb rules per sq yard
    STEEL_PER_SQ_YARD_KG = 3.5    # kg per sq yard
    CEMENT_PER_SQ_YARD = 1.2      # bags per sq yard
    SAND_PER_SQ_YARD_TONS = 0.6   # tons per sq yard

    def __init__(self, built_up_area, floors=1, daily_wage=None, cost_per_sq_yard=None):
        self.built_up_area_yards = float(built_up_area)
        self.built_up_area_ft = self.built_up_area_yards * 9.0
        self.num_floors = self._parse_floors(floors)
        if daily_wage:
            self.DAILY_WAGE_PER_WORKER = daily_wage
        if cost_per_sq_yard:
            self.COST_PER_SQ_YARD = cost_per_sq_yard

    def _parse_floors(self, floors):
        if isinstance(floors, int):
            return floors
        s = str(floors).upper().strip()
        if '+' in s:
            parts = s.split('+')
            try:
                return int(parts[-1]) + 1
            except Exception:
                return 1
        try:
            return int(s)
        except Exception:
            return 1

    def calculate_workers(self):
        """Estimate crew sizes based on built-up area in sq yards."""
        base_workers = math.ceil(self.built_up_area_yards / 100.0) * 2
        return {
            "masons": max(4, base_workers),
            "helpers": max(6, base_workers * 2),
            "steel_workers": max(2, math.ceil(base_workers / 2)),
            "carpenters": max(2, math.ceil(base_workers / 2)),
            "supervisors": max(1, math.ceil(self.num_floors / 2))
        }

    def calculate_materials(self):
        """Return material estimates as numeric values (no unit strings).

        Keys: cement_bags, steel_kg, steel_tons, sand_tons, aggregate_cu_ft (approx), bricks
        """
        total_area_yards = self.built_up_area_yards * self.num_floors
        cement_bags = total_area_yards * self.CEMENT_PER_SQ_YARD
        steel_kg = total_area_yards * self.STEEL_PER_SQ_YARD_KG
        steel_tons = steel_kg / 1000.0
        sand_tons = total_area_yards * self.SAND_PER_SQ_YARD_TONS
        # rough aggregates and bricks using common multipliers (per sq ft -> convert)
        total_area_ft = self.built_up_area_ft * self.num_floors
        aggregate_cu_ft = total_area_ft * 1.5
        bricks = int(total_area_ft * 8)

        return {
            "cement_bags": round(cement_bags),
            "steel_kg": round(steel_kg, 2),
            "steel_tons": round(steel_tons, 2),
            "sand_tons": round(sand_tons, 2),
            "aggregate_cu_ft": round(aggregate_cu_ft, 2),
            "bricks": bricks
        }

    def calculate_costs(self, workers_data):
        total_workers = sum(workers_data.values())
        # Productivity factor: area (sq yards) * floors / (workers * output)
        estimated_days = math.ceil((self.built_up_area_yards * self.num_floors) / (max(1, total_workers) * 5))
        if estimated_days < 30:
            estimated_days = 30

        labor_cost = total_workers * estimated_days * self.DAILY_WAGE_PER_WORKER
        material_cost = self.built_up_area_yards * self.num_floors * (self.COST_PER_SQ_YARD * 0.6)
        overhead = (labor_cost + material_cost) * (self.OVERHEAD_PERCENTAGE / 100.0)
        total_cost = labor_cost + material_cost + overhead

        return {
            "labor_cost": round(labor_cost, 2),
            "material_cost": round(material_cost, 2),
            "overhead": round(overhead, 2),
            "total_cost": round(total_cost, 2),
            "duration_days": estimated_days,
            "duration_weeks": math.ceil(estimated_days / 7.0),
            "duration_months": round(estimated_days / 30.0, 1)
        }

    def generate_blueprint(self):
        """Generate a simple floor-wise layout using `blueprint_gen.generate_floor_layouts`.

        Returns a list of dicts: [{floor: 'Ground Floor', rooms: [...]}, ...]
        """
        return generate_floor_layouts(self.built_up_area_ft, self.num_floors)

    def generate_blueprint(self, room_options=None):
        """Generate blueprint with optional `room_options` overrides.

        `room_options` is a dict mapping room keyword -> options, e.g.
        {"bedroom": {"windows":2, "door_side":"left"}, "bathroom": {"windows":0}}
        """
        return generate_floor_layouts(self.built_up_area_ft, self.num_floors, single_image=True, room_options=room_options)

    def generate_schedule(self):
        # Simple algorithmic schedule (kept for fallback)
        workers = self.calculate_workers()
        weeks = self.calculate_costs(workers)['duration_weeks']
        if weeks < 10:
            weeks = 10

        phases = [
            {"phase": "Site Preparation", "activities": ["Site clearing", "Leveling", "Temporary facilities"]},
            {"phase": "Foundation Work", "activities": ["Excavation", "Foundation laying", "Concrete curing"]},
            {"phase": "Ground Floor Slab", "activities": ["Formwork", "Reinforcement", "Concrete pouring"]},
            {"phase": "Column & Wall Construction", "activities": ["Brickwork", "Column casting"]},
            {"phase": "Floor Slab (Next Floors)", "activities": ["Formwork", "Reinforcement", "Pouring"]},
            {"phase": "Brickwork & Masonry", "activities": ["Wall laying", "Plastering prep"]},
            {"phase": "Plastering", "activities": ["Wall plastering", "Ceiling plastering"]},
            {"phase": "Electrical Fittings", "activities": ["Wiring", "Switch boards", "Light fixtures"]},
            {"phase": "Plumbing Fixtures", "activities": ["Piping", "Sanitary fittings", "Testing"]},
            {"phase": "Wall Painting", "activities": ["Primer", "Base coat", "Final color"]},
            {"phase": "Doors & Windows", "activities": ["Frame installation", "Glass fitting"]},
            {"phase": "Final Finishing", "activities": ["Cleaning", "Inspection", "Handover"]}
        ]

        schedule = []
        steps = max(1, len(phases) // weeks)
        current_week = 1
        for i in range(0, len(phases), steps):
            phase_group = phases[i:i+steps]
            if current_week > weeks:
                break
            all_activities = []
            for p in phase_group:
                all_activities.extend(p['activities'])
            schedule.append({"week": current_week, "phase": phase_group[0]['phase'], "activities": all_activities})
            current_week += 2
        return schedule
