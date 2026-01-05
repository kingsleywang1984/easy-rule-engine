## Release guide (TestPyPI -> PyPI)

This project is published to PyPI as **easy-rule-engine** and imported as **easy_rule_engine**.

### 0) Prerequisites

- Create accounts on PyPI and TestPyPI
- Prefer **Trusted Publishing** (recommended) or create an API token for uploads

### 1) Build artifacts locally

In a clean environment:

```bash
python -m pip install -U build
python -m build
```

Artifacts will be in `dist/` (`.whl` and `.tar.gz`).

### 2) Upload to TestPyPI (recommended)

```bash
python -m pip install -U twine
twine upload --repository testpypi dist/*
```

Install from TestPyPI:

```bash
python -m pip install -i https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ easy-rule-engine
```

### 3) Upload to PyPI

```bash
twine upload dist/*
```

### 4) Verify install

```bash
python -c "import easy_rule_engine; print(easy_rule_engine.RuleEngine)"
```


