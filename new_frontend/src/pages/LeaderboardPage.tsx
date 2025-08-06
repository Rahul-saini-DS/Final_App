import { useState, useEffect } from 'react';
import axios from 'axios';

const API_BASE_URL = 'http://localhost:5000/api';

interface LeaderboardEntry {
  rank: number;
  name: string;
  child_name: string;
  parent_name: string;
  score: number;
  age_group: string;
  completed_at: string;
}

export default function LeaderboardPage() {
  const [leaderboard, setLeaderboard] = useState<LeaderboardEntry[]>([]);
  const [filteredData, setFilteredData] = useState<LeaderboardEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [sortField, setSortField] = useState<keyof LeaderboardEntry>('score');
  const [sortDirection, setSortDirection] = useState<'asc' | 'desc'>('desc');
  const [ageFilter, setAgeFilter] = useState<string>('all');

  useEffect(() => {
    fetchLeaderboard();
  }, []);

  useEffect(() => {
    filterAndSortData();
  }, [leaderboard, ageFilter, sortField, sortDirection]);

  const fetchLeaderboard = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/leaderboard`);
      setLeaderboard(response.data);
    } catch (error) {
      console.error('Error fetching leaderboard:', error);
    } finally {
      setLoading(false);
    }
  };

  const filterAndSortData = () => {
    let filtered = [...leaderboard];
    
    // Apply age filter
    if (ageFilter !== 'all') {
      filtered = filtered.filter(entry => entry.age_group === ageFilter);
    }
    
    // Apply sorting
    filtered.sort((a, b) => {
      let aValue = a[sortField];
      let bValue = b[sortField];
      
      // Handle date sorting
      if (sortField === 'completed_at') {
        aValue = new Date(aValue as string).getTime() as any;
        bValue = new Date(bValue as string).getTime() as any;
      }
      
      if (sortDirection === 'asc') {
        return aValue > bValue ? 1 : -1;
      } else {
        return aValue < bValue ? 1 : -1;
      }
    });
    
    // Update ranks after filtering and sorting
    filtered = filtered.map((entry, index) => ({ ...entry, rank: index + 1 }));
    
    setFilteredData(filtered);
  };

  const handleSort = (field: keyof LeaderboardEntry) => {
    if (sortField === field) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      setSortField(field);
      setSortDirection('desc');
    }
  };

  const getSortIcon = (field: keyof LeaderboardEntry) => {
    if (sortField !== field) return '↕️';
    return sortDirection === 'asc' ? '↑' : '↓';
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString();
  };

  const getRankEmoji = (rank: number) => {
    switch (rank) {
      case 1: return '🥇';
      case 2: return '🥈';
      case 3: return '🥉';
      default: return '🏅';
    }
  };

  const getAgeGroups = () => {
    const groups = [...new Set(leaderboard.map(entry => entry.age_group))];
    return groups.sort();
  };

  if (loading) {
    return (
      <div style={{
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        height: '400px',
        fontSize: '18px'
      }}>
        <div style={{ textAlign: 'center' }}>
          <div style={{ fontSize: '48px', marginBottom: '10px' }}>⏳</div>
          Loading leaderboard...
        </div>
      </div>
    );
  }

  return (
    <div className="container" style={{ maxWidth: '1200px', margin: '0 auto', padding: '20px' }}>
      {/* Header */}
      <div style={{
        textAlign: 'center',
        marginBottom: '30px',
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        color: 'white',
        padding: '30px',
        borderRadius: '20px',
        boxShadow: '0 10px 30px rgba(0,0,0,0.2)'
      }}>
        <h1 style={{ margin: '0 0 10px 0', fontSize: '32px' }}>🏆 Leaderboard</h1>
        <p style={{ margin: 0, fontSize: '18px', opacity: 0.9 }}>
          See how everyone is performing!
        </p>
      </div>

      {/* Filters and Controls */}
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: '30px',
        flexWrap: 'wrap',
        gap: '15px',
        background: 'white',
        padding: '20px',
        borderRadius: '15px',
        boxShadow: '0 5px 15px rgba(0,0,0,0.1)'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <label style={{ fontWeight: '600', color: '#374151' }}>Filter by Age Group:</label>
          <select
            value={ageFilter}
            onChange={(e) => setAgeFilter(e.target.value)}
            style={{
              padding: '8px 12px',
              borderRadius: '8px',
              border: '2px solid #e5e7eb',
              fontSize: '14px',
              background: 'white'
            }}
          >
            <option value="all">All Ages</option>
            {getAgeGroups().map(group => (
              <option key={group} value={group}>{group} years</option>
            ))}
          </select>
        </div>
        
        <div style={{ color: '#6b7280', fontSize: '14px' }}>
          Showing {filteredData.length} of {leaderboard.length} entries
        </div>
      </div>

      {/* Leaderboard Table */}
      <div style={{
        background: 'white',
        borderRadius: '15px',
        boxShadow: '0 10px 30px rgba(0,0,0,0.1)',
        overflow: 'hidden'
      }}>
        <div style={{ overflowX: 'auto' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead>
              <tr style={{ 
                background: 'linear-gradient(135deg, #f3f4f6 0%, #e5e7eb 100%)',
                borderBottom: '2px solid #d1d5db'
              }}>
                <th style={{ 
                  padding: '20px 15px', 
                  textAlign: 'left',
                  fontWeight: '700',
                  color: '#374151',
                  fontSize: '14px'
                }}>
                  Rank
                </th>
                <th 
                  onClick={() => handleSort('name')}
                  style={{ 
                    padding: '20px 15px', 
                    textAlign: 'left',
                    fontWeight: '700',
                    color: '#374151',
                    fontSize: '14px',
                    cursor: 'pointer',
                    userSelect: 'none'
                  }}
                >
                  Name {getSortIcon('name')}
                </th>
                <th 
                  onClick={() => handleSort('score')}
                  style={{ 
                    padding: '20px 15px', 
                    textAlign: 'center',
                    fontWeight: '700',
                    color: '#374151',
                    fontSize: '14px',
                    cursor: 'pointer',
                    userSelect: 'none'
                  }}
                >
                  Score {getSortIcon('score')}
                </th>
                <th 
                  onClick={() => handleSort('age_group')}
                  style={{ 
                    padding: '20px 15px', 
                    textAlign: 'center',
                    fontWeight: '700',
                    color: '#374151',
                    fontSize: '14px',
                    cursor: 'pointer',
                    userSelect: 'none'
                  }}
                >
                  Age Group {getSortIcon('age_group')}
                </th>
                <th 
                  onClick={() => handleSort('completed_at')}
                  style={{ 
                    padding: '20px 15px', 
                    textAlign: 'center',
                    fontWeight: '700',
                    color: '#374151',
                    fontSize: '14px',
                    cursor: 'pointer',
                    userSelect: 'none'
                  }}
                >
                  Date {getSortIcon('completed_at')}
                </th>
              </tr>
            </thead>
            <tbody>
              {filteredData.map((entry, index) => (
                <tr 
                  key={`${entry.child_name}-${entry.completed_at}-${index}`}
                  style={{ 
                    borderBottom: '1px solid #f3f4f6',
                    background: entry.rank <= 3 ? 'rgba(99, 102, 241, 0.05)' : 'white',
                    transition: 'background 0.2s ease'
                  }}
                  onMouseOver={(e) => {
                    if (entry.rank > 3) {
                      e.currentTarget.style.background = '#f9fafb';
                    }
                  }}
                  onMouseOut={(e) => {
                    if (entry.rank > 3) {
                      e.currentTarget.style.background = 'white';
                    }
                  }}
                >
                  <td style={{ padding: '20px 15px', fontSize: '16px', fontWeight: '600' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                      <span style={{ fontSize: '20px' }}>{getRankEmoji(entry.rank)}</span>
                      <span style={{ color: entry.rank <= 3 ? '#6366f1' : '#374151' }}>
                        #{entry.rank}
                      </span>
                    </div>
                  </td>
                  <td style={{ padding: '20px 15px' }}>
                    <div>
                      <div style={{ 
                        fontWeight: '600', 
                        color: '#374151', 
                        fontSize: '16px',
                        marginBottom: '2px'
                      }}>
                        {entry.child_name || 'Child'}
                      </div>
                      <div style={{ 
                        fontSize: '12px', 
                        color: '#6b7280'
                      }}>
                        Parent: {entry.parent_name}
                      </div>
                    </div>
                  </td>
                  <td style={{ 
                    padding: '20px 15px', 
                    textAlign: 'center',
                    fontSize: '18px',
                    fontWeight: '700',
                    color: entry.rank <= 3 ? '#6366f1' : '#374151'
                  }}>
                    {entry.score}
                  </td>
                  <td style={{ 
                    padding: '20px 15px', 
                    textAlign: 'center',
                    fontSize: '14px',
                    fontWeight: '500'
                  }}>
                    <span style={{
                      background: 'rgba(99, 102, 241, 0.1)',
                      color: '#6366f1',
                      padding: '4px 8px',
                      borderRadius: '12px',
                      fontSize: '12px',
                      fontWeight: '600'
                    }}>
                      {entry.age_group}
                    </span>
                  </td>
                  <td style={{ 
                    padding: '20px 15px', 
                    textAlign: 'center',
                    fontSize: '14px',
                    color: '#6b7280'
                  }}>
                    {formatDate(entry.completed_at)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        
        {filteredData.length === 0 && (
          <div style={{
            textAlign: 'center',
            padding: '60px 20px',
            color: '#6b7280'
          }}>
            <div style={{ fontSize: '48px', marginBottom: '15px' }}>📊</div>
            <h3 style={{ margin: '0 0 10px 0' }}>No results found</h3>
            <p style={{ margin: 0 }}>
              {ageFilter !== 'all' 
                ? `No assessments found for age group ${ageFilter}`
                : 'No assessments have been completed yet.'
              }
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
