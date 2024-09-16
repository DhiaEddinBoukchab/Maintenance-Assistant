import os
import fitz  # PyMuPDF
from langdetect import detect
import re
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma 
from langchain_openai import OpenAIEmbeddings
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI
from langchain_core.runnables import RunnablePassthrough
from langchain_core.prompts import ChatPromptTemplate
from langchain.load import dumps, loads
from operator import itemgetter
from dotenv import load_dotenv

load_dotenv()

openai_api_key = os.getenv("OPENAI_API_KEY")

def clean_text(text):
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'[^\x00-\x7F]+', '', text)
    text = text.strip()
    return text

def extract_and_clean_english_text(pdf_path, max_page=66):
    pdf_document = fitz.open(pdf_path)
    english_text = []
    for page_num in range(min(len(pdf_document), max_page)):
        page = pdf_document.load_page(page_num)
        text = page.get_text("text")
        lines = re.split(r'\n', text)
        for line in lines:
            try:
                if detect(line) == 'en':
                    cleaned_line = clean_text(line)
                    if cleaned_line:
                        english_text.append(cleaned_line)
            except:
                continue
    return " ".join(english_text)

def split_text_into_chunks(text, chunk_size=2000, chunk_overlap=350):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap
    )
    return text_splitter.split_text(text)

def generate_queries(question):
    template = """You are an AI language model assistant. Your task is to generate five 
different versions of the given user question to retrieve relevant documents from a vector 
database. By generating multiple perspectives on the user question, your goal is to help
the user overcome some of the limitations of the distance-based similarity search. 
Provide these alternative questions separated by newlines. Original question: {question}"""
    prompt_perspectives = ChatPromptTemplate.from_template(template)
    return (
        prompt_perspectives 
        | ChatOpenAI(temperature=0) 
        | StrOutputParser() 
        | (lambda x: x.split("\n"))
    )

def get_unique_union(documents: list[list]):
    flattened_docs = [dumps(doc) for sublist in documents for doc in sublist]
    unique_docs = list(set(flattened_docs))
    return [loads(doc) for doc in unique_docs]

def answer_question(user_question, pdf_path):
    cleaned_english_text = extract_and_clean_english_text(pdf_path)
    text_chunks = split_text_into_chunks(cleaned_english_text)
    
    vectorstore = Chroma.from_texts(
      texts=text_chunks,
      collection_name="rag-chroma",
      embedding=OpenAIEmbeddings()
    )
    retriever = vectorstore.as_retriever()
    
    template = """You are a helpful assistant. Answer the question based only on the following context:
{context}

Answer the question based on the above context: {question}

Provide a detailed answer.
Do not justify your answers.
Do not give information not mentioned in the CONTEXT INFORMATION.
If you don't know the answer, say: "I can't answer this question since it is not mentioned in the context."""
    prompt = ChatPromptTemplate.from_template(template)
    retrieval_chain = generate_queries(user_question) | retriever.map() | get_unique_union
    docs = retrieval_chain.invoke({"question": user_question})
    
    final_rag_chain = (
        {"context": retrieval_chain, "question": itemgetter("question")} 
        | prompt
        | ChatOpenAI(temperature=0)
        | StrOutputParser()
    )
    response = final_rag_chain.invoke({"question": user_question})
    return response