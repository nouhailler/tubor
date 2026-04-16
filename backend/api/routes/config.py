"""
Tubor Web — Routes API : configuration
"""

from fastapi import APIRouter

from core.config import Config
from models.schemas import ConfigResponse, ConfigUpdateRequest

router = APIRouter(prefix="/api/config", tags=["config"])
_config = Config()


@router.get("", response_model=ConfigResponse)
def get_config():
    """Retourne la configuration courante."""
    return _config.all()


@router.put("", response_model=ConfigResponse)
def update_config(req: ConfigUpdateRequest):
    """Met à jour un ou plusieurs champs de configuration et sauvegarde."""
    updates = {k: v for k, v in req.model_dump().items() if v is not None}
    _config.update(updates)
    _config.save()
    return _config.all()
