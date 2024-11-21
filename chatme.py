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
        api_url = "http://127.0.0.1:5000/list_all"  # API endpoint for exercises list
        response = requests.get(api_url)
    
        if response.status_code == 200:
            data = response.json()  # Assumes the API returns a JSON with exercises data
            exercises = data['exercises']  # Extract the exercise names
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

    Use the following list of exercise names:
    {exercises}

    Sample question: {sample}
    Please provide clear, informative recommendations based on the user’s question: {question}
    
    If the user asks a question outside the scope of gym, fitness, and exercise, respond with: "Sorry, I can only assist with questions related to gym workouts and exercises."

    When recommending workout sessions, provide only the names of the exercises, **no detailed information or instructions**. If the question asks for a list of workouts (such as a workout plan), return only the names of the exercises, with no further details.

    For a weekly or monthly workout plan:
    - Organize the plan by days of the week, from Day 1 to Day 7 (e.g., Day 1: Exercise 1, Exercise 2, ...; Day 2: Rest day).
    - Include rest days explicitly if applicable (e.g., "Day 3: Rest day").
    - Specify the number of repetitions for each workout.
    - You can provide a workout plan for up to one month. If the user requests a plan longer than one month, politely inform them that the service is limited to one month. However, you can suggest that for subsequent months, they can repeat the same plan while progressively increasing repetitions or weights for continued improvement.
    - If the user does not specify their fitness level or the focus of their workout (e.g., strength, cardio, etc.), ask them to clarify their preferences to ensure the workout plan is tailored to their needs.

    When the user asks for details on a specific exercise (e.g., "Can you give me the instructions for Squats?", or "How to squat?"):
    - Provide detailed step-by-step workout instructions for the requested exercise.
    - Make sure the instructions are clear and easy to follow, ensuring the user understands how to perform the exercise correctly and safely.

    Respond in a friendly and motivational tone.
    """

    # Correctly using the variables `question` and `sample`
    llm_prompt = PromptTemplate(
        template=prompt,
        input_variables=["question", "sample", "exercises"]
    )

    # Inisialisasi percakapan
    if "historical" not in st.session_state:
        st.session_state.historical = []

    # LLM Chain
    llm_chain = LLMChain(llm=llm, prompt=llm_prompt, verbose=True)

    # Sample question for context (can be dynamic if needed)
    sample_question = "What is a good workout for building strength with dumbbells?"
    
    # def extract_exercise_name(response, exercises):
    #     """
    #     This function checks if the response contains the name of an exercise from the list
    #     and returns the name if found. It assumes the exercise name is directly mentioned.
    #     """
    #     for exercise in exercises:
    #         if exercise.lower() in response.lower():
    #             return exercise
    #     return None 
    def extract_exercise_name(response, exercises):
        """
        This function checks if the response contains the name of an exercise from the list
        and returns the name if found. It assumes the exercise name is directly mentioned.
        """
        # Mengubah nama exercise dalam response dan exercises menjadi PascalCase
        response_pascal = to_pascal_case(response)

        for exercise in exercises:
            # Ubah nama exercise dalam daftar menjadi PascalCase
            exercise_pascal = to_pascal_case(exercise)
            if exercise_pascal.lower() in response_pascal.lower():
                return exercise_pascal
        return None


    def display_images(exercise_name):
        """
        This function displays images related to a specific exercise.
        It will try to show two images (i=0 and i=1) for the given exercise.
        """
        try:
            for i in range(2):  # Two images per exercise (i=0 and i=1)
                img_url = f"http://127.0.0.1:5000/exercises/{exercise_name}/images/{i}.jpg"
                exercise_name_img = exercise_name.lower()
                exercise_name_img = exercise_name.replace("_", " ")
                st.image(img_url, caption=f"Step {i+1} - {exercise_name_img} ", use_column_width=True)
        except Exception as e:
            st.error(f"Error loading images for {exercise_name}: {e}")
            # Fungsi untuk mengubah string menjadi PascalCase
    def to_pascal_case(text):
        words = text.split()  # Pisahkan berdasarkan spasi
        return '_'.join(word.capitalize() for word in words)  # Gabungkan dan kapitalisasi setiap kata
  
    def should_display_images(question):
        """
        This function checks if the user's question contains keywords like 'caranya' or 'how to'.
        If true, images will be displayed.
        """
        return "caranya" in question.lower() or "how to" in question.lower() or "cara" in question.lower()

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
            conversation_context = "\n".join([f"{entry['message']}" for entry in st.session_state.historical])
            full_question = f"{conversation_context}\nUser: {prompt}\nAI:"
            
            # Generate the AI response, passing the fetched exercises data
            response = llm_chain.run({
                "question": full_question,
                "sample": sample_question,
                "exercises": ", ".join(exercises)  # Pass the exercises list as a string
            })
            
            # Save user input and AI response in historical list
            st.session_state.historical.append({"role": "user", "message": prompt})
            
            # Display the user message once
            with st.chat_message("user"):
                st.markdown(prompt)
            
            # Display the assistant response once
            with st.chat_message("assistant"):
                st.markdown(response)
                
                # Ubah nama exercise dalam response menjadi PascalCase
                exercise_name = extract_exercise_name(response, exercises)
                if exercise_name and should_display_images(prompt):
                    # Ubah nama exercise yang diekstrak menjadi PascalCase
                    exercise_name_pascal = to_pascal_case(exercise_name)
                    display_images(exercise_name_pascal)    

            # Add assistant response to chat history
            st.session_state.historical.append({"role": "assistant", "message": response})  

        except Exception as e:
            st.error(f"Error occurred: {e}")


# Run the app
if __name__ == "__main__":
    run()
