import streamlit as st
import requests
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.chat_models import ChatOpenAI

def run():
# Judul aplikasi
    st.title("GoGym: Workout Recommender 🤖")
    st.write(
        """
        Your intelligent fitness companion for personalized workout plans and weekly gym schedules. 
        Just type your fitness goals, level, or specific preferences, and let the AI handle the rest.
        """
    )
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
    
    # Get exercises data via API
    try:
        api_url = "https://0845-139-228-111-126.ngrok-free.app/list_all"  # API endpoint for exercises list
        response = requests.get(api_url)
    
        if response.status_code == 200:
            data = response.json()  # Assumes the API returns a JSON with exercises data
        else:
            st.error(f"Failed to retrieve data from API. Status code: {response.status_code}")
            st.stop()
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching data from the API: {e}")
        st.stop()
    
    # Prompt for LLM
    prompt = """
    You are a highly intelligent AI assistant and a fitness expert. 
    Your job is to recommend weekly workout sessions tailored to the user's preferences and goals.
    
    Use the following structure of the data:
    1. *name*: Name of the workout session.
    2. *force*: Type of force used (e.g., push, pull, static).
    3. *level*: Difficulty level (beginner, intermediate, expert).
    4. *mechanic*: Type of mechanic (compound, isolation).
    5. *equipment*: Required equipment.
    6. *primaryMuscles*: Main muscle groups targeted.
    7. *secondaryMuscles*: Supporting muscle groups.
    8. *instructions*: Step-by-step workout instructions.
    9. *category*: Workout category (strength, cardio, powerlifting, stretching, etc.).
    10. *images*: List of images showcasing the workout.
    11. *id*: Unique identifier for the workout session.
    
    Sample question: {sample}
    Please provide clear, informative recommendations based on the user’s question: {question}
    
    If the user asks a question or give a sentence that outside the scope of gym, fitness, or exercise, respond with: "Sorry, I can only assist with questions related to gym workouts and exercises."
    
    When recommending workout sessions, provide only the names of the exercises, **no detailed information or instructions**. If the question asks for a list of workouts (such as a workout plan), return only the names of the exercises, with no further details.
    
    For a weekly or monthly workout plan:
    - Organize the plan by days of the week, from Day 1 to Day 7 (e.g., Day 1: Exercise 1, Exercise 2, ...; Day 2: Rest day).
    - Include rest days explicitly if applicable (e.g., "Day 3: Rest day").
    - Specify the number of repetitions for each workout.
    - You can provide a workout plan for up to one month. If the user requests a plan longer than one month, politely inform them that the service is limited to one month. However, you can suggest for subsequent months, they can repeat the same plan while progressively increasing repetitions or weights for continued improvement.
    - If the user does not specify their fitness level or the focus of their workout (e.g., strength, cardio, etc.), ask them to clarify their preferences to ensure the workout plan is tailored to their needs.
    
    When the user asks for details on a specific exercise (e.g., "Can you give me the instructions for Squats?", or "How to squat?"):
    - Provide detailed step-by-step workout instructions for the requested exercise.
    - Make sure the instructions are clear and easy to follow, ensuring the user understands how to perform the exercise correctly and safely.
    
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
    
    # Sample question for context (can be dynamic if needed)
    sample_question = "What is a good workout for building strength with dumbbells?"
    
    if "openai_model" not in st.session_state:
        st.session_state["openai_model"] = "gpt-4o-mini"
    
    if "historical" not in st.session_state:
        st.session_state.historical = []
    
    # Display chat messages from history on app rerun
    for message in st.session_state.historical:
        with st.chat_message(message["role"]):
            st.markdown(message["message"])
    
    # Tombol submit untuk memulai percakapan
    if prompt := st.chat_input("Enter your fitness-related question here"):
        try:
            # Generate response based on the question and historical context
            # Add previous inputs and responses to the prompt context for more personalized responses
            conversation_context = "\n".join([f"User: {entry['message']}\nAI: {entry['message']}" for entry in st.session_state.historical])
            full_question = f"{conversation_context}\nUser: {prompt}\nAI:"
            # Generate the AI response
            response = llm_chain.run({
                "question": full_question,
                "sample": sample_question
            })
            # Save user input and AI response in historical list
            st.session_state.historical.append({"role": "user", "message": prompt})
            
            with st.chat_message("user"):
                st.markdown(prompt)
            # Display assistant response in chat message container
            with st.chat_message("assistant"):
                st.markdown(response)
            # Add assistant response to chat history
            st.session_state.historical.append({"role": "assistant", "message": response})
        except Exception as e:
            st.error(f"Error occurred: {e}")

# Run the app
if __name__ == "__main__":
    run()