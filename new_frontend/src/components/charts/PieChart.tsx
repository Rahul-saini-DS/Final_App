import { useState } from 'react';

interface PieChartProps {
  data: {
    intelligence: number;
    physical: number;
    linguistic: number;
  };
}

export default function PieChart({ data }: PieChartProps) {
  const [hoveredSegment, setHoveredSegment] = useState<string | null>(null);
  
  const total = data.intelligence + data.physical + data.linguistic;
  
  if (total === 0) {
    return (
      <div style={{ padding: '20px', textAlign: 'center' }}>
        <h3 style={{ color: '#374151', marginBottom: '20px' }}>🥧 Score Distribution</h3>
        <div style={{
          width: '200px',
          height: '200px',
          borderRadius: '50%',
          background: '#e5e7eb',
          margin: '0 auto',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          color: '#6b7280'
        }}>
          No scores yet
        </div>
      </div>
    );
  }

  const categories = [
    { name: 'Intelligence', value: data.intelligence, color: '#6366f1', emoji: '🧠' },
    { name: 'Physical', value: data.physical, color: '#10b981', emoji: '💪' },
    { name: 'Linguistic', value: data.linguistic, color: '#f59e0b', emoji: '🗣️' }
  ]; // Don't filter out zero values - show all categories

  // For zero values, use a small slice to make them visible
  const adjustedCategories = categories.map(cat => ({
    ...cat,
    displayValue: cat.value === 0 ? 0.1 : cat.value // Small value for display purposes
  }));

  const adjustedTotal = adjustedCategories.reduce((sum, cat) => sum + cat.displayValue, 0);

  let cumulativePercentage = 0;

  return (
    <div style={{ padding: '20px' }}>
      <h3 style={{ textAlign: 'center', marginBottom: '20px', color: '#374151' }}>
        🥧 Score Distribution
      </h3>
      
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', gap: '30px' }}>
        {/* Pie Chart */}
        <div style={{ position: 'relative' }}>
          <svg width="200" height="200" style={{ transform: 'rotate(-90deg)' }}>
            {adjustedCategories.map((category, index) => {
              const percentage = (category.displayValue / adjustedTotal) * 100;
              const angle = (percentage / 100) * 360;
              const startAngle = (cumulativePercentage / 100) * 360;
              
              // Calculate path for SVG arc
              const radius = 80;
              const centerX = 100;
              const centerY = 100;
              
              const startAngleRad = (startAngle * Math.PI) / 180;
              const endAngleRad = ((startAngle + angle) * Math.PI) / 180;
              
              const x1 = centerX + radius * Math.cos(startAngleRad);
              const y1 = centerY + radius * Math.sin(startAngleRad);
              const x2 = centerX + radius * Math.cos(endAngleRad);
              const y2 = centerY + radius * Math.sin(endAngleRad);
              
              const largeArcFlag = angle > 180 ? 1 : 0;
              
              const pathData = [
                `M ${centerX} ${centerY}`,
                `L ${x1} ${y1}`,
                `A ${radius} ${radius} 0 ${largeArcFlag} 1 ${x2} ${y2}`,
                'Z'
              ].join(' ');
              
              cumulativePercentage += percentage;
              
              return (
                <path
                  key={index}
                  d={pathData}
                  fill={category.value === 0 ? '#e5e7eb' : category.color} // Gray for zero values
                  stroke="white"
                  strokeWidth="2"
                  style={{
                    cursor: 'pointer',
                    opacity: hoveredSegment === category.name ? 0.8 : 1,
                    transform: hoveredSegment === category.name ? 'scale(1.05)' : 'scale(1)',
                    transformOrigin: 'center',
                    transition: 'all 0.2s ease'
                  }}
                  onMouseEnter={() => setHoveredSegment(category.name)}
                  onMouseLeave={() => setHoveredSegment(null)}
                />
              );
            })}
            
            {/* Center circle */}
            <circle
              cx="100"
              cy="100"
              r="30"
              fill="white"
              stroke="#e5e7eb"
              strokeWidth="2"
            />
            
            {/* Total score in center */}
            <text
              x="100"
              y="95"
              textAnchor="middle"
              style={{ 
                fontSize: '14px', 
                fontWeight: 'bold', 
                fill: '#374151',
                transform: 'rotate(90deg)',
                transformOrigin: '100px 100px'
              }}
            >
              Total
            </text>
            <text
              x="100"
              y="110"
              textAnchor="middle"
              style={{ 
                fontSize: '18px', 
                fontWeight: 'bold', 
                fill: '#6366f1',
                transform: 'rotate(90deg)',
                transformOrigin: '100px 100px'
              }}
            >
              {total}
            </text>
          </svg>
        </div>
        
        {/* Legend */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
          {categories.map((category, index) => {
            const percentage = ((category.value / total) * 100).toFixed(1);
            return (
              <div
                key={index}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '10px',
                  padding: '8px',
                  borderRadius: '6px',
                  background: hoveredSegment === category.name ? '#f3f4f6' : 'transparent',
                  cursor: 'pointer',
                  transition: 'background 0.2s ease'
                }}
                onMouseEnter={() => setHoveredSegment(category.name)}
                onMouseLeave={() => setHoveredSegment(null)}
              >
                <div style={{
                  width: '16px',
                  height: '16px',
                  backgroundColor: category.color,
                  borderRadius: '4px'
                }}></div>
                <div style={{ fontSize: '14px' }}>
                  <span style={{ fontWeight: '600' }}>{category.emoji} {category.name}</span>
                  <br />
                  <span style={{ color: '#6b7280', fontSize: '12px' }}>
                    {category.value} points ({percentage}%)
                  </span>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
