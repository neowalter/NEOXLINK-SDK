from __future__ import annotations

from collections.abc import Callable
from typing import Any, Protocol

from .engine import DataSource, ModelAdapter
from .models import MatchCandidate, NormalizedIntent


class RankingStrategy(Protocol):
    def __call__(self, signals: dict[str, float], intent: NormalizedIntent, candidate: MatchCandidate) -> float:
        """Return a normalized ranking score in [0, 1]."""


PluginFactory = Callable[..., Any]


class PluginRegistry:
    """Simple plugin registry for model adapters, data connectors, and ranking logic.

    The registry is intentionally lightweight so integrators can wire custom factories
    without inheriting SDK base classes.
    """

    def __init__(self) -> None:
        self._model_adapters: dict[str, PluginFactory] = {}
        self._data_sources: dict[str, PluginFactory] = {}
        self._ranking_strategies: dict[str, PluginFactory] = {}

    def register_model_adapter(self, name: str, factory: PluginFactory) -> None:
        self._model_adapters[name] = factory

    def register_data_source(self, name: str, factory: PluginFactory) -> None:
        self._data_sources[name] = factory

    def register_ranking_strategy(self, name: str, factory: PluginFactory) -> None:
        self._ranking_strategies[name] = factory

    def create_model_adapter(self, name: str, **kwargs: Any) -> ModelAdapter:
        if name not in self._model_adapters:
            raise KeyError(f"Unknown model adapter plugin: {name}")
        adapter = self._model_adapters[name](**kwargs)
        return adapter

    def create_data_source(self, name: str, **kwargs: Any) -> DataSource:
        if name not in self._data_sources:
            raise KeyError(f"Unknown data source plugin: {name}")
        data_source = self._data_sources[name](**kwargs)
        return data_source

    def create_ranking_strategy(self, name: str, **kwargs: Any) -> RankingStrategy:
        if name not in self._ranking_strategies:
            raise KeyError(f"Unknown ranking strategy plugin: {name}")
        strategy = self._ranking_strategies[name](**kwargs)
        return strategy

    def list_plugins(self) -> dict[str, list[str]]:
        return {
            "model_adapters": sorted(self._model_adapters.keys()),
            "data_sources": sorted(self._data_sources.keys()),
            "ranking_strategies": sorted(self._ranking_strategies.keys()),
        }
