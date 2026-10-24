import streamlit as st
import datetime
import file_manager as fm
from ir_engine import SimpleIRSystem
from knowledge_engine import KnowledgeEngine

st.set_page_config(
    page_title="AgroAI Pro",
    page_icon="🌱",
    layout="wide"
)

st.markdown("""
<style>
.stApp {
    background-color: #0b1220;
    color: #f3f4f6;
}
[data-testid="stSidebar"] {
    background-color: #111827;
}
h1, h2, h3 {
    color: #10b981;
}
.stButton > button {
    background-color: #059669;
    color: white;
    border-radius: 8px;
    border: none;
}
.stButton > button:hover {
    background-color: #047857;
    color: white;
}
</style>
""", unsafe_allow_html=True)


@st.cache_resource
def load_engines():
    return KnowledgeEngine(), SimpleIRSystem()


ke, ir_sys = load_engines()


def refresh_engines():
    ke.reload()
    ir_sys.load_documents()
    ir_sys.inverted_index.clear()
    ir_sys.vocab.clear()
    ir_sys.doc_vectors.clear()
    ir_sys.build_inverted_index()
    ir_sys.compute_tfidf()


def log_action(message):
    fm.log_event(message)


st.sidebar.title("🌱 AgroAI Pro")
st.sidebar.caption("Smart Farming Advisor System")

page = st.sidebar.radio(
    "Navigate",
    [
        "Dashboard",
        "Plant Diagnosis",
        "Crop Recommendation",
        "IoT Monitor",
        "Expert Hub",
        "Agricultural Chatbot"
    ]
)

st.sidebar.divider()
st.sidebar.info(
    "AgroAI Pro uses an expert knowledge engine, "
    "TF-IDF information retrieval, and rule-based IoT advice."
)


if page == "Dashboard":
    st.title("🌱 AgroAI Pro")
    st.subheader("Smart Farming Advisor System")
    st.write(
        "An agricultural information platform for plant diagnosis, "
        "crop recommendations, sensor advice, and knowledge search."
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Crop Records", len(ke.crops))

    with col2:
        st.metric("Disease Rules", len(ke.rules))

    with col3:
        st.metric("Knowledge Documents", len(ir_sys.documents))

    st.divider()
    st.subheader("System Features")

    st.markdown("""
    - 🌿 Plant disease diagnosis and treatment recommendations
    - 🌾 Crop recommendations based on season and soil type
    - 📡 Environmental sensor analysis and agricultural advice
    - 🛠️ Expert hub for adding disease rules
    - 💬 Chatbot for searching agricultural knowledge documents
    """)


elif page == "Plant Diagnosis":
    st.title("🌿 Plant Disease Diagnosis")
    st.write("Enter the crop name and symptoms to check the available rules.")

    with st.form("diagnosis_form"):
        crop = st.text_input("Crop Name", placeholder="Tomato")
        symptoms = st.text_input(
            "Symptoms",
            placeholder="yellow spots, dark spots"
        )
        submitted = st.form_submit_button("Diagnose Plant")

    if submitted:
        if not crop.strip() or not symptoms.strip():
            st.error("Please enter both the crop name and symptoms.")
        else:
            results = ke.diagnose_plant(crop.strip(), symptoms.strip())
            log_action(f"Plant diagnosis query: {crop} - {symptoms}")

            if results:
                st.success("Matching diagnosis rules found.")

                for result in results:
                    with st.container(border=True):
                        st.subheader(result["diagnosis"])
                        st.write("**Recommended Treatment**")
                        st.write(result["treatment"])
                        st.write("**Matched Symptoms**")
                        st.write(", ".join(result["matched_symptoms"]))
            else:
                st.warning(
                    "No exact disease rule matched. Searching the text guides..."
                )
                search_results = ir_sys.search(
                    f"{crop} {symptoms}"
                )

                if search_results:
                    for doc_id, content, score in search_results[:3]:
                        with st.expander(
                            f"{doc_id} — Similarity: {score:.3f}"
                        ):
                            st.write(content)
                else:
                    st.info("No matching diagnosis rules or text guides found.")


elif page == "Crop Recommendation":
    st.title("🌾 Crop Recommendation")
    st.write("Find crops matching your selected season and soil type.")

    with st.form("crop_form"):
        season = st.selectbox("Season", ["Summer", "Winter"])
        soil = st.selectbox("Soil Type", ["Loamy", "Clay", "Sandy"])
        submitted = st.form_submit_button("Find Suitable Crops")

    if submitted:
        suitable = ke.recommend_crops(season, soil)
        log_action(f"Crop recommendation: {season} - {soil}")

        if suitable:
            st.success(f"Found {len(suitable)} suitable crop record(s).")

            for item in suitable:
                with st.container(border=True):
                    st.subheader(item["crop_name"])
                    st.write(
                        f"**Recommended Temperature:** "
                        f"{item['recommended_temp']}"
                    )
                    st.write(f"**Season:** {item['season']}")
                    st.write(f"**Soil Type:** {item['soil_type']}")
        else:
            st.info("No matching crops were found in the current database.")


elif page == "IoT Monitor":
    st.title("📡 IoT Environmental Monitor")
    st.write("Enter sensor readings to receive rule-based agricultural advice.")

    with st.form("iot_form"):
        col1, col2, col3 = st.columns(3)

        with col1:
            temperature = st.number_input(
                "Temperature (°C)",
                value=25.0
            )

        with col2:
            humidity = st.number_input(
                "Air Humidity (%)",
                min_value=0.0,
                max_value=100.0,
                value=50.0
            )

        with col3:
            moisture = st.number_input(
                "Soil Moisture (%)",
                min_value=0.0,
                max_value=100.0,
                value=50.0
            )

        submitted = st.form_submit_button("Analyze Sensors")

    if submitted:
        advisories = ke.analyze_iot_data(
            temperature,
            humidity,
            moisture
        )

        log_action(
            f"IoT analysis: temp={temperature}, "
            f"humidity={humidity}, moisture={moisture}"
        )

        st.subheader("Analysis Results")
        st.caption(datetime.datetime.now().strftime("%Y-%m-%d %H:%M"))

        for advice in advisories:
            st.info(advice)


elif page == "Expert Hub":
    st.title("🛠️ Expert Knowledge Hub")
    st.write("Add a disease rule to the existing JSON knowledge base.")

    with st.form("expert_form"):
        crop = st.text_input("Crop Name")
        symptoms = st.text_input(
            "Symptoms",
            placeholder="yellow leaves, brown spots"
        )
        diagnosis = st.text_input("Diagnosis")
        treatment = st.text_area("Recommended Treatment")

        submitted = st.form_submit_button("Save Disease Rule")

    if submitted:
        if not all([
            crop.strip(),
            symptoms.strip(),
            diagnosis.strip(),
            treatment.strip()
        ]):
            st.error("Please complete all fields.")
        else:
            rules = fm.load_rules_json()

            new_rule = {
                "id": f"rule_{len(rules) + 1}",
                "crop": crop.strip(),
                "symptoms": [
                    symptom.strip()
                    for symptom in symptoms.split(",")
                    if symptom.strip()
                ],
                "diagnosis": diagnosis.strip(),
                "treatment": treatment.strip()
            }

            rules.append(new_rule)
            fm.save_rules_json(rules)
            refresh_engines()

            log_action(
                f"Expert added disease rule for {crop}: {diagnosis}"
            )

            st.success("Disease rule saved successfully.")


elif page == "Agricultural Chatbot":
    st.title("💬 Agricultural Chatbot")
    st.write(
        "Ask a question about agriculture. The chatbot searches "
        "the existing text documents and displays the most relevant results."
    )

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    question = st.chat_input(
        "Ask about irrigation, soil, crops, or plant diseases..."
    )

    if question:
        st.session_state.chat_history.append({
            "role": "user",
            "content": question
        })

        with st.chat_message("user"):
            st.markdown(question)

        results = ir_sys.search(question)
        log_action(f"Chatbot knowledge search: {question}")

        with st.chat_message("assistant"):
            if results:
                doc_id, content, score = results[0]

                st.markdown("Here is the most relevant information I found:")
                st.markdown(content)
                st.caption(
                    f"Source: {doc_id} | Similarity score: {score:.3f}"
                )

                if len(results) > 1:
                    with st.expander("Related information"):
                        for other_id, other_content, other_score in results[1:3]:
                            st.markdown(f"**{other_id}**")
                            st.caption(
                                f"Similarity score: {other_score:.3f}"
                            )
                            st.write(other_content)
            else:
                st.info(
                    "I couldn't find a matching document. "
                    "Try different keywords or ask a broader question."
                )

        if results:
            doc_id, content, score = results[0]
            answer = (
                f"Here is the most relevant information I found:\n\n"
                f"{content}\n\n"
                f"Source: {doc_id} | Similarity: {score:.3f}"
            )
        else:
            answer = (
                "I couldn't find a matching document. "
                "Try different keywords or ask a broader question."
            )

        st.session_state.chat_history.append({
            "role": "assistant",
            "content": answer
        })

    if st.session_state.chat_history:
        if st.button("Clear Conversation"):
            st.session_state.chat_history = []
            st.rerun()