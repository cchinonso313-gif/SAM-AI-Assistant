import json
from unittest.mock import MagicMock, patch

import pytest

from backend.agent.safety import is_command_safe
from backend.agent.tools import build_default_registry
from backend.agent.tools import file_tools, project_tools, shell_tools, system_tools, web_tools


class TestSafety:
    def test_safe_command(self):
        ok, reason = is_command_safe("echo hello")
        assert ok and reason == ""

    def test_blocked_keyword(self):
        ok, reason = is_command_safe("please hack the server")
        assert ok is False
        assert "blocked keyword" in reason

    def test_dangerous_pattern(self):
        ok, reason = is_command_safe("rm -rf /")
        assert ok is False
        assert "dangerous pattern" in reason


class TestFileTools:
    def test_write_read_roundtrip(self, tmp_path):
        target = tmp_path / "sub" / "file.txt"
        w = file_tools.write_file(str(target), "hello")
        assert w.success
        r = file_tools.read_file(str(target))
        assert r.output == "hello"

    def test_append(self, tmp_path):
        target = tmp_path / "f.txt"
        file_tools.write_file(str(target), "a")
        file_tools.append_file(str(target), "b")
        assert file_tools.read_file(str(target)).output == "ab"

    def test_read_missing(self, tmp_path):
        r = file_tools.read_file(str(tmp_path / "nope.txt"))
        assert r.success is False

    def test_list_and_make_dir(self, tmp_path):
        d = tmp_path / "d"
        assert project_tools  # ensure import used
        mk = file_tools.make_dir(str(d))
        assert mk.success
        (d / "x.txt").write_text("1")
        listing = file_tools.list_dir(str(d))
        assert "x.txt" in listing.output

    def test_list_dir_not_a_dir(self, tmp_path):
        f = tmp_path / "f.txt"
        f.write_text("1")
        assert file_tools.list_dir(str(f)).success is False


class TestProjectTools:
    def test_scaffold_from_dict(self, tmp_path):
        root = tmp_path / "site"
        result = project_tools.scaffold_project(
            str(root), {"index.html": "<h1>hi</h1>", "css/app.css": "body{}"}
        )
        assert result.success
        assert (root / "index.html").read_text() == "<h1>hi</h1>"
        assert (root / "css" / "app.css").exists()

    def test_scaffold_from_json_string(self, tmp_path):
        root = tmp_path / "app"
        payload = json.dumps({"main.py": "print(1)"})
        result = project_tools.scaffold_project(str(root), payload)
        assert result.success
        assert (root / "main.py").exists()

    def test_scaffold_invalid_json(self, tmp_path):
        result = project_tools.scaffold_project(str(tmp_path), "{not json}")
        assert result.success is False

    def test_scaffold_empty(self, tmp_path):
        result = project_tools.scaffold_project(str(tmp_path), {})
        assert result.success is False


class TestShellTools:
    def test_run_shell_success(self):
        result = shell_tools.run_shell("echo nova")
        assert result.success
        assert "nova" in result.output

    def test_run_shell_refuses_dangerous(self):
        result = shell_tools.run_shell("rm -rf /tmp/whatever")
        assert result.success is False
        assert "Refused" in result.error

    def test_run_shell_nonzero_exit(self):
        result = shell_tools.run_shell("exit 3")
        assert result.success is False
        assert "exit code 3" in result.error


class TestSystemTools:
    def test_system_info(self):
        result = system_tools.system_info()
        assert result.success
        assert "os:" in result.output


class TestWebTools:
    def test_web_fetch_rejects_bad_scheme(self):
        result = web_tools.web_fetch("ftp://example.com")
        assert result.success is False

    def test_web_fetch_mocked(self):
        fake_resp = MagicMock()
        fake_resp.ok = True
        fake_resp.status_code = 200
        fake_resp.text = "hello world"
        with patch("requests.get", return_value=fake_resp):
            result = web_tools.web_fetch("https://example.com")
        assert result.success
        assert "hello world" in result.output

    def test_web_search_mocked(self):
        html_body = (
            '<a class="result__a" href="/l/?uddg=https%3A%2F%2Fexample.com%2Fa">'
            "First Result</a>"
            '<a class="result__a" href="/l/?uddg=https%3A%2F%2Fexample.com%2Fb">'
            "Second Result</a>"
        )
        fake_resp = MagicMock()
        fake_resp.text = html_body
        with patch("requests.post", return_value=fake_resp):
            result = web_tools.web_search("example", max_results=1)
        assert result.success
        assert "First Result" in result.output
        assert "https://example.com/a" in result.output
        assert "Second Result" not in result.output


class TestDefaultRegistry:
    def test_all_tools_registered(self):
        reg = build_default_registry()
        for name in [
            "read_file",
            "write_file",
            "append_file",
            "list_dir",
            "make_dir",
            "scaffold_project",
            "run_shell",
            "system_info",
            "web_fetch",
            "web_search",
            "run_python",
            "screenshot",
            "move_mouse",
            "type_text",
            "copy_to_clipboard",
        ]:
            assert name in reg


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
