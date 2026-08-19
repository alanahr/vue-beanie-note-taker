"""Application settings loaded from environment variables.

Uses ``pydantic-settings`` to read configuration from a ``.env`` file or
environment variables. A module-level ``settings`` singleton is instantiated
on import so other modules can simply ``from app.config import settings``.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Strongly-typed application configuration.

    All fields are required (no defaults) unless explicitly noted.
    Values are read from a ``.env`` file in the server directory or from
    the process environment.

    Attributes:
        mongo_data_url: Connection string for the primary (data) MongoDB.
        mongo_data_db: Database name for document and comment storage.
        mongo_rag_url: Connection string for the RAG MongoDB.
        mongo_rag_db: Database name for vector embeddings.
        server_host: Host address the API binds to.
        server_port: Port the API listens on.
        embedding_model_name: Hugging Face model ID for embedding generation.
        cors_origins: Comma-separated list of allowed CORS origins.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Primary MongoDB (data storage)
    mongo_data_url: str
    mongo_data_db: str

    # RAG MongoDB (vector search)
    mongo_rag_url: str
    mongo_rag_db: str

    # Server
    server_host: str
    server_port: int

    # Embedding model
    embedding_model_name: str

    # CORS
    cors_origins: str = "*"


settings = Settings()
