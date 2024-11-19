import streamlit as st
import json
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.chat_models import ChatOpenAI

# Judul aplikasi
st.title("GoGym: Gym Session Recommender AI 🤖")
st.write(
    """
    Welcome to Gym Session Recommender AI! 
    Your intelligent fitness companion for personalized workout plans and weekly gym schedules. 
    Just type your fitness goals, level, or specific preferences, and let the AI handle the rest.
    """
)
# st.image("3_4_Sit-Up/1.jpg")

# Membuat garis pemisah
st.markdown("---")

# Inisialisasi OpenAI Chat Model
try:
    # Set API Key
    api_key = st.secrets["OPENAI_API_KEY"]
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)
except Exception as e:
    st.error(f"Error initializing the AI model: {e}")
    st.stop()

# Load data dari data.json
try:
    with open("data.json", "r") as file:
        data = json.load(file)
except FileNotFoundError:
    st.error("File `data.json` tidak ditemukan. Pastikan file tersebut ada di direktori.")
    st.stop()
except json.JSONDecodeError:
    st.error("File `data.json` tidak dapat dibaca. Periksa formatnya.")
    st.stop()

# Prompt untuk LLM
prompt = """
You are a highly intelligent AI assistant and a fitness expert. 
Your job is to recommend weekly workout sessions tailored to the user's preferences and goals.

Use the following structure of the data:
1. *name*: Name of the workout session.
2. *force*: Type of force used (e.g., push, pull).
3. *level*: Difficulty level (beginner, intermediate, advanced).
4. *mechanic*: Type of mechanic (compound, isolation).
5. *equipment*: Required equipment (body only, dumbbells, etc.).
6. *primaryMuscles*: Main muscle groups targeted.
7. *secondaryMuscles*: Supporting muscle groups.
8. *instructions*: Step-by-step workout instructions.
9. *category*: Workout category (strength, cardio, etc.).
10. *images*: List of images showcasing the workout.
11. *id*: Unique identifier for the workout session.

Sample question: {sample}
Please provide clear, informative recommendations based on the user’s question: {question}

When recommending workout sessions, provide only the names of the exercises, **no detailed information or instructions**. If the question asks for a list of workouts (such as a workout plan), return only the names of the exercises, with no further details.

For a weekly or monthly workout plan:
- Organize the plan by days of the week, from Day 1 to Day 7 (e.g., Day 1: Exercise 1, Exercise 2, ...; Day 2: Rest day).
- If a rest day is included, mention it explicitly (e.g., Day 3: Rest day).
- If the user doesn't specify the focus of the workout (strength, cardio, etc.), ask them to clarify their preference to ensure the workout is tailored correctly.

When the user asks for details on a specific exercise (e.g., "Can you give me the instructions for Squats?", or "How to squats?):
- Provide detailed step-by-step workout instructions for the requested exercise.
- Provide exercise images where the images path is located on the json; exercise['images'].
- Make sure the instructions are clear and easy to follow, ensuring the user understands how to perform the exercise correctly and safely.

If the user asks a question outside the scope of gym, fitness, and exercise, respond with: "Sorry, I can only assist with questions related to gym workouts and exercises."

Respond in a friendly and motivational tone.
"""

# Correctly using the variables `question` and `sample`
llm_prompt = PromptTemplate(
    template=prompt,
    input_variables=["question", "sample"]
)

# Inisialisasi percakapan
if "historical" not in st.session_state:
    st.session_state.historical = []

# LLM Chain
llm_chain = LLMChain(llm=llm, prompt=llm_prompt, verbose=True)

# Function to display chat messages
def display_chat(historical):
    for entry in historical:
        # Chat bubble styles for User and AI
        if entry["role"] == "user":
            st.markdown(f'<div style="text-align:right; padding: 5px; background-color: #E8E8E8; border-radius: 15px; margin-bottom: 5px;">{entry["message"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div style="text-align:left; padding: 5px; border-radius: 15px; margin-bottom: 5px;">{entry["message"]}</div>', unsafe_allow_html=True)

def display_exercise_details(exercise_name):
    # Mencari exercise yang sesuai dengan nama
    exercise = next((ex for ex in data['exercises'] if ex['name'].lower() == exercise_name.lower()), None)
    
    if exercise:
        # Menampilkan instruksi exercise
        st.write(f"### {exercise['name']} Instructions:")
        for instruction in exercise['instructions']:
            st.write(instruction)
        
        st.write(f"### {exercise['name']} Images:")
        
        # Pastikan ada gambar yang tersedia
        if exercise.get('images'):
            for image in exercise['images']:
                st.image(image)
        else:
            st.warning(f"Tidak ada gambar untuk {exercise['name']}.")
            
# Display chat history at the top
st.markdown("### Chat")
chat_placeholder = st.empty()  # Placeholder for chat history

# Tombol untuk memulai percakapan
input_question = st.text_area("Enter your fitness-related question here", label_visibility="collapsed")

# Sample question for context (can be dynamic if needed)
sample_question = "What is a good workout for building strength with dumbbells?"

# Tombol submit untuk memulai percakapan
if st.button("Submit"):
    if input_question:
        try:
            # Generate response based on the question and historical context
            # Add previous inputs and responses to the prompt context for more personalized responses
            conversation_context = "\n".join([f"User: {entry['message']}\nAI: {entry['message']}" for entry in st.session_state.historical])

            full_question = f"{conversation_context}\nUser: {input_question}\nAI:"

            # Generate the AI response
            response = llm_chain.run({
                "question": full_question,
                "sample": sample_question
            })

            # Save user input and AI response in historical list
            st.session_state.historical.append({"role": "user", "message": input_question})
            st.session_state.historical.append({"role": "bot", "message": response})

            # Display chat history
            with chat_placeholder.container():
                display_chat(st.session_state.historical)

        except Exception as e:
            st.error(f"Error occurred: {e}")
    else:
        st.warning("Please enter a question to start the conversation!")

# The input box remains at the bottom
st.markdown("---")
