

interface RadarChartProps {
  data: {
    category: string;
    userScore: number;
    averageScore: number;
    maxScore: number;
  }[];
  title?: string;
  className?: string;
}

export default function RadarChart({ data, title = "Performance Comparison", className = "" }: RadarChartProps) {
  const size = 300;
  const center = size / 2;
  const radius = size * 0.35;
  const levels = 5;

  // Calculate points for polygon
  const getPolygonPoints = (scores: number[], maxValues: number[]) => {
    return scores.map((score, index) => {
      const angle = (index * 2 * Math.PI) / data.length - Math.PI / 2;
      const normalizedScore = Math.min(score / maxValues[index], 1);
      const x = center + radius * normalizedScore * Math.cos(angle);
      const y = center + radius * normalizedScore * Math.sin(angle);
      return `${x},${y}`;
    }).join(' ');
  };

  // Calculate label positions
  const getLabelPosition = (index: number) => {
    const angle = (index * 2 * Math.PI) / data.length - Math.PI / 2;
    const labelRadius = radius + 30;
    const x = center + labelRadius * Math.cos(angle);
    const y = center + labelRadius * Math.sin(angle);
    return { x, y };
  };

  const userScores = data.map(d => d.userScore);
  const averageScores = data.map(d => d.averageScore);
  const maxValues = data.map(d => d.maxScore);

  return (
    <div className={`radar-chart ${className}`} style={{
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

      <div style={{ position: 'relative', display: 'inline-block' }}>
        <svg width={size} height={size} style={{ display: 'block' }}>
          {/* Background circles (levels) */}
          {Array.from({ length: levels }, (_, i) => {
            const levelRadius = radius * ((i + 1) / levels);
            return (
              <circle
                key={`level-${i}`}
                cx={center}
                cy={center}
                r={levelRadius}
                fill="none"
                stroke="#f3f4f6"
                strokeWidth="1"
              />
            );
          })}

          {/* Axis lines */}
          {data.map((_, index) => {
            const angle = (index * 2 * Math.PI) / data.length - Math.PI / 2;
            const x = center + radius * Math.cos(angle);
            const y = center + radius * Math.sin(angle);
            return (
              <line
                key={`axis-${index}`}
                x1={center}
                y1={center}
                x2={x}
                y2={y}
                stroke="#e5e7eb"
                strokeWidth="1"
              />
            );
          })}

          {/* Average scores polygon */}
          <polygon
            points={getPolygonPoints(averageScores, maxValues)}
            fill="rgba(156, 163, 175, 0.2)"
            stroke="#9ca3af"
            strokeWidth="2"
            strokeDasharray="5,5"
          />

          {/* User scores polygon */}
          <polygon
            points={getPolygonPoints(userScores, maxValues)}
            fill="rgba(99, 102, 241, 0.3)"
            stroke="#6366f1"
            strokeWidth="3"
          />

          {/* Data points for user scores */}
          {userScores.map((score, index) => {
            const angle = (index * 2 * Math.PI) / data.length - Math.PI / 2;
            const normalizedScore = Math.min(score / maxValues[index], 1);
            const x = center + radius * normalizedScore * Math.cos(angle);
            const y = center + radius * normalizedScore * Math.sin(angle);
            return (
              <circle
                key={`user-point-${index}`}
                cx={x}
                cy={y}
                r="4"
                fill="#6366f1"
                stroke="white"
                strokeWidth="2"
              />
            );
          })}

          {/* Data points for average scores */}
          {averageScores.map((score, index) => {
            const angle = (index * 2 * Math.PI) / data.length - Math.PI / 2;
            const normalizedScore = Math.min(score / maxValues[index], 1);
            const x = center + radius * normalizedScore * Math.cos(angle);
            const y = center + radius * normalizedScore * Math.sin(angle);
            return (
              <circle
                key={`avg-point-${index}`}
                cx={x}
                cy={y}
                r="3"
                fill="#9ca3af"
                stroke="white"
                strokeWidth="2"
              />
            );
          })}

          {/* Category labels */}
          {data.map((item, index) => {
            const { x, y } = getLabelPosition(index);
            return (
              <text
                key={`label-${index}`}
                x={x}
                y={y}
                textAnchor="middle"
                dominantBaseline="central"
                style={{
                  fontSize: '12px',
                  fontWeight: '600',
                  fill: '#374151'
                }}
              >
                {item.category}
              </text>
            );
          })}
        </svg>

        {/* Center score display */}
        <div style={{
          position: 'absolute',
          top: '50%',
          left: '50%',
          transform: 'translate(-50%, -50%)',
          background: 'rgba(255, 255, 255, 0.9)',
          borderRadius: '50px',
          padding: '10px',
          backdropFilter: 'blur(10px)',
          border: '2px solid rgba(99, 102, 241, 0.2)'
        }}>
          <div style={{ fontSize: '16px', fontWeight: '700', color: '#6366f1' }}>
            {Math.round(userScores.reduce((a, b) => a + b, 0) / userScores.length * 10) / 10}
          </div>
          <div style={{ fontSize: '10px', color: '#6b7280' }}>
            Avg Score
          </div>
        </div>
      </div>

      {/* Legend */}
      <div style={{
        display: 'flex',
        justifyContent: 'center',
        gap: '20px',
        marginTop: '15px',
        fontSize: '12px'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '5px' }}>
          <div style={{
            width: '12px',
            height: '12px',
            background: '#6366f1',
            borderRadius: '2px'
          }}></div>
          <span style={{ color: '#374151' }}>Your Score</span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '5px' }}>
          <div style={{
            width: '12px',
            height: '12px',
            background: '#9ca3af',
            borderRadius: '2px'
          }}></div>
          <span style={{ color: '#374151' }}>Age Group Average</span>
        </div>
      </div>

      {/* Score breakdown */}
      <div style={{
        marginTop: '20px',
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))',
        gap: '10px',
        fontSize: '12px'
      }}>
        {data.map((item, index) => (
          <div key={index} style={{
            background: '#f9fafb',
            padding: '8px',
            borderRadius: '8px',
            border: '1px solid #e5e7eb'
          }}>
            <div style={{ fontWeight: '600', color: '#374151', marginBottom: '2px' }}>
              {item.category}
            </div>
            <div style={{ color: '#6366f1', fontWeight: '600' }}>
              You: {item.userScore}/{item.maxScore}
            </div>
            <div style={{ color: '#9ca3af' }}>
              Avg: {item.averageScore.toFixed(1)}/{item.maxScore}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
