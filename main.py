#!/usr/bin/env python3
# File: main.py
"""
Main script for running the Deep Research System.
"""

import asyncio
import logging
import os
import sys
from typing import List

from dotenv import load_dotenv

from deep_research import DeepResearchSystem, SourceQuality

# Load environment variables
load_dotenv()

# Configure logging
def setup_logging():
    """Configure logging for the application."""
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()
    logging.basicConfig(
        level=getattr(logging, log_level, logging.INFO),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('research.log')
        ]
    )

async def run_test_queries():
    """Run predefined test queries to validate the system."""
    system = DeepResearchSystem()
    
    test_queries = [
        "What are pros and cons of electric cars?",
        "Compare renewable energy vs fossil fuels", 
        "Environmental impact of cryptocurrency mining",
        "Benefits and risks of artificial intelligence in healthcare"
    ]
    
    print("🔬 Running Deep Research System Tests")
    print("=" * 60)
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n📋 Test {i}/{len(test_queries)}: {query}")
        print("-" * 60)
        
        try:
            findings = await system.research(query)
            
            # Print summary
            print(f"✅ Research completed successfully!")
            print(f"📊 Sources found: {len(findings.sources)}")
            print(f"🏆 High quality sources: {len([s for s in findings.sources if s.quality == SourceQuality.HIGH])}")
            print(f"⚠️  Conflicts detected: {len(findings.conflicts)}")
            print(f"💡 Key insights: {len(findings.key_insights)}")
            
            # Print brief report excerpt
            report_lines = findings.report.split('\n')
            excerpt = '\n'.join(report_lines[:20])  # First 20 lines
            print(f"\n📄 Report Excerpt:\n{excerpt}")
            
            if len(report_lines) > 20:
                print("\n... (truncated for brevity)")
            
        except Exception as e:
            print(f"❌ Test failed: {e}")
            logging.error(f"Test query failed: {query}", exc_info=True)
        
        print("\n" + "=" * 60)


async def run_interactive_mode():
    """Run the system in interactive mode."""
    system = DeepResearchSystem()
    
    print("🔍 Deep Research System - Interactive Mode")
    print("=" * 50)
    print("Enter your research queries below. Type 'quit' to exit.")
    print()
    
    while True:
        try:
            query = input("🤔 Research Query: ").strip()
            
            if not query:
                continue
                
            if query.lower() in ['quit', 'exit', 'q']:
                print("👋 Thanks for using Deep Research System!")
                break
            
            print(f"\n🔬 Researching: {query}")
            print("-" * 50)
            
            findings = await system.research(query)
            system.print_findings(findings)
            
            print(f"\n📊 Research Summary:")
            print(f"- Sources analyzed: {len(findings.sources)}")
            print(f"- High quality sources: {len([s for s in findings.sources if s.quality == SourceQuality.HIGH])}")
            print(f"- Conflicts detected: {len(findings.conflicts)}")
            print(f"- Key insights generated: {len(findings.key_insights)}")
            
        except KeyboardInterrupt:
            print("\n\n👋 Exiting Deep Research System...")
            break
        except Exception as e:
            print(f"❌ Research failed: {e}")
            logging.error(f"Interactive research failed: {query}", exc_info=True)


async def run_single_query(query: str):
    """Run a single research query."""
    system = DeepResearchSystem()
    
    print(f"🔬 Researching: {query}")
    print("=" * 60)
    
    try:
        findings = await system.research(query)
        system.print_findings(findings)
        
        print(f"\n📊 Research completed successfully!")
        print(f"- Sources: {len(findings.sources)}")
        print(f"- Quality distribution: {len([s for s in findings.sources if s.quality == SourceQuality.HIGH])} high, "
              f"{len([s for s in findings.sources if s.quality == SourceQuality.MEDIUM])} medium, "
              f"{len([s for s in findings.sources if s.quality == SourceQuality.LOW])} low")
        print(f"- Conflicts: {len(findings.conflicts)}")
        
    except Exception as e:
        print(f"❌ Research failed: {e}")
        logging.error(f"Single query research failed: {query}", exc_info=True)


def check_environment():
    """Check if required environment variables are set."""
    required_vars = []
    optional_vars = ["TAVILY_API_KEY", "SEARCH_API_KEY"]
    
    missing_optional = [var for var in optional_vars if not os.getenv(var)]
    
    if missing_optional:
        print("⚠️  Warning: No search API keys found")
        print("   The system will use DuckDuckGo as fallback")
        print("   For better results, set TAVILY_API_KEY in your .env file")
        print()
    
    # Check if duckduckgo-search is available
    try:
        import duckduckgo_search
    except ImportError:
        if missing_optional:
            print("❌ Error: No search providers available!")
            print("   Either set an API key in .env or install: pip install duckduckgo-search")
            return False
    
    return True


def main():
    """Main entry point."""
    setup_logging()
    
    if not check_environment():
        sys.exit(1)
    
    import argparse
    
    parser = argparse.ArgumentParser(description="Deep Research System")
    parser.add_argument("--query", "-q", type=str, help="Single query to research")
    parser.add_argument("--test", action="store_true", help="Run test queries")
    parser.add_argument("--interactive", "-i", action="store_true", help="Run in interactive mode")
    
    args = parser.parse_args()
    
    if args.query:
        asyncio.run(run_single_query(args.query))
    elif args.test:
        asyncio.run(run_test_queries())
    elif args.interactive:
        asyncio.run(run_interactive_mode())
    else:
        print("🔍 Deep Research System")
        print("=" * 30)
        print("Usage:")
        print("  python main.py --query 'Your research question'")
        print("  python main.py --test")
        print("  python main.py --interactive")
        print()
        print("For help: python main.py --help")


if __name__ == "__main__":
    main()