"""
Slack & Discord Bot Integration for LangHub
Chat commands for team collaboration
"""
import os
import json
import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from django.conf import settings
from django.utils import timezone
from api.models import Repository, Contributor, Commit, Issue, RepositoryWork
import google.generativeai as genai
import requests

logger = logging.getLogger(__name__)

# Configure Gemini API
genai.configure(api_key=os.getenv('GEMINI_API_KEY', ''))


class ChatBotService:
    """
    Base class for chat bot integrations
    """
    
    def __init__(self):
        self.model = genai.GenerativeModel('gemini-pro')
    
    def generate_pr_summary(self, pr_number: int, repository_name: str) -> str:
        """
        Generate AI summary of a pull request
        
        Args:
            pr_number: PR number
            repository_name: Repository name (e.g., 'owner/repo')
            
        Returns:
            Formatted PR summary
        """
        try:
            # Fetch PR data from GitHub API
            github_token = os.getenv('GITHUB_TOKEN', '')
            url = f"https://api.github.com/repos/{repository_name}/pulls/{pr_number}"
            headers = {
                'Authorization': f'token {github_token}',
                'Accept': 'application/vnd.github.v3+json'
            }
            
            response = requests.get(url, headers=headers)
            
            if response.status_code != 200:
                return f"❌ Could not fetch PR #{pr_number}. Status: {response.status_code}"
            
            pr_data = response.json()
            
            # Get PR files
            files_url = pr_data['url'] + '/files'
            files_response = requests.get(files_url, headers=headers)
            files_data = files_response.json() if files_response.status_code == 200 else []
            
            # Generate summary using LLM
            prompt = f"""
Analyze this Pull Request and provide a concise summary:

Title: {pr_data['title']}
Description: {pr_data['body'] or 'No description provided'}
Author: {pr_data['user']['login']}
State: {pr_data['state']}
Created: {pr_data['created_at']}
Files Changed: {pr_data['changed_files']}
Additions: +{pr_data['additions']}
Deletions: -{pr_data['deletions']}
Comments: {pr_data['comments']}

Changed Files: {', '.join([f['filename'] for f in files_data[:10]])}

Provide a summary in this format:
**📝 PR #{pr_number}: [Title]**

🎯 **Purpose**: [One sentence purpose]

🔧 **Changes**:
• [Key change 1]
• [Key change 2]
• [Key change 3]

📊 **Stats**: 
• Files: X | Lines: +A/-D
• Complexity: [Low/Medium/High]

⚠️ **Risks**: [Any potential risks or concerns]

✅ **Recommendation**: [Approve/Review Needed/Changes Requested]

Keep it concise and actionable.
"""
            
            response = self.model.generate_content(prompt)
            summary = response.text
            
            # Add direct link
            summary += f"\n\n🔗 [View PR]({pr_data['html_url']})"
            
            return summary
            
        except Exception as e:
            logger.error(f"Error generating PR summary: {e}")
            return f"❌ Error generating summary: {str(e)}"
    
    def get_team_health(self, repository_id: Optional[int] = None) -> str:
        """
        Generate team health radar chart data
        
        Args:
            repository_id: Optional repository ID to filter
            
        Returns:
            Team health summary with metrics
        """
        try:
            # Calculate metrics
            if repository_id:
                repo = Repository.objects.get(id=repository_id)
                repositories = [repo]
            else:
                repositories = Repository.objects.all()[:5]  # Top 5 repos
            
            # Aggregate metrics
            total_commits = 0
            total_contributors = 0
            avg_deployment_freq = 0
            avg_lead_time = 0
            avg_mttr = 0
            avg_change_failure = 0
            
            for repo in repositories:
                # Create DORA calculator for this repository
                from api.dora_metrics import DORAMetricsCalculator
                dora_calculator = DORAMetricsCalculator(repo)
                metrics = dora_calculator.calculate_all_metrics()
                
                total_commits += repo.commits.count()
                total_contributors += Contributor.objects.filter(
                    repository_works__repository=repo
                ).distinct().count()
                
                # Parse DORA metrics
                if metrics['deployment_frequency']:
                    avg_deployment_freq += metrics['deployment_frequency'].get('daily_average', 0)
                if metrics['lead_time_for_changes']:
                    avg_lead_time += metrics['lead_time_for_changes'].get('average_hours', 0)
                if metrics['mean_time_to_restore']:
                    avg_mttr += metrics['mean_time_to_restore'].get('average_hours', 0)
                if metrics['change_failure_rate']:
                    avg_change_failure += metrics['change_failure_rate'].get('failure_rate', 0)
            
            num_repos = len(repositories)
            if num_repos > 0:
                avg_deployment_freq /= num_repos
                avg_lead_time /= num_repos
                avg_mttr /= num_repos
                avg_change_failure /= num_repos
            
            # Generate health report
            health_report = f"""
📊 **Team Health Dashboard**

**🎯 DORA Metrics**
• Deployment Frequency: {avg_deployment_freq:.1f} deploys/day
• Lead Time: {avg_lead_time:.1f} hours
• MTTR: {avg_mttr:.1f} hours  
• Change Failure Rate: {avg_change_failure:.1%}

**👥 Team Stats**
• Active Contributors: {total_contributors}
• Total Commits (30d): {total_commits}
• Repositories: {num_repos}

**📈 Health Indicators**
{self._generate_health_indicators(avg_deployment_freq, avg_lead_time, avg_mttr, avg_change_failure)}

**🎨 Radar Chart Data** (Copy to visualize):
```json
{{
  "labels": ["Deploy Freq", "Lead Time", "MTTR", "Quality", "Velocity"],
  "data": [{self._calculate_radar_scores(avg_deployment_freq, avg_lead_time, avg_mttr, avg_change_failure)}]
}}
```
"""
            return health_report
            
        except Exception as e:
            logger.error(f"Error generating team health: {e}")
            return f"❌ Error generating team health: {str(e)}"
    
    def _generate_health_indicators(self, deploy_freq, lead_time, mttr, failure_rate):
        """Generate health indicators with emojis"""
        indicators = []
        
        # Deployment Frequency
        if deploy_freq > 5:
            indicators.append("✅ Excellent deployment frequency")
        elif deploy_freq > 1:
            indicators.append("⚠️ Good deployment frequency")
        else:
            indicators.append("❌ Low deployment frequency")
        
        # Lead Time
        if lead_time < 24:
            indicators.append("✅ Fast lead time")
        elif lead_time < 72:
            indicators.append("⚠️ Moderate lead time")
        else:
            indicators.append("❌ Slow lead time")
        
        # MTTR
        if mttr < 1:
            indicators.append("✅ Excellent MTTR")
        elif mttr < 24:
            indicators.append("⚠️ Good MTTR")
        else:
            indicators.append("❌ High MTTR")
        
        # Failure Rate
        if failure_rate < 0.05:
            indicators.append("✅ Low failure rate")
        elif failure_rate < 0.15:
            indicators.append("⚠️ Moderate failure rate")
        else:
            indicators.append("❌ High failure rate")
        
        return "\n".join(indicators)
    
    def _calculate_radar_scores(self, deploy_freq, lead_time, mttr, failure_rate):
        """Calculate normalized radar scores (0-100)"""
        # Normalize to 0-100 scale
        deploy_score = min(deploy_freq * 10, 100)  # 10 deploys/day = 100
        lead_time_score = max(100 - lead_time, 0)  # Lower is better
        mttr_score = max(100 - mttr * 4, 0)  # Lower is better
        quality_score = max((1 - failure_rate) * 100, 0)  # Lower failure = better
        velocity_score = deploy_score  # Use deployment as proxy
        
        return f"{deploy_score:.0f}, {lead_time_score:.0f}, {mttr_score:.0f}, {quality_score:.0f}, {velocity_score:.0f}"
    
    def generate_daily_digest(self, date: Optional[datetime] = None) -> str:
        """
        Generate daily digest of activity
        
        Args:
            date: Date to generate digest for (defaults to yesterday)
            
        Returns:
            Formatted daily digest
        """
        if not date:
            date = timezone.now() - timedelta(days=1)
        
        start_date = date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = start_date + timedelta(days=1)
        
        try:
            # Get activity for the day
            commits = Commit.objects.filter(
                committed_at__gte=start_date,
                committed_at__lt=end_date
            )
            
            # Get unique contributors
            contributors = Contributor.objects.filter(
                commits__in=commits
            ).distinct()
            
            # Calculate stats
            total_commits = commits.count()
            total_additions = sum(c.additions for c in commits)
            total_deletions = sum(c.deletions for c in commits)
            total_files = sum(c.files_changed for c in commits)
            
            # Top contributors
            contributor_stats = {}
            for commit in commits:
                if commit.contributor:
                    username = commit.contributor.username
                    if username not in contributor_stats:
                        contributor_stats[username] = 0
                    contributor_stats[username] += 1
            
            top_contributors = sorted(
                contributor_stats.items(),
                key=lambda x: x[1],
                reverse=True
            )[:5]
            
            # Format digest
            digest = f"""
📅 **Daily Digest - {start_date.strftime('%B %d, %Y')}**

**📊 Activity Summary**
• Total Commits: {total_commits}
• Lines Added: +{total_additions}
• Lines Removed: -{total_deletions}
• Files Changed: {total_files}
• Active Contributors: {contributors.count()}

**🏆 Top Contributors**
{self._format_top_contributors(top_contributors)}

**🎯 Focus Areas**
{self._identify_focus_areas(commits)}

---
💡 *Keep up the great work! 🚀*
"""
            return digest
            
        except Exception as e:
            logger.error(f"Error generating daily digest: {e}")
            return f"❌ Error generating digest: {str(e)}"
    
    def _format_top_contributors(self, top_contributors: List[tuple]) -> str:
        """Format top contributors list"""
        if not top_contributors:
            return "• No activity today"
        
        medals = ['🥇', '🥈', '🥉', '  ', '  ']
        lines = []
        for i, (username, count) in enumerate(top_contributors):
            medal = medals[i] if i < len(medals) else '  '
            lines.append(f"{medal} {username}: {count} commits")
        
        return '\n'.join(lines)
    
    def _identify_focus_areas(self, commits) -> str:
        """Identify main focus areas from commits"""
        # Simple heuristic based on file changes
        frontend_keywords = ['jsx', 'tsx', 'css', 'html', 'component']
        backend_keywords = ['py', 'api', 'model', 'view', 'serializer']
        devops_keywords = ['docker', 'yml', 'yaml', 'deploy', 'ci']
        
        areas = {'frontend': 0, 'backend': 0, 'devops': 0, 'other': 0}
        
        for commit in commits:
            summary = commit.summary.lower()
            if any(kw in summary for kw in frontend_keywords):
                areas['frontend'] += 1
            elif any(kw in summary for kw in backend_keywords):
                areas['backend'] += 1
            elif any(kw in summary for kw in devops_keywords):
                areas['devops'] += 1
            else:
                areas['other'] += 1
        
        # Get top areas
        sorted_areas = sorted(areas.items(), key=lambda x: x[1], reverse=True)
        focus = [f"• {area.capitalize()}: {count} commits" for area, count in sorted_areas if count > 0]
        
        return '\n'.join(focus[:3]) if focus else "• Mixed development"
    
    def detect_risks(self) -> str:
        """
        Detect and alert on potential risks
        
        Returns:
            Risk alert message
        """
        try:
            risks = []
            
            # Check recent failures
            recent_commits = Commit.objects.filter(
                committed_at__gte=timezone.now() - timedelta(days=7)
            )
            
            # High churn rate
            high_churn_commits = [c for c in recent_commits if c.code_churn_ratio > 0.5]
            if len(high_churn_commits) > 10:
                risks.append({
                    'level': 'warning',
                    'title': 'High Code Churn',
                    'description': f'{len(high_churn_commits)} commits with >50% churn detected',
                    'action': 'Review code quality and refactoring practices'
                })
            
            # Large commits
            large_commits = [c for c in recent_commits if c.files_changed > 20]
            if len(large_commits) > 5:
                risks.append({
                    'level': 'warning',
                    'title': 'Large Commits',
                    'description': f'{len(large_commits)} commits changed >20 files',
                    'action': 'Encourage smaller, focused commits'
                })
            
            # Inactive contributors
            active_contributors = Contributor.objects.filter(
                commits__committed_at__gte=timezone.now() - timedelta(days=30)
            ).distinct().count()
            
            total_contributors = Contributor.objects.count()
            inactive_ratio = 1 - (active_contributors / max(total_contributors, 1))
            
            if inactive_ratio > 0.5:
                risks.append({
                    'level': 'critical',
                    'title': 'Low Team Activity',
                    'description': f'{inactive_ratio:.0%} of contributors inactive in last 30 days',
                    'action': 'Check team engagement and capacity'
                })
            
            # Format risks
            if not risks:
                return "✅ **No risks detected** - Everything looks good! 🎉"
            
            risk_message = "⚠️ **Risk Alerts Detected**\n\n"
            for risk in risks:
                emoji = '🔴' if risk['level'] == 'critical' else '🟡'
                risk_message += f"{emoji} **{risk['title']}**\n"
                risk_message += f"   {risk['description']}\n"
                risk_message += f"   💡 {risk['action']}\n\n"
            
            return risk_message
            
        except Exception as e:
            logger.error(f"Error detecting risks: {e}")
            return f"❌ Error detecting risks: {str(e)}"


class SlackBot(ChatBotService):
    """
    Slack bot integration
    """
    
    def __init__(self):
        super().__init__()
        self.webhook_url = os.getenv('SLACK_WEBHOOK_URL', '')
        self.bot_token = os.getenv('SLACK_BOT_TOKEN', '')
    
    def send_message(self, channel: str, message: str):
        """Send message to Slack channel"""
        if not self.webhook_url:
            logger.warning("Slack webhook URL not configured")
            return
        
        payload = {
            'text': message,
            'channel': channel
        }
        
        try:
            response = requests.post(self.webhook_url, json=payload)
            response.raise_for_status()
            logger.info(f"Message sent to Slack channel {channel}")
        except Exception as e:
            logger.error(f"Error sending Slack message: {e}")
    
    def handle_command(self, command: str, args: List[str]) -> str:
        """
        Handle slash commands
        
        Commands:
        - /langhub pr <number> - Get PR summary
        - /langhub team-health - Get team health metrics
        - /langhub digest - Get daily digest
        - /langhub risks - Get risk alerts
        """
        if command == 'pr' and len(args) >= 1:
            pr_number = int(args[0])
            repo_name = args[1] if len(args) > 1 else os.getenv('DEFAULT_REPO', 'owner/repo')
            return self.generate_pr_summary(pr_number, repo_name)
        
        elif command == 'team-health':
            repo_id = int(args[0]) if args else None
            return self.get_team_health(repo_id)
        
        elif command == 'digest':
            return self.generate_daily_digest()
        
        elif command == 'risks':
            return self.detect_risks()
        
        else:
            return self._help_message()
    
    def _help_message(self) -> str:
        """Generate help message"""
        return """
🤖 **LangHub Bot Commands**

`/langhub pr <number> [repo]` - AI summary of PR
`/langhub team-health [repo_id]` - Team health radar chart
`/langhub digest` - Yesterday's activity digest
`/langhub risks` - Detect potential risks
`/langhub help` - Show this message

Examples:
• `/langhub pr 123` - Summarize PR #123
• `/langhub team-health` - Show team metrics
"""


class DiscordBot(ChatBotService):
    """
    Discord bot integration
    """
    
    def __init__(self):
        super().__init__()
        self.webhook_url = os.getenv('DISCORD_WEBHOOK_URL', '')
    
    def send_message(self, message: str):
        """Send message to Discord channel"""
        if not self.webhook_url:
            logger.warning("Discord webhook URL not configured")
            return
        
        payload = {
            'content': message
        }
        
        try:
            response = requests.post(self.webhook_url, json=payload)
            response.raise_for_status()
            logger.info("Message sent to Discord")
        except Exception as e:
            logger.error(f"Error sending Discord message: {e}")
    
    def handle_command(self, command: str, args: List[str]) -> str:
        """
        Handle Discord bot commands
        Same as Slack but with Discord formatting
        """
        # Reuse Slack command handling
        slack_bot = SlackBot()
        return slack_bot.handle_command(command, args)


# Global instances
slack_bot = SlackBot()
discord_bot = DiscordBot()
