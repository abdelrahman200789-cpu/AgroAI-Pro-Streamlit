from ir_engine import SimpleIRSystem
from knowledge_engine import KnowledgeEngine
import file_manager as fm

def farmer_interface(ke, ir_sys):
    print("\n--- 🌾 FARMER / USER INTERFACE ---")
    print("1. Diagnose Plant Problem")
    print("2. Find Suitable Crops for Season & Soil")
    print("3. Search Knowledge Base (Text Search)")
    print("4. IoT Environmental Smart Monitor (Sensors Data)")
    choice = input("Select an option (1-4): ")

    if choice == '1':
        crop = input("Enter Crop Name (e.g., Tomato, Wheat): ")
        symptoms = input("Enter Symptoms (comma separated, e.g., yellow spots, dark spots): ")
        results = ke.diagnose_plant(crop, symptoms)
        
        fm.log_event(f"Farmer Diagnosis Query: Crop={crop}, Symptoms={symptoms}")
        
        print("\n--- Diagnosis Results ---")
        if results:
            for idx, res in enumerate(results, 1):
                print(f"{idx}. Diagnosis: {res['diagnosis']}")
                print(f"   Treatment: {res['treatment']}")
                print(f"   Matched Symptoms: {', '.join(res['matched_symptoms'])}\n")
        else:
            print("No exact rule matched. Searching descriptive documents...\n")
            search_res = ir_sys.search(f"{crop} {symptoms}")
            if search_res:
                print("Relevant Guides Found:")
                for doc_id, content, score in search_res:
                    print(f"[{doc_id}] (Score: {score:.2f})\n{content}\n")
            else:
                print("No diagnosis or guides found.")

    elif choice == '2':
        season = input("Enter Season (Summer/Winter): ")
        soil = input("Enter Soil Type (Loamy/Clay/Sandy): ")
        suitable = ke.recommend_crops(season, soil)
        
        fm.log_event(f"Crop Recommendation Query: Season={season}, Soil={soil}")
        
        print(f"\n--- Recommended Crops for {season} & {soil} ---")
        if suitable:
            for item in suitable:
                print(f"- Crop: {item['crop_name']} | Ideal Temp: {item['recommended_temp']}")
        else:
            print("No exact match found in database.")

    elif choice == '3':
        query = input("Enter search terms: ")
        results = ir_sys.search(query)
        fm.log_event(f"IR Search Query: {query}")
        
        print("\n--- Search Results (TF-IDF + Cosine Similarity) ---")
        for doc_id, text, score in results:
            print(f"📄 Document: {doc_id} | Similarity: {score:.4f}")
            print(f"   Content: {text}\n")

    elif choice == '4':
        print("\n--- 🌡️ IoT Sensor Readings Analysis ---")
        try:
            temp = float(input("Enter Temperature (°C): "))
            humidity = float(input("Enter Air Humidity (%): "))
            moisture = float(input("Enter Soil Moisture (%): "))
            
            advisories = ke.analyze_iot_data(temp, humidity, moisture)
            fm.log_event(f"IoT Analysis: Temp={temp}, Humidity={humidity}, Moisture={moisture}")
            
            print("\n--- 📡 IoT System Recommendations ---")
            for adv in advisories:
                print(adv)
        except ValueError:
            print("Invalid numerical input for IoT sensors!")

def expert_interface(ke):
    print("\n--- 🛠️ EXPERT / ADMIN INTERFACE ---")
    print("1. Add New Rule")
    print("2. Add New Crop Entry")
    choice = input("Select an option (1-2): ")

    if choice == '1':
        crop = input("Crop Name: ")
        symptoms_str = input("Symptoms (comma separated): ")
        diagnosis = input("Diagnosis: ")
        treatment = input("Treatment: ")

        symptoms = [s.strip() for s in symptoms_str.split(',')]
        rules = fm.load_rules_json()
        new_rule = {
            "id": f"rule_{len(rules) + 1}",
            "crop": crop,
            "symptoms": symptoms,
            "diagnosis": diagnosis,
            "treatment": treatment
        }
        rules.append(new_rule)
        fm.save_rules_json(rules)
        ke.reload()
        fm.log_event(f"Expert added new rule: {diagnosis} for {crop}")
        print("✅ New rule added successfully!")

    elif choice == '2':
        crop_name = input("Crop Name: ")
        season = input("Season: ")
        soil_type = input("Soil Type: ")
        temp = input("Recommended Temp: ")

        crop_dict = {
            "crop_name": crop_name,
            "season": season,
            "soil_type": soil_type,
            "recommended_temp": temp
        }
        fm.add_crop_csv(crop_dict)
        ke.reload()
        fm.log_event(f"Expert added new crop: {crop_name}")
        print("✅ New crop added to CSV successfully!")

def main():
    ke = KnowledgeEngine()
    ir_sys = SimpleIRSystem()

    while True:
        print("\n==========================================")
        print(" 🌱 SMART FARMING ADVISOR SYSTEM 🌱 ")
        print("==========================================")
        print("1. Farmer Mode")
        print("2. Expert/Admin Mode")
        print("3. Exit")
        
        mode = input("Choose Mode (1-3): ")
        if mode == '1':
            farmer_interface(ke, ir_sys)
        elif mode == '2':
            expert_interface(ke)
        elif mode == '3':
            print("Exiting system. Goodbye!")
            break
        else:
            print("Invalid selection, try again.")

if __name__ == "__main__":
    main()