# AgroAI Pro — Technical Report

## 1. Project overview

AgroAI Pro is a small Streamlit-based agricultural information prototype. Its current implementation uses three complementary mechanisms: exact/partial symptom matching against a local expert-rule JSON file, table matching for crop records, and TF-IDF document retrieval for agricultural text notes. A separate rule-based module turns manually entered sensor readings into advisories.

## 2. Main modules

- `smart_agro_pro_app.py`: Streamlit navigation, forms, display, image-upload interface, suggested chatbot questions, and PDF report export.
- `plant_disease_model.py`: downloads/caches the quantized MobileNetV2 ONNX weights and runs CPU inference on uploaded leaf images.
- `knowledge_engine.py`: disease-rule matching, crop-record filtering, and IoT advisory thresholds.
- `ir_engine.py`: tokenization, inverted index, TF-IDF vectors, and cosine-similarity ranking.
- `file_manager.py`: CSV/JSON persistence and application logging.
- `data/rules.json`: editable plant symptom rules.
- `data/crops.csv`: sample crop, season, soil, and temperature rows.
- `data/text_docs/`: searchable knowledge notes with source links where relevant.

## 3. Information retrieval

The chatbot uses a lightweight information-retrieval (IR) approach. It loads text files, tokenizes them, calculates term frequency and inverse document frequency, represents the query in the same vector space, then ranks documents using cosine similarity. The application shows retrieved passages and source filenames. It does not synthesize new answers and is not a large language model (LLM).

## 4. PDF reports

Plant Diagnosis exports the input crop and symptoms plus matched rules or retrieved knowledge passages. IoT Monitor exports the entered sensor values and the generated advisory messages. Reports include the project label, generation timestamp, and a disclaimer that results are informational and not official certification or a substitute for local expertise.

## 5. Testing and validation

The included unit tests check the current sample data, symptom matching, crop filtering, IoT thresholds, and retrieval ranking. These tests check software behavior only; they do not validate agronomic accuracy or field performance.

## 6. Known limitations

- The disease rules and crop table are small sample datasets.
- Symptom matching is keyword-based and may miss synonyms or match symptoms shared by different conditions.
- TF-IDF is lexical retrieval; it does not understand context as a language model would.
- IoT thresholds are demonstration settings and are not calibrated to a particular sensor, crop, soil, or location.
- The application does not connect to physical sensors, weather feeds, or live agricultural databases. The image-classification page uses a pretrained MobileNetV2 ONNX model with 38 PlantVillage classes; its weights are downloaded from Hugging Face on first use, while inference itself runs locally on the Streamlit server without an inference API.
- Local agronomic and pesticide guidance must be verified with qualified sources.

## 7. Future improvements

1. Expand the local knowledge base with reviewed, geographically relevant sources and update dates.
2. Add synonym handling and retrieval evaluation with a labeled query set.
3. Add crop-specific, sensor-specific threshold configuration.
4. Add source metadata and review status for every rule.
5. If adding an image-based disease model, document its dataset, supported classes, limitations, and evaluation metrics, and avoid presenting model output as certain diagnosis.


## 8. Computer vision: image-based disease classification

The added Plant Disease Detection page accepts JPG, JPEG, PNG, or WEBP images up to 10 MB. It preprocesses the image to 224×224 with normalization, runs a quantized MobileNetV2 ONNX model using ONNX Runtime on CPU, and displays the top three classes. The model was fine-tuned on PlantVillage and includes 38 classes across several crops. The app downloads the approximately 2.7 MB quantized model file on first use and reuses the cached file; no inference API is called.

This is an educational prototype. Benchmark performance reported by the model publisher is not a guarantee of real-world accuracy. PlantVillage images are often captured under controlled conditions, so background, lighting, multiple leaves, unseen diseases, and unsupported crops can reduce accuracy. The model score is not a calibrated probability. Important diagnoses and treatment decisions should be confirmed by a qualified agricultural specialist.
