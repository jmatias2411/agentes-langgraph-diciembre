from langchain_core.messages import AIMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import JsonOutputParser
from langchain_community.tools import WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper
from rich.console import Console

from agent.state import AgentState
from utils.llm import llm, llm_creative, llm_json

console = Console()

# --- MEJORA 1: AUMENTAR CONTEXTO ---
# Aumentamos top_k a 2 y chars a 5000 para tener mucha más información
api_wrapper = WikipediaAPIWrapper(top_k_results=2, doc_content_chars_max=5000, lang="es")
search_tool = WikipediaQueryRun(api_wrapper=api_wrapper)

def researcher_node(state: AgentState):
    """Busca información en Wikipedia."""
    last_message = state["messages"][-1]
    query = last_message.content
    
    console.print(f"[cyan]🔍 [bold]Investigador:[/bold] Consultando Wikipedia sobre: '{query}'...[/cyan]")
    
    try:
        search_result = search_tool.run(query)
    except Exception as e:
        search_result = f"Error: {str(e)}"

    content = f"Resultados de la investigación: {search_result}"
    return {"messages": [AIMessage(content=content, name="Researcher")]}

def writer_node(state: AgentState):
    """Redacta el contenido final basándose en el historial."""
    console.print("[green]✍️  [bold]Redactor:[/bold] Escribiendo el artículo completo...[/green]")
    
    messages = state["messages"]
    
    # --- MEJORA 2: PROMPT PROFESIONAL ---
    # Le damos instrucciones de estructura y permiso para complementar información.
    system_prompt = (
        "Actúa como un Escritor Técnico Senior para un blog de tecnología importante. "
        "Tu tarea es escribir un artículo completo y atractivo basado en la investigación proporcionada "
        "y complementándolo con tu propio conocimiento general si hace falta.\n\n"
        "ESTRUCTURA OBLIGATORIA:\n"
        "1. Un Título atractivo (H1)\n"
        "2. Una Introducción que enganche al lector.\n"
        "3. Desarrollo: 2 o 3 secciones con subtítulos (H2) explicando los detalles.\n"
        "4. Una Conclusión breve.\n\n"
        "FORMATO:\n"
        "- Usa Markdown correctamente.\n"
        "- Usa emojis para hacerlo visual.\n"
        "- No te limites a resumir, CREA contenido nuevo y fluido.\n"
        "- Escribe SIEMPRE en Español."
    )
    
    response = llm_creative.invoke([SystemMessage(content=system_prompt)] + messages)
    response.name = "Writer"
    return {"messages": [response]}

def supervisor_node(state: AgentState):
    """El cerebro que decide el siguiente paso."""
    messages = state["messages"]
    last_message = messages[-1]

    # Lógica de seguridad: Si el Researcher ya trajo datos, pasamos al Writer
    if hasattr(last_message, "name") and last_message.name == "Researcher":
        console.print(f"[yellow]👉 Decisión (Forzada): Datos recibidos, pasando a [bold]Writer[/bold][/yellow]")
        return {"next": "Writer"}

    system_prompt = (
        "Eres un supervisor. Tu tarea es gestionar el flujo.\n"
        "1. Si el usuario pide algo y NO ha hablado el 'Researcher' -> Responde {\"next\": \"Researcher\"}\n"
        "2. Si el 'Researcher' ya habló -> Responde {\"next\": \"Writer\"}"
    )
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        MessagesPlaceholder(variable_name="messages"),
    ])
    
    supervisor_chain = prompt | llm_json | JsonOutputParser()
    
    with console.status("[bold yellow]🧠 Supervisor analizando flujo...[/]", spinner="dots"):
        try:
            result = supervisor_chain.invoke({"messages": messages})
            decision = result["next"]
        except Exception:
            decision = "Researcher"
        
    console.print(f"[yellow]👉 Decisión: Delegar a [bold]{decision}[/bold][/yellow]")
    return {"next": decision}