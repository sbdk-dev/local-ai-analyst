# Contributing to Claude-Analyst

First off, thank you for considering contributing to Claude-Analyst! 🎉

It's people like you that make Claude-Analyst such a great tool for AI-powered data analysis.

## Code of Conduct

This project and everyone participating in it is governed by our [Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code.

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check the existing issues to avoid duplicates. When you create a bug report, include as many details as possible:

- **Use a clear and descriptive title**
- **Describe the exact steps to reproduce the problem**
- **Provide specific examples** (code snippets, data samples, etc.)
- **Describe the behavior you observed** and what you expected
- **Include your environment details** (OS, Python version, etc.)

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion, include:

- **Use a clear and descriptive title**
- **Provide a detailed description** of the suggested enhancement
- **Explain why this enhancement would be useful**
- **Include examples** of how it would work

### Pull Requests

1. **Fork the repo** and create your branch from `main`
2. **Follow the coding style** used in the project
3. **Add tests** if you've added code that should be tested
4. **Ensure the test suite passes** (`uv run python test_all_functionality.py`)
5. **Update documentation** as needed
6. **Write clear commit messages**
7. **Submit your pull request**!

## Development Setup

### Prerequisites

- Python 3.10+
- [uv](https://github.com/astral-sh/uv) package manager

### Setup Steps

```bash
# 1. Clone your fork
git clone https://github.com/YOUR_USERNAME/claude-analyst.git
cd claude-analyst

# 2. Run setup script
./scripts/setup.sh

# 3. Create a branch for your feature
git checkout -b feature/my-new-feature

# 4. Make your changes
# ...

# 5. Run tests
cd semantic-layer
uv run python test_all_functionality.py

# 6. Commit and push
git add .
git commit -m "Add my new feature"
git push origin feature/my-new-feature

# 7. Open a Pull Request on GitHub
```

## Development Guidelines

### Code Style

- **Python**: Follow PEP 8 style guide
- **Docstrings**: Use Google-style docstrings
- **Type hints**: Use type annotations where possible
- **Line length**: Max 100 characters (soft limit, can exceed for readability)

Example:

```python
async def query_model(
    model_name: str,
    dimensions: List[str],
    measures: List[str],
    filters: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Query a semantic model with specified dimensions and measures.

    Args:
        model_name: Name of the semantic model to query
        dimensions: List of dimension names to group by
        measures: List of measure names to calculate
        filters: Optional dictionary of filter conditions

    Returns:
        Dictionary containing query results and metadata

    Raises:
        ValueError: If model_name is not found
    """
    # Implementation...
```

### Testing

- **Write tests** for all new features
- **Maintain 100% pass rate** - all tests must pass before merging
- **Test files**: Place in `semantic-layer/tests/`
- **Test naming**: `test_<feature>_<behavior>.py`

Example test:

```python
import pytest
from mcp_server.semantic_layer_integration import SemanticLayerManager

@pytest.mark.asyncio
async def test_query_model_returns_data():
    """Test that querying a model returns valid data"""
    manager = SemanticLayerManager()
    await manager.initialize()

    result = await manager.build_and_execute_query(
        model_name="users",
        dimensions=[],
        measures=["total_users"],
    )

    assert result["status"] == "success"
    assert "data" in result
    assert len(result["data"]) > 0
```

### Documentation

- **Update README.md** if you change functionality
- **Add docstrings** to all public functions/classes
- **Update docs/** if you add features
- **Add examples** for new features in `examples/`

### Commit Messages

Use clear, descriptive commit messages:

```
feat: Add SQL validation layer

- Implement dry-run validation using EXPLAIN
- Add complexity scoring algorithm
- Add result size estimation
- Update documentation

Closes #123
```

Commit types:
- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation changes
- `test:` - Test additions/changes
- `refactor:` - Code refactoring
- `perf:` - Performance improvements
- `chore:` - Maintenance tasks

## Project Structure

```
claude-analyst/
├── semantic-layer/          # Main implementation
│   ├── mcp_server/         # Server components
│   │   ├── server.py       # MCP server (Claude Desktop)
│   │   ├── openai_server.py # OpenAI API server (ChatGPT)
│   │   └── ...             # Other components
│   ├── models/             # Semantic models (YAML)
│   ├── data/               # DuckDB database
│   ├── docs/               # User documentation
│   └── tests/              # Test suite
├── scripts/                # Setup and utility scripts
├── examples/               # Usage examples
├── CLAUDE.md               # Complete specification
└── README.md               # This file
```

## Areas for Contribution

We especially welcome contributions in these areas:

### High Priority
- 🌐 **Multi-database support** (Postgres, BigQuery, Snowflake)
- 📊 **Visualization layer** (charts and graphs)
- 🎨 **Web UI** for configuration and management
- 📱 **Mobile-friendly** interfaces
- 🐳 **Docker deployment** configurations

### Medium Priority
- 📚 **More examples** and use cases
- 🔧 **Additional workflow templates**
- 🧪 **More comprehensive tests**
- 📖 **Better documentation**
- 🌍 **Internationalization** (i18n)

### Good First Issues

Look for issues tagged with `good first issue` - these are great for newcomers!

## Getting Help

- 💬 **GitHub Discussions**: Ask questions and share ideas
- 🐛 **GitHub Issues**: Report bugs and request features
- 📖 **Documentation**: Check the [docs](semantic-layer/docs/) folder

## Recognition

Contributors will be:
- Listed in our [Contributors](https://github.com/YOUR_USERNAME/claude-analyst/graphs/contributors) page
- Mentioned in release notes for significant contributions
- Given credit in documentation where appropriate

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

**Thank you for contributing to Claude-Analyst!** 🚀

Your contributions help make AI-powered data analysis better for everyone.
