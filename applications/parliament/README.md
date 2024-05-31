# MMRAG Video Document Assistant

## Tools and Technologies

Ollama and OpenAi, with LangChain ChromaDB

## ollama version install and run
Install ollama with ```curl -fsSL https://ollama.com/install.sh | sh```
install mistral ```ollama pull mistral```
install openhermes ```ollama pull openhermes```
install llama3 ```ollama pull llama3```

use ollama ```ollama create mmrag -f ./Modelfile```

to create mmrag specialized llm

to regenerate it ```ollama rm mmrag ; ollama create mmrag -f ./Modelfile```

## install graphviz
Run ```sudo apt-get install graphviz```

## Examples for openai version and chromadb
copy previous processed files to documents folder
Run ```cp ../../target/*_merged.txt ./frontend/web_application/documents```

ingest the videos in documents folder
Run ```python3 vectorize.py --use_openai --use_chromadb```

start the web interface
Run ```streamlit run mmrag.py -- --use_openai --use_chromadb```

## Examples for ollama version and chromadb
ingest the videos in documents folder
Run ```python3 vectorize.py --use_hf --use_chromadb```

start the web interface
Run ```streamlit run mmrag.py -- --use_ollama --use_chromadb```

## access to the web interface
Open a browser and go to
https://localhost:8501/?video_id=AI_20240130_ch36_24417&lang=it

## start web frontend
```bash 
cd frontend
# edit configurations in configurations.py
docker-compose up -d
```


