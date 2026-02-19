import math

class ConstructionCalculator:
    def __init__(self, area_sq_yards, floors=1):
        self.area_sq_yards = area_sq_yards
        self.area_sq_ft = area_sq_yards * 9
        self.floors = floors

    def calculate_materials(self):
        """Estimate basic materials based on square footage."""
        # Standard estimation constants per sq ft
        cement_bags = self.area_sq_ft * 0.4 * self.floors
        steel_kg = self.area_sq_ft * 4 * self.floors
        sand_cu_ft = self.area_sq_ft * 1.2 * self.floors
        aggregate_cu_ft = self.area_sq_ft * 1.5 * self.floors
        bricks = self.area_sq_ft * 8 * self.floors
        
        return {
            "cement": round(cement_bags, 2),
            "steel": round(steel_kg, 2),
            "sand": round(sand_cu_ft, 2),
            "aggregate": round(aggregate_cu_ft, 2),
            "bricks": round(bricks)
        }

    def calculate_labor(self, timeline_days=None):
        """Estimate labor requirements."""
        total_man_days = self.area_sq_ft * 0.3 * self.floors
        
        if timeline_days:
            # If timeline is constrained, we need more workers
            workers_needed = math.ceil(total_man_days / timeline_days)
        else:
            # Standard crew size for the area
            workers_needed = math.ceil(self.area_sq_ft / 500) + 2
            timeline_days = math.ceil(total_man_days / workers_needed)

        # Breakdown of labor types (approximate percentages)
        return {
            "total_man_days": round(total_man_days),
            "estimated_days": timeline_days,
            "masons": math.ceil(workers_needed * 0.2),
            "helpers": math.ceil(workers_needed * 0.4),
            "steel_workers": math.ceil(workers_needed * 0.15),
            "carpenters": math.ceil(workers_needed * 0.15),
            "supervisors": 1 if workers_needed < 15 else 2
        }

    def calculate_costs(self, rates=None):
        """Estimate costs based on current market rates."""
        if not rates:
            rates = {
                "cement": 400,    # per bag
                "steel": 70,      # per kg
                "sand": 50,       # per cu ft
                "bricks": 10,     # per brick
                "labor": 800      # average per man-day
            }
            
        materials = self.calculate_materials()
        labor = self.calculate_labor()
        
        material_cost = (
            materials["cement"] * rates["cement"] +
            materials["steel"] * rates["steel"] +
            materials["sand"] * rates["sand"] +
            materials["bricks"] * rates["bricks"]
        )
        
        labor_cost = labor["total_man_days"] * rates["labor"]
        overhead = (material_cost + labor_cost) * 0.10
        
        total_cost = material_cost + labor_cost + overhead
        
        return {
            "material_cost": round(material_cost, 2),
            "labor_cost": round(labor_cost, 2),
            "overhead": round(overhead, 2),
            "total_cost": round(total_cost, 2),
            "cost_per_sq_yard": round(total_cost / self.area_sq_yards, 2)
        }
