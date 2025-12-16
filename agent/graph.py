from langgraph.graph import StateGraph, END
from agent.state import AgentState
from agent.nodes import supervisor_node, researcher_node, writer_node

# Inicializamos el grafo
workflow = StateGraph(AgentState)

# 1. Añadimos los nodos
workflow.add_node("Supervisor", supervisor_node)
workflow.add_node("Researcher", researcher_node)
workflow.add_node("Writer", writer_node)

# 2. Definimos el punto de entrada
workflow.set_entry_point("Supervisor")

# 3. Aristas Condicionales (El Router)
workflow.add_conditional_edges(
    "Supervisor",
    lambda x: x["next"],
    {
        "Researcher": "Researcher",
        "Writer": "Writer",
        "FINISH": END
    }
)

# 4. CICLOS Y CIERRES
# El investigador SÍ vuelve al supervisor para entregar datos
workflow.add_edge("Researcher", "Supervisor")

# --- EL CAMBIO CLAVE AQUÍ ---
# El Redactor NO vuelve al supervisor. Si escribe, terminamos.
workflow.add_edge("Writer", END)

# 5. Compilación
app = workflow.compile()