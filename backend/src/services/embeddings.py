"""
Google Generative AI embeddings service.

Generates embeddings for text chunks using Google's Generative AI API.
"""

import google.generativeai as genai
from typing import List
import asyncio
import logging
from ..config import Settings

logger = logging.getLogger(__name__)

# Load settings
settings = Settings()


class EmbeddingService:
    """Service for generating text embeddings using Google Generative AI."""

    def __init__(self):
        """Initialize Google Generative AI client with API key."""
        logger.info("Initializing Google Generative AI embeddings")
        genai.configure(api_key=settings.gemini_api_key)
        self.embedding_dim = 768  # Google's embedding dimension
        logger.info(f"Google Generative AI initialized. Embedding dimension: {self.embedding_dim}")

    async def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for a single text.

        Args:
            text: Input text

        Returns:
            Embedding vector (768 dimensions)
        """
        try:
            # Run embedding generation in executor since API calls are I/O-bound
            loop = asyncio.get_event_loop()
            embedding = await loop.run_in_executor(
                None,
                lambda: genai.embed_content(model="models/embedding-001", content=text)
            )
            return embedding['embedding']

        except Exception as e:
            logger.error(f"Failed to generate embedding: {str(e)}")
            raise

    async def generate_embeddings_batch(
        self,
        texts: List[str],
        batch_size: int = 100
    ) -> List[List[float]]:
        """
        Generate embeddings for multiple texts in batches.

        Google's API supports batch processing efficiently.

        Args:
            texts: List of input texts
            batch_size: Number of texts to process at once (default: 100)

        Returns:
            List of embedding vectors
        """
        all_embeddings = []

        try:
            # Process in batches for efficiency
            for i in range(0, len(texts), batch_size):
                batch = texts[i:i + batch_size]

                # Run batch embedding in executor
                loop = asyncio.get_event_loop()
                batch_embeddings = await loop.run_in_executor(
                    None,
                    lambda b=batch: [
                        genai.embed_content(model="models/embedding-001", content=text)['embedding']
                        for text in b
                    ]
                )

                all_embeddings.extend(batch_embeddings)
                logger.info(f"Generated {len(batch_embeddings)} embeddings (batch {i // batch_size + 1}/{(len(texts) + batch_size - 1) // batch_size})")

            logger.info(f"✅ Total embeddings generated: {len(all_embeddings)}")
            return all_embeddings

        except Exception as e:
            logger.error(f"Failed to generate embeddings: {str(e)}")
            raise


# Global instance
embedding_service = EmbeddingService()
