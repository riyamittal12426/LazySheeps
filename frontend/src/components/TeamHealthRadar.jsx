import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { 
  UsersIcon,
  ExclamationTriangleIcon,
  ArrowTrendingUpIcon,
  ArrowTrendingDownIcon,
  ClockIcon,
  CodeBracketIcon,
  CommandLineIcon,
  ChartBarIcon,
  HeartIcon,
  CheckCircleIcon,
  ExclamationCircleIcon,
  XCircleIcon,
  BoltIcon,
  PresentationChartLineIcon
} from '@heroicons/react/24/outline';
import './TeamHealthRadar.css';

const TeamHealthRadar = () => {
  const [teamData, setTeamData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedMember, setSelectedMember] = useState(null);
  const [view, setView] = useState('overview'); // 'overview' or 'heatmap'

  useEffect(() => {
    fetchTeamHealth();
  }, []);

  const fetchTeamHealth = async () => {
    try {
      setLoading(true);
      const response = await axios.get('http://localhost:8000/api/team-health/');
      setTeamData(response.data);
      setError(null);
    } catch (err) {
      console.error('Error fetching team health:', err);
      setError('Failed to load team health data');
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status) => {
    const colors = {
      green: '#10b981',
      yellow: '#f59e0b',
      red: '#ef4444'
    };
    return colors[status] || '#6b7280';
  };

  const getStatusIcon = (status) => {
    if (status === 'green') return <CheckCircleIcon className="status-icon green w-5 h-5" />;
    if (status === 'yellow') return <ExclamationCircleIcon className="status-icon yellow w-5 h-5" />;
    return <XCircleIcon className="status-icon red w-5 h-5" />;
  };

  const getHealthGradeColor = (grade) => {
    if (grade.includes('A')) return '#10b981';
    if (grade === 'B') return '#3b82f6';
    if (grade === 'C') return '#f59e0b';
    if (grade === 'D') return '#f97316';
    return '#ef4444';
  };

  const MetricCard = ({ icon: Icon, title, value, status, detail }) => (
    <div className={`metric-card metric-${status}`}>
      <div className="metric-header">
        <Icon className="metric-icon" />
        <span className="metric-title">{title}</span>
      </div>
      <div className="metric-value">{value}</div>
      {detail && <div className="metric-detail">{detail}</div>}
      {getStatusIcon(status)}
    </div>
  );

  const HeatmapCell = ({ value, label, status }) => (
    <div className={`heatmap-cell heatmap-${status}`} title={label}>
      <div className="heatmap-value">{value}</div>
    </div>
  );

  const TeamMemberCard = ({ member, onClick }) => {
    const { username, avatar_url, metrics, overall_health } = member;

    return (
      <div 
        className={`team-member-card priority-${member.priority}`}
        onClick={onClick}
      >
        <div className="member-header">
          <img 
            src={avatar_url || `https://ui-avatars.com/api/?name=${username}&background=random`} 
            alt={username}
            className="member-avatar"
          />
          <div className="member-info">
            <h3 className="member-name">{username}</h3>
            <div className="member-grade" style={{ color: getHealthGradeColor(overall_health.health_grade) }}>
              Grade: {overall_health.health_grade}
            </div>
          </div>
          <div className={`member-status member-status-${overall_health.status}`}>
            {overall_health.score.toFixed(0)}
          </div>
        </div>

        <div className="member-metrics">
          <div className="metric-row">
            <ChartBarIcon className="w-3.5 h-3.5" />
            <span>Workload</span>
            <div className={`metric-bar metric-${metrics.workload.status}`}>
              <div 
                className="metric-fill" 
                style={{ width: `${metrics.workload.score}%` }}
              />
            </div>
            <span className="metric-score">{metrics.workload.score}%</span>
          </div>

          <div className="metric-row">
            <HeartIcon className="w-3.5 h-3.5" />
            <span>Burnout</span>
            <div className={`metric-bar metric-${metrics.burnout_risk.status}`}>
              <div 
                className="metric-fill" 
                style={{ width: `${metrics.burnout_risk.score}%` }}
              />
            </div>
            <span className="metric-score">{metrics.burnout_risk.score}%</span>
          </div>

          <div className="metric-row">
            <ClockIcon className="w-3.5 h-3.5" />
            <span>Review Latency</span>
            <div className={`metric-bar metric-${metrics.review_latency.status}`}>
              <div 
                className="metric-fill" 
                style={{ width: `${metrics.review_latency.score}%` }}
              />
            </div>
            <span className="metric-score">{metrics.review_latency.score}%</span>
          </div>

          <div className="metric-row">
            <CodeBracketIcon className="w-3.5 h-3.5" />
            <span>Code Churn</span>
            <div className={`metric-bar metric-${metrics.code_churn.status}`}>
              <div 
                className="metric-fill" 
                style={{ width: `${metrics.code_churn.score}%` }}
              />
            </div>
            <span className="metric-score">{metrics.code_churn.score}%</span>
          </div>
        </div>
      </div>
    );
  };

  const TeamHeatmap = ({ teamHealth }) => (
    <div className="heatmap-container">
      <div className="heatmap-header">
        <div className="heatmap-label"></div>
        <div className="heatmap-label">Workload</div>
        <div className="heatmap-label">Burnout</div>
        <div className="heatmap-label">Reviews</div>
        <div className="heatmap-label">Churn</div>
        <div className="heatmap-label">Collab</div>
      </div>
      {teamHealth.map(member => (
        <div key={member.id} className="heatmap-row" onClick={() => setSelectedMember(member)}>
          <div className="heatmap-member-name">
            <img 
              src={member.avatar_url || `https://ui-avatars.com/api/?name=${member.username}&background=random`} 
              alt={member.username}
              className="heatmap-avatar"
            />
            {member.username}
          </div>
          <HeatmapCell 
            value={member.metrics.workload.score.toFixed(0)} 
            status={member.metrics.workload.status}
            label={`Workload: ${member.metrics.workload.score}%`}
          />
          <HeatmapCell 
            value={member.metrics.burnout_risk.score.toFixed(0)} 
            status={member.metrics.burnout_risk.status}
            label={`Burnout Risk: ${member.metrics.burnout_risk.score}%`}
          />
          <HeatmapCell 
            value={member.metrics.review_latency.score.toFixed(0)} 
            status={member.metrics.review_latency.status}
            label={`Review Latency: ${member.metrics.review_latency.score}%`}
          />
          <HeatmapCell 
            value={member.metrics.code_churn.score.toFixed(0)} 
            status={member.metrics.code_churn.status}
            label={`Code Churn: ${member.metrics.code_churn.score}%`}
          />
          <HeatmapCell 
            value={member.metrics.collaboration.score.toFixed(0)} 
            status={member.metrics.collaboration.status}
            label={`Collaboration: ${member.metrics.collaboration.score}%`}
          />
        </div>
      ))}
    </div>
  );

  const RecommendationCard = ({ recommendation }) => {
    const priorityColors = {
      high: '#ef4444',
      warning: '#f59e0b',
      info: '#3b82f6'
    };

    return (
      <div 
        className="recommendation-card" 
        style={{ borderLeftColor: priorityColors[recommendation.priority] }}
      >
        <div className="recommendation-header">
          <ExclamationTriangleIcon 
            className="w-5 h-5" 
            style={{ color: priorityColors[recommendation.priority] }}
          />
          <span className="recommendation-category">{recommendation.category}</span>
        </div>
        <div className="recommendation-message">{recommendation.message}</div>
        {recommendation.actions && recommendation.actions.length > 0 && (
          <div className="recommendation-actions">
            <strong>Actions:</strong>
            <ul>
              {recommendation.actions.map((action, idx) => (
                <li key={idx}>{action}</li>
              ))}
            </ul>
          </div>
        )}
      </div>
    );
  };

  if (loading) {
    return (
      <div className="team-health-container">
        <div className="loading-spinner">
          <ChartBarIcon className="spinner-icon w-12 h-12 animate-spin" />
          <p>Analyzing team health...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="team-health-container">
        <div className="error-message">
          <ExclamationTriangleIcon className="w-12 h-12" />
          <p>{error}</p>
          <button onClick={fetchTeamHealth} className="retry-button">
            Try Again
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="team-health-container">
      <div className="team-health-header">
        <div className="header-title">
          <PresentationChartLineIcon className="header-icon w-8 h-8" />
          <h1>Team Health Radar</h1>
        </div>
        <div className="header-actions">
          <button 
            className={`view-toggle ${view === 'overview' ? 'active' : ''}`}
            onClick={() => setView('overview')}
          >
            <UsersIcon className="w-4.5 h-4.5" />
            Overview
          </button>
          <button 
            className={`view-toggle ${view === 'heatmap' ? 'active' : ''}`}
            onClick={() => setView('heatmap')}
          >
            <CommandLineIcon className="w-4.5 h-4.5" />
            Heatmap
          </button>
          <button onClick={fetchTeamHealth} className="refresh-button">
            <BoltIcon className="w-4.5 h-4.5" />
            Refresh
          </button>
        </div>
      </div>

      {/* Overall Team Stats */}
      <div className="team-stats-grid">
        <MetricCard
          icon={UsersIcon}
          title="Team Members"
          value={teamData.overall_stats.total_members}
          status="green"
          detail="Total contributors"
        />
        <MetricCard
          icon={ExclamationCircleIcon}
          title="At Risk"
          value={teamData.overall_stats.at_risk_count}
          status={teamData.overall_stats.at_risk_count > 0 ? 'red' : 'green'}
          detail="Need immediate attention"
        />
        <MetricCard
          icon={ExclamationTriangleIcon}
          title="Warning"
          value={teamData.overall_stats.warning_count}
          status={teamData.overall_stats.warning_count > 0 ? 'yellow' : 'green'}
          detail="Monitor closely"
        />
        <MetricCard
          icon={CheckCircleIcon}
          title="Healthy"
          value={teamData.overall_stats.healthy_count}
          status="green"
          detail="Performing well"
        />
        <MetricCard
          icon={ChartBarIcon}
          title="Avg Workload"
          value={`${teamData.overall_stats.avg_workload}%`}
          status={
            teamData.overall_stats.avg_workload < 40 ? 'green' :
            teamData.overall_stats.avg_workload < 70 ? 'yellow' : 'red'
          }
          detail="Team average"
        />
        <MetricCard
          icon={HeartIcon}
          title="Avg Burnout Risk"
          value={`${teamData.overall_stats.avg_burnout_risk}%`}
          status={
            teamData.overall_stats.avg_burnout_risk < 30 ? 'green' :
            teamData.overall_stats.avg_burnout_risk < 60 ? 'yellow' : 'red'
          }
          detail="Team average"
        />
      </div>

      {/* Team Recommendations */}
      {teamData.team_recommendations && teamData.team_recommendations.length > 0 && (
        <div className="recommendations-section">
          <h2>
            <ExclamationTriangleIcon className="w-6 h-6" />
            Actionable Recommendations
          </h2>
          <div className="recommendations-grid">
            {teamData.team_recommendations.map((rec, idx) => (
              <RecommendationCard key={idx} recommendation={rec} />
            ))}
          </div>
        </div>
      )}

      {/* View Toggle */}
      {view === 'heatmap' ? (
        <div className="heatmap-section">
          <h2>
            <CommandLineIcon className="w-6 h-6" />
            Team Health Heatmap
          </h2>
          <TeamHeatmap teamHealth={teamData.team_health} />
          <div className="heatmap-legend">
            <span className="legend-item">
              <span className="legend-color" style={{ background: '#10b981' }}></span>
              Green (0-40): Healthy
            </span>
            <span className="legend-item">
              <span className="legend-color" style={{ background: '#f59e0b' }}></span>
              Yellow (40-70): Warning
            </span>
            <span className="legend-item">
              <span className="legend-color" style={{ background: '#ef4444' }}></span>
              Red (70+): At Risk
            </span>
          </div>
        </div>
      ) : (
        <div className="team-members-section">
          <h2>
            <UsersIcon className="w-6 h-6" />
            Team Members ({teamData.team_health.length})
          </h2>
          <div className="team-members-grid">
            {teamData.team_health.map(member => (
              <TeamMemberCard
                key={member.id}
                member={member}
                onClick={() => setSelectedMember(member)}
              />
            ))}
          </div>
        </div>
      )}

      {/* Member Detail Modal */}
      {selectedMember && (
        <div className="modal-overlay" onClick={() => setSelectedMember(null)}>
          <div className="modal-content" onClick={e => e.stopPropagation()}>
            <button className="modal-close" onClick={() => setSelectedMember(null)}>×</button>
            
            <div className="modal-header">
              <img 
                src={selectedMember.avatar_url || `https://ui-avatars.com/api/?name=${selectedMember.username}&background=random`}
                alt={selectedMember.username}
                className="modal-avatar"
              />
              <div>
                <h2>{selectedMember.username}</h2>
                <div className="modal-grade" style={{ color: getHealthGradeColor(selectedMember.overall_health.health_grade) }}>
                  Health Grade: {selectedMember.overall_health.health_grade} ({selectedMember.overall_health.score.toFixed(1)}/100)
                </div>
              </div>
            </div>

            <div className="modal-metrics">
              <div className="modal-metric">
                <ChartBarIcon className="w-5 h-5" />
                <div className="modal-metric-info">
                  <strong>Workload</strong>
                  <div className="modal-metric-bar">
                    <div 
                      className={`modal-metric-fill metric-${selectedMember.metrics.workload.status}`}
                      style={{ width: `${selectedMember.metrics.workload.score}%` }}
                    />
                  </div>
                  <p>{selectedMember.metrics.workload.recommendation}</p>
                  <span className="metric-details">
                    {selectedMember.metrics.workload.recent_commits} commits, {selectedMember.metrics.workload.recent_issues} issues (30 days)
                  </span>
                </div>
              </div>

              <div className="modal-metric">
                <HeartIcon className="w-5 h-5" />
                <div className="modal-metric-info">
                  <strong>Burnout Risk</strong>
                  <div className="modal-metric-bar">
                    <div 
                      className={`modal-metric-fill metric-${selectedMember.metrics.burnout_risk.status}`}
                      style={{ width: `${selectedMember.metrics.burnout_risk.score}%` }}
                    />
                  </div>
                  <p>{selectedMember.metrics.burnout_risk.recommendation}</p>
                  <span className="metric-details">
                    Weekend work: {selectedMember.metrics.burnout_risk.weekend_work_ratio}% | 
                    Late nights: {selectedMember.metrics.burnout_risk.late_night_ratio}%
                    {selectedMember.metrics.burnout_risk.activity_spike && ' | 🚨 Activity spike detected'}
                  </span>
                </div>
              </div>

              <div className="modal-metric">
                <ClockIcon className="w-5 h-5" />
                <div className="modal-metric-info">
                  <strong>Review Latency</strong>
                  <div className="modal-metric-bar">
                    <div 
                      className={`modal-metric-fill metric-${selectedMember.metrics.review_latency.status}`}
                      style={{ width: `${selectedMember.metrics.review_latency.score}%` }}
                    />
                  </div>
                  <p>{selectedMember.metrics.review_latency.recommendation}</p>
                  <span className="metric-details">
                    Avg response: {selectedMember.metrics.review_latency.avg_response_days} days | 
                    Pending: {selectedMember.metrics.review_latency.pending_reviews}
                  </span>
                </div>
              </div>

              <div className="modal-metric">
                <CodeBracketIcon className="w-5 h-5" />
                <div className="modal-metric-info">
                  <strong>Code Churn</strong>
                  <div className="modal-metric-bar">
                    <div 
                      className={`modal-metric-fill metric-${selectedMember.metrics.code_churn.status}`}
                      style={{ width: `${selectedMember.metrics.code_churn.score}%` }}
                    />
                  </div>
                  <p>{selectedMember.metrics.code_churn.recommendation}</p>
                  <span className="metric-details">
                    +{selectedMember.metrics.code_churn.total_additions} / 
                    -{selectedMember.metrics.code_churn.total_deletions} | 
                    Ratio: {selectedMember.metrics.code_churn.churn_ratio}
                  </span>
                </div>
              </div>

              <div className="modal-metric">
                <CommandLineIcon className="w-5 h-5" />
                <div className="modal-metric-info">
                  <strong>Collaboration</strong>
                  <div className="modal-metric-bar">
                    <div 
                      className={`modal-metric-fill metric-${selectedMember.metrics.collaboration.status}`}
                      style={{ width: `${selectedMember.metrics.collaboration.score}%` }}
                    />
                  </div>
                  <p>{selectedMember.metrics.collaboration.recommendation}</p>
                  <span className="metric-details">
                    Issues created: {selectedMember.metrics.collaboration.issues_created}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      <div className="team-health-footer">
        <p className="update-time">
          Last updated: {new Date(teamData.last_updated).toLocaleString()}
        </p>
      </div>
    </div>
  );
};

export default TeamHealthRadar;
