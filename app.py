
import streamlit as st
from dotenv import load_dotenv
from PyPDF2 import PdfReader
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain.chat_models import  ChatOpenAI
from langchain_community.embeddings import OpenAIEmbeddings, HuggingFaceInstructEmbeddings
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain
from htmlTemplates import css, bot_template, user_template

def get_pdf_text(pdf_docs):
    text = ''
    for pdf in pdf_docs:
        pdf_reader = PdfReader(pdf)
        for page in pdf_reader.pages:
            text += page.extract_text()
    return text

def get_text_chunks(raw_text):
    text_splitter = CharacterTextSplitter(
        separator="\n",
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len
    )
    chunks = text_splitter.split_text(raw_text)
    return chunks
def get_vectorstore(chunks):
    embeddings = OpenAIEmbeddings()
    #embeddings = HuggingFaceInstructEmbeddings()
    vectorStore = FAISS.from_texts(texts=chunks,embedding=embeddings)
    return vectorStore

def handle_userInput(user_question):
    response = st.session_state.conversation({'question':user_question})
    st.write(response)


def get_conversation_chain(vectorstore):
    llm = ChatOpenAI()
    memory = ConversationBufferMemory(
        memory_key='chat_history',return_messages=True)
    conversation_chain = ConversationalRetrievalChain.from_llm(
        llm= llm,
        retriever= vectorstore.as_retriever(),
        memory = memory
    )

    return conversation_chain

def main():
    load_dotenv()
    st.set_page_config(page_title='Chat with Multiple PDFs', page_icon=':books:')
    st.header('Chat with Multiple PDFs :books:')
    # add custom HTML
    st.write(css, unsafe_allow_html = True)
    # Initialize conversation session state
    if 'conversation' not in st.session_state:
        st.session_state.conversation = None

    user_question = st.text_input('Ask your Questions about your Documents')

    if user_question:
        # handle user input
        handle_userInput(user_question)
    st.write(user_template.replace(
        "{{MSG}}", "Hello Human"), unsafe_allow_html=True)

    st.write(bot_template.replace(
        "{{MSG}}", "Hello Robot"), unsafe_allow_html = True)

    with st.sidebar:
        st.subheader('Your Documents')
        pdf_docs = st.file_uploader('Upload your documents and click Process',accept_multiple_files=True)
        if st.button('Process'):
            with st.spinner("Processing..."):
                # get the PDF text
                raw_text = get_pdf_text(pdf_docs)
                #st.write(raw_text)

                # get the text chunks
                text_chunks = get_text_chunks(raw_text)
                #st.write(text_chunks)

                # create vector store with embeddings
                vector_store = get_vectorstore(text_chunks)

                # create conversation chain
                st.session_state.conversation = get_conversation_chain(
                    vector_store)



if __name__ == '__main__':
    main()