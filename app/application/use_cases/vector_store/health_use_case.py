"""Health check use case."""

from dataclasses import dataclass
from app.application.interfaces.services.vector_store_service import IVectorStoreService


@dataclass
class HealthCheckOutput:
    healthy: bool
    message: str


class HealthCheckUseCase:
    """Check vector store health."""

    def __init__(self, vector_store: IVectorStoreService):
        self.vector_store = vector_store

    def execute(self) -> HealthCheckOutput:
        healthy = self.vector_store.is_healthy()
        return HealthCheckOutput(
            healthy=healthy, message="OK" if healthy else "Connection failed"
        )
