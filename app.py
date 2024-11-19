import streamlit as st
import json
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.chat_models import ChatOpenAI

# Judul aplikasi
st.title("Gym Session Recommender AI")
# st.image("gym_image.png", caption="Your personalized gym session recommender!")

# Deskripsi aplikasi
st.write(
    """
    Gym Session Recommender AI is an intelligent assistant designed to recommend personalized workout sessions 
    based on user preferences. Input your fitness goal, level, or target muscle group, and let the AI provide 
    tailored suggestions to help you achieve your fitness journey!
    """
)

# Membuat garis pemisah
st.markdown("---")

# Inisialisasi OpenAI Chat Model
try:
    # Set your OpenAI API Key
    api_key = st.secrets["OPENAI_API_KEY"]  # Pastikan secret ini sudah ada di Hugging Face 
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.0)
except Exception as e:
    st.error(f"Gagal menginisialisasi model AI: {e}")
    st.stop()

# Load data dari data.json
try:
    with open("data.json", "r") as file:
        data = json.load(file)
except FileNotFoundError:
    st.error("File `data.json` tidak ditemukan. Pastikan file tersebut ada di direktori yang sama dengan skrip ini.")
    st.stop()
except json.JSONDecodeError:
    st.error("File `data.json` tidak dapat dibaca. Pastikan file berformat JSON yang valid.")
    st.stop()

# Prompt untuk LLM
prompt_template = """
You are a highly intelligent AI assistant, an expert in recommending gym workout sessions based on user preferences. 
Your task is to provide detailed responses in complete sentences, including session types, targeted muscles, 
instructions, and recommendations for beginners, intermediates, and advanced users.

Here’s the structure of the data:
1. *name*: Name of the workout session.
2. *force*: The type of force used (e.g., push, pull).
3. *level*: Difficulty level (e.g., beginner, intermediate, advanced).
4. *mechanic*: Type of mechanic (e.g., compound, isolation).
5. *equipment*: Required equipment (e.g., body only, dumbbells).
6. *primaryMuscles*: Main muscle groups targeted.
7. *secondaryMuscles*: Supporting muscle groups.
8. *instructions*: Step-by-step workout instructions.
9. *category*: Workout category (e.g., strength, cardio).

Use this information to generate personalized workout recommendations.

**User preferences:**
1. Fitness level: {fitness_level}
2. Target muscle group: {target_muscle}
3. Workout category: {workout_category}

Provide recommendations in a friendly and motivational tone.
"""

# Input dari pengguna
st.sidebar.header("Preferences")
fitness_level = st.sidebar.selectbox("Select your fitness level:", ["beginner", "intermediate", "advanced"])
target_muscle = st.sidebar.selectbox("Target muscle group:", ["abdominals", "legs", "arms", "chest", "back", "shoulders"])
workout_category = st.sidebar.selectbox("Workout category:", ["strength", "cardio", "flexibility"])

# LLM Chain
try:
    llm_prompt = PromptTemplate(
        template=prompt_template,
        input_variables=["fitness_level", "target_muscle", "workout_category"]
    )
    llm_chain = LLMChain(llm=llm, prompt=llm_prompt, verbose=True)
except Exception as e:
    st.error(f"Gagal membuat prompt chain: {e}")
    st.stop()

# Tampilkan data jika pengguna memilih
if st.checkbox("Show raw data"):
    st.json(data)

# Tombol untuk meminta rekomendasi
if st.button("Get Recommendation"):
    try:
        response = llm_chain.run({
            "fitness_level": fitness_level,
            "target_muscle": target_muscle,
            "workout_category": workout_category,
        })

        # Tampilkan hasil rekomendasi
        if response:
            st.subheader("Recommended Workout:")
            st.write(response)
        else:
            st.error("Failed to generate a recommendation. Please try again.")
    except Exception as e:
        st.error(f"Terjadi kesalahan saat menghasilkan rekomendasi: {e}")

        
        
