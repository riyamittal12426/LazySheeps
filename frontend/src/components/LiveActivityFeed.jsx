import { useEffect, useState } from 'react';
import { BellIcon, CodeBracketIcon, ChatBubbleLeftIcon, ExclamationCircleIcon } from '@heroicons/react/24/outline';

export default function LiveActivityFeed() {
    const [events, setEvents] = useState([]);
    const [connected, setConnected] = useState(false);

    useEffect(() => {
        // Connect to Server-Sent Events stream
        const eventSource = new EventSource('http://localhost:8000/api/events/stream/');
        
        eventSource.onopen = () => {
            console.log('✅ Connected to live event stream');
            setConnected(true);
        };
        
        eventSource.onmessage = (e) => {
            try {
                const event = JSON.parse(e.data);
                console.log('📡 Received event:', event);
                
                // Add to events list (keep last 20)
                setEvents(prev => [event, ...prev].slice(0, 20));
                
                // Show browser notification if permitted
                if (Notification.permission === 'granted') {
                    showNotification(event);
                }
            } catch (err) {
                // Ignore heartbeat messages
            }
        };
        
        eventSource.onerror = (err) => {
            // Silently fail if endpoint doesn't exist (feature not yet implemented)
            setConnected(false);
            eventSource.close();
        };
        
        // Request notification permission
        if (Notification.permission === 'default') {
            Notification.requestPermission();
        }
        
        // Cleanup on unmount
        return () => {
            eventSource.close();
        };
    }, []);

    const showNotification = (event) => {
        const { type, data } = event;
        let title = '';
        let body = '';
        
        switch (type) {
            case 'push':
                title = '📝 New Commits Pushed';
                body = `${data.author} pushed ${data.commits} commit(s) to ${data.repository}`;
                break;
            case 'pull_request':
                title = '🔀 Pull Request Activity';
                body = `${data.author} ${data.action} PR #${data.number}: ${data.title}`;
                break;
            case 'issues':
                title = '🐛 Issue Activity';
                body = `Issue #${data.issue_number} ${data.action} in ${data.repository}`;
                break;
            default:
                return;
        }
        
        new Notification(title, { body, icon: '/logo.png' });
    };

    const getEventIcon = (type) => {
        switch (type) {
            case 'push':
                return <CodeBracketIcon className="h-5 w-5 text-blue-500" />;
            case 'pull_request':
                return <ChatBubbleLeftIcon className="h-5 w-5 text-purple-500" />;
            case 'issues':
                return <ExclamationCircleIcon className="h-5 w-5 text-red-500" />;
            default:
                return <BellIcon className="h-5 w-5 text-gray-500" />;
        }
    };

    const formatEventMessage = (event) => {
        const { type, data } = event;
        
        switch (type) {
            case 'push':
                return (
                    <div>
                        <span className="font-semibold text-blue-600">{data.author}</span>
                        {' '}pushed {data.commits} commit{data.commits > 1 ? 's' : ''} to{' '}
                        <span className="font-medium">{data.repository}</span>
                    </div>
                );
            case 'pull_request':
                return (
                    <div>
                        <span className="font-semibold text-purple-600">{data.author}</span>
                        {' '}{data.action} PR{' '}
                        <span className="font-medium">#{data.number}</span>:{' '}
                        {data.title}
                    </div>
                );
            case 'issues':
                return (
                    <div>
                        Issue <span className="font-medium">#{data.issue_number}</span>
                        {' '}{data.action} in{' '}
                        <span className="font-medium">{data.repository}</span>
                    </div>
                );
            default:
                return <div>Unknown event</div>;
        }
    };

    const formatTimestamp = (timestamp) => {
        const seconds = Math.floor((Date.now() / 1000) - timestamp);
        if (seconds < 60) return `${seconds}s ago`;
        if (seconds < 3600) return `${Math.floor(seconds / 60)}m ago`;
        if (seconds < 86400) return `${Math.floor(seconds / 3600)}h ago`;
        return `${Math.floor(seconds / 86400)}d ago`;
    };

    return (
        <div className="bg-white rounded-lg shadow-lg p-6">
            {/* Header */}
            <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-bold text-gray-900 flex items-center gap-2">
                    {connected ? (
                        <span className="flex items-center">
                            <span className="relative flex h-3 w-3 mr-2">
                                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
                                <span className="relative inline-flex rounded-full h-3 w-3 bg-green-500"></span>
                            </span>
                            Live Activity
                        </span>
                    ) : (
                        <span className="flex items-center">
                            <span className="h-3 w-3 rounded-full bg-red-500 mr-2"></span>
                            Disconnected
                        </span>
                    )}
                </h3>
                {events.length > 0 && (
                    <span className="text-sm text-gray-500">
                        {events.length} event{events.length > 1 ? 's' : ''}
                    </span>
                )}
            </div>

            {/* Events List */}
            <div className="space-y-3 max-h-96 overflow-y-auto">
                {events.length === 0 ? (
                    <div className="text-center py-8 text-gray-500">
                        <BellIcon className="h-12 w-12 mx-auto mb-2 text-gray-400" />
                        <p>Waiting for activity...</p>
                        <p className="text-sm mt-1">Push code to GitHub to see real-time updates</p>
                    </div>
                ) : (
                    events.map((event, index) => (
                        <div
                            key={index}
                            className="flex items-start gap-3 p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors animate-fadeIn"
                        >
                            <div className="mt-0.5">
                                {getEventIcon(event.type)}
                            </div>
                            <div className="flex-1 min-w-0">
                                <div className="text-sm text-gray-900">
                                    {formatEventMessage(event)}
                                </div>
                                <div className="text-xs text-gray-500 mt-1">
                                    {formatTimestamp(event.timestamp)}
                                </div>
                            </div>
                        </div>
                    ))
                )}
            </div>

            {/* Connection Status */}
            {!connected && events.length > 0 && (
                <div className="mt-4 p-3 bg-yellow-50 border border-yellow-200 rounded-lg text-sm text-yellow-800">
                    ⚠️ Reconnecting to live feed...
                </div>
            )}
        </div>
    );
}
