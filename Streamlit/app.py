import streamlit as st
import tempfile
from RAG_MultiQuery import answer_question
import datetime

# Set up the page configuration
st.set_page_config(page_title="Maintenance Assistant")

# Display the title on the main page
st.title("Maintenance Assistant")

if 'history' not in st.session_state:
    st.session_state.history = []

# File uploader for PDF files
uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")

if uploaded_file:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
        temp_file.write(uploaded_file.read())
        pdf_path = temp_file.name

    # Input text for questions
    input_text = st.text_input("Input: ", key="input")
    submit = st.button("Ask the question")

    if submit:
        response = answer_question(input_text, pdf_path)
        st.session_state.history.append({
            'timestamp': datetime.datetime.now(),
            'question': input_text,
            'response': response
        })
        st.subheader("The Response is")
        st.write(response)

# Sidebar for displaying chat history
with st.sidebar:
    st.title("EAExpertise")
    
    if st.session_state.history:
        selected_question = st.selectbox(
            "Select a question:",
            options=[entry['question'] for entry in st.session_state.history],
            index=len(st.session_state.history) - 1
        )
        
        selected_entry = next((entry for entry in st.session_state.history if entry['question'] == selected_question), None)
        
        if selected_entry:
            st.subheader("Response")
            st.write(selected_entry['response'])
        
        st.subheader("Full Chat History")
        for entry in st.session_state.history:
            st.write(f"**{entry['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}**")
         
