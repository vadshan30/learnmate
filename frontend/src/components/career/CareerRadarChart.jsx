import { useMemo } from 'react'
import { Radar, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, ResponsiveContainer, Tooltip } from 'recharts'

export default function CareerRadarChart({ scores }) {
  const chartData = useMemo(() => {
    return scores.slice(0, 10).map((s) => ({
      career: s.career_name.length > 15 ? s.career_name.slice(0, 12) + '...' : s.career_name,
      fullName: s.career_name,
      score: s.percentage,
    }))
  }, [scores])

  if (chartData.length === 0) return null

  return (
    <div className="w-full h-80">
      <ResponsiveContainer width="100%" height="100%">
        <RadarChart data={chartData} cx="50%" cy="50%" outerRadius="70%">
          <PolarGrid stroke="#e5e7eb" />
          <PolarAngleAxis
            dataKey="career"
            tick={{ fontSize: 11, fill: '#6b7280' }}
          />
          <PolarRadiusAxis
            angle={30}
            domain={[0, 100]}
            tick={{ fontSize: 10, fill: '#9ca3af' }}
          />
          <Radar
            name="Score"
            dataKey="score"
            stroke="#6366f1"
            fill="#6366f1"
            fillOpacity={0.3}
          />
          <Tooltip
            formatter={(value, name, props) => [`${value}%`, props.payload.fullName]}
            contentStyle={{
              backgroundColor: 'rgba(255,255,255,0.95)',
              border: '1px solid #e5e7eb',
              borderRadius: '8px',
              fontSize: '12px',
            }}
          />
        </RadarChart>
      </ResponsiveContainer>
    </div>
  )
}
