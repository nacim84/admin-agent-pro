"""Agent Orchestrateur pour l'analyse du langage naturel."""

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, ToolMessage
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
import json

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
        
        # Map for execution
        self.tools_map = {t.name: t for t in self.tools}
        
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
            ("system", ORCHESTRATOR_SYSTEM_PROMPT + "\n\nCURRENT DATE: {current_date}"),
            MessagesPlaceholder(variable_name="history"),
            MessagesPlaceholder(variable_name="agent_scratchpad"), # For current turn intermediate steps
            ("user", "{input}")
        ])
        
        # We handle the chain execution manually in the loop
        self.runnable = self.prompt | self.llm

    async def analyze_message(self, text: str, user_id: int) -> IntentResult:
        """
        Analyse un message texte et retourne l'intention, les données et les appels d'outils.
        Exécute les outils si nécessaire (Loop).
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
            
            from datetime import datetime
            current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            agent_scratchpad = []
            max_iterations = 5
            
            for i in range(max_iterations):
                response = await self.runnable.ainvoke({
                    "input": text,
                    "history": history_messages,
                    "agent_scratchpad": agent_scratchpad,
                    "current_date": current_date
                })
                
                # Si Tool Calls
                if response.tool_calls:
                    logger.info(f"🛠️ Tool calls détectés (Iter {i+1}): {[tc['name'] for tc in response.tool_calls]}")
                    
                    # Ajouter la réponse de l'assistant aux messages temporaires
                    agent_scratchpad.append(response)
                    
                    # Exécuter les outils
                    for tool_call in response.tool_calls:
                        tool_name = tool_call["name"]
                        args = tool_call["args"]
                        tool_call_id = tool_call["id"]
                        
                        tool = self.tools_map.get(tool_name)
                        if tool:
                            try:
                                # Execution: Always prefer async invoke if tool is async
                                # In LangChain, ainvoke handles the routing to _arun automatically
                                tool_output = await tool.ainvoke(args)
                                    
                                logger.info(f"   ✅ Output {tool_name}: {str(tool_output)[:50]}...")
                            except Exception as e:
                                tool_output = f"Error executing {tool_name}: {str(e)}"
                                logger.error(f"   ❌ Error {tool_name}: {e}")
                        else:
                            tool_output = f"Tool {tool_name} not found."
                        
                        # Ajouter le résultat au scratchpad
                        agent_scratchpad.append(ToolMessage(
                            content=str(tool_output),
                            tool_call_id=tool_call_id
                        ))
                    
                    # Continuer la boucle pour que le LLM traite le résultat
                    continue
                
                # Si pas de tool call, c'est la réponse finale
                content = response.content
                intent = "chat"
                data = {}
                reply = None
                
                if content and "{" in content:
                    try:
                        # Extraire le JSON si entouré de texte
                        json_str = content[content.find("{"):content.rfind("}")+1]
                        result = json.loads(json_str)
                        intent = result.get("intent", "chat")
                        data = result.get("extracted_data", {})
                        reply = result.get("reply_text")
                    except Exception as e:
                        logger.warning(f"Failed to parse JSON content: {e}")
                        reply = content
                else:
                    reply = content

                logger.info(f"🎯 Intention détectée: {intent}")
                
                return {
                    "intent": intent,
                    "confidence": 1.0,
                    "extracted_data": data,
                    "reply_text": reply,
                    "tool_calls": None
                }
            
            # Si max iterations atteint
            logger.warning("⚠️ Max iterations reached without final response")
            return {
                "intent": "chat",
                "confidence": 0.0,
                "extracted_data": {},
                "reply_text": "Je travaille dessus mais cela prend plus de temps que prévu.",
                "tool_calls": None
            }
            
        except Exception as e:
            logger.error(f"❌ Erreur d'analyse NLU: {e}", exc_info=True)
            return {
                "intent": "chat",
                "confidence": 0.0,
                "extracted_data": {},
                "reply_text": "Désolé, une erreur technique est survenue.",
                "tool_calls": None
            }