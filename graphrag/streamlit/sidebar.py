from constants import SCHEMA_IMG_PATH, LANGCHAIN_IMG_PATH
import streamlit as st
import streamlit.components.v1 as components

def ChangeButtonColour(wgt_txt, wch_hex_colour = '12px'):
    htmlstr = """<script>var elements = window.parent.document.querySelectorAll('*'), i;
                for (i = 0; i < elements.length; ++i) 
                    { if (elements[i].innerText == |wgt_txt|) 
                        { elements[i].style.color ='""" + wch_hex_colour + """'; } }</script>  """

    htmlstr = htmlstr.replace('|wgt_txt|', "'" + wgt_txt + "'")
    components.html(f"{htmlstr}", height=0, width=0)

def sidebar():
    with st.sidebar:


# Define the options for the selectbox
        options = ["Traditional RAG", "Parent Retriever RAG", "Summary Retriever RAG", "Hypothetical Questions RAG"]

        # Create the selectbox for users to choose an option
        selected_option = st.selectbox("Which strategy to use:", options)
        st.session_state["strategy"] = selected_option

#        st.markdown(f"""This the schema in which the EDGAR filings are stored in Neo4j: \n <img style="width: 70%; height: auto;" src="{SCHEMA_IMG_PATH}"/>""", unsafe_allow_html=True)

#        st.markdown(f"""This is how the Chatbot flow goes: \n <img style="width: 70%; height: auto;" src="{LANGCHAIN_IMG_PATH}"/>""", unsafe_allow_html=True)

        st.markdown("""Questions you can ask of the dataset:""", unsafe_allow_html=True)

        # To style buttons closer together
        st.markdown("""
                    <style>
                        div[data-testid="column"] {
                            width: fit-content !important;
                            flex: unset;
                        }
                        div[data-testid="column"] * {
                            width: fit-content !important;
                        }
                    </style>
                    """, unsafe_allow_html=True)
        
        sample_questions = "How many companies are in the filings?", "Which companies are in the healthcare industry?","Which companies are vulnerable to lithium shortage?", "Which managers own more than one company?", "List the top 3 managers by the number of companies they own.", "Which 5 companies have the most managers?"

        for text, col in zip(sample_questions, st.columns(len(sample_questions))):
            if col.button(text, key=text):
                st.session_state["sample"] = text
