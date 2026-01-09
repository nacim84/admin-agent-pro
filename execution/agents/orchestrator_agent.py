"""Agent Orchestrateur pour l'analyse du langage naturel."""

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from execution.core.config import get_settings
from execution.prompts.orchestrator_prompts import ORCHESTRATOR_SYSTEM_PROMPT
from execution.tools.db_manager import DatabaseManager
from typing import Any, Dict, TypedDict
import logging

logger = logging.getLogger(__name__)

class IntentResult(TypedDict):
    intent: str
    confidence: float
    extracted_data: Dict[str, Any]
    reply_text: str | None

class OrchestratorAgent:
    """
    Agent principal qui analyse les messages utilisateurs
    et les dirige vers le bon agent spécialisé.
    """

    def __init__(self):
        self.settings = get_settings()
        self.db = DatabaseManager()
        
        # Initialisation du LLM via OpenRouter
        self.llm = ChatOpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=self.settings.openrouter_api_key,
            model=self.settings.openrouter_model,
            temperature=0,
        )
        
        self.parser = JsonOutputParser()
        
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", ORCHESTRATOR_SYSTEM_PROMPT),
            MessagesPlaceholder(variable_name="history"),
            ("user", "{input}")
        ])
        
        self.chain = self.prompt | self.llm | self.parser

    async def analyze_message(self, text: str, user_id: int) -> IntentResult:
        """
        Analyse un message texte et retourne l'intention et les données.
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
            
            result = await self.chain.ainvoke({
                "input": text,
                "history": history_messages
            })
            
            # Normalisation des résultats
            intent = result.get("intent", "chat")
            data = result.get("extracted_data", {})
            reply = result.get("reply_text")
            
            logger.info(f"🎯 Intention détectée: {intent}")
            
            return {
                "intent": intent,
                "confidence": result.get("confidence", 0.0),
                "extracted_data": data,
                "reply_text": reply
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