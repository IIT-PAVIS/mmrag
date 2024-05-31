"""
This script is used to create a chatbot that can answer questions about the Italian Chamber of Deputies' WebTV.
It uses the Langchain library to interact with OpenAI and ChromaDB for question answering.
The script takes the following arguments:
    --translate: Translate the question to English and response from English
    --ollama_model: Ollama model
    --openai_model: OpenAI model
    --use_openai: Use OpenAI model
    --use_ollama: Use Ollama model
    --target_source_chunks: Number of source chunks to target
    --use_faiss: Use FAISS embeddings
    --use_chromadb: Use ChromaDB embeddings
    --hf_embeddings: HuggingFace embeddings model
    --openai_embeddings: OpenAI embeddings model
    --system_file: System file
    --documents: Path to the documents files
The script uses the OpenAI and Ollama models to generate responses to user questions.
The script uses ChromaDB and FAISS to retrieve relevant documents for answering questions.
Author: Pavis
Date: 25/03/2024
"""
import streamlit as st
import pickle
from langchain.llms import OpenAI
from langchain.chains.question_answering import load_qa_chain
from langchain.callbacks import get_openai_callback
from dotenv import load_dotenv
from streamlit_extras.add_vertical_space import add_vertical_space
import argparse
import os
from googletrans import Translator, LANGUAGES
from langchain.llms import Ollama
from langchain.vectorstores import Chroma
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.chains import RetrievalQA
from graphviz import Source
from PIL import Image
import random
import re
import streamlit.components.v1 as components
import json

def create_knowledge_base(args, persist_directory):
    if args.use_ollama:
        embeddings = HuggingFaceEmbeddings(model_name=args.hf_embeddings)

    if args.use_openai:
        embeddings = OpenAIEmbeddings(model=args.openai_embeddings)

    db = Chroma(persist_directory=persist_directory,
                embedding_function=embeddings)

    retriever = db.as_retriever(search_kwargs={"k": args.target_source_chunks})

    return retriever


def create_sidebar(id, language="it", args=None):
    with st.sidebar:
        # Display image from web
        html = f"""<img width="280" height="70" src="https://pavis.iit.it/image/layout_set_logo?img_id=1459610&t=1714401579818">"""
        st.markdown(html, unsafe_allow_html=True)

        # Set title and subtitle
        st.title("webtv.camera.it Assistant")

        # Put a separator
        # st.markdown("---")

        # open file with header informations
        header = []
        with open(f'./{args.documents}/{id}_merged.txt', 'r') as file:
            for line in file:

                if line == 'Time windows:\n':
                    break

                header.append(line)

        if header[0] != "" or header[0] != None:
            title = header[0].replace('Title:', '')
        else:
            title = "Title not available"

        if header[1] != "" or header[1] != None:
            content = header[1].replace('Content:', '')
        else:
            content = "Content not available"

        if header[2] != "" or header[2] != None:
            dates = header[2].replace('Dates:', '')
        else:
            dates = "Dates not available"

        # Transalte all the headers
        if args.translate:
            translator = Translator()

            try:
                title = translator.translate(
                    title, src="en", dest=language).text
            except:
                title = ""

            try:
                content = translator.translate(
                    content, src="en", dest=language).text
            except:
                content = ""

            try:
                dates = translator.translate(
                    dates, src="en", dest=language).text
            except:
                dates = ""

        st.title(title)

        html = f"""<img width="280" height="200" src="https://webtv.camera.it/assets/thumbs/flash_7/2024/thumb_20/{id}.jpg">"""

        st.markdown(html, unsafe_allow_html=True)
        st.markdown(f"""{content}""")
        st.markdown(f"""{dates}""")

        elements = id.split('_')
        video_id = elements[3]

        st.markdown(
            f"""[Vai al video](https://webtv.camera.it/evento/{video_id})""")

        st.markdown(f"""
        ## About:
        Created by Pavis Research Line (IIT) for the WebTV 
        of the Italian Chamber of Deputies.
        - [Streamlit](https://streamlit.io/)
        - [Langchain](https://python.langchian.com/)
        - [OpenAI](https://platform.openai.com/docs/models)
        - [HuggingFace](https://huggingface.co/)
        - [Ollama](https://ollama.com)
        - [Data Source](https://webtv.camera.it)
        """)

        # Put an image to close the sidebar
        html = f"""<img width="280" height="100" src="https://www.iit.it/image/company_logo?img_id=155280&t=1712562226949">"""
        st.markdown(html, unsafe_allow_html=True)


def load_vector_store(vector_store_path):
    with open(vector_store_path, 'rb') as f:
        VectorStore = pickle.load(f)
    return VectorStore


def build_context(chat_history, system, max_history=4, use_openai=False):
    # Build context from the last `max_history` interactions
    if use_openai:
        context = f"system: {system}\n"
    else:
        context = ""

    for interaction in chat_history[-max_history:]:
        context += f"Q: {interaction['question']} A: {interaction['answer']} "
    return context


def extract_code(text):
    code = []
    start = 0
    while True:
        start = text.find('```', start)
        if start == -1:
            break
        end = text.find('```', start+3)
        code.append(text[start+3:end])
        start = end

    # remove the code blocks from the text and all code
    for c in code:
        text = text.replace(f'```{c}```', '')
        text = text.replace(c, '')

    return code, text


def translate_strings(code, language):
    # Initialize the translator
    translator = Translator()
    # Find all strings within quotation marks
    strings = re.findall(r'"(.*?)"', code)

    translated_code = code
    for string in strings:
        # Translate each string
        translated_text = translator.translate(
            string, src='en', dest=language).text
        # Replace the original string with its translation in the code
        translated_code = translated_code.replace(
            f'"{string}"', f'"{translated_text}"')

    return translated_code


def graphviz_to_image_file(graphviz_code, directory="."):
    """
    Generates an image from Graphviz code, saves it with a unique random filename,
    and returns the file path.

    Parameters:
    - graphviz_code: A string containing Graphviz code.
    - directory: The directory where the image file will be saved. Defaults to the current working directory.

    Returns:
    - The path to the saved image file.
    """
    # Ensure the specified directory exists
    os.makedirs(directory, exist_ok=True)

    # Generate a unique filename for the image
    filename = f"{random.randint(100000, 999999)}"
    filepath = os.path.join(directory, filename)

    # Generate the image from Graphviz code and save it
    src = Source(graphviz_code)
    src.render(filepath, format='png', cleanup=True)

    # Return the full path to the generated image file
    return filepath


def display_messages():
    for message in st.session_state.history:
        if 'images' in message:
            for image in message['images']:
                st.image(image)

        if 'question' in message:
            with st.chat_message('user'):
                st.markdown(message['question'])

            with st.chat_message('assistant'):
                st.markdown(message['answer'])


def display_text_with_color(text, color='black', background_color='white'):
    html_str = f"""
    <div style='background-color: {background_color}; color: {color}; padding: 10px; border-radius: 5px;'>
        {text}
    </div>
    """
    st.markdown(html_str, unsafe_allow_html=True)


def display_message():
    st.error(translate("Use ask button to get the response.", 
                       st.session_state.language, st.session_state.translate))


def get_questions(args):
    if args.use_openai:
        with open(args.system_file, 'r') as file:
            system_message = file.read()
        system = system_message

    if args.use_ollama:
        system = ""

    full_query = """Can you give me a list of questions about the document 
    in json format [{\"question\":\"text of the question\"}] ?"""

    if args.use_chromadb:
        # Retrieve the most similar documents from the vector store
        qa = RetrievalQA.from_chain_type(llm=st.session_state.llm, chain_type="stuff",
                                         retriever=st.session_state.retriever, return_source_documents=False)
        res = qa(full_query)
        response = res['result']

    # Isolate the JSON object from the response
    response = response.split('[')[-1].split(']')[0]

    # Convert the JSON object to a list of questions
    questions = response.split('\"question\": \"')[1:]

    # Extract the text of each question
    questions = [question.split('\"')[0] for question in questions]

    print(questions)

    return questions


def load_questions(args):
    # load questions from file
    questions = []
    with open(args.questions, 'r') as file:
        questions = file.read()
        questions = json.loads(questions)
    
    return questions["questions"]


def translate(value, language, translate):
    if translate:
        value = st.session_state.translator.translate(
                value, src="en", dest=language).text
    return value


def main(args):
    # Load environment variables
    load_dotenv()

    # Get the video ID from the URL
    params = st.experimental_get_query_params()

    # Check if a video is selected
    if "video_id" not in params:
        st.write("Please select a video to start the chatbot.")
        st.stop()

    if "lang" not in params:
        st.write("Please select a language to start the chatbot.")
        st.stop()

    video_id = params.get("video_id", [""])[0]
    language = params.get("lang", [""])[0]

    # Initialize the translator
    if args.translate:
        if 'translator' not in st.session_state:
            st.session_state.translator = Translator()
            st.session_state.language = language
            st.session_state.translate = args.translate

    # Initialize or load chat history
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []

    # Initialize or load history
    if 'history' not in st.session_state:
        st.session_state.history = []

    # Initialze model
    if 'llm' not in st.session_state:
        if args.use_openai:
            st.session_state.llm = OpenAI(model_name=args.openai_model)
        if args.use_ollama:
            st.session_state.llm = Ollama(
                model=args.ollama_model, base_url=args.base_url)

    # Initialize memory
    if 'retriver' not in st.session_state:
        if args.use_chromadb:
            vectorstore = os.path.join('embeddings', video_id)
            st.session_state.retriever = create_knowledge_base(
                args, vectorstore)

    st.title("📚 webtv.camera.it Assistant 💬")

    # Create the sidebar
    create_sidebar(video_id, language, args)

    # Get the questions if chromaDB is used and generate questions is enabled
    loaded_questions = load_questions(args)

    if args.use_chromadb and args.generate_questions:
        loaded_questions += get_questions(args)
    
    # Preload questions
    if "questions" not in st.session_state:
        st.session_state.questions = loaded_questions
        questions = []

        for question in loaded_questions:
            if args.translate:
                question = st.session_state.translator.translate(
                    question, src="en", dest=language).text

            questions.append(question)

        st.session_state.questions = questions

    init_prompt = st.selectbox(
        translate("Select a question from the list or type your own question...", language, args.translate),
        st.session_state.questions
    )

    # Load the vector store if necessary
    if args.use_faiss:
        vectorstore = os.path.join('embeddings', f'{video_id}.pkl')

        # Load the vector store
        VectorStore = load_vector_store(vectorstore)

    user_input = st.text_input(
        translate("Ask me anyting",language,args.translate), value=init_prompt,
        placeholder=translate("Type here .....",language,args.translate), on_change=display_message)

    # Create a button to ask the question
    ask_button = st.button(translate("Ask", language, args.translate))

    if ask_button:
        if args.use_openai:
            with open(args.system_file, 'r') as file:
                system_message = file.read()
            system = system_message

        if args.use_ollama:
            system = ""

        context = build_context(
            st.session_state.chat_history, system, use_openai=args.use_openai)

        # Translate the user input if necessary
        if args.translate:
            user_translated = st.session_state.translator.translate(
                user_input, src=language, dest="en").text
            full_query = context + user_translated  # Prepend context to the current query
        else:
            full_query = context + user_input

        # Generate the response
        if args.use_faiss:
            # Retrieve the most similar documents from the vector store
            chain = load_qa_chain(
                llm=st.session_state.llm, chain_type='stuff')

            docs = VectorStore.similarity_search(query=full_query)

            with get_openai_callback() as cb:
                response = chain.run(
                    input_documents=docs, question=full_query)

        if args.use_chromadb:
            # Retrieve the most similar documents from the vector store
            qa = RetrievalQA.from_chain_type(llm=st.session_state.llm, chain_type="stuff",
                                             retriever=st.session_state.retriever, return_source_documents=False)
            res = qa(full_query)
            response = res['result']

        # Update chat history
        st.session_state.chat_history.append(
            {"question": user_input, "answer": response})

        code_blocks, response = extract_code(response)

        images = []
        for code in code_blocks:
            code_block = code.replace('graphviz\n', '')
            code_block = code_block.replace('dot\n', '')

            if 'digraph' in code_block:
                try:
                    # Generate an image from the Graphviz code
                    image_path = graphviz_to_image_file(
                        code_block, directory="./images")

                    # Append the image path to the list of images
                    images.append(f"{image_path}.png")
                except Exception as e:
                    st.error(f"Error generating image: {e}")

        st.session_state.history.append({"images": images})

        # Translate the response if necessary
        if args.translate:
            response_tr = st.session_state.translator.translate(
                response, src="en", dest=language).text

            st.session_state.history.append(
                {"question": user_input, "answer": response_tr})

        else:
            st.session_state.history.append(
                {"question": user_input, "answer": response})

    for interaction in reversed(st.session_state.history):
        if 'question' in interaction:
            display_text_with_color(
                f"Q:{interaction['question']}", color="black", background_color='lightgreen')
            st.markdown("---")  # Separator for visual clarity

            display_text_with_color(
                f"A:{interaction['answer']}", color="black", background_color='lightgray')
            st.markdown("---")  # Separator for visual clarity

        if 'images' in interaction:
            for image in interaction['images']:
                st.image(image)


if __name__ == "__main__":
    # read from command line arguments
    parser = argparse.ArgumentParser(description='Video Chatbot')

    parser.add_argument('--translate', type=bool, default=True,
                        help='Translate the question to English and resonse from English')
    parser.add_argument('--ollama_model', type=str,
                        default="mmrag", help='Ollama model')
    parser.add_argument('--openai_model', type=str,
                        default="gpt-4-turbo-preview", help='OpenAI model')  # gpt-4-turbo-preview/gpt-3.5-turbo
    parser.add_argument('--use_openai', action="store_true",
                        default=False, help='Use OpenAI model')
    parser.add_argument('--use_ollama', action="store_true",
                        default=False, help='Use Ollama model')
    parser.add_argument('--target_source_chunks', type=int,
                        default=16, help='Number of source chunks to target')
    parser.add_argument('--use_faiss', action="store_true",
                        default=False, help='Use FAISS embeddings')
    parser.add_argument('--use_chromadb', action="store_true",
                        default=False, help='Use ChromaDB embeddings')
    parser.add_argument('--hf_embeddings', type=str,
                        default="all-MiniLM-L6-v2", help='HuggingFace embeddings model')
    parser.add_argument('--openai_embeddings', type=str,
                        default="text-embedding-3-large", help='OpenAI embeddings model')
    parser.add_argument('--system_file', type=str,
                        default="system.txt", help='System file')
    parser.add_argument('--documents', type=str, default="./frontend/web_application/documents",
                        help='Path to the documents files')
    parser.add_argument('--base_url', type=str, default="http://127.0.0.1:11434",
                        help='Base URL for Ollama model')
    parser.add_argument('--generate_questions', action="store_true",
                        default=False, help='Generate questions')
    parser.add_argument('--questions', type=str, default="./questions.json",
                        help='Path to the questions file')
    
    args = parser.parse_args()

    main(args)
