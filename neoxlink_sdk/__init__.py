import importlib

from .async_client import AsyncNeoXlinkClient
from .async_pipeline import AsyncStructuredSubmissionPipeline
from .chains import NeoxlinkSubmissionChain, SubmissionChainInput
from .client import NeoXlinkClient
from .credits import CreditAccount, CreditLedger, CreditLimitExceeded, CreditPolicy, MeteredNeoXlinkClient
from .easy import create_engine
from .engine import (
    HeuristicModelAdapter,
    InMemoryDataSource,
    ProcurementIntentEngine,
    default_ranking_strategy,
)
from .mcp import NeoxlinkMCPAdapter
from .model_adapters import OpenAIChatCompletionsModel, OpenAICompatibleModelAdapter
from .models import (
    ClarificationQuestion,
    ClarificationState,
    ConfirmedEntry,
    MatchCandidate,
    ModelCallTrace,
    NormalizedIntent,
    ParsedIntent,
    ParsedPreview,
    ParseDraft,
    PipelineOutcome,
    PipelineStageTrace,
    ProcurementEngineResult,
    RankedMatch,
    ResolveResult,
    SkillRequest,
    SkillResponse,
    UNSPSCCandidate,
    UNSPSCClassification,
)
from .pipeline import StructuredSubmissionPipeline
from .plugins import PluginRegistry, RankingStrategy
from .skill import NeoxlinkSkill
from .typed_outputs import TypedLLMOutput, parse_typed_output, try_parse_typed_output
from .unspsc import classify_unspsc, unspsc_candidates


def __getattr__(name: str):
    if name == "open_source":
        return importlib.import_module(".open_source", __name__)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def __dir__() -> list[str]:
    return sorted({*globals().keys(), "open_source"})


__all__ = [
    "ClarificationQuestion",
    "ClarificationState",
    "ConfirmedEntry",
    "CreditAccount",
    "CreditLedger",
    "CreditLimitExceeded",
    "CreditPolicy",
    "default_ranking_strategy",
    "HeuristicModelAdapter",
    "InMemoryDataSource",
    "MatchCandidate",
    "ModelCallTrace",
    "AsyncNeoXlinkClient",
    "AsyncStructuredSubmissionPipeline",
    "NeoXlinkClient",
    "MeteredNeoXlinkClient",
    "NormalizedIntent",
    "NeoxlinkSubmissionChain",
    "NeoxlinkMCPAdapter",
    "NeoxlinkSkill",
    "OpenAIChatCompletionsModel",
    "OpenAICompatibleModelAdapter",
    "open_source",
    "ParseDraft",
    "ParsedIntent",
    "ParsedPreview",
    "PipelineStageTrace",
    "PipelineOutcome",
    "PluginRegistry",
    "ProcurementEngineResult",
    "ProcurementIntentEngine",
    "RankedMatch",
    "RankingStrategy",
    "ResolveResult",
    "SkillRequest",
    "SkillResponse",
    "StructuredSubmissionPipeline",
    "SubmissionChainInput",
    "TypedLLMOutput",
    "UNSPSCCandidate",
    "UNSPSCClassification",
    "classify_unspsc",
    "create_engine",
    "parse_typed_output",
    "try_parse_typed_output",
    "unspsc_candidates",
]
