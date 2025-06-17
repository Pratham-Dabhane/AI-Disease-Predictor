import streamlit as st
import joblib
import pandas as pd

# Load saved assets
model = joblib.load("../model/disease_predictor_model.joblib")
symptom_list = joblib.load("../model/meta/symptom_list.pkl")
metadata = joblib.load("../model/meta/disease_metadata.pkl")
le = joblib.load("../model/meta/label_encoder.pkl")

# ---------- Page Configuration ----------
st.set_page_config(
    page_title="AI Disease Predictor",
    page_icon="🩺",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ---------- Header Section ----------
st.markdown("""
    <h1 style='text-align: center; color: #0077b6;'>🩺 AI Disease Predictor</h1>
    <p style='text-align: center; color: #caf0f8;'>Get possible disease predictions based on your symptoms using Machine Learning.</p>
    <hr>
""", unsafe_allow_html=True)

# ---------- User Input Section ----------
st.subheader("Enter Your Symptoms")

user_input = st.text_input(
    label="📝 Separate each symptom by a comma (e.g., fever, headache, vomiting)",
    placeholder="Type symptoms here...",
)

# ---------- Helper Functions ----------
def encode_input(symptoms_raw):
    symptoms_clean = [s.strip().lower().replace(" ", "_") for s in symptoms_raw.split(",")]
    input_vector = [1 if symptom in symptoms_clean else 0 for symptom in symptom_list]
    return [input_vector], symptoms_clean

def predict_top_diseases(input_df, top_n=3):
    probs = model.predict_proba(input_df)[0]
    top_indices = probs.argsort()[-top_n:][::-1]
    return [(le.inverse_transform([i])[0], probs[i]) for i in top_indices]

def display_results(predictions):
    for disease_name, prob in predictions:
        disease_key = disease_name.lower()
        disease_info = metadata.get(disease_key)
        st.markdown(f"### 🧾 Predicted Disease: `{disease_name}` ({prob:.2%} confidence)")
        if disease_info:
            st.markdown("---")
            st.markdown(f"**📖 Description:**\n{disease_info['description']}")
            st.markdown("\n**🩺 Precautions:**")
            for p in disease_info['precautions']:
                st.markdown(f"- {p}")
        else:
            st.warning("⚠️ Sorry, no additional info found for this disease.")
        st.markdown("---")

# ---------- Predict Button ----------
if st.button("🔍 Predict top 3 Likely Diseases"):
    if user_input.strip() == "":
        st.error("Please enter some symptoms to proceed.")
    else:
        input_vector, cleaned = encode_input(user_input)
        input_df = pd.DataFrame(input_vector, columns=symptom_list)
        predictions = predict_top_diseases(input_df, top_n=3)
        display_results(predictions)

        st.markdown("""
        <hr>
        <div style='font-size: 13px; color: #95a5a6;'>
        ⚠️ This tool is for educational purposes only. It is not a substitute for professional medical advice, diagnosis, or treatment. Always consult a qualified healthcare provider for serious or persistent symptoms.<br>
        🧠 This app is a prototype ML tool and may not always give accurate predictions. Always consult a doctor.
        </div>
        """, unsafe_allow_html=True)

# ---------- Footer ----------
st.markdown("""
    <hr>
    <p style='text-align: center; font-size: 12px; color: #bdc3c7;'>
        Made with ❤️ using Machine Learning | Not a Medical Device
    </p>
""", unsafe_allow_html=True)