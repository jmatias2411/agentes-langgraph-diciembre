from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.markdown import Markdown
from langchain_core.messages import HumanMessage

# Importamos la app compilada desde nuestro módulo modular
from agent.graph import app

console = Console()

def main():
    console.clear()
    console.print(Panel.fit(
        "[bold magenta]🤖 Agencia de Marketing AI - Modular & Local[/bold magenta]\n"
        "[dim]Architecture: LangGraph | Model: Ollama | UI: Rich[/dim]",
        border_style="magenta"
    ))

    while True:
        user_input = Prompt.ask("\n[bold cyan]¿Sobre qué quieres que escriba? (o 'salir')[/]")
        
        if user_input.lower() in ['salir', 'exit', 'quit']:
            break

        # Estado inicial
        initial_state = {
            "messages": [HumanMessage(content=user_input)],
            "next": "Supervisor"
        }

        console.rule("[bold white]Iniciando Workflow[/]")
        
        # Ejecución del grafo
        # stream_mode="updates" nos permite interceptar el output final
        for event in app.stream(initial_state):
            for key, value in event.items():
                if key == "Writer":
                    final_content = value["messages"][0].content
                    console.print("\n")
                    console.print(Panel(
                        Markdown(final_content),
                        title="[bold green]Resultado Final[/]",
                        border_style="green"
                    ))

    console.print("[bold red]👋 ¡Hasta luego![/]")

if __name__ == "__main__":
    main()