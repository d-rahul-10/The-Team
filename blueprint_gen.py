class BlueprintGenerator:
    def __init__(self, area_sq_ft):
        self.area_sq_ft = area_sq_ft

    def generate_layout(self):
        """Generate a basic room layout based on total area."""
        # Simple heuristic for room distribution
        if self.area_sq_ft < 1000:
            rooms = {
                "Living Room": "12' x 14'",
                "Bedroom": "10' x 12'",
                "Kitchen": "8' x 10'",
                "Bathroom": "5' x 8'"
            }
        elif self.area_sq_ft < 2500:
            rooms = {
                "Living Room": "15' x 18'",
                "Master Bedroom": "12' x 15'",
                "Bedroom 2": "11' x 13'",
                "Kitchen": "10' x 12'",
                "Dining Area": "10' x 10'",
                "Bathroom 1": "6' x 8'",
                "Bathroom 2": "5' x 7'"
            }
        else:
            rooms = {
                "Living Room": "20' x 24'",
                "Master Bedroom": "14' x 18'",
                "Bedroom 2": "12' x 15'",
                "Bedroom 3": "12' x 14'",
                "Kitchen": "12' x 14'",
                "Dining Room": "12' x 12'",
                "Guest Room": "11' x 13'",
                "Bathroom 1": "7' x 9'",
                "Bathroom 2": "6' x 8'",
                "Bathroom 3": "5' x 7'"
            }
            
        return {
            "total_area": f"{self.area_sq_ft} sq ft",
            "suggested_rooms": rooms,
            "notes": "Dimensions are approximate and subject to local building codes."
        }
