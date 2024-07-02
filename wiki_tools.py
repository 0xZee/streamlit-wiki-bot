import streamlit as st
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, StorageContext, Settings
from llama_index.core.chat_engine import SimpleChatEngine
from llama_index.core.memory import ChatMemoryBuffer
from llama_index.readers.wikipedia import WikipediaReader
import wikipedia
from llama_index.llms.groq import Groq
from llama_index.embeddings.huggingface import HuggingFaceEmbedding


class WikiTools():

    def __init__(self):
        # model= "llama3-8b-8192" , "mixtral-8x7b-32768" , "gemma-7b-it"
        # embed_model="nomic-embed-text-v1", "sentence-transformers-allMiniLM-L6-v2"
        Settings.llm = Groq(
            model="llama3-8b-8192",
            temperature=0.1,
            api_key=st.secrets['GROQ_API']
        )
        Settings.embed_model = HuggingFaceEmbedding(
            model_name="BAAI/bge-small-en-v1.5",
            # model_kwargs={'device': 'cpu'}
        )

    def load_wiki_index(self, topic):
        results = []
        for page in pages:
            wiki_page = wikipedia.page(page, **load_kwargs)
            page_content = wiki_page.content
            page_id = wiki_page.pageid
            results.append(Document(id_=page_id, text=page_content))
        return results

        reader = WikipediaReader()
        wiki_docs = reader.load_data(
            pages=topic, lang_prefix='fr', auto_suggest=True)
        index = VectorStoreIndex.from_documents(wiki_docs)
        return index

    def load_index(self, topic):
        reader = WikipediaReader()
        wiki_docs = reader.load_data(
            pages=topic, lang_prefix='fr', auto_suggest=True)
        index = VectorStoreIndex.from_documents(wiki_docs)
        return index

    # Set ChatEngine : Condense Chat Mode
    def set_condense_chatengine(self, index):
        memory = ChatMemoryBuffer.from_defaults(token_limit=3900)
        index = index
        chat_engine = index.as_chat_engine(
            chat_mode="condense_plus_context",
            #llm=llm,
            memory=memory,
            context_prompt=("""
                You are a kind and talkative chatbot, able to have normal interactions, as well as provide low-level detailed responses.
                Here are the relevant documents for the context:\n"
                {context_str}
                \nInstruction: Use the previous chat history, or the context above, to interact and help the user. If you don't know, juste respond so, do not make up answers.
                """),
            verbose=True,
        )
        return chat_engine
