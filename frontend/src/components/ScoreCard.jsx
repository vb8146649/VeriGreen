import React from 'react';
import { useTranslation } from 'react-i18next';
import { PieChart, Pie, Cell, ResponsiveContainer } from 'recharts';

const COLORS = { Environmental: '#22c55e', Social: '#3b82f6', Governance: '#a855f7' };

function MiniDonut({ label, value, color }) {
  const data = [
    { name: 'score', value: value },
    { name: 'rest', value: 5 - value },
  ];
  return (
    <div className="flex flex-col items-center">
      <ResponsiveContainer width={90} height={90}>
        <PieChart>
          <Pie data={data} dataKey="value" innerRadius={28} outerRadius={38} startAngle={90} endAngle={-270} paddingAngle={2}>
            <Cell fill={color} />
            <Cell fill="#e5e7eb" />
          </Pie>
        </PieChart>
      </ResponsiveContainer>
      <p className="text-lg font-bold" style={{ color }}>{value.toFixed(1)}</p>
      <p className="text-xs text-gray-500 uppercase tracking-wide">{label}</p>
    </div>
  );
}

export default function ScoreCard({ summary = {}, company = '', year = '' }) {
  const { t } = useTranslation();
  const ps = summary.pillar_scores || {};
  const overall = summary.overall_score || 0;
  const overallColor = overall >= 4 ? 'text-green-600' : overall >= 3 ? 'text-yellow-600' : 'text-red-600';

  return (
    <div className="bg-white rounded-2xl shadow-lg p-6 mb-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div>
          <h2 className="text-xl font-bold text-gray-800">{company}</h2>
          {year && <p className="text-sm text-gray-400">{year}</p>}
        </div>
        <div className="text-right">
          <p className="text-xs text-gray-500 uppercase tracking-wide">{t('overall_score')}</p>
          <p className={`text-5xl font-black ${overallColor}`}>{overall.toFixed(1)}</p>
          <p className="text-xs text-gray-400">/ 5.0</p>
        </div>
      </div>

      {/* Pillar donuts */}
      <div className="flex justify-around my-6">
        <MiniDonut label={t('environmental')} value={ps.Environmental || 0} color={COLORS.Environmental} />
        <MiniDonut label={t('social')} value={ps.Social || 0} color={COLORS.Social} />
        <MiniDonut label={t('governance')} value={ps.Governance || 0} color={COLORS.Governance} />
      </div>

      {/* Stats */}
      <div className="grid grid-cols-3 gap-4 text-center border-t pt-4">
        <div>
          <p className="text-2xl font-bold text-gray-800">{summary.total_claims || 0}</p>
          <p className="text-xs text-gray-500">{t('total_claims')}</p>
        </div>
        <div>
          <p className="text-2xl font-bold text-green-600">{summary.verified || 0}</p>
          <p className="text-xs text-gray-500">{t('verified')}</p>
        </div>
        <div>
          <p className="text-2xl font-bold text-red-500">{summary.flagged || 0}</p>
          <p className="text-xs text-gray-500">{t('flagged')}</p>
        </div>
      </div>
    </div>
  );
}