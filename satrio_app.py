import streamlit as st
import requests
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.chat_models import ChatOpenAI

# Judul aplikasi
st.title("Gym Session Recommender AI")

# Deskripsi aplikasi
st.write(
    """
    Gym Session Recommender AI is an intelligent assistant designed to recommend personalized workout sessions 
    based on user preferences. Just type your fitness goal, level, or target muscle group, and the AI will suggest 
    tailored workouts to help you on your fitness journey!
    """
)

# Membuat garis pemisah
st.markdown("---")

# Inisialisasi OpenAI Chat Model
try:
    api_key = st.secrets.get("OPENAI_API_KEY", None)
    if api_key is None:
        st.error("API Key not found in secrets. Please add your OpenAI API Key in secrets.toml.")
        st.stop()
    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.0, openai_api_key=api_key)
except Exception as e:
    st.error(f"Failed to initialize AI model: {e}")
    st.stop()

# Prompt untuk LLM
prompt_template = """
You are a highly intelligent AI assistant, an expert in recommending gym workout sessions based on user preferences. 
Here is a list of exercises available:

{exercise_list}

The user has asked for a recommendation. From the list above, choose one exercise that matches the user's preferences and return only the name of the exercise exactly as it appears.

**User preferences and requests:**
{user_input}

Respond with the exact name of the selected exercise.
"""

llm_prompt = PromptTemplate(
    template=prompt_template,
    input_variables=["exercise_list", "user_input"]
)
llm_chain = LLMChain(llm=llm, prompt=llm_prompt, verbose=False)

# Input dari pengguna
input_question = st.text_input("What can I help you with? (e.g., 'recommend a workout for legs', 'I want to target chest')")

# Tombol untuk meminta rekomendasi
if st.button("Submit"):
    if input_question:
        try:
            # Kirim permintaan ke API /list_all
            api_url = f"http://127.0.0.1:5000/list_all"
            list_all_response = requests.get(api_url)

            if list_all_response.status_code == 200:
                exercises = list_all_response.json().get("exercises", [])
                
                if exercises:
                    # Gabungkan daftar latihan menjadi string
                    exercise_list_str = "\n".join(exercises)

                    # Kirim prompt ke AI
                    response = llm_chain.run({
                        "exercise_list": exercise_list_str,
                        "user_input": input_question,
                    })

                    # Ambil nama latihan yang direkomendasikan oleh AI
                    recommended_exercise = response.strip()
                    recommended_exercise = recommended_exercise.replace(" ", "_")

                    # Validasi apakah nama latihan ada dalam daftar
                    if recommended_exercise in exercise_list_str:
                    #if recommended_exercise in exercises:
                        # Kirim permintaan detail ke API untuk latihan yang direkomendasikan
                        exercise_detail_url = f"http://127.0.0.1:5000/exercises/{recommended_exercise}"
                        detail_response = requests.get(exercise_detail_url)

                        if detail_response.status_code == 200:
                            detail_data = detail_response.json()

                            # Tampilkan detail latihan
                            st.subheader(detail_data["name"])
                            st.write(f"Category: {detail_data['category']}")
                            st.write(f"Level: {detail_data['level']}")
                            st.write(f"Equipment: {detail_data['equipment']}")
                            st.write(f"Primary Muscles: {', '.join(detail_data['primaryMuscles'])}")
                            st.write(f"Secondary Muscles: {', '.join(detail_data['secondaryMuscles'])}")
                            st.write("Instructions:")
                            for idx, instruction in enumerate(detail_data["instructions"]):
                                st.write(f"{idx + 1}. {instruction}")
                            
                            # Tampilkan gambar latihan jika ada
                            for i in range(2):  # Mengasumsikan gambar bernama 0.jpg dan 1.jpg
                                img_url = f"http://127.0.0.1:5000/exercises/{recommended_exercise}/images/{i}.jpg"
                                img_response = requests.get(img_url)

                                if img_response.status_code == 200:
                                    st.image(img_response.content, caption=f"{detail_data['name']} - Step {i + 1}")
                                else:
                                    st.warning(f"Image {i}.jpg not found for {recommended_exercise}.")
                        else:
                            st.error(f"Failed to fetch details for {recommended_exercise}. Status code: {detail_response.status_code}")
                    else:
                        st.error("AI recommendation does not match any folder name on the server.")
                else:
                    st.error("No exercises found.")
            else:
                st.error(f"Failed to fetch data from API. Status code: {list_all_response.status_code}")
        except Exception as e:
            st.error(f"Error processing request: {e}")
    else:
        st.error("Please enter a question to get a recommendation.")

# Tombol reset percakapan
if st.button("Reset Conversation"):
    st.session_state.conversation = []
    st.write("Conversation reset successfully!")
