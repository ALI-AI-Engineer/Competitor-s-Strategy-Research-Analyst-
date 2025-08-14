import streamlit as st
from langchain.agents import initialize_agent, Tool
from langchain.memory import ConversationBufferMemory
from langchain.chat_models import ChatOpenAI
from langchain.tools import tool
from langchain_community.utilities import GoogleSearchAPIWrapper
import tempfile
import os
from langchain.document_loaders import PyPDFLoader, TextLoader, CSVLoader
from langchain.document_loaders import UnstructuredURLLoader
# =================
# PAGE CONFIG
# =================
st.set_page_config(page_title="Competitive Intelligence Assistant", page_icon="🤖", layout="wide")

st.title("🤖 Multi-Source Competitor's Intelligence Research Agent")
st.write("Ask questions across PDFs, CSVs, TXT, URLs, and Google Search.")
main_agent = st.empty()
# =================
# SIDEBAR – DATA INPUT
# =================
st.sidebar.header("📂 Data Input")

uploaded_files = st.sidebar.file_uploader(
    "Upload PDF/TXT/CSV", type=["pdf", "txt", "csv"], accept_multiple_files=True
)

documents = []
# Loop through files in the data folder
for file in os.listdir(uploaded_files):
    try:
        file_path = os.path.join(uploaded_files, file)

        if file.endswith(".pdf"):
            loader = PyPDFLoader(file_path)
        elif file.endswith(".txt"):
            loader = TextLoader(file_path, encoding="utf-8")  # encoding avoids errors
        elif file.endswith(".csv"):
            loader = CSVLoader(file_path, source_column="industry")  # You can add delimiter="," if needed
        else:
            print(f"Skipped {file}, can't upload this file.")
            continue

        # Load data and extend the documents list
        data = loader.load()
        documents.extend(data)
        print(f"Loaded {len(data)} documents from {file}")

    except Exception as e:
        print(f"Error loading {file}: {e}")


url_input = st.sidebar.text_input("Enter a URL to load data")

url = url_input.strip()
loader = UnstructuredURLLoader(urls=url.split(","))
data = loader.load()
documents.extend(data)
print(f"Loaded {len(data)} documents from URL: {url}")


google_query = st.sidebar.text_input("Google Search Query")

import os
os.environ["GOOGLE_API_KEY"] = os.getenv("Google_API_KEY")
os.environ["GOOGLE_CSE_ID"] = os.getenv("Google_CSE_ID")
search = GoogleSearchAPIWrapper()
tools = [
    Tool(
        name="Google Search",
        func=search.run,
        description="Useful for answering questions about current events or finding information not in the documents."
    )
]
data = tools.run(google_query)
print(f"Google Search returned {data} results.")

documents.extend(data)

run_agent = st.sidebar.button("🚀 Run Agent")

# =================
# MAIN CHAT INTERFACE
# =================
st.subheader("💬 Chat with the Agent")
user_question = st.text_input("Ask me anything:")

if st.button("Send"):
    if user_question.strip() != "":
        with st.spinner("Thinking..."):
            response = agent.run(user_question)
        st.markdown(f"**You:** {user_question}")
        st.markdown(f"**Agent:** {response}")

# =================
# DEV MODE: REASONING TRACE
# =================
with st.expander("🛠 Reasoning Trace (Developer Mode)"):
    st.write(agent.verbose)
