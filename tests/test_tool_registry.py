import pytest

from backend.agent.tool_registry import Tool, ToolRegistry, ToolResult


class TestToolResult:
    def test_success_observation(self):
        assert ToolResult(True, "done").to_observation() == "done"

    def test_error_observation(self):
        assert "ERROR" in ToolResult(False, "", error="nope").to_observation()


class TestTool:
    @pytest.mark.asyncio
    async def test_sync_func_wrapped(self):
        tool = Tool("echo", "echo", lambda text: text)
        result = await tool(text="hi")
        assert result.success and result.output == "hi"

    @pytest.mark.asyncio
    async def test_async_func_awaited(self):
        async def afunc(x):
            return x * 2

        tool = Tool("double", "double", afunc)
        result = await tool(x="ab")
        assert result.output == "abab"

    @pytest.mark.asyncio
    async def test_toolresult_passthrough(self):
        tool = Tool("t", "t", lambda: ToolResult(True, "raw"))
        assert (await tool()).output == "raw"

    @pytest.mark.asyncio
    async def test_exception_captured(self):
        def boom():
            raise ValueError("bad")

        tool = Tool("boom", "boom", boom)
        result = await tool()
        assert result.success is False
        assert "bad" in result.error


class TestToolRegistry:
    def test_register_and_lookup(self):
        reg = ToolRegistry()
        reg.register("a", "desc a", lambda: "x", {"p": "param"})
        assert "a" in reg
        assert reg.names() == ["a"]
        assert len(reg) == 1

    def test_describe_includes_params(self):
        reg = ToolRegistry()
        reg.register("a", "does a", lambda: "x", {"p": "the param"})
        text = reg.describe()
        assert "a: does a" in text
        assert "p (the param)" in text

    @pytest.mark.asyncio
    async def test_execute_unknown_tool(self):
        reg = ToolRegistry()
        result = await reg.execute("missing", {})
        assert result.success is False
        assert "Unknown tool" in result.error

    @pytest.mark.asyncio
    async def test_execute_known_tool(self):
        reg = ToolRegistry()
        reg.register("greet", "greet", lambda name: f"hi {name}", {"name": "n"})
        result = await reg.execute("greet", {"name": "nova"})
        assert result.output == "hi nova"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
