import pytest

from backend.agent.tools import code_tools


def test_run_python_success():
    result = code_tools.run_python("print(2 + 3)")
    assert result.success
    assert "5" in result.output


def test_run_python_no_output():
    result = code_tools.run_python("x = 1")
    assert result.success
    assert result.output == "(no output)"


def test_run_python_error():
    result = code_tools.run_python("raise ValueError('boom')")
    assert result.success is False
    assert "ValueError" in result.error


def test_run_python_timeout():
    result = code_tools.run_python("import time; time.sleep(5)", timeout=1)
    assert result.success is False
    assert "Timed out" in result.error


def test_run_python_refuses_dangerous():
    result = code_tools.run_python("import os; os.system('rm -rf /')")
    assert result.success is False
    assert "Refused" in result.error


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
