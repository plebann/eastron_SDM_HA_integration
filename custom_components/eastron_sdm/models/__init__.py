"""Model register specifications package."""

from __future__ import annotations

from typing import Callable, Dict, List

from ..const import MODEL_SDM120M, MODEL_SDM630M
from .base import RegisterSpec
from .sdm120 import get_register_specs as get_sdm120_specs
from .sdm630m import get_register_specs as get_sdm630_specs


_MODEL_LOADERS: Dict[str, Callable[[], List[RegisterSpec]]] = {
	MODEL_SDM120M: get_sdm120_specs,
	MODEL_SDM630M: get_sdm630_specs,
}


def get_model_specs(model: str) -> List[RegisterSpec]:
	"""Return RegisterSpec list for the requested model (defaults to SDM120M)."""

	loader = _MODEL_LOADERS.get(model, get_sdm120_specs)
	return loader()


def get_spec_by_key(model: str, key: str) -> RegisterSpec:
	"""Lookup a RegisterSpec by key for the given model."""

	specs = get_model_specs(model)
	for spec in specs:
		if spec.key == key:
			return spec
	raise ValueError(f"No spec found for model={model} key={key}")
