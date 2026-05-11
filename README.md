# Betty Judge

## Quick Start
1. Create and activate a virtual environment.
 ### https://docs.astral.sh/uv/getting-started/installation/
## Windows
```bash
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```
## macOS and Linux
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

2. Install dependencies with uv:

```bash
uv sync
```

3. Create a .env file in the project root:

```env
DATABASE_URL=postgresql+psycopg2://user:pass@localhost:5432/betty_judge
```

## run main project

```bash
uv run main.py
```