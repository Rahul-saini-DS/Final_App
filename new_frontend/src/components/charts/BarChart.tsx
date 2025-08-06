import { useRef } from 'react';

interface BarChartProps {
  data: {
    intelligence: number;
    physical: number;
    linguistic: number;
  };
}

export default function BarChart({ data }: BarChartProps) {
  const chartRef = useRef<HTMLDivElement>(null);

  const categories = [
    { name: 'Intelligence', value: data.intelligence, color: '#6366f1', maxScore: 4 }, // Intelligence questions (usually 4)
    { name: 'Physical', value: data.physical, color: '#10b981', maxScore: 1 }, // Binary task (0 or 1)
    { name: 'Linguistic', value: data.linguistic, color: '#f59e0b', maxScore: 1 } // Binary task (0 or 1)
  ];

  return (
    <div ref={chartRef} style={{ padding: '20px' }}>
      <h3 style={{ textAlign: 'center', marginBottom: '20px', color: '#374151' }}>
        📊 Category Comparison
      </h3>
      <div style={{ 
        display: 'flex', 
        alignItems: 'flex-end', 
        justifyContent: 'space-around',
        height: '200px',
        border: '1px solid #e5e7eb',
        borderRadius: '10px',
        padding: '20px',
        background: 'linear-gradient(180deg, #f9fafb 0%, #ffffff 100%)'
      }}>
        {categories.map((category, index) => {
          const percentage = (category.value / category.maxScore) * 100;
          const height = Math.max(percentage * 1.5, 10); // Minimum height for visibility, scaled for better display
          
          return (
            <div key={index} style={{ 
              display: 'flex', 
              flexDirection: 'column', 
              alignItems: 'center',
              position: 'relative'
            }}>
              {/* Bar */}
              <div style={{
                width: '60px',
                height: `${Math.min(height, 150)}px`, // Cap maximum height and use pixels
                backgroundColor: category.value === 0 ? '#e5e7eb' : category.color, // Gray for zero values
                borderRadius: '8px 8px 0 0',
                transition: 'all 0.3s ease',
                position: 'relative',
                boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)',
                cursor: 'pointer',
                border: category.value === 0 ? '2px dashed #9ca3af' : 'none' // Dashed border for zero
              }}
              onMouseOver={(e) => {
                e.currentTarget.style.opacity = '0.8';
                e.currentTarget.style.transform = 'scale(1.05)';
              }}
              onMouseOut={(e) => {
                e.currentTarget.style.opacity = '1';
                e.currentTarget.style.transform = 'scale(1)';
              }}>
                {/* Score label on top of bar */}
                <div style={{
                  position: 'absolute',
                  top: '-25px',
                  left: '50%',
                  transform: 'translateX(-50%)',
                  background: 'rgba(0, 0, 0, 0.8)',
                  color: 'white',
                  padding: '4px 8px',
                  borderRadius: '4px',
                  fontSize: '12px',
                  fontWeight: 'bold'
                }}>
                  {category.value}/{category.maxScore}
                </div>
              </div>
              
              {/* Category label */}
              <div style={{
                marginTop: '10px',
                fontSize: '14px',
                fontWeight: '600',
                color: '#374151',
                textAlign: 'center'
              }}>
                {category.name}
              </div>
            </div>
          );
        })}
      </div>
      
      {/* Legend */}
      <div style={{
        display: 'flex',
        justifyContent: 'center',
        marginTop: '15px',
        gap: '20px'
      }}>
        {categories.map((category, index) => (
          <div key={index} style={{ display: 'flex', alignItems: 'center', gap: '5px' }}>
            <div style={{
              width: '12px',
              height: '12px',
              backgroundColor: category.color,
              borderRadius: '3px'
            }}></div>
            <span style={{ fontSize: '12px', color: '#6b7280' }}>
              {category.name}: {category.value}/{category.maxScore}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}
