import re
from file_manager import load_rules_json, load_crops_csv


class KnowledgeEngine:
    def __init__(self):
        self.reload()

    def reload(self):
        self.rules = load_rules_json()
        self.crops = load_crops_csv()

    @staticmethod
    def _normalise(text):
        return re.sub(r"\s+", " ", str(text).strip().lower())

    def diagnose_plant(self, crop, symptoms_input):
        crop_norm = self._normalise(crop)
        symptom_text = self._normalise(symptoms_input)
        user_symptoms = [s.strip() for s in re.split(r"[,;\n]+", symptom_text) if s.strip()]
        results = []
        for rule in self.rules:
            if self._normalise(rule.get("crop", "")) != crop_norm:
                continue
            matched = []
            for symptom in rule.get("symptoms", []):
                candidate = self._normalise(symptom)
                if candidate and any(candidate in entered or entered in candidate for entered in user_symptoms):
                    matched.append(symptom)
            if matched:
                results.append({
                    "diagnosis": rule.get("diagnosis", "Unknown diagnosis"),
                    "treatment": rule.get("treatment", "No treatment guidance recorded."),
                    "matched_symptoms": matched,
                    "rule_id": rule.get("id", ""),
                    "crop": rule.get("crop", crop),
                })
        return results

    def recommend_crops(self, season, soil_type):
        season_norm, soil_norm = self._normalise(season), self._normalise(soil_type)
        return [crop for crop in self.crops
                if self._normalise(crop.get("season", "")) == season_norm
                and self._normalise(crop.get("soil_type", "")) == soil_norm]

    def analyze_iot_data(self, temp, humidity, soil_moisture):
        advisories = []
        if soil_moisture < 30:
            advisories.append({"level": "High", "message": "Soil moisture is below 30%. Check the sensor and assess whether irrigation is needed."})
        elif soil_moisture > 80:
            advisories.append({"level": "Warning", "message": "Soil moisture is above 80%. Check drainage and avoid adding water until the reading is verified."})
        else:
            advisories.append({"level": "Info", "message": "Soil moisture is within this prototype's configured range (30–80%). Crop-specific needs may differ."})
        if temp > 35:
            advisories.append({"level": "Warning", "message": "Temperature is above 35°C. Check crop-specific heat guidance and consider reducing heat stress where practical."})
        elif temp < 10:
            advisories.append({"level": "Warning", "message": "Temperature is below 10°C. Check the crop's cold sensitivity and local frost forecast."})
        else:
            advisories.append({"level": "Info", "message": "Temperature did not cross the prototype's configured high/low alert thresholds."})
        if humidity > 85:
            advisories.append({"level": "Warning", "message": "Air humidity is above 85%. Inspect plants for disease symptoms and support airflow where appropriate; this reading alone does not diagnose disease."})
        else:
            advisories.append({"level": "Info", "message": "Air humidity did not cross the prototype's configured alert threshold."})
        return advisories
