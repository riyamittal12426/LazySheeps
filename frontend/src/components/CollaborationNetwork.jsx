import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';

const CollaborationNetwork = ({ repoId = null }) => {
  const [networkData, setNetworkData] = useState({ nodes: [], edges: [] });
  const [loading, setLoading] = useState(true);
  const [selectedNode, setSelectedNode] = useState(null);
  const canvasRef = useRef(null);

  useEffect(() => {
    fetchNetworkData();
  }, [repoId]);

  useEffect(() => {
    if (networkData.nodes.length > 0 && canvasRef.current) {
      drawNetwork();
    }
  }, [networkData, selectedNode]);

  const fetchNetworkData = async () => {
    try {
      const url = repoId 
        ? `http://localhost:8000/api/collaboration/network/?repo_id=${repoId}`
        : 'http://localhost:8000/api/collaboration/network/';
      
      const response = await axios.get(url);
      setNetworkData(response.data);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching network data:', error);
      setLoading(false);
    }
  };

  const drawNetwork = () => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    const width = canvas.width;
    const height = canvas.height;

    // Clear canvas
    ctx.clearRect(0, 0, width, height);

    // Simple circular layout
    const { nodes, edges } = networkData;
    const centerX = width / 2;
    const centerY = height / 2;
    const radius = Math.min(width, height) / 3;

    // Position nodes in a circle
    const nodePositions = nodes.map((node, index) => {
      const angle = (2 * Math.PI * index) / nodes.length;
      return {
        ...node,
        x: centerX + radius * Math.cos(angle),
        y: centerY + radius * Math.sin(angle),
      };
    });

    // Draw edges
    ctx.strokeStyle = 'rgba(100, 116, 139, 0.3)';
    edges.forEach(edge => {
      const source = nodePositions.find(n => n.id === edge.source);
      const target = nodePositions.find(n => n.id === edge.target);
      
      if (source && target) {
        ctx.lineWidth = Math.max(1, edge.strength * 3);
        ctx.beginPath();
        ctx.moveTo(source.x, source.y);
        ctx.lineTo(target.x, target.y);
        ctx.stroke();
      }
    });

    // Draw nodes
    nodePositions.forEach(node => {
      const isSelected = selectedNode && selectedNode.id === node.id;
      const nodeSize = Math.max(8, Math.min(20, node.score / 300));
      
      // Node color based on score
      let color;
      if (isSelected) {
        color = '#ef4444';
      } else if (node.score > 5000) {
        color = '#8b5cf6';
      } else if (node.score > 2000) {
        color = '#3b82f6';
      } else {
        color = '#10b981';
      }

      // Draw node circle
      ctx.fillStyle = color;
      ctx.beginPath();
      ctx.arc(node.x, node.y, nodeSize, 0, 2 * Math.PI);
      ctx.fill();

      // Draw border
      ctx.strokeStyle = '#ffffff';
      ctx.lineWidth = 2;
      ctx.stroke();

      // Draw label
      ctx.fillStyle = '#1f2937';
      ctx.font = '12px sans-serif';
      ctx.textAlign = 'center';
      ctx.fillText(node.name, node.x, node.y + nodeSize + 15);
    });
  };

  const handleCanvasClick = (e) => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const rect = canvas.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;

    // Check if click is on a node
    const { nodes } = networkData;
    const centerX = canvas.width / 2;
    const centerY = canvas.height / 2;
    const radius = Math.min(canvas.width, canvas.height) / 3;

    const nodePositions = nodes.map((node, index) => {
      const angle = (2 * Math.PI * index) / nodes.length;
      return {
        ...node,
        x: centerX + radius * Math.cos(angle),
        y: centerY + radius * Math.sin(angle),
      };
    });

    const clickedNode = nodePositions.find(node => {
      const nodeSize = Math.max(8, Math.min(20, node.score / 300));
      const distance = Math.sqrt((x - node.x) ** 2 + (y - node.y) ** 2);
      return distance <= nodeSize;
    });

    setSelectedNode(clickedNode || null);
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-96 bg-white rounded-lg shadow-lg">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading collaboration network...</p>
        </div>
      </div>
    );
  }

  if (networkData.nodes.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow-lg p-8 text-center">
        <div className="text-6xl mb-4">🤝</div>
        <h3 className="text-xl font-semibold text-gray-700 mb-2">No Collaboration Data</h3>
        <p className="text-gray-500">Collaboration data will appear here once contributors start working together.</p>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-lg overflow-hidden">
      <div className="p-4 bg-gradient-to-r from-blue-500 to-purple-600">
        <h2 className="text-xl font-bold text-white flex items-center gap-2">
          <span>🤝</span>
          <span>Collaboration Network</span>
        </h2>
        <p className="text-blue-100 text-sm mt-1">
          {networkData.nodes.length} contributors · {networkData.edges.length} collaborations
        </p>
      </div>

      <div className="relative bg-gray-50" style={{ height: '600px' }}>
        <canvas
          ref={canvasRef}
          width={800}
          height={600}
          onClick={handleCanvasClick}
          className="w-full h-full cursor-pointer"
          style={{ maxWidth: '100%' }}
        />

        {/* Legend */}
        <div className="absolute top-4 left-4 bg-white/90 backdrop-blur-sm rounded-lg shadow-lg p-4">
          <h4 className="font-semibold text-gray-800 mb-2">Legend</h4>
          <div className="space-y-2 text-sm">
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 rounded-full bg-purple-600"></div>
              <span>High Score (&gt;5000)</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 rounded-full bg-blue-600"></div>
              <span>Medium Score (2000-5000)</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 rounded-full bg-green-600"></div>
              <span>Regular (&lt;2000)</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-8 h-0.5 bg-gray-400"></div>
              <span>Collaboration</span>
            </div>
          </div>
        </div>

        {/* Selected Node Info */}
        {selectedNode && (
          <div className="absolute top-4 right-4 bg-white rounded-lg shadow-lg p-4 max-w-xs">
            <div className="flex items-center gap-3 mb-3">
              <img
                src={selectedNode.avatar}
                alt={selectedNode.name}
                className="w-12 h-12 rounded-full border-2 border-blue-500"
              />
              <div>
                <h4 className="font-bold text-gray-800">{selectedNode.name}</h4>
                <p className="text-sm text-gray-600">Level {selectedNode.level}</p>
              </div>
            </div>
            <div className="space-y-1 text-sm">
              <div className="flex justify-between">
                <span className="text-gray-600">Score:</span>
                <span className="font-semibold text-blue-600">{selectedNode.score.toLocaleString()}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Collaborations:</span>
                <span className="font-semibold">
                  {networkData.edges.filter(e => 
                    e.source === selectedNode.id || e.target === selectedNode.id
                  ).length}
                </span>
              </div>
            </div>
            <button
              onClick={() => setSelectedNode(null)}
              className="mt-3 w-full px-3 py-1 text-sm bg-gray-100 hover:bg-gray-200 rounded transition-colors"
            >
              Close
            </button>
          </div>
        )}
      </div>

      {/* Controls */}
      <div className="p-4 bg-gray-50 border-t border-gray-200">
        <div className="flex items-center justify-between text-sm text-gray-600">
          <span>💡 Tip: Click on nodes to see details</span>
          <button
            onClick={fetchNetworkData}
            className="px-3 py-1 bg-blue-500 text-white rounded hover:bg-blue-600 transition-colors"
          >
            Refresh
          </button>
        </div>
      </div>
    </div>
  );
};

export default CollaborationNetwork;
