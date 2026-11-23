import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { ChevronDown, ChevronUp, Download } from 'lucide-react';
import { downloadBadge } from '../api/client';
import EvidencePanel from './EvidencePanel';

const scoreColor = (s) => {
  if (s <= 2) return 'bg-red-500';
  if (s === 3) return 'bg-yellow-500';
  return 'bg-green-500';
};

const pillarColor = (p) => {
  const map = { Environmental: 'bg-emerald-100 text-emerald-800', Social: 'bg-blue-100 text-blue-800', Governance: 'bg-purple-100 text-purple-800' };
  return map[p] || 'bg-gray-100 text-gray-800';
};

export default function ClaimsTable({ claims = [] }) {
  const { t } = useTranslation();
  const [expanded, setExpanded] = useState(null);
  const [filterPillar, setFilterPillar] = useState('');
  const [maxScore, setMaxScore] = useState(5);
  const [sortBy, setSortBy] = useState('score');

  const filtered = claims
    .filter((c) => (!filterPillar || c.pillar === filterPillar))
    .filter((c) => (c.final_score || c.score) <= maxScore)
    .sort((a, b) => {
      if (sortBy === 'score') return (a.final_score || a.score) - (b.final_score || b.score);
      return (a.pillar || '').localeCompare(b.pillar || '');
    });

  const handleDownloadBadge = async (claimId) => {
    try {
      const blob = await downloadBadge(claimId);
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url; a.download = `badge_${claimId}.pdf`; a.click();
      URL.revokeObjectURL(url);
    } catch { /* ignore */ }
  };

  return (
    <div className="bg-white rounded-2xl shadow-lg overflow-hidden">
      {/* Filters */}
      <div className="flex flex-wrap gap-4 p-4 border-b bg-gray-50">
        <select value={filterPillar} onChange={(e) => setFilterPillar(e.target.value)}
          className="border rounded-lg px-3 py-2 text-sm">
          <option value="">{t('pillar')} (All)</option>
          <option value="Environmental">{t('environmental')}</option>
          <option value="Social">{t('social')}</option>
          <option value="Governance">{t('governance')}</option>
        </select>
        <label className="flex items-center gap-2 text-sm text-gray-600">
          Max {t('score')}:
          <input type="range" min="1" max="5" value={maxScore}
            onChange={(e) => setMaxScore(Number(e.target.value))} className="w-24" />
          <span className="font-semibold">{maxScore}</span>
        </label>
        <select value={sortBy} onChange={(e) => setSortBy(e.target.value)}
          className="border rounded-lg px-3 py-2 text-sm">
          <option value="score">Sort by {t('score')}</option>
          <option value="pillar">Sort by {t('pillar')}</option>
        </select>
      </div>

      {/* Table */}
      <table className="w-full text-left">
        <thead className="bg-gray-100 text-xs text-gray-500 uppercase">
          <tr>
            <th className="px-4 py-3 w-10">#</th>
            <th className="px-4 py-3">{t('claim_text')}</th>
            <th className="px-4 py-3 w-32">{t('pillar')}</th>
            <th className="px-4 py-3 w-20">{t('score')}</th>
            <th className="px-4 py-3 w-28">{t('verdict')}</th>
            <th className="px-4 py-3 w-24">{t('actions')}</th>
          </tr>
        </thead>
        <tbody>
          {filtered.map((claim, i) => (
            <React.Fragment key={claim.claim_id || i}>
              <tr className="border-b hover:bg-gray-50 cursor-pointer"
                onClick={() => setExpanded(expanded === i ? null : i)}>
                <td className="px-4 py-3 text-sm text-gray-400">{i + 1}</td>
                <td className="px-4 py-3 text-sm max-w-md truncate">{claim.text}</td>
                <td className="px-4 py-3">
                  <span className={`text-xs font-medium px-2 py-1 rounded-full ${pillarColor(claim.pillar)}`}>{claim.pillar}</span>
                </td>
                <td className="px-4 py-3">
                  <span className={`inline-block w-7 h-7 rounded-full text-white text-xs font-bold flex items-center justify-center ${scoreColor(claim.final_score || claim.score)}`}>
                    {claim.final_score || claim.score}
                  </span>
                </td>
                <td className="px-4 py-3 text-sm">{claim.verdict || '—'}</td>
                <td className="px-4 py-3">
                  <div className="flex items-center gap-2">
                    <button onClick={(e) => { e.stopPropagation(); handleDownloadBadge(claim.claim_id); }}
                      className="text-accent hover:text-amber-800" title={t('download_badge')}>
                      <Download size={16} />
                    </button>
                    {expanded === i ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
                  </div>
                </td>
              </tr>
              {expanded === i && (
                <tr><td colSpan="6" className="p-0">
                  <EvidencePanel claim={claim} />
                </td></tr>
              )}
            </React.Fragment>
          ))}
          {filtered.length === 0 && (
            <tr><td colSpan="6" className="px-4 py-8 text-center text-gray-400">No claims match the current filters.</td></tr>
          )}
        </tbody>
      </table>
    </div>
  );
}