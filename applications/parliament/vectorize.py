"""
This script creates a vector store from all txt files in a folder.
It takes the following arguments:
    --input_folder: Path to the folder containing txt files
    --vectorstore: Path to the vector store
    --openai_model: OpenAI model name
    --hf_model: HuggingFace model name
    --use_openai: Use OpenAI embeddings
    --use_hf: Use HuggingFace embeddings
    --use_faiss: Use FAISS embeddings
    --use_chromadb: Use ChromaDB embeddings
The script uses the RecursiveCharacterTextSplitter to split the text into chunks.
The script uses OpenAIEmbeddings and HuggingFaceEmbeddings to create embeddings.
The script uses FAISS and Chroma to create vector stores.
Author: Pavis
Date: 25/03/2024
"""
import os
import pickle
import argparse
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import Chroma

from dotenv import load_dotenv

def load_and_process(args):
    combined_text = ""
    for filename in os.listdir(args.input_folder):
        if filename.endswith(".txt"):
            path = os.path.join(args.input_folder, filename)
            print(f"Processing {path}")
            with open(path, 'rb') as text_file:
                content = text_file.read().decode('utf-8')
                content.replace("No transcription available", "")

                if args.use_faiss:
                    vector_store = os.path.join(args.vectorstore, filename.replace('_merged.txt', '.pkl'))

                if args.use_chromadb:
                    vector_store = os.path.join(args.vectorstore, filename.replace('_merged.txt', ''))

                create_vector_store_from_text(content, vector_store, args)
    

def create_vector_store_from_text(text, vectorstore, args):

    use_hf = args.use_hf
    use_openai = args.use_openai

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len
    )

    chunks = text_splitter.split_text(text=text)

    if use_hf:
        embeddings = HuggingFaceEmbeddings(model_name=args.hf_model)

    if use_openai:
        embeddings = OpenAIEmbeddings(model=args.openai_model)

    if args.use_faiss:
        VectorStore = FAISS.from_texts(chunks, embedding=embeddings)

        with open(vectorstore, "wb") as f:
            pickle.dump(VectorStore, f)

    if args.use_chromadb:
        db = Chroma().from_texts(chunks, embeddings, persist_directory=vectorstore)
        db.persist()
        db = None

def main(args):
    load_dotenv()

    os.makedirs(args.vectorstore, exist_ok=True)

    load_and_process(args)

    print(f"Vector store created at {args.vectorstore}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Create a vector store from all txt in a folder')
    
    parser.add_argument('--input_folder', type=str, default="./frontend/web_application/documents", help='Path to the folder containing files')
    parser.add_argument('--vectorstore', type=str, default="./embeddings", help='Path to the vectorstore')
    parser.add_argument('--openai_model', type=str, default="text-embedding-3-large", help='OpenAI model name')
    parser.add_argument('--hf_model', type=str, default="all-MiniLM-L6-v2", help='HuggingFace model name')
    parser.add_argument('--use_openai', action="store_true", default=False, help='Use OpenAI embeddings')
    parser.add_argument('--use_hf', action="store_true", default=False, help='Use Ollama embeddings')
    parser.add_argument('--use_faiss', action="store_true", default=False, help='Use FAISS embeddings')
    parser.add_argument('--use_chromadb', action="store_true", default=False, help='Use ChromaDB embeddings')

    args = parser.parse_args()
    main(args)
