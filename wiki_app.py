import streamlit as st
from wiki_tools import WikiTools
import wikipedia

# Page config
st.set_page_config(page_icon="📚", page_title="Ask Wiki",
                   layout="centered", initial_sidebar_state="auto", menu_items=None)

# Initialize session state for index, chat_engine, and messages if not already done
if "topic" not in st.session_state:
    st.session_state["topic"] = None
if "index" not in st.session_state:
    st.session_state["index"] = None
if "chat_engine" not in st.session_state:
    st.session_state["chat_engine"] = None
if "messages" not in st.session_state:
    st.session_state["messages"] = [
        {"role": "assistant",
            "content": ":sparkles: Hello, Posez moi une question sur la page Wikipedia ? :star:"}
    ]
if "response_gen" not in st.session_state:
    st.session_state["response_gen"] = None

# reset messages


def reset_message_session():
    hello_message = {"role": "assistant",
                     "content": ":sparkles: Hello, Posez moi une question sur la page Wikipedia ? :star:"}
    st.session_state["messages"] = [hello_message]


# Sidebar
with st.sidebar:
    "[![Open in GitHub](https://github.com/codespaces/badge.svg)](https://github.com/0xZee/groq-ragbot/)"
    st.code("https://github.com/0xZee/")
    app_info = {
        "📚 🤖": "Ask specific Wikipedia Page",
        "Inference": "Groq LPU",
        "LLM": "llama3-8b",
        "framework": "llama_index",
        "tools": "WikiLoader",
        "Embedding": "HuggingFace Embedding",
    }
    st.json(app_info, expanded=False)
    st.divider()

# Main page
st.subheader(
    "🌐 :orange-background[Ask Wiki] :red-background[ChatBot] 📚", divider="grey")

# User Input container
with st.container(border=True):
    user_input = st.text_input(
        "🤖 Recherche Pages Wikipedia", placeholder="Leo Messi, Mission Appolo...")
    if user_input:
        results = wikipedia.search(user_input, results=9)
        if results:
            st.session_state["topic"] = st.selectbox(
                "📌 Pages Wikipedia Disponibles :", results)
    # x1, x2 = st.columns(2)
    # wk_phys = x1.button("Physique Quantique", use_container_width=True)
    # wk_france = x2.button("Révolution Française",
    #                      use_container_width=True)
    # if wk_phys:
    #    st.session_state.topic = "Physique Quantique"
    # if wk_france:
    #    st.session_state.topic = "Révolution Française"

    submit = st.button("Index Wikipedia Page",
                       use_container_width=True, type="primary")

# Process
if (submit and (st.session_state["topic"] is not None)):
    with st.spinner("Loading and Indexing Data.."):
        try:
            st.session_state["index"] = WikiTools().load_index(
                [st.session_state["topic"]])
            st.success(f"Wikipedia Page Loaded and Indexed")
            reset_message_session()
        except Exception as e:
            st.error(f"Error occurred in load_index: {e}")

    # Set chat engine
    try:
        st.session_state["chat_engine"] = WikiTools().set_condense_chatengine(
            index=st.session_state["index"])
    except Exception as e:
        st.error(f"Error occurred in setting chat engine: {e}")

# Display the prior chat messages
for message in st.session_state["messages"]:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# Chat session controls
with st.sidebar:
    st.subheader("⚙️ CHAT SESSION PARAM.", divider="grey")
    if st.button("Clear Chat Session", use_container_width=True, type="primary"):
        reset_message_session()
        # st.session_state["messages"] = [{"role": "assistant", "content": ":sparkles: Hello, Posez moi une question sur la page Wikipedia ? :star:"}]
    if st.button("Clear Chat Memory", use_container_width=True, type="secondary"):
        if st.session_state["chat_engine"]:
            st.session_state["chat_engine"].reset()

# Prompt for user input and save to chat history
if prompt := st.chat_input("Your question"):
    st.session_state["messages"].append(
        {"role": "user", "content": str(prompt)})

    # Display the new question immediately after it is entered
    with st.chat_message("user"):
        st.write(prompt)

    # Generate a new response
    with st.chat_message("assistant"):
        response = st.session_state["chat_engine"].stream_chat(prompt)
        response_str = ""
        response_container = st.empty()
        for token in response.response_gen:
            response_str += token
            response_container.markdown(response_str)

        st.session_state["messages"].append(
            {"role": "assistant", "content": str(response.response)})

    # Save the state of the generator
    st.session_state["response_gen"]
