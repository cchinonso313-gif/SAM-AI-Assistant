import json
import logging
import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from backend.agent.tool_registry import ToolRegistry

logger = logging.getLogger(__name__)

_JSON_BLOCK = re.compile(r"\{.*\}", re.DOTALL)

SYSTEM_PROMPT = """You are {name}, an autonomous AI assistant that accomplishes \
tasks on the user's computer by reasoning step by step and calling tools.

Available tools:
{tools}

Respond with a SINGLE JSON object and nothing else, using this schema:
{{"thought": "brief reasoning",
  "action": "<tool name> or finish",
  "args": {{ ... tool arguments ... }},
  "final_answer": "<answer, only when action is finish>"}}

Rules:
- Use one tool per step. Inspect the observation before the next step.
- When the task is complete, set "action" to "finish" and put the result in
  "final_answer".
- Never attempt to bypass security, access systems you are not authorized to
  use, or run destructive commands.
"""


@dataclass
class AgentStep:
    thought: str
    action: str
    args: Dict[str, Any]
    observation: str = ""


@dataclass
class AgentResult:
    goal: str
    final_answer: str
    steps: List[AgentStep] = field(default_factory=list)
    completed: bool = True


def _extract_json(text: str) -> Optional[Dict[str, Any]]:
    """Best-effort extraction of a JSON object from an LLM response."""
    if not text:
        return None
    cleaned = text.strip()
    # Strip markdown code fences if present.
    if cleaned.startswith("```"):
        cleaned = cleaned.strip("`")
        cleaned = cleaned.split("\n", 1)[-1] if "\n" in cleaned else cleaned
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass
    match = _JSON_BLOCK.search(cleaned)
    if match:
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError:
            return None
    return None


class Agent:
    """Plan -> act -> observe -> reflect loop over a tool registry."""

    def __init__(self, router, registry: ToolRegistry, name: str = "NOVA", max_steps: int = 8):
        self.router = router
        self.registry = registry
        self.name = name
        self.max_steps = max_steps

    def _build_prompt(self, goal: str, steps: List[AgentStep], context: Optional[str]) -> str:
        prompt = SYSTEM_PROMPT.format(name=self.name, tools=self.registry.describe())
        if context:
            prompt += f"\nContext:\n{context}\n"
        prompt += f"\nTask: {goal}\n"
        if steps:
            prompt += "\nHistory:\n"
            for i, step in enumerate(steps, 1):
                prompt += (
                    f"Step {i}: thought={step.thought} action={step.action} "
                    f"args={json.dumps(step.args)}\nobservation={step.observation}\n"
                )
        prompt += "\nRespond with the next JSON action."
        return prompt

    async def run(self, goal: str, context: Optional[str] = None) -> AgentResult:
        steps: List[AgentStep] = []

        for _ in range(self.max_steps):
            prompt = self._build_prompt(goal, steps, context)
            raw = await self.router.generate(prompt)
            decision = _extract_json(raw or "")

            if decision is None:
                steps.append(
                    AgentStep(
                        thought="(unparseable response)",
                        action="none",
                        args={},
                        observation="Could not parse a JSON action; retrying.",
                    )
                )
                continue

            action = str(decision.get("action", "")).strip()
            thought = str(decision.get("thought", ""))
            args = decision.get("args") or {}

            if action in ("finish", "done", ""):
                return AgentResult(
                    goal=goal,
                    final_answer=str(decision.get("final_answer", "")),
                    steps=steps,
                    completed=True,
                )

            result = await self.registry.execute(action, args)
            step = AgentStep(
                thought=thought,
                action=action,
                args=args,
                observation=result.to_observation(),
            )
            steps.append(step)

        logger.warning("⚠️ Agent hit max steps without finishing")
        return AgentResult(
            goal=goal,
            final_answer="Reached the step limit before completing the task.",
            steps=steps,
            completed=False,
        )
