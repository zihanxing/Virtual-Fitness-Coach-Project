import streamlit as st
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.memory import ConversationBufferMemory
from langchain_community.llms.llamafile import Llamafile
from langchain_community.embeddings import LlamafileEmbeddings
from langchain_chroma import Chroma
import chromadb
import asyncio

embeddings = LlamafileEmbeddings()
persistent_client = chromadb.PersistentClient("./chroma_langchain_db")
vector_store_from_client = Chroma(
    client=persistent_client,
    collection_name="v_db",
    embedding_function=embeddings,
)

# Initialize the local LLM
llm = Llamafile()

# Function to get LLM response using LangChain with chat history
async def get_llm_response(user_input, context, profile, memory):
    # Retrieve relevant information from Chroma DB
    retrieved_docs = vector_store_from_client.similarity_search(user_input, k=3)
    retrieved_info = "\n".join([doc.page_content for doc in retrieved_docs])

    # Create a prompt template
    prompt_template = PromptTemplate(
        input_variables=["name", "age", "fitness_level", "fitness_goals", "context", "chat_history", "user_input", "retrieved_info"],
        template="""You are an fitness coach. The user has the following profile:
        Name: {name}
        Age: {age}
        Fitness Level: {fitness_level}
        Fitness Goals: {fitness_goals}
        
        Chat History:
        {chat_history}

        Relevant Information:
        {retrieved_info}
        
        User Query: {user_input}

        Provide a personalized response directly to the user based on all the information (with YouTube links if it is provided above). Be encouraging and specific in your advice."""
    )

    # Create a LangChain with memory
    chain = LLMChain(llm=llm, prompt=prompt_template, memory=memory)

    # Prepare the input dictionary
    chain_input = {
        "name": profile['name'],
        "age": profile['age'],
        "fitness_level": profile['fitness_level'],
        "fitness_goals": ", ".join(profile['fitness_goals']),
        "context": context,
        "user_input": user_input,
        "retrieved_info": retrieved_info
    }

    # Generate response using astream
    async for chunk in chain.astream(input=chain_input):
        yield chunk["text"]

# Set page config
st.set_page_config(layout="wide", page_title="Virtual Fitness Coach")

# Custom CSS (unchanged)
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

    # Initialize chat history and memory
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "memory" not in st.session_state:
        st.session_state.memory = ConversationBufferMemory(memory_key="chat_history", input_key="user_input")

    # Display chat messages from history on app rerun
    chat_container = st.container()
    with chat_container:
        for message in st.session_state.messages:
            bubble_class = "user-bubble" if message["role"] == "user" else "assistant-bubble"
            st.markdown(f'<div class="chat-bubble {bubble_class}">{message["content"]}</div>', unsafe_allow_html=True)

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

            # Create a placeholder for the assistant's response
            response_placeholder = st.empty()
            
            # Use a list to store the full response
            full_response = [""]

            # Use asyncio to run the asynchronous function
            async def generate_response():
                async for chunk in get_llm_response(user_input, context, st.session_state.profile, st.session_state.memory):
                    full_response[0] += chunk
                    response_placeholder.markdown(f'<div class="chat-bubble assistant-bubble">{full_response[0]}</div>', unsafe_allow_html=True)

            # Run the asynchronous function
            asyncio.run(generate_response())

            # Add the full response to chat history
            st.session_state.messages.append({"role": "assistant", "content": full_response[0]})

            # Clear the input box and rerun to update the chat
            st.rerun()