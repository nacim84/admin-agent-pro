"""Agent Orchestrateur pour l'analyse du langage naturel."""

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from execution.core.config import get_settings
from execution.prompts.orchestrator_prompts import ORCHESTRATOR_SYSTEM_PROMPT
from execution.tools import (
    CalculatorTool,
    DatabaseQueryTool,
    EmailSenderTool,
    WhisperTranscriptionTool,
    MarkdownCleanerTool,
    DatabaseManager
)
from typing import Any, Dict, TypedDict, List
import logging

logger = logging.getLogger(__name__)

class IntentResult(TypedDict):
    intent: str
    confidence: float
    extracted_data: Dict[str, Any]
    reply_text: str | None
    tool_calls: List[Dict[str, Any]] | None

class OrchestratorAgent:
    """
    Agent principal qui analyse les messages utilisateurs,
    utilise des outils et dirige vers le bon agent spécialisé.
    """

    def __init__(self):
        self.settings = get_settings()
        self.db = DatabaseManager()
        
        # Tools
        self.tools = [
            CalculatorTool(),
            DatabaseQueryTool(),
            EmailSenderTool(),
            WhisperTranscriptionTool(),
            MarkdownCleanerTool()
        ]
        
        # Initialisation du LLM via OpenRouter avec support Tools
        self.llm = ChatOpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=self.settings.openrouter_api_key,
            model=self.settings.openrouter_model,
            temperature=0,
            default_headers={
                "HTTP-Referer": "https://github.com/admin-agent-pro",
                "X-Title": self.settings.app_name,
            }
        ).bind_tools(self.tools)
        
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", ORCHESTRATOR_SYSTEM_PROMPT),
            MessagesPlaceholder(variable_name="history"),
            ("user", "{input}")
        ])
        
        self.chain = self.prompt | self.llm

    async def analyze_message(self, text: str, user_id: int) -> IntentResult:
        """
        Analyse un message texte et retourne l'intention, les données et les appels d'outils.
        """
        try:
            logger.info(f"🧠 Analyse du message: '{text[:50]}...'")
            
            # Récupérer l'historique
            history_data = await self.db.get_chat_history(user_id, limit=10)
            
            # Convertir en objets Messages LangChain
            history_messages = []
            for msg in history_data:
                if msg["role"] == "user":
                    history_messages.append(HumanMessage(content=msg["content"]))
                else:
                    history_messages.append(AIMessage(content=msg["content"]))
            
            response = await self.chain.ainvoke({
                "input": text,
                "history": history_messages
            })
            
            # Analyse de la réponse (Tool Calls ou JSON)
            intent = "chat"
            data = {}
            reply = None
            tool_calls = []
            
            if response.tool_calls:
                tool_calls = response.tool_calls
                logger.info(f"🛠️ Tool calls détectés: {[tc['name'] for tc in tool_calls]}")
            
            # Si le modèle a répondu par du texte qui pourrait être du JSON (cas fallback)
            content = response.content
            if content and "{" in content:
                try:
                    import json
                    # Extraire le JSON si entouré de texte
                    json_str = content[content.find("{"):content.rfind("}")+1]
                    result = json.loads(json_str)
                    intent = result.get("intent", "chat")
                    data = result.get("extracted_data", {})
                    reply = result.get("reply_text")
                except Exception:
                    reply = content
            else:
                reply = content

            logger.info(f"🎯 Intention détectée: {intent}")
            
            return {
                "intent": intent,
                "confidence": 1.0 if not tool_calls else 0.5,
                "extracted_data": data,
                "reply_text": reply,
                "tool_calls": tool_calls
            }
            
        except Exception as e:
            logger.error(f"❌ Erreur d'analyse NLU: {e}", exc_info=True)
            # Fallback en mode chat/erreur
            return {
                "intent": "chat",
                "confidence": 0.0,
                "extracted_data": {},
                "reply_text": "Désolé, j'ai eu du mal à comprendre votre demande. Pouvez-vous reformuler ?"
            }