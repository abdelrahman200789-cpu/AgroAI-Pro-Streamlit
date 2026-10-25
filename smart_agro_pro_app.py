import streamlit as st
import datetime
import io
import pandas as pd
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import file_manager as fm
from ir_engine import SimpleIRSystem
from knowledge_engine import KnowledgeEngine
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, PageBreak

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


def create_pdf_chart(history, column, title, ylabel, chart_type):
    values = [item[column] for item in history]
    labels = [item["time"].strftime("%H:%M") for item in history]

    fig, ax = plt.subplots(figsize=(8, 3.2))

    if chart_type == "area":
        ax.fill_between(range(len(values)), values, alpha=0.35)
        ax.plot(range(len(values)), values, linestyle="None")
    elif chart_type == "bar":
        ax.bar(labels, values)
    elif chart_type == "horizontal":
        ax.barh(labels, values)

    if chart_type != "horizontal":
        ax.set_xticks(range(len(labels)))
        ax.set_xticklabels(labels, rotation=35, ha="right")

    ax.set_title(title)
    ax.set_ylabel(ylabel)
    ax.grid(axis="y", alpha=0.25)
    fig.tight_layout()

    image_buffer = io.BytesIO()
    fig.savefig(image_buffer, format="png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    image_buffer.seek(0)

    return image_buffer


def build_iot_pdf(history, advisories):
    pdf_buffer = io.BytesIO()
    document = SimpleDocTemplate(
        pdf_buffer,
        pagesize=A4,
        rightMargin=1.5 * cm,
        leftMargin=1.5 * cm,
        topMargin=1.5 * cm,
        bottomMargin=1.5 * cm
    )

    styles = getSampleStyleSheet()
    story = []

    story.append(Paragraph("AgroAI Pro - IoT Sensor Report", styles["Title"]))
    story.append(Spacer(1, 0.3 * cm))
    story.append(Paragraph(
        f"Report generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        styles["Normal"]
    ))
    story.append(Spacer(1, 0.4 * cm))

    if not history:
        story.append(Paragraph("No sensor readings are available.", styles["Normal"]))
        document.build(story)
        pdf_buffer.seek(0)
        return pdf_buffer.getvalue()

    latest = history[-1]
    story.append(Paragraph("Latest Sensor Readings", styles["Heading2"]))

    latest_data = [
        ["Sensor", "Latest Reading"],
        ["Temperature", f"{latest['temperature']:.1f} °C"],
        ["Air Humidity", f"{latest['humidity']:.1f}%"],
        ["Soil Moisture", f"{latest['moisture']:.1f}%"]
    ]

    readings_table = Table(latest_data, colWidths=[7 * cm, 8 * cm])
    readings_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#059669")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("PADDING", (0, 0), (-1, -1), 8)
    ]))

    story.append(readings_table)
    story.append(Spacer(1, 0.5 * cm))
    story.append(Paragraph("Temperature History", styles["Heading2"]))

    temperature_chart = create_pdf_chart(
        history, "temperature", "Temperature Readings",
        "Temperature (°C)", "area"
    )
    story.append(Image(temperature_chart, width=16 * cm, height=6.2 * cm))
    story.append(Spacer(1, 0.3 * cm))
    story.append(Paragraph("Air Humidity History", styles["Heading2"]))

    humidity_chart = create_pdf_chart(
        history, "humidity", "Air Humidity Readings",
        "Humidity (%)", "bar"
    )
    story.append(Image(humidity_chart, width=16 * cm, height=6.2 * cm))
    story.append(PageBreak())
    story.append(Paragraph("Soil Moisture History", styles["Heading2"]))

    moisture_chart = create_pdf_chart(
        history, "moisture", "Soil Moisture Readings",
        "Moisture (%)", "horizontal"
    )
    story.append(Image(moisture_chart, width=16 * cm, height=6.2 * cm))
    story.append(Spacer(1, 0.5 * cm))
    story.append(Paragraph("Sensor Readings History", styles["Heading2"]))

    table_data = [["Time", "Temperature (°C)", "Air Humidity (%)", "Soil Moisture (%)"]]

    for item in history:
        table_data.append([
            item["time"].strftime("%Y-%m-%d %H:%M"),
            f"{item['temperature']:.1f}",
            f"{item['humidity']:.1f}",
            f"{item['moisture']:.1f}"
        ])

    history_table = Table(
        table_data,
        repeatRows=1,
        colWidths=[5 * cm, 3.5 * cm, 3.5 * cm, 3.5 * cm]
    )
    history_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#059669")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("PADDING", (0, 0), (-1, -1), 5)
    ]))

    story.append(history_table)
    story.append(Spacer(1, 0.5 * cm))
    story.append(Paragraph("Agricultural Advisories", styles["Heading2"]))

    if advisories:
        for advice in advisories:
            story.append(Paragraph(f"&bull; {advice}", styles["Normal"]))
            story.append(Spacer(1, 0.15 * cm))
    else:
        story.append(Paragraph("No advisories are available yet.", styles["Normal"]))

    document.build(story)
    pdf_buffer.seek(0)

    return pdf_buffer.getvalue()


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

if "iot_history" not in st.session_state:
    st.session_state.iot_history = []

if "iot_advisories" not in st.session_state:
    st.session_state.iot_advisories = []


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
    - 📡 Environmental sensor analysis and IoT visualizations
    - 📄 Downloadable PDF report for sensor readings
    - 🛠️ Expert hub for adding disease rules
    - 💬 Chatbot for searching agricultural knowledge documents
    """)


elif page == "Plant Diagnosis":
    st.title("🌿 Plant Disease Diagnosis")
    st.write("Enter the crop name and symptoms to check the available rules.")

    with st.form("diagnosis_form"):
        crop = st.text_input("Crop Name", placeholder="Tomato")
        symptoms = st.text_input("Symptoms", placeholder="yellow spots, dark spots")
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
                st.warning("No exact disease rule matched. Searching the text guides...")
                search_results = ir_sys.search(f"{crop} {symptoms}")

                if search_results:
                    for doc_id, content, score in search_results[:3]:
                        with st.expander(f"{doc_id} — Similarity: {score:.3f}"):
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
                    st.write(f"**Recommended Temperature:** {item['recommended_temp']}")
                    st.write(f"**Season:** {item['season']}")
                    st.write(f"**Soil Type:** {item['soil_type']}")
        else:
            st.info("No matching crops were found in the current database.")


elif page == "IoT Monitor":
    st.title("📡 IoT Environmental Monitor")
    st.write("Enter sensor readings to receive agricultural advice and visualize sensor history.")

    with st.form("iot_form"):
        col1, col2, col3 = st.columns(3)

        with col1:
            temperature = st.number_input(
                "Temperature (°C)",
                min_value=-20.0,
                max_value=80.0,
                value=25.0,
                step=0.5
            )

        with col2:
            humidity = st.number_input(
                "Air Humidity (%)",
                min_value=0.0,
                max_value=100.0,
                value=50.0,
                step=1.0
            )

        with col3:
            moisture = st.number_input(
                "Soil Moisture (%)",
                min_value=0.0,
                max_value=100.0,
                value=50.0,
                step=1.0
            )

        submitted = st.form_submit_button("Analyze Sensors")

    if submitted:
        timestamp = datetime.datetime.now()

        new_reading = {
            "time": timestamp,
            "temperature": temperature,
            "humidity": humidity,
            "moisture": moisture
        }

        st.session_state.iot_history.append(new_reading)

        try:
            advisories = ke.analyze_iot_data(temperature, humidity, moisture)
            st.session_state.iot_advisories = advisories
        except Exception as error:
            st.session_state.iot_advisories = [f"Unable to analyze readings: {error}"]

        log_action(
            f"IoT analysis: temp={temperature}, "
            f"humidity={humidity}, moisture={moisture}"
        )

    history = st.session_state.iot_history

    if history:
        latest = history[-1]

        st.subheader("Latest Sensor Readings")
        st.caption(f"Last updated: {latest['time'].strftime('%Y-%m-%d %H:%M:%S')}")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Temperature", f"{latest['temperature']:.1f} °C")

        with col2:
            st.metric("Air Humidity", f"{latest['humidity']:.1f}%")

        with col3:
            st.metric("Soil Moisture", f"{latest['moisture']:.1f}%")

        st.divider()
        st.subheader("🌡️ Temperature History")

        temperature_fig = go.Figure()
        temperature_fig.add_trace(go.Scatter(
            x=[item["time"] for item in history],
            y=[item["temperature"] for item in history],
            mode="none",
            fill="tozeroy",
            name="Temperature",
            hovertemplate="%{y:.1f} °C<extra></extra>"
        ))
        temperature_fig.update_layout(
            xaxis_title="Time",
            yaxis_title="Temperature (°C)",
            showlegend=False,
            margin=dict(l=10, r=10, t=20, b=10)
        )
        st.plotly_chart(temperature_fig, use_container_width=True)

        st.subheader("💧 Air Humidity History")

        humidity_fig = go.Figure()
        humidity_fig.add_trace(go.Bar(
            x=[item["time"].strftime("%H:%M:%S") for item in history],
            y=[item["humidity"] for item in history],
            name="Air Humidity",
            hovertemplate="%{y:.1f}%<extra></extra>"
        ))
        humidity_fig.update_layout(
            xaxis_title="Time",
            yaxis_title="Air Humidity (%)",
            yaxis=dict(range=[0, 100]),
            showlegend=False,
            margin=dict(l=10, r=10, t=20, b=10)
        )
        st.plotly_chart(humidity_fig, use_container_width=True)

        st.subheader("🌱 Soil Moisture Levels")

        for reading in history:
            st.write(f"{reading['time'].strftime('%H:%M:%S')} — {reading['moisture']:.1f}%")
            st.progress(
                int(max(0, min(100, reading["moisture"]))),
                text="Soil moisture"
            )

        st.divider()
        st.subheader("📋 Agricultural Advisories")

        if st.session_state.iot_advisories:
            for advice in st.session_state.iot_advisories:
                st.info(advice)
        else:
            st.info("Submit sensor readings to generate recommendations.")

        st.divider()
        st.subheader("📄 Download IoT PDF Report")

        pdf_report = build_iot_pdf(history, st.session_state.iot_advisories)

        st.download_button(
            label="Download PDF Report",
            data=pdf_report,
            file_name="AgroAI_IoT_Report.pdf",
            mime="application/pdf"
        )

        if st.button("Clear IoT History"):
            st.session_state.iot_history = []
            st.session_state.iot_advisories = []
            st.rerun()
    else:
        st.info("No sensor readings yet. Enter the readings above and click Analyze Sensors.")


elif page == "Expert Hub":
    st.title("🛠️ Expert Knowledge Hub")
    st.write("Add a disease rule to the existing JSON knowledge base.")

    with st.form("expert_form"):
        crop = st.text_input("Crop Name")
        symptoms = st.text_input("Symptoms", placeholder="yellow leaves, brown spots")
        diagnosis = st.text_input("Diagnosis")
        treatment = st.text_area("Recommended Treatment")
        submitted = st.form_submit_button("Save Disease Rule")

    if submitted:
        if not all([crop.strip(), symptoms.strip(), diagnosis.strip(), treatment.strip()]):
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
            log_action(f"Expert added disease rule for {crop}: {diagnosis}")
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

    question = st.chat_input("Ask about irrigation, soil, crops, or plant diseases...")

    if question:
        st.session_state.chat_history.append({
            "role": "user",
            "content": question
        })

        results = ir_sys.search(question)
        log_action(f"Chatbot knowledge search: {question}")

        if results:
            doc_id, content, score = results[0]
            answer = (
                "Here is the most relevant information I found:\n\n"
                f"{content}\n\n"
                f"Source: {doc_id} | Similarity: {score:.3f}"
            )

            if len(results) > 1:
                answer += "\n\nRelated information:\n"

                for other_id, other_content, other_score in results[1:3]:
                    answer += (
                        f"\n**{other_id}** "
                        f"(Similarity: {other_score:.3f})\n"
                        f"{other_content}\n"
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
        st.rerun()

    if st.session_state.chat_history:
        if st.button("Clear Conversation"):
            st.session_state.chat_history = []
            st.rerun()