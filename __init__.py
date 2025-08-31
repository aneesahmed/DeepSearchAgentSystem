# File: deep_research/__init__.py
"""
Deep Research System
===================
A multi-agent research system for comprehensive information gathering and analysis.

Example usage:
    >>> import asyncio
    >>> from deep_research import DeepResearchSystem
    >>> 
    >>> async def main():
    ...     system = DeepResearchSystem()
    ...     findings = await system.research("What are pros and cons of electric cars?")
    ...     system.print_findings(findings)
    >>> 
    >>> asyncio.run(main())
"""

from .core import (
    DeepResearchSystem,
    Source,
    ResearchTask, 
    ResearchPlan,
    ResearchFindings,
    SourceQuality
)

from .agents import (
    PlanningAgent,
    SearchAgent, 
    SourceCheckerAgent,
    ConflictDetectionAgent,
    SynthesisAgent
)

from .search_providers import (
    TavilySearchProvider,
    DuckDuckGoSearchProvider,
    SearchAPIProvider,
    get_default_search_provider
)

__version__ = "1.0.0"
__author__ = "Deep Research Team"
__description__ = "Multi-agent research system for comprehensive information gathering"

__all__ = [
    # Core classes
    "DeepResearchSystem",
    "Source",
    "ResearchTask", 
    "ResearchPlan",
    "ResearchFindings",
    "SourceQuality",
    
    # Agents
    "PlanningAgent",
    "SearchAgent",
    "SourceCheckerAgent", 
    "ConflictDetectionAgent",
    "SynthesisAgent",
    
    # Search providers
    "TavilySearchProvider",
    "DuckDuckGoSearchProvider",
    "SearchAPIProvider",
    "get_default_search_provider"
]