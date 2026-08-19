"""The ``app`` package contains the FastAPI back-end for the Tiptap editor.

Modules:
    config: Application settings loaded from environment variables.
    database: MongoDB connection initialisation via Beanie.
    main: FastAPI app creation, middleware, and router registration.
    models: Beanie ODM document models for MongoDB collections.
    routers: FastAPI API routers for documents, comments, and RAG.
    services: Helper services such as the embedding model wrapper.
"""
