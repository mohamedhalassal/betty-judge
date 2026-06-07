import os
import sys
from pathlib import Path

import click
from dotenv import load_dotenv
from sqlmodel import SQLModel, create_engine


REPO_DIR = Path(__file__).resolve().parents[2]
BACKEND_DIR = REPO_DIR / "backend"
TEST_SCHEMA_DIR = REPO_DIR / "test_schema"

load_dotenv(BACKEND_DIR / ".env")
sys.path.insert(0, str(TEST_SCHEMA_DIR))

import models  # noqa: F401


DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise click.ClickException("DATABASE_URL must be set in backend/.env")
DATABASE_URL = DATABASE_URL.strip().strip('"').strip("'").replace("\\&", "&")


@click.command()
def create_schema():
    """Create database tables from test_schema models."""
    engine = create_engine(DATABASE_URL)
    SQLModel.metadata.create_all(engine)
    click.echo("Created tables from test_schema models.")


if __name__ == "__main__":
    create_schema()
