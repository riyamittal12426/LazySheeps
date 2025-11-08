"""
Auto-Triage & Labeling System
LLM-powered issue classification and assignment
"""
import os
import json
import logging
from typing import Dict, List, Tuple
from django.conf import settings
from api.models import Issue, Repository, Contributor, RepositoryWork
import google.generativeai as genai

logger = logging.getLogger(__name__)

# Configure Gemini API
genai.configure(api_key=os.getenv('GEMINI_API_KEY', ''))


class IssueTriageService:
    """
    Automatically triage and label issues using LLM
    """
    
    def __init__(self):
        self.model = genai.GenerativeModel('gemini-pro')
    
    def classify_issue(self, issue_data: Dict) -> Dict:
        """
        Classify issue type, component, and priority
        
        Args:
            issue_data: Dict containing issue title, body, labels, etc.
            
        Returns:
            Dict with classification results
        """
        title = issue_data.get('title', '')
        body = issue_data.get('body', '')
        existing_labels = issue_data.get('labels', [])
        
        prompt = f"""
Analyze this GitHub issue and classify it:

Title: {title}
Description: {body}
Existing Labels: {', '.join(existing_labels)}

Provide a JSON response with the following structure:
{{
    "type": "bug|feature|docs|enhancement|question|security",
    "component": "frontend|backend|api|database|devops|docs",
    "priority": "low|medium|high|critical",
    "confidence": 0.0-1.0,
    "reasoning": "brief explanation",
    "suggested_labels": ["label1", "label2"],
    "is_duplicate": false,
    "duplicate_of": null,
    "complexity": "simple|moderate|complex",
    "estimated_effort": "1-3|3-8|8+"
}}

Consider:
- Bug indicators: "error", "crash", "broken", "not working", stack traces
- Feature indicators: "add", "implement", "support for", "new"
- Security indicators: "vulnerability", "security", "exploit", "CVE"
- Documentation indicators: "docs", "readme", "documentation", "guide"
- Frontend: UI, CSS, React, components, styling
- Backend: API, server, database, Django, Python
- Priority based on impact and urgency

Return ONLY valid JSON, no markdown formatting.
"""
        
        try:
            response = self.model.generate_content(prompt)
            result = json.loads(response.text.strip().replace('```json', '').replace('```', ''))
            logger.info(f"Issue classified: {result['type']} - {result['component']} (confidence: {result['confidence']})")
            return result
        except Exception as e:
            logger.error(f"Error classifying issue: {e}")
            return {
                'type': 'question',
                'component': 'backend',
                'priority': 'medium',
                'confidence': 0.5,
                'reasoning': 'Classification failed, using defaults',
                'suggested_labels': [],
                'is_duplicate': False,
                'complexity': 'moderate',
                'estimated_effort': '3-8'
            }
    
    def find_file_owners(self, repository: Repository, component: str) -> List[Contributor]:
        """
        Find potential assignees based on file ownership and component
        
        Args:
            repository: Repository object
            component: Component name (frontend, backend, api, etc.)
            
        Returns:
            List of top contributors for the component
        """
        # Map components to file patterns
        component_patterns = {
            'frontend': ['frontend/', 'src/', '.jsx', '.tsx', '.css', '.html'],
            'backend': ['backend/', 'api/', '.py', 'settings.py', 'models.py'],
            'api': ['api/', 'views.py', 'serializers.py', 'endpoints'],
            'database': ['models.py', 'migrations/', 'schema'],
            'devops': ['.yml', '.yaml', 'docker', 'deploy', 'ci/cd'],
            'docs': ['README', 'docs/', '.md', 'documentation']
        }
        
        patterns = component_patterns.get(component, [])
        
        try:
            # Get repository works
            works = RepositoryWork.objects.filter(repository=repository)
            
            # Score contributors based on their work matching the patterns
            contributor_scores = {}
            
            for work in works:
                contributor = work.contributor
                commits = work.commits.all()
                
                # Simple scoring: count commits that might touch relevant files
                # In real implementation, you'd analyze commit file paths
                score = commits.count()
                
                if contributor.id in contributor_scores:
                    contributor_scores[contributor.id] += score
                else:
                    contributor_scores[contributor.id] = score
            
            # Sort by score and get top contributors
            sorted_contributors = sorted(
                contributor_scores.items(),
                key=lambda x: x[1],
                reverse=True
            )
            
            # Get top 3 contributors
            top_contributor_ids = [c[0] for c in sorted_contributors[:3]]
            contributors = Contributor.objects.filter(id__in=top_contributor_ids)
            
            return list(contributors)
            
        except Exception as e:
            logger.error(f"Error finding file owners: {e}")
            return []
    
    def detect_duplicates(self, issue_data: Dict, repository: Repository) -> Tuple[bool, int]:
        """
        Detect potential duplicate issues using LLM
        
        Args:
            issue_data: New issue data
            repository: Repository object
            
        Returns:
            Tuple of (is_duplicate, duplicate_issue_id)
        """
        title = issue_data.get('title', '')
        body = issue_data.get('body', '')
        
        try:
            # Get recent issues from the repository
            works = RepositoryWork.objects.filter(repository=repository)
            recent_issues = Issue.objects.filter(
                work__in=works,
                state='open'
            ).order_by('-created_at')[:20]
            
            if not recent_issues:
                return False, None
            
            # Build comparison prompt
            issues_summary = "\n".join([
                f"#{i.id}: {i.raw_data.get('title', 'No title')}"
                for i in recent_issues
            ])
            
            prompt = f"""
Compare this new issue with existing issues to detect duplicates:

NEW ISSUE:
Title: {title}
Body: {body}

EXISTING ISSUES:
{issues_summary}

Is the new issue a duplicate of any existing issue?
Respond with JSON:
{{
    "is_duplicate": true/false,
    "duplicate_of": issue_id or null,
    "confidence": 0.0-1.0,
    "reasoning": "explanation"
}}

Return ONLY valid JSON.
"""
            
            response = self.model.generate_content(prompt)
            result = json.loads(response.text.strip().replace('```json', '').replace('```', ''))
            
            if result['is_duplicate'] and result['confidence'] > 0.7:
                return True, result['duplicate_of']
            
            return False, None
            
        except Exception as e:
            logger.error(f"Error detecting duplicates: {e}")
            return False, None
    
    def suggest_assignee(self, issue_data: Dict, repository: Repository, component: str) -> Dict:
        """
        Suggest best assignee based on component and contributor history
        
        Args:
            issue_data: Issue data
            repository: Repository object
            component: Classified component
            
        Returns:
            Dict with assignee suggestion
        """
        owners = self.find_file_owners(repository, component)
        
        if not owners:
            return {
                'assignee': None,
                'confidence': 0.0,
                'reasoning': 'No suitable contributors found'
            }
        
        # Get the top contributor
        top_contributor = owners[0]
        
        return {
            'assignee': top_contributor.username,
            'assignee_id': top_contributor.id,
            'confidence': 0.8,
            'reasoning': f'Top contributor for {component} component',
            'alternatives': [
                {
                    'username': c.username,
                    'id': c.id
                } for c in owners[1:3]
            ]
        }
    
    def triage_issue(self, issue_data: Dict, repository: Repository) -> Dict:
        """
        Complete triage workflow for an issue
        
        Args:
            issue_data: Issue data from webhook
            repository: Repository object
            
        Returns:
            Complete triage results
        """
        # Classify the issue
        classification = self.classify_issue(issue_data)
        
        # Detect duplicates
        is_duplicate, duplicate_id = self.detect_duplicates(issue_data, repository)
        
        # Suggest assignee
        assignee_info = self.suggest_assignee(
            issue_data,
            repository,
            classification['component']
        )
        
        # Build complete triage result
        result = {
            'classification': classification,
            'duplicate_detection': {
                'is_duplicate': is_duplicate,
                'duplicate_of': duplicate_id
            },
            'assignment': assignee_info,
            'labels': self._generate_labels(classification),
            'auto_actions': self._generate_auto_actions(classification, is_duplicate)
        }
        
        logger.info(f"Issue triage complete: {result}")
        return result
    
    def _generate_labels(self, classification: Dict) -> List[str]:
        """Generate label list from classification"""
        labels = [
            classification['type'],
            f"component:{classification['component']}",
            f"priority:{classification['priority']}",
            f"complexity:{classification['complexity']}"
        ]
        labels.extend(classification['suggested_labels'])
        return labels
    
    def _generate_auto_actions(self, classification: Dict, is_duplicate: bool) -> List[str]:
        """Generate recommended auto-actions"""
        actions = []
        
        if is_duplicate:
            actions.append('close_as_duplicate')
        
        if classification['priority'] == 'critical':
            actions.append('notify_team_lead')
            actions.append('add_to_sprint')
        
        if classification['type'] == 'security':
            actions.append('mark_security_issue')
            actions.append('notify_security_team')
        
        if classification['complexity'] == 'simple':
            actions.append('add_good_first_issue_label')
        
        return actions


# Global instance
triage_service = IssueTriageService()
