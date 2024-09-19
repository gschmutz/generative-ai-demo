#from analytics import track
from langchain.globals import set_llm_cache
from langchain_community.cache import InMemoryCache
from streamlit_feedback import streamlit_feedback
from constants import TITLE
import logging
import streamlit as st
from sidebar import sidebar

from graph_chain import get_results
from dotenv import load_dotenv

# Logging options
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# take environment variables from .env
load_dotenv()  

# App title
st.markdown(TITLE, unsafe_allow_html=True)
sidebar()

# Define message placeholder and emoji feedback placeholder
placeholder = st.empty()
emoji_feedback = st.empty()
user_placeholder = st.empty()

# Initialize message history
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "ai",
            "content": f"This is a Proof of Concept application which shows how GenAI can be used with Neo4j to build and consume Knowledge Graphs using both vectors and structured data.\nSee the sidebar for more information!",
        },
    ]

# Display chat messages from history on app rerun
with placeholder.container():
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"], unsafe_allow_html=True)

if "sample" in st.session_state and st.session_state["sample"] is not None:
    user_input = st.session_state["sample"]
else:
    user_input = st.chat_input(
        placeholder="Ask question on the IIHF Rules", key="user_input"
    )

if user_input:
    with user_placeholder.container():
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        with st.chat_message("ai"):

            # Agent response
            with st.spinner("..."):

                message_placeholder = st.empty()
                thought_container = st.container()

                # For displaying chain of thought - this callback handler appears to only works with the deprecated initialize_agent option (see rag_agent.py)
                # st_callback = StreamlitCallbackHandler(
                #   parent_container= thought_container,
                #   expand_new_thoughts=False
                # )
                # StreamlitCcallbackHandler api doc: https://api.python.langchain.com/en/latest/callbacks/langchain_community.callbacks.streamlit.streamlit_callback_handler.StreamlitCallbackHandler.html

                #agent_response = rag_agent.get_results(
                #    question=user_input, callbacks=[]
                #)
                
                result = get_results(question=user_input, strategy=st.session_state["strategy"])

                if isinstance(result, dict) is False:
                    logging.warning(
                        f"Agent response was not the expected dict type: {result}"
                    )
                    result = str(result)

                content = result["result"]

                new_message = {"role": "ai", "content": content}
                st.session_state.messages.append(new_message)

            message_placeholder.markdown(content)

    # Reinsert user chat input if sample quick select was previously used.
    if "sample" in st.session_state and st.session_state["sample"] is not None:
        st.session_state["sample"] = None
        user_input = st.chat_input(
            placeholder="Ask question on the IHHF Rulesbook", key="user_input"
        )

    emoji_feedback = st.empty()

# Emoji feedback
with emoji_feedback.container():
    feedback = streamlit_feedback(feedback_type="thumbs")
    if feedback:
        score = feedback["score"]
        last_bot_message = st.session_state["messages"][-1]["content"]
