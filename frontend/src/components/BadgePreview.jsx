import React from 'react';
import { Download } from 'lucide-react';
import { downloadBadge } from '../api/client';
import { useTranslation } from 'react-i18next';

const scoreColor = (s) => {
  if (s <= 2) return 'border-red-500 text-red-600';
  if (s === 3) return 'border-yellow-500 text-yellow-600';
  return 'border-green-500 text-green-600';
};

const pillarBg = (p) => {
  const map = { Environmental: 'bg-emerald-50', Social: 'bg-blue-50', Governance: 'bg-purple-50' };
  return map[p] || 'bg-gray-50';
};

export default function BadgePreview({ claim }) {
  const { t } = useTranslation();
  if (!claim) return null;

  const score = claim.final_score || claim.score;

  const handleDownload = async () => {
    try {
      const blob = await downloadBadge(claim.claim_id);
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url; a.download = `badge_${claim.claim_id}.pdf`; a.click();
      URL.revokeObjectURL(url);
    } catch { /* ignore */ }
  };

  return (
    <div className={`rounded-xl border-2 p-4 ${pillarBg(claim.pillar)} ${scoreColor(score).split(' ')[0]}`}>
      <div className="flex items-start justify-between mb-2">
        <span className="text-xs font-semibold uppercase tracking-wider text-gray-500">{claim.pillar}</span>
        <span className={`text-2xl font-black ${scoreColor(score).split(' ')[1]}`}>{score}/5</span>
      </div>
      <p className="text-sm text-gray-700 mb-3 line-clamp-2">{claim.text}</p>
      <button onClick={handleDownload}
        className="flex items-center gap-1 text-xs font-medium text-accent hover:text-amber-800 transition">
        <Download size={14} /> {t('download_badge')}
      </button>
    </div>
  );
}