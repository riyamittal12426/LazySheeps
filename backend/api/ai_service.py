"""
Modern AI Service with LangChain
Replaces: Direct Gemini/OpenAI calls, issue_triage.py, chatbot.py

Features:
- Streaming responses
- Prompt caching  
- Memory/context management
- Async support
- Error handling
"""
from typing import Dict, List, Optional, AsyncGenerator
from django.conf import settings
from django.core.cache import cache
import logging
import json

# LangChain imports (install: pip install langchain langchain-google-genai)
try:
    from langchain_google_genai import ChatGoogleGenerativeAI
    from langchain.prompts import ChatPromptTemplate, PromptTemplate
    from langchain.chains import LLMChain
    from langchain.schema import HumanMessage, SystemMessage
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False
    logging.warning("LangChain not installed. Install with: pip install langchain langchain-google-genai")

logger = logging.getLogger(__name__)


class AIService:
    """
    Unified AI service for all LLM operations
    Uses LangChain with Google Gemini
    """
    
    def __init__(self):
        if not LANGCHAIN_AVAILABLE:
            raise ImportError("LangChain is required. Install with: pip install langchain langchain-google-genai")
        
        # Initialize LangChain model
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash-exp",  # Latest Gemini Flash model
            google_api_key=settings.GEMINI_API_KEY,
            temperature=0.3,  # Lower for more consistent outputs
            streaming=True,   # Enable streaming
        )
        
        # Initialize prompt templates
        self._init_prompts()
    
    def _init_prompts(self):
        """Initialize reusable prompt templates"""
        
        # Issue classification prompt
        self.issue_classifier_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert GitHub issue classifier. Analyze the issue and classify it.
Return ONLY valid JSON with this exact structure:
{{
    "type": "bug|feature|documentation|question|security",
    "priority": "low|medium|high|critical",
    "complexity": "trivial|simple|moderate|complex",
    "component": "frontend|backend|database|api|infrastructure|docs|other",
    "estimated_effort": <hours as number>,
    "confidence": <0.0-1.0>,
    "reasoning": "brief explanation"
}}"""),
            ("human", "Title: {title}\nDescription: {body}")
        ])
        
        # PR summary prompt
        self.pr_summary_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a code review assistant. Summarize this pull request concisely.
Include: What changed, why it matters, any risks or concerns.
Keep it under 200 words and use markdown formatting."""),
            ("human", """PR #{number}: {title}
            
Description: {body}

Files changed: {files}

Generate a clear, actionable summary.""")
        ])
        
        # Code health analysis prompt
        self.health_analysis_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a software engineering metrics expert. Analyze this repository's health.
Provide actionable insights in markdown format."""),
            ("human", """Repository: {name}

Metrics:
- Commits (30d): {commits}
- Open issues: {issues}
- Contributors: {contributors}
- Code churn: {churn}
- Deployment frequency: {deploys}

Analyze the health and provide 3-5 specific recommendations.""")
        ])
    
    # =========================================================================
    # Issue Operations
    # =========================================================================
    
    async def classify_issue(self, title: str, body: str) -> Dict:
        """
        Classify a GitHub issue using LLM
        
        Args:
            title: Issue title
            body: Issue description
            
        Returns:
            Dict with classification results
        """
        cache_key = f"issue_classify:{hash(title + body)}"
        
        # Check cache first
        cached = cache.get(cache_key)
        if cached:
            logger.debug("Using cached classification")
            return cached
        
        try:
            # Create chain
            chain = self.issue_classifier_prompt | self.llm
            
            # Invoke
            response = await chain.ainvoke({
                "title": title,
                "body": body or "No description provided"
            })
            
            # Parse JSON response
            result = json.loads(response.content.strip().replace('```json', '').replace('```', ''))
            
            # Cache for 1 hour
            cache.set(cache_key, result, timeout=3600)
            
            logger.info(f"Classified issue as: {result['type']} / {result['priority']}")
            return result
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM response: {e}")
            return self._get_fallback_classification()
        except Exception as e:
            logger.error(f"Issue classification failed: {e}")
            return self._get_fallback_classification()
    
    def classify_issue_sync(self, title: str, body: str) -> Dict:
        """Synchronous version of classify_issue"""
        cache_key = f"issue_classify:{hash(title + body)}"
        
        cached = cache.get(cache_key)
        if cached:
            return cached
        
        try:
            chain = self.issue_classifier_prompt | self.llm
            response = chain.invoke({"title": title, "body": body or ""})
            result = json.loads(response.content.strip().replace('```json', '').replace('```', ''))
            cache.set(cache_key, result, timeout=3600)
            return result
        except Exception as e:
            logger.error(f"Classification failed: {e}")
            return self._get_fallback_classification()
    
    def _get_fallback_classification(self) -> Dict:
        """Return a sensible default when LLM fails"""
        return {
            "type": "question",
            "priority": "medium",
            "complexity": "simple",
            "component": "other",
            "estimated_effort": 2,
            "confidence": 0.0,
            "reasoning": "Auto-classification unavailable"
        }
    
    async def detect_duplicate_issues(self, title: str, body: str, 
                                     existing_issues: List[Dict]) -> Optional[int]:
        """
        Detect if an issue is a duplicate using semantic similarity
        
        Args:
            title: New issue title
            body: New issue body  
            existing_issues: List of recent issues to compare against
            
        Returns:
            ID of duplicate issue, or None
        """
        if not existing_issues:
            return None
        
        # Build comparison prompt
        issues_text = "\n".join([
            f"#{i['id']}: {i.get('title', 'No title')}"
            for i in existing_issues[:10]  # Limit to 10 most recent
        ])
        
        prompt = f"""Compare this new issue with existing issues.
If it's clearly a duplicate (>80% similar), return the issue number.
Otherwise return "none".

NEW ISSUE:
Title: {title}
Body: {body}

EXISTING ISSUES:
{issues_text}

Return ONLY the issue number or "none". No explanation."""
        
        try:
            response = await self.llm.ainvoke([HumanMessage(content=prompt)])
            result = response.content.strip().lower()
            
            if result == "none" or not result.isdigit():
                return None
            
            return int(result)
            
        except Exception as e:
            logger.error(f"Duplicate detection failed: {e}")
            return None
    
    # =========================================================================
    # PR Operations
    # =========================================================================
    
    async def summarize_pr(self, pr_number: int, title: str, body: str,
                          files_changed: List[str]) -> str:
        """
        Generate PR summary using LLM
        
        Args:
            pr_number: PR number
            title: PR title
            body: PR description
            files_changed: List of changed files
            
        Returns:
            Markdown-formatted summary
        """
        cache_key = f"pr_summary:{pr_number}"
        
        cached = cache.get(cache_key)
        if cached:
            return cached
        
        try:
            chain = self.pr_summary_prompt | self.llm
            
            response = await chain.ainvoke({
                "number": pr_number,
                "title": title,
                "body": body or "No description",
                "files": ", ".join(files_changed[:20]) if files_changed else "No files listed"
            })
            
            summary = response.content.strip()
            
            # Cache for 6 hours
            cache.set(cache_key, summary, timeout=21600)
            
            return summary
            
        except Exception as e:
            logger.error(f"PR summary failed: {e}")
            return f"**PR #{pr_number}: {title}**\n\n{body[:200]}..."
    
    # =========================================================================
    # Repository Health Analysis
    # =========================================================================
    
    async def analyze_repository_health(self, repository_data: Dict) -> str:
        """
        Analyze repository health and provide recommendations
        
        Args:
            repository_data: Dict with repository metrics
            
        Returns:
            Markdown-formatted analysis with recommendations
        """
        try:
            chain = self.health_analysis_prompt | self.llm
            
            response = await chain.ainvoke(repository_data)
            
            return response.content.strip()
            
        except Exception as e:
            logger.error(f"Health analysis failed: {e}")
            return "**Analysis unavailable**\n\nUnable to generate health analysis at this time."
    
    # =========================================================================
    # Team Health Insights
    # =========================================================================
    
    async def generate_team_insights(self, team_data: Dict) -> str:
        """
        Generate insights about team health and risks
        
        Args:
            team_data: Dict with team metrics (workload, burnout, etc.)
            
        Returns:
            Markdown-formatted insights
        """
        prompt = f"""Analyze this development team's health metrics and provide insights.

Team Metrics:
- Team size: {team_data.get('total_members', 0)}
- At risk: {team_data.get('at_risk_count', 0)} members
- Average workload: {team_data.get('avg_workload', 0)}%
- Average burnout risk: {team_data.get('avg_burnout_risk', 0)}%

Provide:
1. Overall team health assessment
2. Top 3 concerns
3. 3 specific actionable recommendations

Keep it concise (under 300 words) and actionable."""
        
        try:
            response = await self.llm.ainvoke([HumanMessage(content=prompt)])
            return response.content.strip()
        except Exception as e:
            logger.error(f"Team insights failed: {e}")
            return "**Insights unavailable**"
    
    # =========================================================================
    # Streaming Operations (for chat/real-time)
    # =========================================================================
    
    async def stream_response(self, prompt: str) -> AsyncGenerator[str, None]:
        """
        Stream LLM response token by token
        
        Args:
            prompt: Input prompt
            
        Yields:
            Response chunks
        """
        try:
            async for chunk in self.llm.astream([HumanMessage(content=prompt)]):
                if chunk.content:
                    yield chunk.content
        except Exception as e:
            logger.error(f"Streaming failed: {e}")
            yield f"Error: {str(e)}"
    
    # =========================================================================
    # Helper Methods
    # =========================================================================
    
    def health_check(self) -> Dict:
        """Check if AI service is operational"""
        try:
            # Simple test prompt
            response = self.llm.invoke([HumanMessage(content="Respond with 'OK'")])
            
            return {
                'status': 'healthy',
                'model': 'gemini-2.0-flash-exp',
                'test_response': response.content,
                'langchain_available': LANGCHAIN_AVAILABLE
            }
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e),
                'langchain_available': LANGCHAIN_AVAILABLE
            }


# Global service instance
try:
    ai_service = AIService()
except Exception as e:
    logger.error(f"Failed to initialize AI service: {e}")
    ai_service = None
