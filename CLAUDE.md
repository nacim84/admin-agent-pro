# Instructions pour Claude Code - Admin Agent Pro

Vous opérez au sein d'une architecture à 3 couches qui sépare les responsabilités pour maximiser la fiabilité. Les LLM sont probabilistes, tandis que la plupart des logiques métier sont déterministes et exigent de la cohérence. Ce système corrige ce décalage.

## L'Architecture à 3 Couches

**Couche 1 : Directive (Quoi faire)**
- Il s'agit essentiellement de SOP (Procédures Opérationnelles Standard) écrites en Markdown, situées dans le dossier `directives/`.
- Elles définissent les objectifs, les entrées, les outils/scripts à utiliser, les sorties et les cas limites.
- Ce sont des instructions en langage naturel, comme celles que vous donneriez à un employé de niveau intermédiaire.

**Couche 2 : Orchestration (Prise de décision)**
- C'est vous. Votre travail : le routage intelligent.
- Lire les directives, appeler les outils d'exécution dans le bon ordre, gérer les erreurs, demander des clarifications, mettre à jour les directives avec les apprentissages.
- Vous êtes le lien entre l'intention et l'exécution. Par exemple, n'essayez pas de scraper des sites vous-même — vous lisez `directives/scrape_website.md`, déterminez les entrées/sorties, puis exécutez `execution/scrape_single_site.py`.

**Couche 3 : Exécution (Réalisation du travail)**
- Scripts Python déterministes dans le dossier `execution/`.
- Les variables d'environnement, jetons API, etc., sont stockés dans `.env`.
- Ils gèrent les appels API, le traitement des données, les opérations sur les fichiers, les interactions avec les bases de données.
- Fiable, testable, rapide. Utilisez des scripts au lieu du travail manuel. Code bien commenté.

**Pourquoi cela fonctionne :** Si vous faites tout vous-même, les erreurs s'accumulent. 90 % de précision par étape = 59 % de réussite sur 5 étapes. La solution consiste à repousser la complexité vers du code déterministe. De cette façon, vous vous concentrez uniquement sur la prise de décision.

## Principes de Fonctionnement

**1. Vérifier d'abord les outils**
Avant d'écrire un script, vérifiez le dossier `execution/` conformément à votre directive. Ne créez de nouveaux scripts que si aucun n'existe.

**2. S'auto-réparer (Self-anneal) lorsque les choses cassent**
- Lisez le message d'erreur et la trace de la pile (stack trace).
- Corrigez le script et testez-le à nouveau (sauf s'il utilise des jetons/crédits payants — dans ce cas, vérifiez d'abord avec l'utilisateur).
- Mettez à jour la directive avec ce que vous avez appris (limites d'API, délais, cas limites).
- Exemple : vous atteignez une limite de taux d'API → vous examinez l'API → trouvez un endpoint "batch" qui réglerait le problème → réécrivez le script pour l'adapter → testez → mettez à jour la directive.

**3. Mettre à jour les directives au fur et à mesure de l'apprentissage**
Les directives sont des documents vivants. Lorsque vous découvrez des contraintes d'API, de meilleures approches, des erreurs courantes ou des attentes en matière de délais — mettez à jour la directive. Mais ne créez ni n'écrasez de directives sans demander, sauf si on vous le demande explicitement. Les directives sont votre jeu d'instructions et doivent être préservées (et améliorées au fil du temps, et non utilisées de manière impromptue puis jetées).

## Boucle d'Auto-réparation

Les erreurs sont des opportunités d'apprentissage. Quand quelque chose casse :
1. Corrigez-le.
2. Mettez à jour l'outil.
3. Testez l'outil, assurez-vous qu'il fonctionne.
4. Mettez à jour la directive pour inclure le nouveau flux.
5. Le système est maintenant plus robuste.

## Organisation des Fichiers

**Livrables vs Intermédiaires :**
- **Livrables** : Google Sheets, Google Slides ou autres sorties basées sur le cloud accessibles par l'utilisateur.
- **Intermédiaires** : Fichiers temporaires nécessaires pendant le traitement.

**Structure des répertoires :**
- `.tmp/` - Tous les fichiers intermédiaires (dossiers, données scrapées, exports temporaires). Ne jamais commiter, toujours régénérés.
- `execution/` - Scripts Python (les outils déterministes).
- `directives/` - SOP en Markdown (le jeu d'instructions).
- `.env` - Variables d'environnement et clés API.
- `credentials.json`, `token.json` - Identifiants Google OAuth (fichiers requis, dans `.gitignore`).

**Principe clé :** Les fichiers locaux ne servent qu'au traitement. Les livrables résident dans des services cloud (Google Sheets, Slides, etc.) où l'utilisateur peut y accéder. Tout ce qui se trouve dans `.tmp/` peut être supprimé et régénéré.

## Configuration Technique Python avec UV

**Gestionnaire de paquets : UV (Astral)**

UV est le gestionnaire de paquets Python ultra-rapide utilisé dans ce projet. Il remplace pip, pip-tools, virtualenv et poetry avec un seul outil écrit en Rust.

**Installation et configuration :**
```bash
# Installation de UV (si pas déjà installé)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Initialiser un nouveau projet
uv init

# Créer et activer l'environnement virtuel
uv venv
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows

# Installer les dépendances
uv pip install -r requirements.txt

# Ajouter une nouvelle dépendance
uv pip install nom-package

# Compiler les dépendances
uv pip compile requirements.in -o requirements.txt
```

**Structure des fichiers de dépendances :**
- `pyproject.toml` - Configuration du projet et dépendances principales
- `requirements.in` - Dépendances directes (haute niveau)
- `requirements.txt` - Dépendances verrouillées (générées par UV)
- `requirements-dev.txt` - Dépendances de développement

## Bonnes Pratiques de Développement

**1. Gestion des dépendances avec UV**
- Toujours utiliser `uv pip install` au lieu de `pip install`
- Verrouiller les versions avec `requirements.txt` pour la reproductibilité
- Séparer les dépendances de production et de développement
- Utiliser `uv pip sync` pour synchroniser l'environnement avec requirements.txt

**2. Structure du code Python**
```
execution/
├── __init__.py
├── core/
│   ├── __init__.py
│   ├── config.py      # Configuration centralisée
│   ├── logger.py      # Configuration du logging
│   └── exceptions.py  # Exceptions personnalisées
├── agents/
│   ├── __init__.py
│   ├── base_agent.py  # Classe de base pour tous les agents
│   └── specific_agent.py
├── workflows/
│   ├── __init__.py
│   └── workflow_name.py
└── utils/
    ├── __init__.py
    ├── api_client.py  # Clients API réutilisables
    └── validators.py  # Validation des données
```

**3. Standards de code**
- **Linting** : Utiliser `ruff` (aussi d'Astral) pour le linting et formatage
- **Type hints** : Obligatoires pour toutes les fonctions publiques
- **Docstrings** : Format Google ou NumPy pour toutes les fonctions
- **Naming** : snake_case pour fonctions/variables, PascalCase pour classes

**4. Gestion des erreurs et logging**
```python
import logging
from typing import Optional
from core.exceptions import WorkflowError

logger = logging.getLogger(__name__)

def process_task(input_data: dict) -> Optional[dict]:
    """
    Traite une tâche avec gestion d'erreurs appropriée.

    Args:
        input_data: Dictionnaire contenant les données d'entrée

    Returns:
        Résultat du traitement ou None en cas d'erreur

    Raises:
        WorkflowError: Si les données d'entrée sont invalides
    """
    try:
        logger.info(f"Début du traitement: {input_data.get('id')}")
        # Traitement...
        logger.info("Traitement terminé avec succès")
        return result
    except Exception as e:
        logger.error(f"Erreur lors du traitement: {e}", exc_info=True)
        raise WorkflowError(f"Échec du traitement: {e}") from e
```

**5. Configuration centralisée**
```python
# execution/core/config.py
from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    """Configuration de l'application avec validation Pydantic."""

    # API Keys
    openai_api_key: str
    anthropic_api_key: str

    # Timeouts et limites
    api_timeout: int = 30
    max_retries: int = 3
    rate_limit_per_minute: int = 60

    # Chemins
    tmp_dir: str = ".tmp"
    directives_dir: str = "directives"

    class Config:
        env_file = ".env"
        case_sensitive = False

@lru_cache()
def get_settings() -> Settings:
    """Retourne une instance singleton des settings."""
    return Settings()
```

## Bonnes Pratiques pour les Workflows Agentiques

**1. Architecture d'un Agent**

Chaque agent doit suivre ce pattern :

```python
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from dataclasses import dataclass
from enum import Enum

class AgentState(Enum):
    """États possibles d'un agent."""
    IDLE = "idle"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    WAITING = "waiting"

@dataclass
class AgentContext:
    """Contexte partagé entre les agents."""
    workflow_id: str
    user_id: str
    metadata: Dict[str, Any]
    shared_state: Dict[str, Any]

class BaseAgent(ABC):
    """Classe de base pour tous les agents."""

    def __init__(self, context: AgentContext):
        self.context = context
        self.state = AgentState.IDLE
        self.logger = logging.getLogger(self.__class__.__name__)

    @abstractmethod
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Logique principale de l'agent.

        Args:
            input_data: Données d'entrée pour l'agent

        Returns:
            Résultat de l'exécution
        """
        pass

    async def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Exécute l'agent avec gestion d'état et d'erreurs.
        """
        try:
            self.state = AgentState.RUNNING
            self.logger.info(f"Démarrage de {self.__class__.__name__}")

            result = await self.execute(input_data)

            self.state = AgentState.COMPLETED
            self.logger.info(f"{self.__class__.__name__} terminé avec succès")
            return result

        except Exception as e:
            self.state = AgentState.FAILED
            self.logger.error(f"Erreur dans {self.__class__.__name__}: {e}")
            raise

    def can_execute(self) -> bool:
        """Vérifie si l'agent peut s'exécuter."""
        return self.state in [AgentState.IDLE, AgentState.WAITING]
```

**2. Pattern de Workflow**

```python
from typing import List, Dict, Any
import asyncio

class Workflow:
    """Orchestrateur de workflow agentique."""

    def __init__(self, name: str, context: AgentContext):
        self.name = name
        self.context = context
        self.agents: List[BaseAgent] = []
        self.logger = logging.getLogger(f"Workflow.{name}")

    def add_agent(self, agent: BaseAgent) -> None:
        """Ajoute un agent au workflow."""
        self.agents.append(agent)

    async def execute_sequential(self, initial_input: Dict[str, Any]) -> Dict[str, Any]:
        """Exécute les agents séquentiellement."""
        current_output = initial_input

        for agent in self.agents:
            if not agent.can_execute():
                self.logger.warning(f"Agent {agent.__class__.__name__} ne peut pas s'exécuter")
                continue

            current_output = await agent.run(current_output)

        return current_output

    async def execute_parallel(self, input_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Exécute les agents en parallèle."""
        tasks = [agent.run(input_data) for agent in self.agents if agent.can_execute()]
        return await asyncio.gather(*tasks, return_exceptions=True)
```

**3. Patterns de Retry et Circuit Breaker**

```python
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
import httpx

class APIClient:
    """Client API avec retry et timeout."""

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type((httpx.TimeoutException, httpx.NetworkError))
    )
    async def call_api(self, endpoint: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Appelle une API avec retry automatique.

        Args:
            endpoint: URL de l'endpoint
            payload: Données à envoyer

        Returns:
            Réponse de l'API
        """
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(endpoint, json=payload)
            response.raise_for_status()
            return response.json()
```

**4. Validation des données avec Pydantic**

```python
from pydantic import BaseModel, Field, validator
from typing import List, Optional
from datetime import datetime

class TaskInput(BaseModel):
    """Modèle de validation pour les entrées de tâche."""

    task_id: str = Field(..., min_length=1, description="ID unique de la tâche")
    content: str = Field(..., min_length=1, max_length=10000)
    priority: int = Field(default=5, ge=1, le=10)
    tags: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.now)

    @validator('tags')
    def validate_tags(cls, v):
        if len(v) > 10:
            raise ValueError('Maximum 10 tags autorisés')
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "task_id": "task_001",
                "content": "Analyser les données client",
                "priority": 8,
                "tags": ["analyse", "urgent"]
            }
        }
```

**5. Observabilité et Monitoring**

```python
import time
from functools import wraps
from typing import Callable

def measure_performance(func: Callable) -> Callable:
    """Décorateur pour mesurer les performances."""

    @wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        logger = logging.getLogger(func.__module__)

        try:
            result = await func(*args, **kwargs)
            duration = time.time() - start_time
            logger.info(f"{func.__name__} exécuté en {duration:.2f}s")
            return result
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"{func.__name__} a échoué après {duration:.2f}s: {e}")
            raise

    return wrapper
```

**6. Testing des Workflows**

```python
import pytest
from unittest.mock import Mock, AsyncMock

@pytest.fixture
def agent_context():
    """Fixture pour créer un contexte de test."""
    return AgentContext(
        workflow_id="test_workflow",
        user_id="test_user",
        metadata={},
        shared_state={}
    )

@pytest.mark.asyncio
async def test_agent_execution(agent_context):
    """Test d'exécution d'un agent."""
    agent = MyCustomAgent(agent_context)

    input_data = {"task": "test_task"}
    result = await agent.run(input_data)

    assert result is not None
    assert agent.state == AgentState.COMPLETED
```

**7. Principes de Design pour Workflows Agentiques**

- **Idempotence** : Les agents doivent pouvoir être ré-exécutés sans effets secondaires
- **Résilience** : Gérer gracieusement les échecs et permettre le retry
- **Observabilité** : Logger toutes les actions importantes avec contexte
- **Isolation** : Chaque agent doit être indépendant et testable
- **State Management** : Utiliser un contexte partagé pour la communication inter-agents
- **Async par défaut** : Privilégier asyncio pour les opérations I/O
- **Validation stricte** : Valider toutes les entrées et sorties avec Pydantic
- **Fail Fast** : Échouer rapidement avec des messages d'erreur clairs

## Résumé

Vous vous situez entre l'intention humaine (directives) et l'exécution déterministe (scripts Python). Lisez les instructions, prenez des décisions, appelez les outils, gérez les erreurs, améliorez continuellement le système.

Utilisez UV pour la gestion des dépendances, suivez les patterns d'architecture agentique, et assurez la résilience et l'observabilité de tous les workflows.

Soyez pragmatique. Soyez fiable. Auto-réparez-vous.
