import streamlit as st
import requests
import json

# Function to get LLM response
def get_llm_response(user_input, context, profile):
    # Construct a prompt that includes the user's profile and context
    prompt = f"""You are an AI fitness coach. The user has the following profile:
    Name: {profile['name']}
    Age: {profile['age']}
    Fitness Level: {profile['fitness_level']}
    Fitness Goals: {', '.join(profile['fitness_goals'])}

    The user's query is related to {context}.
    
    User Query: {user_input}

    Provide a personalized response based on the user's profile and query. Be encouraging and specific in your advice."""

    # API call to the local LLM server
    try:
        response = requests.post('http://localhost:8080/completion', 
                                 json={
                                     "prompt": prompt,
                                     "n_predict": 200,
                                     "temperature": 0.7,
                                     "stop": ["User Query:"]  # Stop generation at the next user query
                                 })
        
        if response.status_code == 200:
            llm_response = response.json()['content'].strip()
            return llm_response
        else:
            return f"Error: Unable to get response from LLM server. Status code: {response.status_code}"
    except requests.exceptions.RequestException as e:
        return f"Error: Unable to connect to LLM server. {str(e)}"


# Set page config
st.set_page_config(layout="wide", page_title="Virtual Fitness Coach")

# Custom CSS to inject (updated for scrollable chat)
st.markdown("""
<style>
    .profile-container {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
    }
    .stButton>button {
        width: 100%;
    }
    .chat-container {
        height: 400px;
        overflow-y: auto;
        display: flex;
        flex-direction: column;
        padding: 10px;
        border: 1px solid #ccc;
        border-radius: 5px;
        margin-bottom: 20px;
    }
    .chat-bubble {
        max-width: 70%;
        margin: 5px;
        padding: 10px;
        border-radius: 15px;
        word-wrap: break-word;
    }
    .user-bubble {
        align-self: flex-end;
        background-color: #FE6A01;
        color: white;
    }
    .assistant-bubble {
        align-self: flex-start;
        background-color: #7A706C;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# Main title
st.title("🏋️ Virtual Fitness Coach")

# Create two columns
col1, col2 = st.columns([1, 3])

with col1:
    st.markdown('<div class="profile-container">', unsafe_allow_html=True)
    st.subheader("Your Fitness Profile")
    
    # Initialize session state for profile
    if 'profile' not in st.session_state:
        st.session_state.profile = {
            'name': '',
            'age': 25,
            'fitness_level': 'Beginner',
            'fitness_goals': []
        }
    
    # Profile inputs
    st.session_state.profile['name'] = st.text_input("Name", value=st.session_state.profile['name'])
    st.session_state.profile['age'] = st.number_input("Age", min_value=1, max_value=120, value=st.session_state.profile['age'])
    st.session_state.profile['fitness_level'] = st.selectbox("Fitness Level", ["Beginner", "Intermediate", "Advanced"], index=["Beginner", "Intermediate", "Advanced"].index(st.session_state.profile['fitness_level']))
    st.session_state.profile['fitness_goals'] = st.multiselect("Fitness Goals", ["Weight Loss", "Muscle Gain", "Endurance", "Flexibility"], default=st.session_state.profile['fitness_goals'])

    if st.button("Update Profile"):
        st.success("Profile updated successfully!")
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.write(f"Welcome to your personal AI fitness coach, {st.session_state.profile['name']}! Ask me about workouts, nutrition, or motivation.")

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat messages from history on app rerun
    chat_container = st.container()
    with chat_container:
        # st.markdown('<div class="chat-container">', unsafe_allow_html=True)
        for message in st.session_state.messages:
            bubble_class = "user-bubble" if message["role"] == "user" else "assistant-bubble"
            st.markdown(f'<div class="chat-bubble {bubble_class}">{message["content"]}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # User input
    user_input = st.text_input("What would you like help with?")

    if st.button("Send"):
        if user_input:
            # Add user message to chat history
            st.session_state.messages.append({"role": "user", "content": user_input})

            # Determine context
            context = "general fitness"
            if "workout" in user_input.lower() or "exercise" in user_input.lower():
                context = "workouts and exercises"
            elif "nutrition" in user_input.lower() or "diet" in user_input.lower() or "food" in user_input.lower():
                context = "nutrition and diet"
            elif "motivat" in user_input.lower() or "inspir" in user_input.lower():
                context = "fitness motivation"

            response = get_llm_response(user_input, context, st.session_state.profile)
            
            # Add assistant response to chat history
            st.session_state.messages.append({"role": "assistant", "content": response})

            # Clear the input box and rerun to update the chat
            st.experimental_rerun()

