# Contributing Guide

Thank you for your interest in the BPS Stat Agent project! We welcome contributions of all forms.

## How to Contribute

### Reporting Bugs

If you find a bug, please create an Issue and include the following information:

- **Problem Description**: A clear description of the problem.
- **Steps to Reproduce**: Detailed steps to reproduce the issue.
- **Expected Behavior**: What you expected to happen.
- **Actual Behavior**: What actually happened.
- **Environment Information**:
  - Python version
  - Operating system
  - Versions of relevant dependencies

### Suggesting New Features

If you have an idea for a new feature, please create an Issue first to discuss it:

- Describe the purpose and value of the feature.
- Explain the intended use case.
- Provide a design proposal if possible.

### Submitting Code

#### Getting Started

1. Fork this repository.
2. Clone your fork:
   ```bash
   git clone https://github.com/juliochwd/bps-stat-agent.git
   cd bps-stat-agent
   make install-dev    # Install all dependencies + Playwright
   bpsagent setup      # Configure API keys
   ```

3. Create a new branch:
   ```bash
   git checkout -b feature/your-feature-name
   # or
   git checkout -b fix/your-bug-fix
   ```

4. Install development dependencies:
   ```bash
   uv sync --frozen --group dev
   ```

#### Development Process

1. **Write Code**
   - Follow the project's code style (see the [Development Guide](docs/DEVELOPMENT_GUIDE.md#code-style-guide)).
   - Add necessary comments and docstrings.
   - Keep your code clean and concise.

2. **Add Tests**
   - Add test cases for new features.
   - Ensure all tests pass:
     ```bash
     make test              # Unit tests (excludes live/network tests)
     make test-live         # BPS integration tests (requires BPS_API_KEY)
     make test-all          # All tests (unit + live)
     ```

3. **Update Documentation**
   - If you add a new feature, update the README or relevant documentation.
   - Keep documentation in sync with your code.

4. **Commit Changes**
   - Use clear commit messages:
     ```bash
     git commit -m "feat(tools): Add new file search tool"
     # or
     git commit -m "fix(agent): Fix error handling for tool calls"
     ```
   
   - Commit message format:
     - `feat`: A new feature
     - `fix`: A bug fix
     - `docs`: Documentation updates
     - `style`: Code style adjustments
     - `refactor`: Code refactoring
     - `test`: Test-related changes
     - `chore`: Build or auxiliary tools

5. **Push to Your Fork**
   ```bash
   git push origin feature/your-feature-name
   ```

6. **Create a Pull Request**
   - Create a Pull Request on GitHub.
   - Clearly describe your changes.
   - Reference any related Issues if applicable.

#### Pull Request Checklist

Before submitting a PR, run the quality gate and formatter:

```bash
make format          # Auto-format code
make check           # Run lint + tests — must pass before submitting
```

Please ensure:

- [ ] `make check` passes (lint + tests).
- [ ] The code follows the project's style guide.
- [ ] Necessary tests have been added.
- [ ] Relevant documentation has been updated.
- [ ] The commit message is clear and concise.
- [ ] There are no unrelated changes.

### Code Review

All Pull Requests will be reviewed:

- We will review your code as soon as possible.
- We may request some changes.
- Please be patient and responsive to feedback.
- Once approved, your PR will be merged into the main branch.


### Research Module Contributions

When contributing to the research module (`mini_agent/research/`):

- **New tools**: Create in `mini_agent/tools/`, register in `phase_manager.py` PHASE_TOOLS, add to `cli.py`
- **Phase changes**: Update `constants.py` and ensure max 15 tools per phase
- **Sub-agents**: Add config in `sub_agents.py` AGENT_CONFIGS and prompt in `config/system_prompts/`
- **MCP servers**: Add to `setup_wizard.py` `_write_mcp_json()` and `config/mcp-research.json`
- **Optional deps**: Use try/except with graceful degradation (return helpful ToolResult error)

## Code Style Guide

### Python Code Style

Follow PEP 8 and the Google Python Style Guide:

```python
# Good example ✅
class MyClass:
    """A brief description of the class.
    
    A more detailed description...
    """
    
    def my_method(self, param1: str, param2: int = 10) -> str:
        """A brief description of the method.
        
        Args:
            param1: Description of parameter 1.
            param2: Description of parameter 2.
        
        Returns:
            Description of the return value.
        """
        pass

# Bad example ❌
class myclass:  # Class names should be PascalCase
    def MyMethod(self,param1,param2=10):  # Method names should be snake_case
        pass  # Missing docstring
```

### Type Hinting

Use Python type hints:

```python
from typing import Any

async def process_messages(
    messages: list[dict[str, Any]],
    max_tokens: int | None = None
) -> str:
    """Process a list of messages."""
    pass
```

### Testing

- Write tests for new features.
- Keep tests simple and clear.
- Ensure tests cover critical paths.

```python
import pytest
from mini_agent.tools.my_tool import MyTool

@pytest.mark.asyncio
async def test_my_tool():
    """Test the custom tool."""
    tool = MyTool()
    result = await tool.execute(param="test")
    assert result.success
    assert "expected" in result.content
```

## Community Guidelines

Please follow our [Code of Conduct](CODE_OF_CONDUCT.md) and be friendly and respectful.

## Questions and Help

If you have any questions:

- Check the [README](README.md) and [documentation](docs/).
- Search existing Issues.
- Create a new Issue to ask a question.

## License

By contributing, you agree that your contributions will be licensed under the [MIT License](LICENSE).

---

Thank you again for your contribution! 🎉
