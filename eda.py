# Import libraries
import pandas as pd

# Library for model deployment interface
import streamlit as st

# Visualization
import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud

# Create a function to run the streamlit interface
def run():
    # Center-aligned title
    st.markdown("<h1 style='text-align: center;'>Exploratory Data Analysis</h1>", unsafe_allow_html=True)

    # Banner
    # st.image('CustomerChurnBanner_EDA.jpg')

    # Dataframe section
    # Load dataset
    df = pd.read_json('data.json')

    # Define a function to categorize force
    def categorize_force(exercise_name):
        if exercise_name in [
            "Balance Board", "Conan's Wheel", "Farmer's Walk", "Rickshaw Carry", "Lying Prone Quadriceps", "Yoke Walk"
        ]:
            return "static"
        elif exercise_name in [
            "Bicycling", "Bicycling, Stationary", "Elliptical Trainer", "Jogging, Treadmill", "Push-Up Wide",
            "Recumbent Bike", "Rope Jumping", "Running, Treadmill", "Skating", "Smith Machine Decline Press", 
            "Stairmaster", "Step Mill", "Trail Running/Walking", "Walking, Treadmill", "Carioca Quick Step",
            "Inchworm", "Linear Acceleration Wall Drill", "Moving Claw Series"
        ]:
            return "push"
        elif exercise_name in [
            "Band Assisted Pull-Up", "Incline Inner Biceps Curl", "Internal Rotation with Band", "Rowing, Stationary",
            "Single Dumbbell Raise"
        ]:
            return "pull"
        else:
            return "unknown"  # Fallback for unrecognized exercises

    # Fill missing values in the 'force' column
    df['force'] = df.apply(lambda row: categorize_force(row['name']) if pd.isnull(row['force']) else row['force'], axis=1)

    # Define a function to categorize equipment
    def categorize_equipment(exercise_name):
        body_only = [
            "Ankle Circles", "Ankle On The Knee", "Arm Circles", "Bodyweight Walking Lunge",
            "Calf Stretch Elbows Against Wall", "Calf Stretch Hands Against Wall", "Cat Stretch",
            "Chair Lower Back Stretch", "Child's Pose", "Chin To Chest Stretch", "Crossover Reverse Lunge",
            "Dancer's Stretch", "Decline Push-Up", "Elbow Circles", "Elbows Back", "Groin and Back Stretch",
            "Hamstring Stretch", "Hug Knees To Chest", "Inverted Row", "Knee Across The Body",
            "Kneeling Arm Drill", "Kneeling Forearm Stretch", "Kneeling Hip Flexor", "Leg-Up Hamstring Stretch",
            "Looking At Ceiling", "Middle Back Stretch", "On Your Side Quad Stretch", "One Arm Against Wall",
            "One Half Locust", "One Knee To Chest", "Overhead Stretch", "Pelvic Tilt Into Bridge",
            "Prone Manual Hamstring", "Runner's Stretch", "Scapular Pull-Up", "Seated Calf Stretch",
            "Seated Floor Hamstring Stretch", "Seated Hamstring", "Seated Overhead Stretch", "Shoulder Circles",
            "Shoulder Raise", "Shoulder Stretch", "Side-Lying Floor Stretch", "Side Lying Groin Stretch",
            "Side Neck Stretch", "Side Wrist Pull", "Spinal Stretch", "Standing Gastrocnemius Calf Stretch",
            "Standing Hip Flexors", "Standing Lateral Stretch", "Standing Soleus And Achilles Stretch",
            "Standing Toe Touches", "The Straddle", "Tricep Side Stretch", "Triceps Stretch",
            "Upper Back-Leg Grab", "Upper Back Stretch", "Upward Stretch", "Windmills"
        ]
        return "body only" if exercise_name in body_only else "other"

    # Check for missing values in the 'equipment' column and apply the function only to those rows
    df['equipment'] = df['equipment'].apply(lambda x: categorize_equipment(x) if pd.isna(x) else x)

    # Fill missing values in the 'mechanic' column
    df['mechanic'] = df['mechanic'].fillna('unknown')

    # Fill empty lists in the 'secondaryMuscles' column with 'none'
    df['secondaryMuscles'] = df['secondaryMuscles'].apply(lambda x: ['none'] if isinstance(x, list) and len(x) == 0 else x)

    # Flatten the primaryMuscles column to strings if there's only one muscle in each list
    df['primaryMuscles'] = df['primaryMuscles'].apply(lambda x: x[0] if isinstance(x, list) and len(x) == 1 else x)

    # If 'instructions' contains lists, join them into strings
    df['instructions'] = df['instructions'].apply(lambda x: ' '.join(x) if isinstance(x, list) else x)


    # Description
    st.write('This page will explore the dataset thoroughly.')

    # Show the dataframe
    st.dataframe(df.head())

    # Section EDA
    st.write('## Exploratory Data Analysis (EDA)')

    # Visualization
    st.write('### Pie Chart of Different Column Categories')

    # Option
    option = st.selectbox('Select One Column', ('force', 'level', 'mechanic', 'category'))

    counts = df[option].value_counts()

    # Visiualization
    fig = plt.figure(figsize=(7, 7))
    plt.pie(counts, labels=counts.index, autopct='%1.2f%%', startangle=90)
    plt.title('Distribution of Force Categories')
    plt.axis('equal')  

    # Show the plot
    st.pyplot(fig)

    # Observation
    if option == 'force':
        st.write('**Overview**:\n'
        '- This column represents the type of force exerted during the exercise, where this dataset divides into three categories of force: **Push, Pull and Static**.\n\n'
        '**Background**:\n'
        '- According to [an article done by Aston University Birmingham UK](https://www.aston.ac.uk/sport/news/tips/fitness-exercise/push-pull-legs), **push and pull workouts are the two essential forces used to train all parts of a human body**, where workouts that utilize push forces trains the front side of the body while pull forces trains the back side. These two forces are essential in bodybuilding, and has been a popularized routine since 1987 documented in [a workout book mmade by the legendary bodybuilder Arnold Schwarzenegger](https://search.worldcat.org/title/15244528).\n'
        '- On the other hand, **static exercises refer to the warm-up routines** that people do before workouts in order to improve joint stability, muscle endurance, and posture improvement, as claimed by [an article made by the American Council on Exercise (ACE)](https://www.acefitness.org/resources/everyone/blog/7258/improve-your-posture-with-these-isometric-exercises/).\n'
        '\n**Observation**:\n'
        '- This dataset has almost an equal amount of exercises that exert push forces and pull forces which amount in more or less (44%) of the whole dataset each.\n'
        '- Static exercises, on the other hand, are less-represented with only (12.6%) from the dataset alone.\n'
        '\n**Insights**\n'
        '- This distribution means that the dataset clearly represents a fair balance between pull and push exercises, offering users a wide range of exercises for training opposing muscle groups. This gives the chatbot better fairness in developing workout plans that trains the two essential forces to train all parts of human body.\n'
        '- Whilst static exercises have much lower representation compared to the other two, as [the article by American Heart Association suggests](https://www.heart.org/en/healthy-living/fitness/fitness-basics/warm-up-cool-down#:~:text=Warm%20up%20for%205%20to,Use%20your%20entire%20body.), these exercises only take 5 - 10 minutes each session. Since these exercises only take a minor portion of the whole workout, not much data is needed in comparison to the other two.\n'
        '- In conclusion, the data has enough well-rounded sets of information for the chatbot to recommend users.'
        )
    elif option == 'level':
        st.write('**Overview**:\n'
        '- This column represents the difficulty level of each exercise, where this dataset into three levels of difficulty: **Beginner, Intermediate and Expert**.\n'
        '\n**Background**:\n'
        '- It is no secret that **progressive overload is the key to achieving better fitness results**. [A research done by the Front Physiol in 2019](https://journals.lww.com/acsm-msse/fulltext/2009/03000/progression_models_in_resistance_training_for.26.aspx) suggests that this progression allows for constant stimulation in the muscle as the muscles are already used to the easier repertoire. One way to increase progression is by increase the technical difficulty of exercises, as the research suggests.\n'
        '\n**Observation**:\n'
        '- The majority of exercises in the dataset (59.91%) are categorized as suitable for beginners, indicating a strong emphasis on accessibility for individuals new to fitness.\n'
        '- Another significant portion (33.56%) is aimed at intermediate users, suggesting the dataset also caters to individuals with moderate experience looking to progress in their fitness journey.\n'
        '- Only a small portion (6.53%) of the exercises are categorized for experts, reflecting a smaller focus on advanced-level workouts.\n'
        '\n**Insights**:\n'
        '- This observation implies that the dataset prioritizes inclusivity for the general population over specialized training.\n'
        '- Since the chatbot is designed mostly for the general population, the majority being beginner exercises yet still having a progression to intermediate and expert means it fits the chatbot\'s objective.'
        )
    elif option == 'mechanic':
        st.write('**Overview**:\n'
        '- This column represents how the exercises engage with their respective muscle groups, divided into two: compound exercises (exercises that target multiple muscle groups) and isolation exercises(exercises that target a specific muscle group).\n'
        '\n**Observation**:\n'
        '- The majority of the exercises in this dataset belong in compound exercises with over half the dataset (56.01%).\n'
        '- Isolation belongs in the lower half, with (34.02%) of the dataset.\n'
        '- The last 10% of the exercises in this dataset are unknown, meaning that there is no available information on whether or not these exercises train multiple muscle groups or just individual.\n'
        '\n**Insights**:\n'
        '- The majority belonging to compound might be attributed to the fact that most beginner friendly exercises are compound, and experts like [in this gymshark article](https://row.gymshark.com/blog/article/compound-vs-isolation-exercises) suggest that isolation exercises are more risky to do for beginners.\n'
        )
    elif option == 'category':
        st.write('**Overview**:\n'
        '- This column represents the exercise category based on the type of exercise, which consists of six different categories of exercise: strength, stretching, plyometrics, powerlifting, olympic weightlifting, strongman, and cardio.\n'
        '\n**Observation**\n'
        '- In this dataset, strength category exercises remain the distinct majority with as much as (66.55%) of the dataset being strength exercises.\n'
        '- The second majority, although not as distinct of a majority as strength exercises, are stretching, which contains (14.09%) of the dataset.\n'
        '- The smallest portion of exercises here is cardiovascular exercises, accounting for only (1.6%) of the dataset.\n'
        '- The rest of the exercises here are specialized kind of exercises that are tailored more for a specific kind of purpose, such as plyometrics, powerlifting, olympic weightlifting, and strongman.\n'
        '\n**Insights**:\n'
        '- This suggests that the dataset heavily emphasizes strength-based exercises, making it ideal for the general population looking to build muscle, improve strength, or engage in functional fitness.\n'
        '- Stretching being the substantial proportion of the dataset underlines its significance in warm-up/cool-down routines to ensure that its users do the necessary procedure before starting a workout.\n'
        '- The other, more specific categories, means that this dataset also accounts for the more difficult kind of exercises that are tailored for users looking to learn competition exercises.'
        )
    else:
        st.write('No insights because no column is chosen!')

    # Visualization
    st.write('### Exercise Level Percentage by Category')

    # Ensure 'level' is ordered with "expert" at the top
    df['level'] = pd.Categorical(df['level'], categories=['beginner', 'intermediate', 'expert'], ordered=True)

    # Calculate the ratio of levels within each category
    category_ratio = df.groupby('category')['level'].value_counts(normalize=True).unstack()

    # Create a figure and axis explicitly
    fig1, ax = plt.subplots(figsize=(10, 6))

    # Plot the stacked bar chart with 'expert' at the top
    category_ratio.plot(kind='bar', stacked=True, ax=ax)

    # Customize the plot
    ax.set_title('Proportion of Exercise Levels by Category')
    ax.set_xlabel('Exercise Category')
    ax.set_ylabel('Proportion')
    ax.legend(title='Level', loc='upper right')

    plt.tight_layout()  # Adjust layout

    # Show the plot
    st.pyplot(fig1)

    # Insights
    st.write('**Background**:\n'
    '- Certain exercise categories are bound to be filled with harder exercises than others, especially for the ones that are specialized for the purpose of competition, so displaying information will give us a better understanding on the difficulty distribution of exercises.\n'
    '- In this case, stacked bar chart is used to display the amount of exercises in certain difficulty levels for each category.'
    '\n**Observation**:\n'
    '- From this stacked bar chart, we can see the two categories that represent our dataset, strength and stretching, having roughly the same amount of beginner-intermediate-expert ratio with about 60:30:10 roughly for each of them.\n'
    '- We can also see on the other hand, [specialized category of exercises that are aimed to train experts for competition](https://www.paralympic.org/powerlifting/about) such as olympic weightlifting, powerfilting, and strongman, the amount of exercises that are intermediate and expert far exceeds the beginner level exercises.\n'
    '- Polymetrics have the most percentage of beginner level exercises in comparison to others.\n'
    '\n**Insights**\n'
    '- Categories such as cardio, stretching, and strength exercises are predominantly beginner-friendly. This suggests that these types of exercises are accessible to a broader audience and can serve as a starting point for individuals new to fitness.\n'
    '- Plyometrics and Olympic weightlifting exhibit a higher proportion of intermediate-level exercises. These types of exercises often require a moderate to advanced skill level.\n'
    '- These ratios show us that while the chatbot will predominantly contain beginner-friendly exercises, it also has some exercises category that can be catered towards those who are of intermediate and above skill-level.'
    )

    # Visualization
    st.write('### Word Cloud of Instructions')

    # Combine all instructions into one large string for the word cloud
    all_instructions = ' '.join(df['instructions'])

    # Step 2: Generate the word cloud
    wordcloud = WordCloud(width=800, height=400, background_color='white').generate(all_instructions)

    # Step 3: Plot the word cloud
    fig2 = plt.figure(figsize=(10, 6))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')  # Remove axes
    plt.title('Word Cloud of Instructions', fontsize=16)

    # Show the plot
    st.pyplot(fig2)

    # Insights
    st.write('**Observation**:\n'
    '- Words such as "starting", "position", "back", "knee", "floor", "leg", and "hip" are prominently featured in the word cloud. These terms likely reflect key instructions related to exercise setup and execution.\n'
    '- Other frequent terms include "barbell", "dumbbell", and "movement", indicating common equipment and actions that are commonly used in the exercises.\n'
    '\n**Insights**:\n'
    '- The dominance of terms like "starting",  "position" and body part references shows that the instructions presented in the dataset emphasize proper setup and initial alignment for exercises. This clarifies the validity of the dataset in making accurate instructions, especially for beginners who require detailed guidance on form and technique.\n'
    '- The frequent mention of equipment like "bar" and "dumbbell" suggests that the dataset includes a significant number of weight-training exercises. As evident from [a research done by Jackson J. Fye in 2022](https://link.springer.com/article/10.1007/s40279-021-01605-8), these exercises allow users to perform daily tasks much easier, which will benefit the target users of the ChatBot.\n'
    '- The frequency in words that define human body parts highlights that the exercises cover all kinds of muscle groups, ensuring that the chatbot will offer the users a moe well-rounded workout approach.'
    )

    # Visualization
    st.write('### Heatmap of Category vs Equipment (in terms of percentage)')

    # Step 1: Group by category and equipment, counting occurrences
    heatmap_data = df.groupby(['category', 'equipment']).size().unstack(fill_value=0)

    # Step 2: Convert counts to ratios
    heatmap_data_ratio = heatmap_data.div(heatmap_data.sum(axis=1), axis=0)

    # Step 3: Plot the heatmap
    fig3 = plt.figure(figsize=(12, 8))
    sns.heatmap(heatmap_data_ratio, annot=True, fmt=".2f", cmap="Blues", cbar_kws={'label': 'Proportion'})

    # Step 4: Add labels and title
    plt.title('Proportion Heatmap of Category vs Equipment', fontsize=16)
    plt.xlabel('Equipment', fontsize=12)
    plt.ylabel('Category', fontsize=12)
    plt.xticks(rotation=45, ha='right')
    plt.yticks(rotation=0)
    plt.tight_layout()

    # Show the heatmap
    st.pyplot(fig3)

    # Insights
    st.write('**Observation**:\n'
    '- Cardio exercises predominantly use machine (64%) and other equipment (36%), which indicates that the cardio exercises suggested in this dataset make use of several equipments.\n'
    '- Olympic weightlifting exclusively relies on barbells and no other equipment, which aligns with the nature of Olympic weightlifting focusing on compound barbell movements.\n'
    '- Plyometrics exercises commonly uses a combination of either body only (21%), medicine ball (25%), and other types of equipment not mentioned (51%).\n'
    '- Powerlifting dominantly uses barbells (82%) as expected, given the emphasis on compound exercises like squat, bench press, and deadlift.\n'
    '- Strength training, unlike any other categories in this dataset, utilizies almost every single equipment in the dataset, indicating its variety in equipment usage.\n'
    '- Stretching primarily relies on other types of equipment (61%) and body only (19%).\n'
    '- Exclusively relies on "other" equipment (100%), likely due to the specialized nature of strongman training using stones or yokes or any kind of heavy object.\n'
    '\n**Insights**:\n'
    '- The heatmap highlights clear trends in equipment usage for different exercise categories. For example, cardio and stretching focus on minimal or no equipment, while Olympic weightlifting and powerlifting rely heavily on barbells.\n'
    '- This dataset has a lot of category of exercises that are niche, hence the frequent use of "other" equipments.\n'
    '- For future recommendation of this dataset, the data "other" can be further specified since this dataset incorporates a lot of equipment that do not belong in any other equipment categories.'
    )

if __name__ == '__main__':
    run()