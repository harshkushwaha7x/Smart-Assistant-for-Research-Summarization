import streamlit as st
from src.document_parser import parse_document
from src.summarizer import summarize_document
from src.qa_engine import ask_question, generate_challenges, evaluate_answer, find_snippet
import os
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="Smart Research Assistant", layout="wide")
st.title("Smart Assistant for Research Summarization")

# File upload
uploaded_file = st.file_uploader("Upload a PDF or TXT document", type=["pdf", "txt"])

if uploaded_file:
    # Parse document
    doc_text = parse_document(uploaded_file)
    st.session_state['doc_text'] = doc_text
    # Auto-summary
    summary = summarize_document(doc_text)
    st.session_state['summary'] = summary
    st.subheader("Document Summary (≤ 150 words)")
    st.write(summary)
    # Initialize chat history
    if 'chat_history' not in st.session_state:
        st.session_state['chat_history'] = []
    # Mode selection
    mode = st.radio("Choose an interaction mode:", ["Ask Anything", "Challenge Me"])
    if mode == "Ask Anything":
        st.subheader("Ask Anything")
        user_q = st.text_input("Enter your question about the document:")
        if user_q:
            # Add chat history to context
            chat_context = ""
            for q, a, just in st.session_state['chat_history'][-3:]:
                chat_context += f"Q: {q}\nA: {a}\nJustification: {just}\n"
            answer, justification = ask_question(doc_text, user_q, chat_context)
            st.session_state['chat_history'].append((user_q, answer, justification))
            st.markdown(f"**Answer:** {answer}")
            st.markdown(f"_Justification:_ {justification}")
            # Highlight snippet if found
            snippet = find_snippet(doc_text, justification)
            if snippet:
                st.markdown(f"<span style='background-color: #ffe066'>{snippet}</span>", unsafe_allow_html=True)
    elif mode == "Challenge Me":
        st.subheader("Challenge Me")
        if 'challenges' not in st.session_state:
            st.session_state['challenges'] = generate_challenges(doc_text)
            st.session_state['user_answers'] = [None]*3
            st.session_state['feedback'] = [None]*3
        for i, q in enumerate(st.session_state['challenges']):
            st.markdown(f"**Q{i+1}: {q}**")
            user_a = st.text_input(f"Your answer to Q{i+1}", key=f"ans_{i}")
            if user_a:
                feedback, justification = evaluate_answer(doc_text, q, user_a)
                st.session_state['feedback'][i] = (feedback, justification)
            if st.session_state['feedback'][i]:
                fb, just = st.session_state['feedback'][i]
                st.markdown(f"**Feedback:** {fb}")
                st.markdown(f"_Justification:_ {just}")
                snippet = find_snippet(doc_text, just)
                if snippet:
                    st.markdown(f"<span style='background-color: #ffe066'>{snippet}</span>", unsafe_allow_html=True) 