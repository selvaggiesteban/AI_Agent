import os
import sys
import time
import threading
import json
from datetime import datetime
from typing import List, Dict, Any, Optional

from core.logger import logger
from core.integrations import TelegramIntegration
from core.ai_engine import llm
from core.state import state_store
from core.tools import registry
import core.capabilities # This triggers registration of all tools

# Legacy campaign imports for backward compatibility
try:
    from scripts.campaigns.trabajo_campaign import run_trabajo_campaign
    from scripts.campaigns.posicionamiento_campaign import run_posicionamiento_campaign
    from scripts.campaigns.contable_campaign import run_contable_campaign
except ImportError:
    logger.warning("Legacy campaigns could not be imported.")

class AgentOrchestrator:
    """
    The SOTA Reasoning Core of the AI Agent.
    Handles perception, planning, action, and evaluation.
    """
    def __init__(self):
        self.tools = registry
        self.state = state_store

    def perceive(self) -> Dict[str, Any]:
        """Collects current state and environmental context."""
        return {
            "current_metrics": self.state.get_metrics(),
            "available_tools": self.tools.list_tools(),
            "timestamp": datetime.now().isoformat()
        }

    def plan(self, goal: str, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Uses the LLM to generate a sequence of tool calls to achieve the goal.
        """
        system_prompt = (
            "You are the Master Orchestrator for Esteban Selvaggi's AI Agent. "
            "Your goal is to decompose a high-level request into a sequence of tool calls. "
            "You have access to the following tools:\n"
            f"{json.dumps(context['available_tools'], indent=2)}\n\n"
            "Current system state:\n"
            f"{json.dumps(context['current_metrics'], indent=2)}\n\n"
            "Return a JSON array of tool calls. Each call must be: "
            "{\"tool\": \"ToolName\", \"args\": {\\\"arg_name\\\": \\\"value\\\"}}"
        )

        prompt = f"Goal: {goal}\n\nGenerate the sequence of tool calls to achieve this goal."

        try:
            result = llm.generate_structured(
                prompt=prompt,
                system_instruction=system_prompt,
                model="gemini"
            )
            # The LLM might return a dict with a list, or just a list.
            if isinstance(result, dict) and "plan" in result:
                return result["plan"]
            if isinstance(result, list):
                return result
            return []
        except Exception as e:
            logger.error(f"Planning failed: {e}")
            return []

    def act(self, plan: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Executes the sequence of tools and collects results."""
        results = []
        for step in plan:
            tool_name = step.get("tool")
            args = step.get("args", {})

            logger.info(f"Executing tool: {tool_name} with args {args}")
            tool = self.tools.get_tool(tool_name)

            if tool:
                try:
                    res = tool.execute(**args)
                    results.append({"tool": tool_name, "status": "success", "result": res})
                except Exception as e:
                    logger.error(f"Tool {tool_name} failed: {e}")
                    results.append({"tool": tool_name, "status": "error", "error": str(e)})
            else:
                logger.error(f"Tool {tool_name} not found in registry.")
                results.append({"tool": tool_name, "status": "not_found"})

        return results

    def evaluate(self, goal: str, results: List[Dict[str, Any]]) -> str:
        """
        Synthesizes the results into a final report and updates the state store.
        """
        system_prompt = "You are a Business Analyst. Synthesize the tool results into a professional report for Esteban Selvaggi."
        prompt = f"Goal: {goal}\n\nTool Results:\n{json.dumps(results, indent=2)}\n\nSynthesize a final report."

        try:
            report = llm.generate_structured(
                prompt=prompt,
                system_instruction=system_prompt,
                model="gemini"
            )
            final_text = report.get("report", str(report))

            # Update state store with a summary of this execution
            self.state.set(f"last_run_{datetime.now().strftime('%Y%m%d')}", {
                "goal": goal,
                "status": "completed",
                "summary": final_text[:200] + "..."
            })
            self.state.save()

            return final_text
        except Exception as e:
            logger.error(f"Evaluation failed: {e}")
            return "Error synthesizing final report."

    def run(self, goal: str) -> str:
        """The main agentic loop: Perceive -> Plan -> Act -> Evaluate."""
        logger.info(f"Starting goal-oriented execution: {goal}")

        context = self.perceive()
        plan = self.plan(goal, context)

        if not plan:
            return "I couldn't determine a plan to achieve this goal."

        results = self.act(plan)
        return self.evaluate(goal, results)

def load_conventions():
    """Loads conventions and rules from project documentation files."""
    conventions = []
    files = ["AGENTS.md", "ENRICH_RULES.md", "ESTEBAN.md"]
    for file_name in files:
        path = os.path.join(os.getcwd(), file_name)
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    content = f.read()
                    conventions.append(f"--- {file_name} ---\\n{content}")
            except Exception as e:
                logger.error(f"Could not read convention file {file_name}: {e}")
    return "\\n\\n".join(conventions)

def decode_instruction(text, conventions):
    """Maps natural language to a goal for the Orchestrator."""
    system_prompt = (
        "You are the Instruction Decoder. Map the request to a clear goal for the Orchestrator. "
        "If the request is a known campaign, translate it into a high-level goal. "
        f"Project Conventions:\\n{conventions}"
    )
    prompt = f"Instruction: {text}\\n\\nReturn a JSON object with the key 'goal'."
    try:
        result = llm.generate_structured(prompt=prompt, system_instruction=system_prompt, model="gemini")
        return result.get("goal", "Run general system check")
    except Exception as e:
        logger.error(f"Error decoding instruction: {e}")
        return "Run general system check"

def execute_action(action_goal, chat_id, tg, conventions):
    """Helper to execute a goal and notify via Telegram."""
    def wrapper():
        try:
            orchestrator = AgentOrchestrator()
            tg.send_message(chat_id, f"🚀 Planning goal: {action_goal}...")
            report = orchestrator.run(action_goal)
            tg.send_message(chat_id, f"✅ Goal completed.\n\n{report}")
        except Exception as e:
            logger.exception(f"Error executing goal {action_goal}: {e}")
            tg.send_message(chat_id, f"❌ An error occurred: {str(e)}")

    threading.Thread(target=wrapper, daemon=True).start()

def listen_telegram():
    """Polls Telegram for new messages and triggers the Orchestrator."""
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    if not token:
        logger.error("TELEGRAM_BOT_TOKEN not set.")
        return

    tg = TelegramIntegration(token)
    conventions = load_conventions()
    offset = None

    logger.info("Telegram listener started. Waiting for instructions...")

    while True:
        try:
            updates = tg.get_updates(offset=offset)
            if "result" in updates:
                for update in updates["result"]:
                    offset = update["update_id"] + 1
                    if "message" in update and "text" in update["message"]:
                        chat_id = update["message"]["chat"]["id"]
                        text = update["message"]["text"]
                        logger.info(f"Received message from {chat_id}: {text}")
                        goal = decode_instruction(text, conventions)
                        execute_action(goal, chat_id, tg, conventions)
            time.sleep(10)
        except Exception as e:
            logger.error(f"Unexpected error in Telegram listener: {e}")
            time.sleep(30)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "--now":
            # Legacy support for --now: run a general health check goal
            AgentOrchestrator().run("Perform a general health check of all system metrics.")
        elif sys.argv[1] == "--listen":
            listen_telegram()
    else:
        listen_telegram()
