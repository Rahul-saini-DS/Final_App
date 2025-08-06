interface ProgressChartProps {
  data: {
    date: string;
    intelligence: number;
    physical: number;
    linguistic: number;
    total: number;
  }[];
  title?: string;
  className?: string;
}

export default function ProgressChart({ data, title = "Progress Over Time", className = "" }: ProgressChartProps) {
  const width = 600;
  const height = 300;
  const padding = { top: 20, right: 20, bottom: 40, left: 50 };
  const chartWidth = width - padding.left - padding.right;
  const chartHeight = height - padding.top - padding.bottom;

  // Get min/max values for scaling
  const allScores = data.flatMap(d => [d.intelligence, d.physical, d.linguistic, d.total]);
  const maxScore = Math.max(...allScores, 10); // Minimum scale of 10
  const minScore = Math.min(...allScores, 0);

  // Scale functions
  const scaleX = (index: number) => (index / Math.max(data.length - 1, 1)) * chartWidth;
  const scaleY = (value: number) => chartHeight - ((value - minScore) / (maxScore - minScore)) * chartHeight;

  // Create path strings for each category
  const createPath = (values: number[]) => {
    return values
      .map((value, index) => {
        const x = padding.left + scaleX(index);
        const y = padding.top + scaleY(value);
        return index === 0 ? `M ${x} ${y}` : `L ${x} ${y}`;
      })
      .join(' ');
  };

  const categories = [
    { key: 'total', color: '#6366f1', label: 'Total Score', strokeWidth: 3 },
    { key: 'intelligence', color: '#8b5cf6', label: 'Intelligence', strokeWidth: 2 },
    { key: 'physical', color: '#06b6d4', label: 'Physical', strokeWidth: 2 },
    { key: 'linguistic', color: '#10b981', label: 'Linguistic', strokeWidth: 2 }
  ];

  // Generate Y-axis labels
  const yAxisLabels = [];
  const steps = 5;
  for (let i = 0; i <= steps; i++) {
    const value = minScore + (maxScore - minScore) * (i / steps);
    yAxisLabels.push(Math.round(value));
  }

  if (data.length === 0) {
    return (
      <div className={`progress-chart ${className}`} style={{
        background: 'white',
        borderRadius: '15px',
        padding: '20px',
        boxShadow: '0 5px 15px rgba(0,0,0,0.1)',
        textAlign: 'center'
      }}>
        <h3 style={{
          margin: '0 0 20px 0',
          color: '#374151',
          fontSize: '18px',
          fontWeight: '600'
        }}>
          {title}
        </h3>
        <div style={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          padding: '40px',
          color: '#6b7280'
        }}>
          <div style={{ fontSize: '48px', marginBottom: '15px' }}>📈</div>
          <p>Take more assessments to see your progress over time!</p>
        </div>
      </div>
    );
  }

  return (
    <div className={`progress-chart ${className}`} style={{
      background: 'white',
      borderRadius: '15px',
      padding: '20px',
      boxShadow: '0 5px 15px rgba(0,0,0,0.1)'
    }}>
      <h3 style={{
        margin: '0 0 20px 0',
        color: '#374151',
        fontSize: '18px',
        fontWeight: '600',
        textAlign: 'center'
      }}>
        {title}
      </h3>

      <div style={{ display: 'flex', justifyContent: 'center', marginBottom: '20px' }}>
        <svg width={width} height={height} style={{ border: '1px solid #f3f4f6', borderRadius: '8px' }}>
          {/* Grid lines */}
          {yAxisLabels.map((label, index) => {
            const y = padding.top + chartHeight - (index / (yAxisLabels.length - 1)) * chartHeight;
            return (
              <g key={`grid-${index}`}>
                <line
                  x1={padding.left}
                  y1={y}
                  x2={width - padding.right}
                  y2={y}
                  stroke="#f3f4f6"
                  strokeWidth="1"
                />
                <text
                  x={padding.left - 10}
                  y={y}
                  textAnchor="end"
                  dominantBaseline="middle"
                  style={{ fontSize: '10px', fill: '#6b7280' }}
                >
                  {label}
                </text>
              </g>
            );
          })}

          {/* X-axis labels */}
          {data.map((point, index) => {
            const x = padding.left + scaleX(index);
            return (
              <text
                key={`x-label-${index}`}
                x={x}
                y={height - 10}
                textAnchor="middle"
                style={{ fontSize: '10px', fill: '#6b7280' }}
              >
                {new Date(point.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
              </text>
            );
          })}

          {/* Lines for each category */}
          {categories.map(category => {
            const values = data.map(d => d[category.key as keyof typeof d] as number);
            const path = createPath(values);
            
            return (
              <g key={category.key}>
                {/* Line */}
                <path
                  d={path}
                  fill="none"
                  stroke={category.color}
                  strokeWidth={category.strokeWidth}
                  strokeLinecap="round"
                  strokeLinejoin="round"
                />
                
                {/* Data points */}
                {values.map((value, index) => {
                  const x = padding.left + scaleX(index);
                  const y = padding.top + scaleY(value);
                  return (
                    <circle
                      key={`${category.key}-point-${index}`}
                      cx={x}
                      cy={y}
                      r="4"
                      fill={category.color}
                      stroke="white"
                      strokeWidth="2"
                    />
                  );
                })}
              </g>
            );
          })}
        </svg>
      </div>

      {/* Legend */}
      <div style={{
        display: 'flex',
        justifyContent: 'center',
        flexWrap: 'wrap',
        gap: '15px',
        fontSize: '12px'
      }}>
        {categories.map(category => (
          <div key={category.key} style={{ display: 'flex', alignItems: 'center', gap: '5px' }}>
            <div style={{
              width: '12px',
              height: '12px',
              background: category.color,
              borderRadius: '2px'
            }}></div>
            <span style={{ color: '#374151', fontWeight: '500' }}>{category.label}</span>
          </div>
        ))}
      </div>

      {/* Latest scores summary */}
      {data.length > 0 && (
        <div style={{
          marginTop: '20px',
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(120px, 1fr))',
          gap: '10px',
          fontSize: '12px'
        }}>
          {categories.slice(1).map(category => {
            const latestValue = data[data.length - 1][category.key as keyof typeof data[0]] as number;
            const previousValue = data.length > 1 ? data[data.length - 2][category.key as keyof typeof data[0]] as number : latestValue;
            const change = latestValue - previousValue;
            const trend = change > 0 ? '↗️' : change < 0 ? '↘️' : '➡️';
            
            return (
              <div key={category.key} style={{
                background: '#f9fafb',
                padding: '10px',
                borderRadius: '8px',
                border: '1px solid #e5e7eb',
                textAlign: 'center'
              }}>
                <div style={{ 
                  fontWeight: '600', 
                  color: category.color, 
                  marginBottom: '4px',
                  fontSize: '14px'
                }}>
                  {latestValue}
                </div>
                <div style={{ color: '#374151', marginBottom: '2px', fontSize: '11px' }}>
                  {category.label}
                </div>
                {data.length > 1 && (
                  <div style={{ 
                    color: change >= 0 ? '#10b981' : '#ef4444',
                    fontSize: '10px',
                    fontWeight: '500'
                  }}>
                    {trend} {change !== 0 ? Math.abs(change) : 'No change'}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
