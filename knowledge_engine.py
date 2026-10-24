from file_manager import load_rules_json, load_crops_csv

class KnowledgeEngine:
    def __init__(self):
        self.rules = load_rules_json()
        self.crops = load_crops_csv()

    def reload(self):
        self.rules = load_rules_json()
        self.crops = load_crops_csv()

    def diagnose_plant(self, crop, symptoms_input):
        matched_diagnoses = []
        user_symptoms = [s.strip().lower() for s in symptoms_input.split(',')]

        for rule in self.rules:
            if rule['crop'].lower() == crop.lower():
                rule_symptoms = [s.lower() for s in rule['symptoms']]
                matches = set(user_symptoms).intersection(set(rule_symptoms))
                if matches:
                    matched_diagnoses.append({
                        'diagnosis': rule['diagnosis'],
                        'treatment': rule['treatment'],
                        'matched_symptoms': list(matches)
                    })
        return matched_diagnoses

    def recommend_crops(self, season, soil_type):
        suitable_crops = []
        for crop in self.crops:
            if crop['season'].lower() == season.lower() and crop['soil_type'].lower() == soil_type.lower():
                suitable_crops.append(crop)
        return suitable_crops

    def analyze_iot_data(self, temp, humidity, soil_moisture):
        """IoT Advisory System Integration"""
        advisories = []
        
        # تحليل رطوبة التربة (Soil Moisture Analysis)
        if soil_moisture < 30:
            advisories.append("🚨 Critical: Soil moisture is very low (<30%). Immediate irrigation required!")
        elif soil_moisture > 80:
            advisories.append("⚠️ Warning: Soil moisture is too high (>80%). Reduce watering to prevent root rot.")
        else:
            advisories.append("✅ Soil moisture level is optimal.")

        # تحليل الحرارة والرطوبة (Temperature & Air Humidity Analysis)
        if temp > 35:
            advisories.append("🌡️ Heat Stress Alert: Temperature exceeds 35°C. Provide shading or light misting.")
        elif temp < 10:
            advisories.append("❄️ Frost Alert: Temperature below 10°C. Protect cold-sensitive plants.")
            
        if humidity > 85:
            advisories.append("🍄 Fungal Risk: High atmospheric humidity (>85%) increases risk of blight/mildew.")

        return advisories