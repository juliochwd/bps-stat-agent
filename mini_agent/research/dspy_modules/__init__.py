"""DSPy pipeline modules for optimizable research workflows.

Provides composable, optimizable modules for each research step.
Falls back gracefully if DSPy is not installed.
"""

from __future__ import annotations

from .._dspy_compat import (  # noqa: F401
    DSPY_AVAILABLE,
    _require_dspy,
)

# Re-export tool classes from the compat module
from .._dspy_compat import (  # noqa: F401
    DSPyOptimizeTool as DSPyOptimizeTool,
)

# Sub-module exports
try:
    from .signatures import (  # noqa: F401
        EvidenceSynthesisSignature,
        MethodologyDesignSignature,
        ResultsInterpretationSignature,
        SearchQuerySignature,
        SectionWritingSignature,
    )
except ImportError:
    pass

try:
    from .modules import (  # noqa: F401
        DataAnalysisModule,
        LiteratureReviewModule,
        PaperGenerationModule,
        QualityCheckModule,
    )
except ImportError:
    pass

__all__ = [
    "DSPY_AVAILABLE",
    "_require_dspy",
]
