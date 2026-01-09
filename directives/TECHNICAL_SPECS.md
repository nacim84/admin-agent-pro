# Spécifications Techniques - Workflows Agentiques Python

Ce document définit les spécifications techniques, les frameworks et les bonnes pratiques pour construire des workflows agentiques robustes et évolutifs avec Python.

## 🎯 Objectif du Projet

Créer une alternative **by-code** aux plateformes no-code comme N8N, en s'appuyant sur :
- Des agents IA autonomes et collaboratifs
- Un écosystème complet d'outils et MCPs
- Une architecture à 3 couches (Directive → Orchestration → Exécution)
- Des workflows reproductibles, testables et maintenables

---

## 📋 Table des Matières

1. [Stack Technique Core](#1-stack-technique-core)
2. [Frameworks Agentiques](#2-frameworks-agentiques)
3. [Model Context Protocol (MCP)](#3-model-context-protocol-mcp)
4. [LLM Providers & Intégrations](#4-llm-providers--intégrations)
5. [Infrastructure & Outils](#5-infrastructure--outils)
6. [Patterns Agentiques](#6-patterns-agentiques)
7. [Observabilité & Monitoring](#7-observabilité--monitoring)
8. [Migration N8N → Code](#8-migration-n8n--code)
9. [Standards de Développement](#9-standards-de-développement)

---

## 1. Stack Technique Core

### Python Version
- **Minimum requis** : Python 3.11+
- **Recommandé** : Python 3.12+ pour meilleures performances
- **Raisons** :
  - Support natif des types génériques améliorés
  - Meilleures performances asyncio
  - Pattern matching (match/case)
  - Better error messages

### Gestionnaire de Paquets : UV (Astral)

**UV** est le gestionnaire de paquets ultra-rapide d'Astral, écrit en Rust. Il remplace pip, pip-tools, poetry et virtualenv.

```bash
# Installation
curl -LsSf https://astral.sh/uv/install.sh | sh

# Initialiser un projet
uv init

# Créer un environnement virtuel
uv venv

# Activer l'environnement
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows

# Installer les dépendances
uv pip install -r requirements.txt

# Ajouter une dépendance
uv add langchain langgraph

# Synchroniser l'environnement
uv pip sync requirements.txt
```

### Fichiers de Configuration

```
pyproject.toml          # Configuration projet et métadonnées
requirements.txt        # Dépendances lockées (production)
requirements-dev.txt    # Dépendances développement
.python-version         # Version Python fixée
uv.lock                 # Lockfile UV
```

---

## 2. Frameworks Agentiques

### 2.1 LangGraph ⭐ (Recommandé Principal)

**Description** : Framework de LangChain pour orchestrer des workflows stateful avec graphes. Permet de créer des agents complexes avec cycles, branches conditionnelles et state management.

**Use Cases** :
- Workflows multi-étapes avec décisions conditionnelles
- Agents nécessitant de la mémoire entre étapes
- Orchestration complexe avec retours en arrière

**Installation** :
```bash
uv add langgraph langchain-core langchain-anthropic
```

**Exemple d'architecture** :
```python
from langgraph.graph import StateGraph, END
from typing import TypedDict, Annotated
import operator

class AgentState(TypedDict):
    messages: Annotated[list, operator.add]
    next_action: str
    context: dict

def create_workflow():
    workflow = StateGraph(AgentState)

    # Nœuds du graphe
    workflow.add_node("analyzer", analyze_input)
    workflow.add_node("executor", execute_task)
    workflow.add_node("validator", validate_output)

    # Edges conditionnels
    workflow.add_conditional_edges(
        "analyzer",
        route_decision,
        {
            "execute": "executor",
            "validate": "validator",
            "end": END
        }
    )

    workflow.set_entry_point("analyzer")
    return workflow.compile()
```

**Avantages** :
- Visualisation native des graphes
- State management robuste
- Support des checkpoints pour persistance
- Debugging facilité

---

### 2.2 CrewAI

**Description** : Framework pour orchestrer des équipes d'agents IA autonomes qui collaborent pour accomplir des tâches complexes.

**Use Cases** :
- Agents avec rôles spécifiques (analyst, writer, reviewer)
- Workflows collaboratifs type "équipe"
- Délégation de tâches entre agents

**Installation** :
```bash
uv add crewai crewai-tools
```

**Exemple** :
```python
from crewai import Agent, Task, Crew, Process

# Définir les agents
researcher = Agent(
    role='Researcher',
    goal='Find and synthesize information',
    backstory='Expert data analyst',
    tools=[search_tool, scrape_tool],
    verbose=True
)

writer = Agent(
    role='Content Writer',
    goal='Create compelling content',
    backstory='Professional writer',
    tools=[write_tool],
    verbose=True
)

# Définir les tâches
research_task = Task(
    description='Research about {topic}',
    agent=researcher,
    expected_output='Comprehensive research report'
)

write_task = Task(
    description='Write article based on research',
    agent=writer,
    expected_output='Published article'
)

# Créer l'équipe
crew = Crew(
    agents=[researcher, writer],
    tasks=[research_task, write_task],
    process=Process.sequential,
    verbose=True
)

result = crew.kickoff(inputs={'topic': 'AI Agents'})
```

**Avantages** :
- API intuitive pour agents collaboratifs
- Gestion automatique de la délégation
- Outils préconstruits

---

### 2.3 AutoGen (Microsoft)

**Description** : Framework pour créer des systèmes multi-agents conversationnels avec support human-in-the-loop.

**Use Cases** :
- Conversations multi-agents
- Code generation collaboratif
- Workflows nécessitant validation humaine

**Installation** :
```bash
uv add pyautogen
```

**Exemple** :
```python
from autogen import AssistantAgent, UserProxyAgent, GroupChat, GroupChatManager

# Agents
assistant = AssistantAgent(
    name="assistant",
    llm_config={"model": "gpt-4"}
)

user_proxy = UserProxyAgent(
    name="user_proxy",
    human_input_mode="TERMINATE",
    code_execution_config={"work_dir": "coding"}
)

# Group chat
groupchat = GroupChat(
    agents=[assistant, user_proxy],
    messages=[],
    max_round=10
)

manager = GroupChatManager(groupchat=groupchat)
```

---

### 2.4 LlamaIndex

**Description** : Framework pour construire des agents avec capacités RAG (Retrieval-Augmented Generation) et accès à des données.

**Use Cases** :
- Agents nécessitant accès à des documents
- Question-answering sur données privées
- Agents avec knowledge base

**Installation** :
```bash
uv add llama-index llama-index-llms-anthropic
```

**Exemple** :
```python
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from llama_index.core.agent import ReActAgent
from llama_index.core.tools import QueryEngineTool

# Charger des documents
documents = SimpleDirectoryReader("./data").load_data()
index = VectorStoreIndex.from_documents(documents)

# Créer un outil de query
query_tool = QueryEngineTool.from_defaults(
    query_engine=index.as_query_engine(),
    name="knowledge_base",
    description="Useful for answering questions about documents"
)

# Créer agent ReAct
agent = ReActAgent.from_tools([query_tool], verbose=True)
response = agent.chat("What are the key insights?")
```

---

### 2.5 Pydantic AI ⭐

**Description** : Framework récent de Pydantic pour créer des agents type-safe avec validation stricte.

**Use Cases** :
- Agents nécessitant validation stricte des données
- Production systems avec garanties de types
- Intégration avec écosystème Pydantic

**Installation** :
```bash
uv add pydantic-ai
```

**Exemple** :
```python
from pydantic import BaseModel
from pydantic_ai import Agent

class UserProfile(BaseModel):
    name: str
    age: int
    interests: list[str]

agent = Agent(
    'openai:gpt-4',
    result_type=UserProfile,
    system_prompt='Extract user profile from text'
)

result = agent.run_sync('John is 30 years old and loves coding and music')
print(result.data)  # UserProfile validé
```

---

### 2.6 Haystack

**Description** : Framework pour pipelines NLP, search et question-answering.

**Use Cases** :
- Pipelines de traitement de documents
- Search sémantique
- RAG pipelines customisés

**Installation** :
```bash
uv add haystack-ai
```

---

### 🎯 Recommandations par Use Case

| Use Case | Framework Recommandé |
|----------|---------------------|
| Workflows complexes stateful | **LangGraph** |
| Équipes d'agents collaboratifs | **CrewAI** |
| Conversations multi-agents | **AutoGen** |
| RAG et knowledge bases | **LlamaIndex** |
| Validation stricte et type-safety | **Pydantic AI** |
| Pipelines NLP/Search | **Haystack** |

---

## 3. Model Context Protocol (MCP)

### Qu'est-ce que MCP ?

Le **Model Context Protocol** est un protocole ouvert développé par Anthropic pour permettre aux applications LLM de se connecter à des sources de données externes et des outils de manière standardisée.

### Architecture MCP

```
┌─────────────┐
│ LLM Client  │
│ (Claude,    │
│  etc.)      │
└──────┬──────┘
       │
       │ MCP Protocol
       │
┌──────▼──────┐
│ MCP Server  │
│ (Python)    │
└──────┬──────┘
       │
       │
┌──────▼──────┐
│ Data Source │
│ (DB, API,   │
│  Files...)  │
└─────────────┘
```

### Implémentation Python

**Installation** :
```bash
uv add mcp anthropic-mcp
```

**Créer un MCP Server** :
```python
from mcp.server import Server
from mcp.types import Tool, TextContent

app = Server("my-mcp-server")

@app.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="search_database",
            description="Search in the database",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string"}
                },
                "required": ["query"]
            }
        )
    ]

@app.call_tool()
async def call_tool(name: str, arguments: dict):
    if name == "search_database":
        query = arguments["query"]
        results = await search_db(query)
        return [TextContent(type="text", text=results)]
```

### MCPs Utiles à Implémenter

1. **Filesystem MCP** : Accès fichiers locaux
2. **Database MCP** : PostgreSQL, MongoDB, SQLite
3. **API Integration MCP** : REST APIs, GraphQL
4. **Google Workspace MCP** : Sheets, Docs, Drive
5. **Email MCP** : Gmail, Outlook
6. **Slack/Discord MCP** : Messaging platforms
7. **Git MCP** : Opérations Git
8. **Web Scraping MCP** : Beautiful Soup, Playwright

**Voir** : `directives/mcp-servers-guide.md` pour guide détaillé

---

## 4. LLM Providers & Intégrations

### 4.1 Anthropic Claude ⭐

**Modèles Recommandés** :
- **claude-3-5-sonnet** : Meilleur rapport qualité/prix
- **claude-3-opus** : Tasks complexes
- **claude-3-haiku** : Rapide et économique

```bash
uv add anthropic
```

```python
from anthropic import Anthropic

client = Anthropic(api_key="sk-ant-...")
response = client.messages.create(
    model="claude-3-5-sonnet-20241022",
    max_tokens=1024,
    messages=[{"role": "user", "content": "Hello"}]
)
```

### 4.2 OpenAI

```bash
uv add openai
```

```python
from openai import OpenAI

client = OpenAI(api_key="sk-...")
response = client.chat.completions.create(
    model="gpt-4-turbo",
    messages=[{"role": "user", "content": "Hello"}]
)
```

### 4.3 LiteLLM ⭐ (Recommandé)

**Abstraction unifiée** pour tous les LLM providers.

```bash
uv add litellm
```

```python
from litellm import completion

# Utiliser n'importe quel provider
response = completion(
    model="claude-3-5-sonnet-20241022",
    messages=[{"role": "user", "content": "Hello"}]
)

response = completion(
    model="gpt-4",
    messages=[{"role": "user", "content": "Hello"}]
)

response = completion(
    model="ollama/llama3",  # Local
    messages=[{"role": "user", "content": "Hello"}]
)
```

### 4.4 Autres Providers

- **Mistral AI** : `mistralai`
- **Groq** : `groq` (inférence ultra-rapide)
- **Ollama** : Pour modèles locaux
- **Azure OpenAI** : `openai` avec endpoint Azure

---

## 5. Infrastructure & Outils

### 5.1 API Framework : FastAPI ⭐

```bash
uv add fastapi uvicorn pydantic
```

**Exemple API agentique** :
```python
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class WorkflowRequest(BaseModel):
    workflow_id: str
    input_data: dict

@app.post("/workflows/execute")
async def execute_workflow(request: WorkflowRequest):
    result = await orchestrate_workflow(
        workflow_id=request.workflow_id,
        data=request.input_data
    )
    return {"status": "completed", "result": result}
```

### 5.2 State Management

**Redis** pour state distribué :
```bash
uv add redis asyncio-redis
```

**PostgreSQL** pour persistance :
```bash
uv add asyncpg sqlalchemy
```

**SQLite** pour développement :
```python
import sqlite3
```

### 5.3 Task Queue : Celery

```bash
uv add celery redis
```

```python
from celery import Celery

app = Celery('tasks', broker='redis://localhost:6379/0')

@app.task
def run_agent_workflow(workflow_id: str, data: dict):
    # Exécution asynchrone du workflow
    result = execute_workflow(workflow_id, data)
    return result
```

### 5.4 Linting & Formatting : Ruff ⭐

```bash
uv add ruff --dev
```

**Configuration** (`pyproject.toml`) :
```toml
[tool.ruff]
line-length = 100
target-version = "py311"

[tool.ruff.lint]
select = ["E", "F", "I", "N", "W"]
ignore = ["E501"]
```

### 5.5 Testing

```bash
uv add pytest pytest-asyncio pytest-cov --dev
```

```python
import pytest
from agents.my_agent import MyAgent

@pytest.mark.asyncio
async def test_agent_execution():
    agent = MyAgent()
    result = await agent.execute({"task": "test"})
    assert result["status"] == "success"
```

### 5.6 Containerisation : Docker

**Dockerfile** :
```dockerfile
FROM python:3.12-slim

WORKDIR /app

# Installer UV
RUN pip install uv

# Copier les dépendances
COPY requirements.txt .
RUN uv pip install -r requirements.txt --system

# Copier le code
COPY . .

CMD ["python", "-m", "execution.main"]
```

---

## 6. Patterns Agentiques

### 6.1 ReAct (Reasoning + Acting)

**Pattern** : L'agent raisonne (Thought) puis agit (Action) de manière itérative.

```
Thought: I need to find the current temperature
Action: search_weather(city="Paris")
Observation: 15°C, cloudy
Thought: Now I can answer the question
Final Answer: It's 15°C in Paris
```

**Implémentation** :
```python
class ReActAgent:
    def __init__(self, tools: list[Tool], llm):
        self.tools = tools
        self.llm = llm

    async def run(self, question: str) -> str:
        prompt = f"Question: {question}\n"

        for _ in range(max_iterations):
            response = await self.llm.generate(prompt)

            if "Final Answer:" in response:
                return extract_answer(response)

            if "Action:" in response:
                action, args = parse_action(response)
                observation = await self.execute_tool(action, args)
                prompt += f"Observation: {observation}\n"
```

### 6.2 Chain-of-Thought (CoT)

Demander au LLM de raisonner étape par étape avant de répondre.

```python
system_prompt = """
You are a helpful assistant. When solving problems:
1. Break down the problem into steps
2. Think through each step carefully
3. Show your reasoning
4. Provide the final answer

Always use this format:
Reasoning: [your step-by-step thinking]
Answer: [final answer]
"""
```

### 6.3 Tool Calling Pattern

```python
from typing import Callable, Dict

class ToolRegistry:
    def __init__(self):
        self.tools: Dict[str, Callable] = {}

    def register(self, name: str):
        def decorator(func: Callable):
            self.tools[name] = func
            return func
        return decorator

    async def execute(self, name: str, **kwargs):
        if name not in self.tools:
            raise ValueError(f"Tool {name} not found")
        return await self.tools[name](**kwargs)

registry = ToolRegistry()

@registry.register("search_web")
async def search_web(query: str) -> str:
    # Implémentation
    return results
```

### 6.4 Memory Management

**Short-term Memory** : Dans le contexte de conversation

```python
class ConversationMemory:
    def __init__(self, max_tokens: int = 4000):
        self.messages = []
        self.max_tokens = max_tokens

    def add_message(self, role: str, content: str):
        self.messages.append({"role": role, "content": content})
        self._trim_if_needed()

    def _trim_if_needed(self):
        # Garder seulement les N derniers messages
        if self.count_tokens() > self.max_tokens:
            self.messages = self.messages[-10:]
```

**Long-term Memory** : Stockage persistant

```python
from chromadb import Client

class LongTermMemory:
    def __init__(self):
        self.client = Client()
        self.collection = self.client.create_collection("agent_memory")

    def store(self, key: str, value: str, metadata: dict):
        self.collection.add(
            documents=[value],
            metadatas=[metadata],
            ids=[key]
        )

    def retrieve(self, query: str, n_results: int = 5):
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results
        )
        return results
```

### 6.5 Error Handling & Retry

```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10)
)
async def call_llm_with_retry(prompt: str):
    try:
        return await llm.generate(prompt)
    except RateLimitError:
        logger.warning("Rate limit hit, retrying...")
        raise
    except Exception as e:
        logger.error(f"LLM call failed: {e}")
        raise
```

---

## 7. Observabilité & Monitoring

### 7.1 Structured Logging

```bash
uv add structlog
```

```python
import structlog

logger = structlog.get_logger()

logger.info(
    "workflow_started",
    workflow_id="wf_123",
    user_id="user_456",
    timestamp=datetime.now()
)
```

### 7.2 LLM Tracing : LangSmith / LangFuse

**LangSmith** (LangChain) :
```bash
export LANGCHAIN_TRACING_V2=true
export LANGCHAIN_API_KEY="lsv2_..."
```

**LangFuse** (Open-source alternative) :
```bash
uv add langfuse
```

```python
from langfuse import Langfuse

langfuse = Langfuse()

trace = langfuse.trace(name="agent_workflow")
span = trace.span(name="llm_call", input={"prompt": "..."})
# ... exécution
span.end(output={"response": "..."})
```

### 7.3 Métriques : Prometheus

```bash
uv add prometheus-client
```

```python
from prometheus_client import Counter, Histogram, start_http_server

workflow_counter = Counter(
    'workflows_total',
    'Total workflows executed',
    ['workflow_type', 'status']
)

workflow_duration = Histogram(
    'workflow_duration_seconds',
    'Workflow execution duration'
)

@workflow_duration.time()
async def execute_workflow(...):
    # ...
    workflow_counter.labels(
        workflow_type="data_processing",
        status="success"
    ).inc()
```

### 7.4 Dashboards : Grafana

Configurer Grafana pour visualiser les métriques Prometheus :
- Taux de succès/échec des workflows
- Durée d'exécution
- Coûts LLM (tokens consommés)
- Erreurs et retries

---

## 8. Migration N8N → Code

### 8.1 Mapping des Concepts

| N8N Concept | Équivalent Code |
|-------------|-----------------|
| **Workflow** | Python async function / LangGraph |
| **Node** | Tool / Function |
| **Trigger** | FastAPI endpoint / Scheduler |
| **Credentials** | Environment variables (.env) |
| **Variables** | Python variables / State dict |
| **IF Node** | Conditional logic (if/else) |
| **Switch Node** | Pattern matching (match/case) |
| **Loop** | for/while loops |
| **HTTP Request** | httpx / requests |
| **Code Node** | Python function inline |

### 8.2 Exemple de Migration

**N8N Workflow** :
```
[Webhook] → [HTTP Request] → [IF] → [Send Email]
```

**Équivalent Code** :
```python
from fastapi import FastAPI, Request
import httpx
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

app = FastAPI()

@app.post("/webhook")
async def webhook_handler(request: Request):
    # 1. Recevoir webhook
    data = await request.json()

    # 2. HTTP Request
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "https://api.example.com/data",
            params={"id": data["id"]}
        )
        result = response.json()

    # 3. Condition IF
    if result["status"] == "success":
        # 4. Send Email
        message = Mail(
            from_email='noreply@example.com',
            to_emails=data["email"],
            subject='Success',
            html_content='<strong>Done!</strong>'
        )
        sg = SendGridAPIClient(os.environ['SENDGRID_API_KEY'])
        sg.send(message)

    return {"status": "processed"}
```

### 8.3 Avantages du Code vs N8N

| Aspect | N8N | Code Python |
|--------|-----|-------------|
| **Version Control** | JSON export | Git natif ✅ |
| **Testing** | Limité | Pytest complet ✅ |
| **Debugging** | UI limitée | Debugger Python ✅ |
| **Performance** | Overhead | Optimal ✅ |
| **Scalabilité** | Single instance | Horizontal scaling ✅ |
| **Type Safety** | Aucune | Pydantic ✅ |
| **Agents IA** | Basique | Frameworks complets ✅ |
| **Complexité** | UI limitante | Illimité ✅ |
| **Cost** | Self-hosted | Self-hosted ✅ |

---

## 9. Standards de Développement

### 9.1 Structure de Projet

```
workflows-boilerplate/
├── directives/           # SOPs et spécifications
│   ├── TECHNICAL_SPECS.md
│   ├── workflow_*.md
│   └── mcp-servers-guide.md
├── execution/            # Code d'exécution
│   ├── __init__.py
│   ├── core/
│   │   ├── config.py
│   │   ├── logger.py
│   │   └── exceptions.py
│   ├── agents/
│   │   ├── base_agent.py
│   │   └── specific_agents.py
│   ├── workflows/
│   │   └── workflow_implementations.py
│   ├── tools/
│   │   └── tool_registry.py
│   ├── mcp_servers/
│   │   └── custom_servers.py
│   └── utils/
│       ├── api_clients.py
│       └── validators.py
├── tests/
│   ├── unit/
│   ├── integration/
│   └── e2e/
├── .tmp/                 # Fichiers temporaires (gitignore)
├── .env                  # Variables d'environnement
├── pyproject.toml        # Config UV et dépendances
├── requirements.txt      # Dépendances lockées
├── Dockerfile
├── docker-compose.yml
└── README.md
```

### 9.2 Conventions de Code

**Naming** :
- `snake_case` : fonctions, variables, fichiers
- `PascalCase` : classes
- `UPPER_CASE` : constantes
- Préfixes : `_private`, `__very_private`

**Type Hints** (obligatoire) :
```python
def process_data(
    input_data: dict[str, Any],
    config: Config,
    timeout: float = 30.0
) -> ProcessingResult:
    ...
```

**Docstrings** (Google style) :
```python
def execute_workflow(workflow_id: str, data: dict) -> dict:
    """
    Exécute un workflow agentique.

    Args:
        workflow_id: Identifiant unique du workflow
        data: Données d'entrée pour le workflow

    Returns:
        Résultat de l'exécution avec status et outputs

    Raises:
        WorkflowNotFoundError: Si le workflow n'existe pas
        ValidationError: Si les données sont invalides
    """
    pass
```

### 9.3 Configuration (.env)

```bash
# LLM APIs
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...
MISTRAL_API_KEY=...

# Infrastructure
REDIS_URL=redis://localhost:6379
DATABASE_URL=postgresql://user:pass@localhost/db

# MCP Servers
MCP_SERVER_PORT=3000

# Observability
LANGSMITH_API_KEY=...
LANGFUSE_PUBLIC_KEY=...
LANGFUSE_SECRET_KEY=...

# Application
ENVIRONMENT=development
LOG_LEVEL=INFO
MAX_RETRIES=3
TIMEOUT=30
```

### 9.4 Pre-commit Hooks

```bash
uv add pre-commit --dev
```

`.pre-commit-config.yaml` :
```yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.1.6
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format

  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
```

---

## 🎯 Checklist de Démarrage

Lors de la création d'un nouveau workflow agentique :

- [ ] Créer une directive dans `directives/workflow_name.md`
- [ ] Définir les Pydantic models pour validation
- [ ] Implémenter les agents dans `execution/agents/`
- [ ] Créer les outils nécessaires dans `execution/tools/`
- [ ] Configurer le logging structuré
- [ ] Ajouter les tests (unit + integration)
- [ ] Configurer le monitoring (métriques + traces)
- [ ] Documenter dans la directive les learnings
- [ ] Dockeriser si nécessaire
- [ ] Configurer les variables d'environnement

---

## 📚 Ressources

### Documentation Officielle
- [LangGraph](https://langchain-ai.github.io/langgraph/)
- [CrewAI](https://docs.crewai.com/)
- [AutoGen](https://microsoft.github.io/autogen/)
- [LlamaIndex](https://docs.llamaindex.ai/)
- [Pydantic AI](https://ai.pydantic.dev/)
- [MCP Protocol](https://modelcontextprotocol.io/)
- [UV Documentation](https://docs.astral.sh/uv/)

### Outils
- [LangSmith](https://smith.langchain.com/) - Tracing LLM
- [LangFuse](https://langfuse.com/) - Open-source LLM observability
- [Ruff](https://docs.astral.sh/ruff/) - Linter/Formatter

---

**Version** : 1.0.0
**Dernière mise à jour** : 2026-01-09
**Maintenu par** : L'équipe du projet
