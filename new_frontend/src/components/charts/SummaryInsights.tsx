interface SummaryInsightsProps {
  data: {
    intelligence: number;
    physical: number;
    linguistic: number;
  };
  ageGroup: string;
  maxTotal?: number; // Optional prop for maximum total score
}

export default function SummaryInsights({ data, ageGroup, maxTotal = 6 }: SummaryInsightsProps) {
  const { intelligence, physical, linguistic } = data;
  const total = intelligence + physical + linguistic;
  
  // Generate insights based on scores
  const generateInsights = () => {
    const insights = [];
    const maxScore = Math.max(intelligence, physical, linguistic);
    const minScore = Math.min(intelligence, physical, linguistic);
    
    // Determine strongest area
    if (intelligence === maxScore && intelligence > 0) {
      insights.push({
        type: 'strength',
        icon: '🌟',
        text: `Excellent intelligence skills! Your child shows strong cognitive abilities.`,
        color: '#10b981'
      });
    }
    
    if (physical === maxScore && physical > 0) {
      insights.push({
        type: 'strength',
        icon: '💪',
        text: `Great physical development! Your child has good motor skills.`,
        color: '#10b981'
      });
    }
    
    if (linguistic === maxScore && linguistic > 0) {
      insights.push({
        type: 'strength',
        icon: '🗣️',
        text: `Strong linguistic abilities! Your child communicates very well.`,
        color: '#10b981'
      });
    }
    
    // Suggest improvements
    if (intelligence === minScore && intelligence < 1) {
      insights.push({
        type: 'improvement',
        icon: '📚',
        text: `Try puzzle games and reading activities to boost cognitive skills.`,
        color: '#f59e0b'
      });
    }
    
    if (physical === minScore && physical < 1) {
      insights.push({
        type: 'improvement',
        icon: '🏃‍♂️',
        text: `Encourage more physical activities like running, jumping, and dancing.`,
        color: '#f59e0b'
      });
    }
    
    if (linguistic === minScore && linguistic < 1) {
      insights.push({
        type: 'improvement',
        icon: '📖',
        text: `Practice speaking, storytelling, and word games to improve language skills.`,
        color: '#f59e0b'
      });
    }
    
    // Overall performance (scaled to maxTotal)
    const scorePercentage = (total / maxTotal) * 100;
    if (scorePercentage >= 85) {
      insights.push({
        type: 'overall',
        icon: '🎉',
        text: `Outstanding performance! Your child is excelling across all areas.`,
        color: '#6366f1'
      });
    } else if (scorePercentage >= 65) {
      insights.push({
        type: 'overall',
        icon: '👍',
        text: `Good progress! Your child is developing well in multiple areas.`,
        color: '#6366f1'
      });
    } else if (scorePercentage >= 40) {
      insights.push({
        type: 'overall',
        icon: '📈',
        text: `Keep practicing! There's room for improvement in all areas.`,
        color: '#6366f1'
      });
    } else {
      insights.push({
        type: 'overall',
        icon: '🌱',
        text: `Just getting started! Focus on fun, engaging activities to build skills.`,
        color: '#6366f1'
      });
    }
    
    return insights;
  };

  const insights = generateInsights();
  
  // Age-specific recommendations
  const getAgeRecommendations = () => {
    const ageRecommendations: { [key: string]: string[] } = {
      '0-1': [
        'Focus on sensory play and simple cause-and-effect toys',
        'Practice tummy time and reaching for objects',
        'Talk and sing to your baby frequently'
      ],
      '1-2': [
        'Encourage walking and climbing safely',
        'Read picture books together daily',
        'Play simple games like peek-a-boo and pat-a-cake'
      ],
      '2-3': [
        'Provide building blocks and shape sorters',
        'Encourage running, jumping, and ball games',
        'Ask simple questions and expand their vocabulary'
      ],
      '3-4': [
        'Try puzzles and matching games',
        'Practice hopping, skipping, and balance activities',
        'Encourage storytelling and pretend play'
      ],
      '4-5': [
        'Introduce basic counting and letter recognition',
        'Play sports and dance together',
        'Practice conversations and asking "why" questions'
      ],
      '5-6': [
        'Work on pre-reading and writing skills',
        'Try organized sports and complex physical games',
        'Encourage detailed storytelling and jokes'
      ]
    };
    
    return ageRecommendations[ageGroup] || [];
  };

  const recommendations = getAgeRecommendations();

  return (
    <div style={{ 
      padding: '25px',
      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      borderRadius: '15px',
      color: 'white',
      margin: '20px 0'
    }}>
      <h3 style={{ 
        textAlign: 'center', 
        marginBottom: '25px', 
        fontSize: '24px',
        fontWeight: 'bold'
      }}>
        💡 Personalized Insights
      </h3>
      
      {/* Insights Grid */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
        gap: '15px',
        marginBottom: '25px'
      }}>
        {insights.map((insight, index) => (
          <div
            key={index}
            style={{
              background: 'rgba(255, 255, 255, 0.15)',
              backdropFilter: 'blur(10px)',
              borderRadius: '12px',
              padding: '15px',
              border: '1px solid rgba(255, 255, 255, 0.2)'
            }}
          >
            <div style={{
              display: 'flex',
              alignItems: 'flex-start',
              gap: '10px'
            }}>
              <span style={{ fontSize: '24px' }}>{insight.icon}</span>
              <p style={{ 
                margin: 0, 
                fontSize: '14px', 
                lineHeight: '1.5',
                opacity: 0.95
              }}>
                {insight.text}
              </p>
            </div>
          </div>
        ))}
      </div>
      
      {/* Age-specific recommendations */}
      {recommendations.length > 0 && (
        <div style={{
          background: 'rgba(255, 255, 255, 0.1)',
          borderRadius: '12px',
          padding: '20px',
          border: '1px solid rgba(255, 255, 255, 0.2)'
        }}>
          <h4 style={{ 
            marginBottom: '15px', 
            fontSize: '18px',
            display: 'flex',
            alignItems: 'center',
            gap: '8px'
          }}>
            🎯 Recommended Activities for Age {ageGroup}
          </h4>
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
            gap: '10px'
          }}>
            {recommendations.map((rec, index) => (
              <div
                key={index}
                style={{
                  display: 'flex',
                  alignItems: 'flex-start',
                  gap: '8px',
                  fontSize: '14px',
                  lineHeight: '1.4'
                }}
              >
                <span style={{ color: '#fbbf24', fontSize: '16px' }}>•</span>
                <span style={{ opacity: 0.9 }}>{rec}</span>
              </div>
            ))}
          </div>
        </div>
      )}
      
      {/* Score summary */}
      <div style={{
        textAlign: 'center',
        marginTop: '20px',
        padding: '15px',
        background: 'rgba(255, 255, 255, 0.1)',
        borderRadius: '10px',
        border: '1px solid rgba(255, 255, 255, 0.2)'
      }}>
        <p style={{ 
          margin: 0, 
          fontSize: '16px', 
          fontWeight: '600',
          opacity: 0.95
        }}>
          Overall Score: {total}/{maxTotal} • Age Group: {ageGroup} • Keep up the great work! 🌟
        </p>
      </div>
    </div>
  );
}
