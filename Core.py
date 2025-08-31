# File: deep_research/core.py
"""
Deep Research System - Core Module
=================================
Multi-agent research system for comprehensive information gathering and analysis.
"""

import asyncio
import json
import logging
import os
import re
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Tuple, Any
from urllib.parse import urlparse

import aiohttp
import requests

# Configure logging
logger = logging.getLogger(__name__)

class SourceQuality(Enum):
    HIGH = "high"      # .edu, .gov, major news
    MEDIUM = "medium"  # Wikipedia, industry sites
    LOW = "low"        # blogs, forums, unknown


@dataclass
class Source:
    """Represents a research source with quality assessment."""
    url: str
    title: str
    snippet: str
    quality: SourceQuality
    timestamp: datetime = field(default_factory=datetime.now)
    
    def get_domain(self) -> str:
        """Extract domain from URL."""
        try:
            return urlparse(self.url).netloc.lower()
        except:
            return "unknown"


@dataclass
class ResearchTask:
    """Represents a specific research task."""
    id: str
    query: str
    priority: int = 1
    completed: bool = False
    results: List[Source] = field(default_factory=list)
    analysis: str = ""


@dataclass
class ResearchPlan:
    """Represents a complete research plan."""
    main_query: str
    tasks: List[ResearchTask]
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class ResearchFindings:
    """Consolidated research findings."""
    main_query: str
    sources: List[Source]
    key_insights: List[str]
    conflicts: List[str]
    citations: Dict[str, int]
    report: str


class SearchProvider(ABC):
    """Abstract base class for search providers."""
    
    @abstractmethod
    async def search(self, query: str, num_results: int = 10) -> List[Dict]:
        """Perform search and return results."""
        pass


class Agent(ABC):
    """Base class for all research agents."""
    
    def __init__(self, name: str):
        self.name = name
        self.logger = logging.getLogger(f"Agent.{name}")
    
    @abstractmethod
    async def execute(self, *args, **kwargs):
        """Execute the agent's primary function."""
        pass


class DeepResearchSystem:
    """Main orchestrator for the multi-agent research system."""
    
    def __init__(self, search_provider: Optional[SearchProvider] = None):
        from .search_providers import get_default_search_provider
        from .agents import (
            PlanningAgent, SearchAgent, SourceCheckerAgent, 
            ConflictDetectionAgent, SynthesisAgent
        )
        
        self.search_provider = search_provider or get_default_search_provider()
        
        # Initialize agents
        self.planning_agent = PlanningAgent()
        self.search_agent = SearchAgent(self.search_provider)
        self.source_checker = SourceCheckerAgent()
        self.conflict_detector = ConflictDetectionAgent()
        self.synthesis_agent = SynthesisAgent()
        
        self.logger = logging.getLogger("DeepResearchSystem")
    
    async def research(self, query: str) -> ResearchFindings:
        """Conduct comprehensive research on a query."""
        self.logger.info(f"Starting deep research for: {query}")
        
        # Phase 1: Planning
        research_plan = await self.planning_agent.execute(query)
        
        # Phase 2: Parallel Research
        all_sources = []
        tasks = []
        
        # Execute research tasks in parallel
        for task in research_plan.tasks:
            task_coroutine = self.search_agent.execute(task)
            tasks.append(task_coroutine)
        
        # Wait for all tasks to complete
        completed_tasks = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Collect all sources
        for completed_task in completed_tasks:
            if isinstance(completed_task, ResearchTask):
                all_sources.extend(completed_task.results)
        
        # Phase 3: Quality Assessment
        all_sources = await self.source_checker.execute(all_sources)
        
        # Phase 4: Conflict Detection
        conflicts = await self.conflict_detector.execute(all_sources)
        
        # Phase 5: Synthesis
        findings = await self.synthesis_agent.execute(research_plan, all_sources, conflicts)
        
        self.logger.info(f"Research completed. Found {len(all_sources)} sources with {len(conflicts)} conflicts detected.")
        
        return findings
    
    def print_findings(self, findings: ResearchFindings):
        """Print research findings in a formatted way."""
        print("=" * 80)
        print(f"DEEP RESEARCH RESULTS")
        print("=" * 80)
        print(findings.report)