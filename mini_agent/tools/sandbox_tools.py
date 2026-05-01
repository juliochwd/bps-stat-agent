"""Sandbox execution tools for safe Python code execution.

Provides:
- python_repl: Execute Python code in a sandboxed environment
  with support for local subprocess, Docker, and E2B backends.
"""

from __future__ import annotations

import asyncio
import os
import sys
import tempfile
from pathlib import Path
from typing import Any

from .base import Tool, ToolResult

# ---------------------------------------------------------------------------
# Optional dependency flags
# ---------------------------------------------------------------------------

_HAS_DOCKER = False
try:
    import docker  # noqa: F401

    _HAS_DOCKER = True
except ImportError:
    pass

_HAS_E2B = False
try:
    from e2b_code_interpreter import CodeInterpreter  # noqa: F401

    _HAS_E2B = True
except ImportError:
    pass


# ===================================================================
# PythonREPLTool
# ===================================================================


class PythonREPLTool(Tool):
    """Execute Python code in a sandboxed environment.

    Supports three execution backends:
    - **local**: Uses subprocess with timeout (default, always available)
    - **docker**: Uses Docker SDK for isolated container execution
    - **e2b**: Uses E2B Code Interpreter for cloud sandboxing

    Captures stdout, stderr, and any generated files.
    """

    def __init__(self, workspace_dir: str = "./workspace") -> None:
        self._workspace_dir = workspace_dir

    @property
    def name(self) -> str:
        return "python_repl"

    @property
    def description(self) -> str:
        return (
            "Execute Python code in a sandboxed environment. Supports "
            "local subprocess (with timeout), Docker container, or E2B "
            "cloud sandbox. Captures stdout, stderr, and generated files. "
            "Use for data analysis, visualization, and computation."
        )

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "code": {
                    "type": "string",
                    "description": "Python code to execute",
                },
                "timeout": {
                    "type": "integer",
                    "description": "Execution timeout in seconds (default: 30)",
                },
                "sandbox_type": {
                    "type": "string",
                    "enum": ["local", "docker", "e2b"],
                    "description": "Sandbox backend to use (default: local)",
                },
            },
            "required": ["code"],
        }

    async def execute(
        self,
        code: str,
        timeout: int = 30,
        sandbox_type: str = "local",
        **kwargs: Any,
    ) -> ToolResult:
        """Execute Python code in the specified sandbox."""
        if not code.strip():
            return ToolResult(success=False, error="No code provided")

        if sandbox_type == "docker":
            if not _HAS_DOCKER:
                return ToolResult(
                    success=False,
                    error="Package docker not installed. Run: pip install docker",
                )
            return await self._execute_docker(code, timeout)
        elif sandbox_type == "e2b":
            if not _HAS_E2B:
                return ToolResult(
                    success=False,
                    error="Package e2b-code-interpreter not installed. Run: pip install e2b-code-interpreter",
                )
            return await self._execute_e2b(code, timeout)
        else:
            return await self._execute_local(code, timeout)

    async def _execute_local(self, code: str, timeout: int) -> ToolResult:
        """Execute code in a local subprocess with timeout."""
        workspace = Path(self._workspace_dir)
        workspace.mkdir(parents=True, exist_ok=True)

        # Write code to a temporary file
        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".py",
            dir=str(workspace),
            delete=False,
            encoding="utf-8",
        ) as tmp:
            tmp.write(code)
            tmp_path = tmp.name

        try:
            # Execute in subprocess
            env = os.environ.copy()
            env["PYTHONPATH"] = str(workspace)

            process = await asyncio.create_subprocess_exec(
                sys.executable,
                tmp_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=str(workspace),
                env=env,
            )

            try:
                stdout_bytes, stderr_bytes = await asyncio.wait_for(process.communicate(), timeout=timeout)
            except TimeoutError:
                process.kill()
                await process.communicate()
                return ToolResult(
                    success=False,
                    error=f"Execution timed out after {timeout} seconds",
                )

            stdout = stdout_bytes.decode("utf-8", errors="replace")
            stderr = stderr_bytes.decode("utf-8", errors="replace")
            return_code = process.returncode

            # Check for generated files (new files in workspace)
            generated_files: list[str] = []
            for f in workspace.iterdir():
                if f.is_file() and f.name != Path(tmp_path).name:
                    if f.suffix in {".png", ".pdf", ".csv", ".xlsx", ".html", ".json"}:
                        generated_files.append(f.name)

            result_parts: list[str] = []
            if stdout:
                result_parts.append(f"**stdout:**\n```\n{stdout[:5000]}\n```")
            if stderr:
                result_parts.append(f"**stderr:**\n```\n{stderr[:2000]}\n```")
            if generated_files:
                result_parts.append(f"**Generated files:** {', '.join(generated_files)}")
            if return_code != 0:
                result_parts.append(f"**Exit code:** {return_code}")

            content = "\n\n".join(result_parts) if result_parts else "(no output)"

            return ToolResult(
                success=(return_code == 0),
                content=content,
                error=stderr[:500] if return_code != 0 else None,
            )

        finally:
            # Clean up temp file
            try:
                os.unlink(tmp_path)
            except OSError:
                pass

    async def _execute_docker(self, code: str, timeout: int) -> ToolResult:
        """Execute code in a Docker container."""
        import docker

        workspace = Path(self._workspace_dir)
        workspace.mkdir(parents=True, exist_ok=True)

        # Write code to workspace for mounting
        code_file = workspace / "_sandbox_code.py"
        code_file.write_text(code, encoding="utf-8")

        try:
            client = docker.from_env()

            # Run in a Python container with workspace mounted
            container = client.containers.run(
                image="python:3.11-slim",
                command=["python", "/workspace/_sandbox_code.py"],
                volumes={str(workspace.resolve()): {"bind": "/workspace", "mode": "rw"}},
                working_dir="/workspace",
                detach=True,
                mem_limit="512m",
                cpu_period=100000,
                cpu_quota=50000,
                network_disabled=True,
            )

            # Wait for completion with timeout
            try:
                result = container.wait(timeout=timeout)
                exit_code = result.get("StatusCode", -1)
            except Exception:
                container.kill()
                return ToolResult(
                    success=False,
                    error=f"Docker execution timed out after {timeout} seconds",
                )

            stdout = container.logs(stdout=True, stderr=False).decode("utf-8", errors="replace")
            stderr = container.logs(stdout=False, stderr=True).decode("utf-8", errors="replace")

            container.remove(force=True)

            result_parts: list[str] = []
            if stdout:
                result_parts.append(f"**stdout:**\n```\n{stdout[:5000]}\n```")
            if stderr:
                result_parts.append(f"**stderr:**\n```\n{stderr[:2000]}\n```")

            content = "\n\n".join(result_parts) if result_parts else "(no output)"

            return ToolResult(
                success=(exit_code == 0),
                content=content,
                error=stderr[:500] if exit_code != 0 else None,
            )

        except docker.errors.DockerException as e:
            return ToolResult(success=False, error=f"Docker execution failed: {e}")
        finally:
            try:
                code_file.unlink()
            except OSError:
                pass

    async def _execute_e2b(self, code: str, timeout: int) -> ToolResult:
        """Execute code using E2B Code Interpreter."""
        from e2b_code_interpreter import CodeInterpreter

        api_key = os.environ.get("E2B_API_KEY", "")
        if not api_key:
            return ToolResult(
                success=False,
                error="E2B_API_KEY environment variable not set. Get one at https://e2b.dev",
            )

        try:
            with CodeInterpreter(api_key=api_key) as sandbox:
                execution = sandbox.notebook.exec_cell(
                    code,
                    timeout=timeout,
                )

                stdout = execution.logs.stdout if hasattr(execution.logs, "stdout") else ""
                stderr = execution.logs.stderr if hasattr(execution.logs, "stderr") else ""
                error_msg = str(execution.error) if execution.error else ""

                result_parts: list[str] = []
                if stdout:
                    stdout_text = "\n".join(stdout) if isinstance(stdout, list) else str(stdout)
                    result_parts.append(f"**stdout:**\n```\n{stdout_text[:5000]}\n```")
                if stderr:
                    stderr_text = "\n".join(stderr) if isinstance(stderr, list) else str(stderr)
                    result_parts.append(f"**stderr:**\n```\n{stderr_text[:2000]}\n```")

                # Check for results (plots, dataframes, etc.)
                if execution.results:
                    for r in execution.results:
                        if hasattr(r, "png") and r.png:
                            result_parts.append("**Generated:** plot (PNG)")
                        elif hasattr(r, "text") and r.text:
                            result_parts.append(f"**Result:**\n```\n{r.text[:2000]}\n```")

                content = "\n\n".join(result_parts) if result_parts else "(no output)"

                return ToolResult(
                    success=(not execution.error),
                    content=content,
                    error=error_msg[:500] if error_msg else None,
                )

        except Exception as e:
            return ToolResult(success=False, error=f"E2B execution failed: {e}")
