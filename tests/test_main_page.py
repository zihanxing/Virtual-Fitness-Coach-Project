import pytest
from unittest.mock import MagicMock, patch
import asyncio

# Simulate the Streamlit session state
@pytest.fixture
def session_state(mocker):
    # Mock the session state as a dictionary
    session_state = mocker.MagicMock()
    session_state.__getitem__.side_effect = lambda x: session_state._data[x]
    session_state.__setitem__.side_effect = lambda x, y: session_state._data.__setitem__(x, y)
    session_state._data = {
        'profile': {
            'name': '',
            'age': 25,
            'fitness_level': 'Beginner',
            'fitness_goals': []
        },
        'messages': [],
        'memory': MagicMock()  # Mock ConversationBufferMemory
    }
    mocker.patch('streamlit.session_state', session_state)
    return session_state

# Test updating the user profile
def test_update_profile(session_state):
    session_state['profile']['name'] = 'John Doe'
    session_state['profile']['age'] = 30
    session_state['profile']['fitness_level'] = 'Intermediate'
    session_state['profile']['fitness_goals'] = ['Weight Loss', 'Muscle Gain']
    
    assert session_state['profile']['name'] == 'John Doe'
    assert session_state['profile']['age'] == 30
    assert session_state['profile']['fitness_level'] == 'Intermediate'
    assert session_state['profile']['fitness_goals'] == ['Weight Loss', 'Muscle Gain']

# Test adding a message to chat history
def test_add_user_message(session_state):
    user_input = "How can I improve my endurance?"
    session_state['messages'].append({"role": "user", "content": user_input})
    
    assert len(session_state['messages']) == 1
    assert session_state['messages'][0]['role'] == 'user'
    assert session_state['messages'][0]['content'] == user_input

# Test generating a response using the LLM
@pytest.mark.asyncio
async def test_generate_response(session_state):
    user_input = "Tell me about a good workout routine."
    context = "workouts and exercises"
    
    # Mock the get_llm_response function
    async def mock_get_llm_response(*args, **kwargs):
        yield "Here is a workout routine for you."
    
    # Patch the function to use the mock version
    with patch('main_page.get_llm_response', mock_get_llm_response):
        # Add user message to chat history
        session_state['messages'].append({"role": "user", "content": user_input})
        
        # Create a placeholder for the assistant's response
        response_placeholder = MagicMock()
        
        # Use asyncio to run the asynchronous function
        full_response = [""]
        
        async for chunk in mock_get_llm_response(user_input, context, session_state['profile'], session_state['memory']):
            full_response[0] += chunk
            response_placeholder.markdown(f'<div class="chat-bubble assistant-bubble">{full_response[0]}</div>', unsafe_allow_html=True)
        
        # Check that the markdown method was called with the expected content
        response_placeholder.markdown.assert_called_with(
            '<div class="chat-bubble assistant-bubble">Here is a workout routine for you.</div>',
            unsafe_allow_html=True
        )
        
        # Add the full response to chat history
        session_state['messages'].append({"role": "assistant", "content": full_response[0]})
        
        assert len(session_state['messages']) == 2
        assert session_state['messages'][1]['role'] == 'assistant'
        assert session_state['messages'][1]['content'] == "Here is a workout routine for you."

