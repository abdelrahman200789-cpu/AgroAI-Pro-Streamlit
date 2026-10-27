# AgroAI Pro — Smart Farming Advisor System

AgroAI Pro is a student prototype built with Python and Streamlit. It combines a small rule-based knowledge engine, a local TF-IDF information-retrieval engine, crop records, and demonstration IoT thresholds.

## Features

- **Plant Diagnosis:** matches entered symptoms against local rules and retrieves knowledge notes when no rule matches.
- **Plant Disease Detection (Image AI):** uploads a leaf photo and runs a quantized MobileNetV2 ONNX classifier locally on the Streamlit server (38 PlantVillage classes; no inference API). Model weights are downloaded from Hugging Face on first use and cached on the server.
- **Crop Recommendation:** finds rows in `data/crops.csv` matching the selected season and soil type.
- **IoT Monitor:** applies simple configurable thresholds to manually entered temperature, air-humidity, and soil-moisture readings.
- **Expert Hub:** adds new symptom rules to `data/rules.json`.
- **Agricultural Knowledge Search:** uses TF-IDF and cosine similarity to retrieve passages from `data/text_docs/`; includes suggested questions and source links.
- **PDF reports:** exports plant-diagnosis results and IoT analysis with project label, generated date/time, inputs, results, and a prototype disclaimer.

## Project structure

```text
AgroAI_Pro_Updated/
├── smart_agro_pro_app.py
├── plant_disease_model.py
├── ir_engine.py
├── knowledge_engine.py
├── file_manager.py
├── requirements.txt
├── README.md
├── REPORT.md
├── data/
│   ├── crops.csv
│   ├── rules.json
│   ├── app.log                 # created automatically
│   └── text_docs/
│       ├── crop_planning.txt
│       ├── doc1_blight.txt
│       ├── doc2_wheat.txt
│       ├── integrated_pest_management.txt
│       ├── irrigation_basics.txt
│       ├── plant_disease_scouting.txt
│       ├── sensor_quality.txt
│       └── soil_ph.txt
└── tests/
    └── test_agro_engine.py
```

## Run locally (Ubuntu/Linux)

From the project directory:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
python -m streamlit run smart_agro_pro_app.py
```

Open the local URL shown by Streamlit, usually `http://localhost:8501`.

## How the retrieval system works

1. It reads every `.txt` file in `data/text_docs/`.
2. It tokenizes text into lowercase alphanumeric terms.
3. It builds an inverted index.
4. It computes simple TF-IDF vectors for documents and a query.
5. It ranks documents by cosine similarity and displays the best matching passages.

This is **information retrieval**, not a generative LLM or a trained plant-disease model. Similarity scores rank documents; they are not diagnostic confidence values.

## Data and safety limitations

- The four crop rows and the disease-rule set are small demonstration data, not an official local crop calendar.
- IoT alerts use simple prototype thresholds; sensor calibration, soil type, crop, crop stage, and local conditions can change the correct interpretation.
- A symptom match is not a confirmed plant diagnosis. Confirm uncertain cases with a local agricultural extension service or qualified specialist.
- Use only plant-protection products registered for the crop and problem in your area and follow the product label.
- The PDF is a project-generated report, not official certification.

## Knowledge sources

Source links are included in the relevant text documents and in the chatbot's source panel. Current source notes include University of Minnesota Extension on early blight, AHDB on wheat powdery mildew, FAO on integrated pest management and irrigation, and USDA NRCS soil resources. Verify that guidance is applicable to your location and crop before acting on it.

## Tests

```bash
python -m unittest discover -s tests -v
```

## Image-based plant disease detection

The image classifier uses the quantized ONNX export of `onnx-community/mobilenet_v2_1.0_224-plant-disease-identification-ONNX`, fine-tuned on PlantVillage. It predicts among 38 classes, including healthy classes. The first image analysis downloads the model weights from Hugging Face; subsequent inference runs on the Streamlit server with ONNX Runtime CPU. No hosted inference endpoint or paid API is used.

**Deployment note:** `onnxruntime` and `Pillow` are added to `requirements.txt`. Commit both `smart_agro_pro_app.py`, `plant_disease_model.py`, and `requirements.txt` to GitHub so Streamlit Community Cloud installs the dependencies. Keep the model file out of Git; it is downloaded and cached at runtime.

**Limitations:** PlantVillage contains controlled images and 38 supported classes. Predictions on field images may be wrong, and diseases/crops outside the model classes may be mislabeled. The displayed score is a model score, not a calibrated probability or a confirmed diagnosis.
