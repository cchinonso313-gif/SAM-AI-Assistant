import json

import pytest

from backend.agent.agent import Agent, _extract_json
from backend.agent.tool_registry import ToolRegistry


class ScriptedRouter:
    """Router stub that returns a preset sequence of responses."""

    def __init__(self, responses):
        self._responses = list(responses)
        self.prompts = []

    async def generate(self, prompt, preferred=None):
        self.prompts.append(prompt)
        return self._responses.pop(0) if self._responses else None


def make_registry():
    reg = ToolRegistry()
    reg.register("write_note", "write a note", lambda text: f"noted:{text}", {"text": "t"})
    return reg


class TestExtractJson:
    def test_plain_json(self):
        assert _extract_json('{"a": 1}') == {"a": 1}

    def test_fenced_json(self):
        assert _extract_json('```json\n{"a": 2}\n```') == {"a": 2}

    def test_embedded_json(self):
        assert _extract_json('sure! {"a": 3} done') == {"a": 3}

    def test_unparseable(self):
        assert _extract_json("no json here") is None

    def test_empty(self):
        assert _extract_json("") is None


class TestAgent:
    @pytest.mark.asyncio
    async def test_finish_immediately(self):
        router = ScriptedRouter([json.dumps({"action": "finish", "final_answer": "done"})])
        agent = Agent(router, make_registry())

        result = await agent.run("do nothing")

        assert result.completed is True
        assert result.final_answer == "done"
        assert result.steps == []

    @pytest.mark.asyncio
    async def test_executes_tool_then_finishes(self):
        router = ScriptedRouter([
            json.dumps({"thought": "note it", "action": "write_note", "args": {"text": "hi"}}),
            json.dumps({"action": "finish", "final_answer": "all set"}),
        ])
        agent = Agent(router, make_registry())

        result = await agent.run("take a note")

        assert result.final_answer == "all set"
        assert len(result.steps) == 1
        assert result.steps[0].observation == "noted:hi"

    @pytest.mark.asyncio
    async def test_unparseable_then_finish(self):
        router = ScriptedRouter([
            "garbage not json",
            json.dumps({"action": "finish", "final_answer": "ok"}),
        ])
        agent = Agent(router, make_registry())

        result = await agent.run("goal")

        assert result.completed is True
        assert len(result.steps) == 1
        assert "parse" in result.steps[0].observation.lower()

    @pytest.mark.asyncio
    async def test_hits_max_steps(self):
        # Always asks to run a tool, never finishes.
        never_finish = json.dumps({"action": "write_note", "args": {"text": "x"}})
        router = ScriptedRouter([never_finish] * 10)
        agent = Agent(router, make_registry(), max_steps=3)

        result = await agent.run("loop")

        assert result.completed is False
        assert len(result.steps) == 3

    @pytest.mark.asyncio
    async def test_unknown_tool_observation(self):
        router = ScriptedRouter([
            json.dumps({"action": "no_such_tool", "args": {}}),
            json.dumps({"action": "finish", "final_answer": "x"}),
        ])
        agent = Agent(router, make_registry())

        result = await agent.run("goal")

        assert "Unknown tool" in result.steps[0].observation


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
