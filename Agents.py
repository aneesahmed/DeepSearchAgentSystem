# File: deep_research/agents.py
"""
Research Agents Module
=====================
Contains all specialized agents for the deep research system.
"""

import re
from datetime import datetime
from typing import List, Dict
from urllib.parse import urlparse

from .core import (
    Agent, Source, ResearchTask, ResearchPlan, 
    ResearchFindings, SourceQuality
)


class PlanningAgent(Agent):
    """Breaks down complex research questions into manageable tasks."""
    
    def __init__(self):
        super().__init__("PlanningAgent")
    
    async def execute(self, query: str) -> ResearchPlan:
        """Break down the main query into specific research tasks."""
        self.logger.info(f"Planning research for: {query}")
        
        # Analyze query complexity and create subtasks
        tasks = await self._create_research_tasks(query)
        
        plan = ResearchPlan(
            main_query=query,
            tasks=tasks
        )
        
        self.logger.info(f"Created research plan with {len(tasks)} tasks")
        return plan
    
    async def _create_research_tasks(self, query: str) -> List[ResearchTask]:
        """Create specific research tasks based on the main query."""
        tasks = []
        
        # Basic task decomposition logic
        if "compare" in query.lower():
            # Extract items to compare
            items = self._extract_comparison_items(query)
            for i, item in enumerate(items):
                task = ResearchTask(
                    id=f"compare_{i}",
                    query=f"Research {item} in context of {query}",
                    priority=1
                )
                tasks.append(task)
        elif "pros and cons" in query.lower():
            # Create tasks for advantages and disadvantages
            tasks.append(ResearchTask("pros", f"Advantages of {query}", 1))
            tasks.append(ResearchTask("cons", f"Disadvantages of {query}", 1))
        else:
            # Break into general research areas
            tasks.append(ResearchTask("overview", f"General overview: {query}", 1))
            tasks.append(ResearchTask("details", f"Detailed analysis: {query}", 2))
            tasks.append(ResearchTask("context", f"Context and background: {query}", 2))
        
        return tasks
    
    def _extract_comparison_items(self, query: str) -> List[str]:
        """Extract items to compare from query."""
        # Simple extraction logic - can be enhanced with NLP
        if "vs" in query.lower():
            items = query.lower().split("vs")
        elif "versus" in query.lower():
            items = query.lower().split("versus")
        elif "electric" in query.lower() and "gas" in query.lower():
            items = ["electric vehicles", "gas vehicles"]
        else:
            # Default fallback
            items = [query]
        
        return [item.strip() for item in items[:5]]  # Limit to 5 items


class SearchAgent(Agent):
    """Conducts web searches for specific research tasks."""
    
    def __init__(self, search_provider):
        super().__init__("SearchAgent")
        self.search_provider = search_provider
        self.source_checker = SourceCheckerAgent()
    
    async def execute(self, task: ResearchTask) -> ResearchTask:
        """Execute search for a research task."""
        self.logger.info(f"Searching for: {task.query}")
        
        # Perform search
        results = await self.search_provider.search(task.query, num_results=10)
        
        # Convert results to Sources with quality assessment
        sources = []
        for result in results:
            source = Source(
                url=result.get('url', ''),
                title=result.get('title', ''),
                snippet=result.get('content', ''),
                quality=self.source_checker.assess_quality(result.get('url', ''))
            )
            sources.append(source)
        
        task.results = sources
        task.completed = True
        
        self.logger.info(f"Found {len(sources)} sources for task {task.id}")
        return task


class SourceCheckerAgent(Agent):
    """Assesses the quality and reliability of sources."""
    
    def __init__(self):
        super().__init__("SourceChecker")
        
        # Define quality indicators
        self.high_quality_domains = {
            'edu', 'gov', 'org',  # Educational, government, non-profit
            'nature.com', 'sciencemag.org', 'pnas.org',  # Scientific journals
            'bbc.com', 'reuters.com', 'ap.org', 'npr.org'  # Reputable news
        }
        
        self.medium_quality_indicators = {
            'wikipedia.org', 'investopedia.com', 'britannica.com'
        }
        
        self.low_quality_indicators = {
            'blog', 'personal', 'forum', 'reddit.com'
        }
    
    def assess_quality(self, url: str) -> SourceQuality:
        """Assess the quality of a source based on its URL."""
        if not url:
            return SourceQuality.LOW
        
        domain = urlparse(url).netloc.lower()
        
        # Check for high quality indicators
        for indicator in self.high_quality_domains:
            if indicator in domain:
                return SourceQuality.HIGH
        
        # Check for medium quality indicators
        for indicator in self.medium_quality_indicators:
            if indicator in domain:
                return SourceQuality.MEDIUM
        
        # Check for low quality indicators
        for indicator in self.low_quality_indicators:
            if indicator in domain:
                return SourceQuality.LOW
        
        # Default to medium if unknown
        return SourceQuality.MEDIUM
    
    async def execute(self, sources: List[Source]) -> List[Source]:
        """Re-assess and validate source quality."""
        for source in sources:
            source.quality = self.assess_quality(source.url)
        
        return sources


class ConflictDetectionAgent(Agent):
    """Identifies conflicting information across sources."""
    
    def __init__(self):
        super().__init__("ConflictDetection")
    
    async def execute(self, sources: List[Source]) -> List[str]:
        """Detect conflicts between sources."""
        conflicts = []
        
        # Simple conflict detection based on contradictory keywords
        positive_indicators = ['benefit', 'advantage', 'positive', 'good', 'better', 'improved']
        negative_indicators = ['problem', 'disadvantage', 'negative', 'bad', 'worse', 'harmful']
        
        positive_sources = []
        negative_sources = []
        
        for source in sources:
            text = (source.title + " " + source.snippet).lower()
            
            pos_count = sum(1 for word in positive_indicators if word in text)
            neg_count = sum(1 for word in negative_indicators if word in text)
            
            if pos_count > neg_count:
                positive_sources.append(source)
            elif neg_count > pos_count:
                negative_sources.append(source)
        
        if positive_sources and negative_sources:
            conflicts.append(
                f"Conflicting viewpoints detected: {len(positive_sources)} sources "
                f"present positive views while {len(negative_sources)} sources "
                f"present negative views on the topic."
            )
        
        return conflicts


class SynthesisAgent(Agent):
    """Synthesizes research findings into coherent insights."""
    
    def __init__(self):
        super().__init__("Synthesis")
    
    async def execute(self, research_plan: ResearchPlan, all_sources: List[Source], 
                     conflicts: List[str]) -> ResearchFindings:
        """Synthesize all research into final findings."""
        self.logger.info("Synthesizing research findings")
        
        # Extract key insights
        insights = await self._extract_insights(all_sources)
        
        # Create citation mapping
        citations = {source.url: i+1 for i, source in enumerate(all_sources)}
        
        # Generate comprehensive report
        report = await self._generate_report(
            research_plan.main_query, 
            insights, 
            all_sources, 
            conflicts, 
            citations
        )
        
        findings = ResearchFindings(
            main_query=research_plan.main_query,
            sources=all_sources,
            key_insights=insights,
            conflicts=conflicts,
            citations=citations,
            report=report
        )
        
        return findings
    
    async def _extract_insights(self, sources: List[Source]) -> List[str]:
        """Extract key insights from sources."""
        insights = []
        
        # Group sources by quality
        high_quality = [s for s in sources if s.quality == SourceQuality.HIGH]
        medium_quality = [s for s in sources if s.quality == SourceQuality.MEDIUM]
        
        if high_quality:
            insights.append(f"High-quality sources ({len(high_quality)}) provide authoritative information")
        
        if medium_quality:
            insights.append(f"Additional context from {len(medium_quality)} medium-quality sources")
        
        # Extract common themes (simplified)
        all_text = " ".join([s.title + " " + s.snippet for s in sources]).lower()
        common_words = self._find_common_themes(all_text)
        
        if common_words:
            insights.append(f"Key themes identified: {', '.join(common_words[:5])}")
        
        return insights
    
    def _find_common_themes(self, text: str) -> List[str]:
        """Find common themes in text (simplified implementation)."""
        # Remove common stop words and find frequent terms
        stop_words = {'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'a', 'an'}
        words = re.findall(r'\b\w+\b', text.lower())
        word_freq = {}
        
        for word in words:
            if word not in stop_words and len(word) > 3:
                word_freq[word] = word_freq.get(word, 0) + 1
        
        # Return most frequent words
        return sorted(word_freq.keys(), key=lambda x: word_freq[x], reverse=True)[:10]
    
    async def _generate_report(self, query: str, insights: List[str], 
                              sources: List[Source], conflicts: List[str], 
                              citations: Dict[str, int]) -> str:
        """Generate comprehensive research report."""
        
        report = f"""# Research Report: {query}

## Executive Summary
This report presents findings from a comprehensive analysis of {len(sources)} sources regarding "{query}". The research was conducted using a multi-agent system that evaluated source quality, detected conflicts, and synthesized key insights.

## Key Findings
"""
        
        for i, insight in enumerate(insights, 1):
            report += f"{i}. {insight}\n"
        
        if conflicts:
            report += "\n## Conflicting Information\n"
            for conflict in conflicts:
                report += f"⚠️ {conflict}\n"
        
        report += "\n## Source Quality Distribution\n"
        high_count = len([s for s in sources if s.quality == SourceQuality.HIGH])
        medium_count = len([s for s in sources if s.quality == SourceQuality.MEDIUM])
        low_count = len([s for s in sources if s.quality == SourceQuality.LOW])
        
        report += f"- **High Quality Sources**: {high_count} (.edu, .gov, major news)\n"
        report += f"- **Medium Quality Sources**: {medium_count} (Wikipedia, industry sites)\n"
        report += f"- **Low Quality Sources**: {low_count} (blogs, forums)\n"
        
        report += "\n## Detailed Analysis\n"
        
        # Group findings by source quality
        for quality in [SourceQuality.HIGH, SourceQuality.MEDIUM]:
            quality_sources = [s for s in sources if s.quality == quality]
            if quality_sources:
                report += f"\n### {quality.value.title()} Quality Sources\n"
                for source in quality_sources[:5]:  # Limit to top 5 per category
                    citation_num = citations[source.url]
                    report += f"- {source.title} [{citation_num}]\n"
                    report += f"  {source.snippet[:150]}...\n\n"
        
        report += "\n## References\n"
        for url, num in sorted(citations.items(), key=lambda x: x[1]):
            source = next((s for s in sources if s.url == url), None)
            if source:
                report += f"[{num}] {source.title} - {url}\n"
        
        report += f"\n---\n*Report generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*"
        
        return report