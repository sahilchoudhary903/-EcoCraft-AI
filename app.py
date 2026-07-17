import streamlit as st
from PIL import Image
import google.generativeai as genai
from dotenv import load_dotenv
import os
import urllib.parse
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from io import BytesIO
def create_pdf(material_name, category, response_text, youtube_url):
    buffer = BytesIO()

    doc = SimpleDocTemplate(buffer)

    styles = getSampleStyleSheet()

    story = []

    story.append(
        Paragraph(
            "<b>EcoCraft AI Report</b>",
            styles["Title"]
        )
    )

    story.append(Spacer(1, 20))

    story.append(
        Paragraph(
            f"<b>Detected Material:</b> {material_name}",
            styles["Normal"]
        )
    )

    story.append(
        Paragraph(
            f"<b>Category:</b> {category}",
            styles["Normal"]
        )
    )

    story.append(
        Paragraph(
            "<b>Eco Impact Score:</b> 9.2 / 10",
            styles["Normal"]
        )
    )

    story.append(Spacer(1, 20))

    story.append(
        Paragraph(
            "<b>AI Suggestions:</b>",
            styles["Heading2"]
        )
    )

    story.append(
        Paragraph(
            response_text.replace("\n", "<br/>"),
            styles["Normal"]
        )
    )

    story.append(Spacer(1, 20))

    story.append(
        Paragraph(
            f"<b>YouTube Tutorials:</b><br/>{youtube_url}",
            styles["Normal"]
        )
    )

    doc.build(story)

    pdf = buffer.getvalue()

    buffer.close()

    return pdf

# -----------------------------
# Load Environment Variables
# -----------------------------
load_dotenv()

api_key = st.secrets.get(
    "GEMINI_API_KEY",
    os.getenv("GEMINI_API_KEY")
)

# Configure Gemini
genai.configure(api_key=api_key)

# Load Gemini Model
model = genai.GenerativeModel("gemini-2.5-flash")

# -----------------------------
# Page Configuration
# -----------------------------
st.set_page_config(
    page_title="EcoCraft AI",
    page_icon="♻️",
    layout="wide"
)

# -----------------------------
# Header Section
# -----------------------------
st.title("♻️ EcoCraft AI")
st.subheader("Transform Waste Into Creativity with AI")

st.write("""
Upload an image of any waste material and let AI suggest creative,
useful, and eco-friendly ways to reuse it.
""")

# -----------------------------
# Category Selection
# -----------------------------
category = st.selectbox(
    "Choose the type of ideas you want:",
    [
        "Decoration",
        "Storage",
        "Gardening",
        "School Project",
        "Kids Craft",
        "Gift Ideas"
    ]
)

# -----------------------------
# Image Upload
# -----------------------------
uploaded_file = st.file_uploader(
    "Upload an image of waste material",
    type=["jpg", "jpeg", "png", "webp"]
)

# -----------------------------
# Process Uploaded Image
# -----------------------------
if uploaded_file is not None:

    image = Image.open(uploaded_file)

    # Layout columns
    col1, col2 = st.columns([1, 2])

    # Left column -> Image
    with col1:
        st.image(
            image,
            caption="Uploaded Waste Material",
            use_container_width=True
        )

    # Right column -> AI Output
    with col2:

        st.info(f"Selected Category: {category}")

        if st.button("🔍 Analyze Waste Material"):

            prompt = f"""
Analyze this image carefully.

IMPORTANT:
Start your response with:

Material: <material name>

Then provide:

1. Suggest 5 creative {category} ideas using this material.

For each idea provide:
- Idea Name
- Difficulty Level
- Estimated Time Required
- Materials Needed
- Step-by-step Instructions

At the end provide:

YouTube Search Query: <best tutorial search phrase>

Format the response using headings and bullet points.

Make the ideas practical, unique and eco-friendly.
"""

            with st.spinner("🤖 AI is analyzing the image..."):

                response = model.generate_content(
                    [
                        prompt,
                        image
                    ]
                )

            response_text = response.text

            # -----------------------------
            # Extract Material Name
            # -----------------------------
            material_name = "waste material"
            youtube_search_query = None

            for line in response_text.split("\n"):

                if line.startswith("Material:"):
                    material_name = (
                        line.replace(
                            "Material:",
                            ""
                        ).strip()
                    )

                if line.startswith("YouTube Search Query:"):
                    youtube_search_query = (
                        line.replace(
                            "YouTube Search Query:",
                            ""
                        ).strip()
                    )

            # Fallback query if AI doesn't provide one
            if not youtube_search_query:
                youtube_search_query = (
                    f"DIY {category} ideas using {material_name}"
                )
            # -----------------------------
            # Smart Eco Score
            # -----------------------------
            eco_scores = {
                "tin can": 9.5,
                "aluminium can": 9.5,
                "glass bottle": 9.3,
                "newspaper": 9.0,
                "cardboard": 8.8,
                "plastic bottle": 8.5,
                "plastic container": 8.2,
                "cloth": 8.7,
                "wood": 9.1,
                "thermocol": 5.5,
                "plastic bag": 7.0
            }

            eco_score = 8.0

            for material, score in eco_scores.items():
                if material in material_name.lower():
                    eco_score = score
                    break
            # -----------------------------
            # Display Results
            # -----------------------------
            st.success("✅ Analysis Complete!")

            st.markdown("## ♻️ EcoCraft AI Suggestions")

            st.markdown(
                f"""
<div style="
padding:20px;
border-radius:15px;
background-color:#f0f2f6;
color:black;
">
{response_text}
</div>
""",
                unsafe_allow_html=True
            )

            # -----------------------------
            # Eco Score
            # -----------------------------
            st.metric(
                label="🌍 Eco Impact Score",
                    value=f"{eco_score} / 10"

            )

            # -----------------------------
            # Tutorial Section
            # -----------------------------
            st.markdown("## 🎥 Tutorial Videos")

            youtube_url = (
                "https://www.youtube.com/results?search_query="
                + urllib.parse.quote(
                    youtube_search_query
                )
            )

            st.link_button(
                "🎥 Watch Relevant Tutorials",
                youtube_url
            )

            pdf = create_pdf(
                material_name,
                category,
                response_text,
                youtube_url
            )

            st.download_button(
                label="📄 Download Craft Guide as PDF",
                data=pdf,
                file_name="EcoCraft_Report.pdf",
                mime="application/pdf"
            )

            # -----------------------------
            # Show Detected Material
            # -----------------------------
            st.info(
                f"Detected Material: {material_name}"
            )