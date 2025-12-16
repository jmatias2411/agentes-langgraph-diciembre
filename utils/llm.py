from langchain_ollama import ChatOllama

# Ajusta el modelo según lo que tengas descargado en Ollama (llama3.1, mistral, deepseek-coder)
MODEL_NAME = "llama3.1"

# Modelo estándar para razonamiento (temperatura baja para precisión)
llm = ChatOllama(model=MODEL_NAME, temperature=0)

# Modelo para tareas creativas (temperatura más alta)
llm_creative = ChatOllama(model=MODEL_NAME, temperature=0.7)

# Modelo forzado a JSON (vital para el Supervisor)
llm_json = ChatOllama(model=MODEL_NAME, format="json", temperature=0)