import tkinter as tk
from tkinter import messagebox, ttk
from ir_engine import SimpleIRSystem
from knowledge_engine import KnowledgeEngine
import file_manager as fm

class SmartFarmingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Smart Farming Advisor System")
        self.root.geometry("700x550")
        self.root.config(bg="#f4f6f7")

        self.ke = KnowledgeEngine()
        self.ir_sys = SimpleIRSystem()

        # العنوان الرئيسي
        title_label = tk.Label(root, text="🌱 Smart Farming Advisor System 🌱", font=("Arial", 16, "bold"), bg="#f4f6f7", fg="#27ae60")
        title_label.pack(pady=15)

        # Notebook (Tabs) للواجهات المختلفة
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill='both', expand=True, padx=15, pady=10)

        # Tab 1: Disease Diagnosis
        self.tab_diagnosis = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_diagnosis, text="🌿 Disease Diagnosis")
        self.create_diagnosis_tab()

        # Tab 2: Crop Recommendation
        self.tab_crops = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_crops, text="🌾 Crop Recommendation")
        self.create_crops_tab()

        # Tab 3: IoT Monitor
        self.tab_iot = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_iot, text="📡 IoT Smart Monitor")
        self.create_iot_tab()

    def create_diagnosis_tab(self):
        frame = tk.Frame(self.tab_diagnosis, bg="white", padx=20, pady=20)
        frame.pack(fill='both', expand=True)

        tk.Label(frame, text="Crop Name (e.g., Tomato):", font=("Arial", 11), bg="white").pack(anchor='w', pady=5)
        self.crop_entry = tk.Entry(frame, font=("Arial", 11), width=30)
        self.crop_entry.pack(anchor='w', pady=5)

        tk.Label(frame, text="Symptoms (comma separated):", font=("Arial", 11), bg="white").pack(anchor='w', pady=5)
        self.symptoms_entry = tk.Entry(frame, font=("Arial", 11), width=50)
        self.symptoms_entry.pack(anchor='w', pady=5)

        btn = tk.Button(frame, text="Diagnose Plant", bg="#27ae60", fg="white", font=("Arial", 11, "bold"), command=self.run_diagnosis)
        btn.pack(pady=15)

        self.diag_result_text = tk.Text(frame, height=10, width=70, font=("Arial", 10))
        self.diag_result_text.pack(pady=5)

    def run_diagnosis(self):
        crop = self.crop_entry.get().strip()
        symptoms = self.symptoms_entry.get().strip()
        if not crop or not symptoms:
            messagebox.showerror("Error", "Please fill in all fields!")
            return

        results = self.ke.diagnose_plant(crop, symptoms)
        self.diag_result_text.delete("1.0", tk.END)
        
        if results:
            for res in results:
                self.diag_result_text.insert(tk.END, f"Diagnosis: {res['diagnosis']}\n")
                self.diag_result_text.insert(tk.END, f"Treatment: {res['treatment']}\n")
                self.diag_result_text.insert(tk.END, f"Matched Symptoms: {', '.join(res['matched_symptoms'])}\n\n")
        else:
            self.diag_result_text.insert(tk.END, "No exact rule matched. Searching text guides...\n\n")
            search_res = self.ir_sys.search(f"{crop} {symptoms}")
            for doc_id, content, score in search_res:
                self.diag_result_text.insert(tk.END, f"[{doc_id}] (Score: {score:.2f})\n{content}\n")

    def create_crops_tab(self):
        frame = tk.Frame(self.tab_crops, bg="white", padx=20, pady=20)
        frame.pack(fill='both', expand=True)

        tk.Label(frame, text="Season (Summer/Winter):", font=("Arial", 11), bg="white").pack(anchor='w', pady=5)
        self.season_entry = tk.Entry(frame, font=("Arial", 11), width=30)
        self.season_entry.pack(anchor='w', pady=5)

        tk.Label(frame, text="Soil Type (Loamy/Clay/Sandy):", font=("Arial", 11), bg="white").pack(anchor='w', pady=5)
        self.soil_entry = tk.Entry(frame, font=("Arial", 11), width=30)
        self.soil_entry.pack(anchor='w', pady=5)

        btn = tk.Button(frame, text="Find Suitable Crops", bg="#2980b9", fg="white", font=("Arial", 11, "bold"), command=self.run_crop_rec)
        btn.pack(pady=15)

        self.crop_result_text = tk.Text(frame, height=10, width=70, font=("Arial", 10))
        self.crop_result_text.pack(pady=5)

    def run_crop_rec(self):
        season = self.season_entry.get().strip()
        soil = self.soil_entry.get().strip()
        if not season or not soil:
            messagebox.showerror("Error", "Please fill in all fields!")
            return

        suitable = self.ke.recommend_crops(season, soil)
        self.crop_result_text.delete("1.0", tk.END)

        if suitable:
            for item in suitable:
                self.crop_result_text.insert(tk.END, f"🌾 Crop: {item['crop_name']} | Ideal Temp: {item['recommended_temp']}\n")
        else:
            self.crop_result_text.insert(tk.END, "No matching crops found in database.")

    def create_iot_tab(self):
        frame = tk.Frame(self.tab_iot, bg="white", padx=20, pady=20)
        frame.pack(fill='both', expand=True)

        tk.Label(frame, text="Temperature (°C):", font=("Arial", 11), bg="white").pack(anchor='w', pady=5)
        self.temp_entry = tk.Entry(frame, font=("Arial", 11), width=20)
        self.temp_entry.pack(anchor='w', pady=5)

        tk.Label(frame, text="Air Humidity (%):", font=("Arial", 11), bg="white").pack(anchor='w', pady=5)
        self.humidity_entry = tk.Entry(frame, font=("Arial", 11), width=20)
        self.humidity_entry.pack(anchor='w', pady=5)

        tk.Label(frame, text="Soil Moisture (%):", font=("Arial", 11), bg="white").pack(anchor='w', pady=5)
        self.moisture_entry = tk.Entry(frame, font=("Arial", 11), width=20)
        self.moisture_entry.pack(anchor='w', pady=5)

        btn = tk.Button(frame, text="Analyze IoT Sensors", bg="#e67e22", fg="white", font=("Arial", 11, "bold"), command=self.run_iot_analysis)
        btn.pack(pady=15)

        self.iot_result_text = tk.Text(frame, height=8, width=70, font=("Arial", 10))
        self.iot_result_text.pack(pady=5)

    def run_iot_analysis(self):
        try:
            temp = float(self.temp_entry.get())
            humidity = float(self.humidity_entry.get())
            moisture = float(self.moisture_entry.get())
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numbers for sensors!")
            return

        advisories = self.ke.analyze_iot_data(temp, humidity, moisture)
        self.iot_result_text.delete("1.0", tk.END)

        for adv in advisories:
            self.iot_result_text.insert(tk.END, f"{adv}\n")

if __name__ == "__main__":
    root = tk.Tk()
    app = SmartFarmingApp(root)
    root.mainloop()