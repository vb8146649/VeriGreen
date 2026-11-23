import React from 'react';
import { useTranslation } from 'react-i18next';
import { FileText, ExternalLink } from 'lucide-react';

export default function EvidencePanel({ claim }) {
  const { t } = useTranslation();
  if (!claim) return null;

  const evidence = claim.evidence || [];
  const citations = (() => {
    try {
      return typeof claim.citations === 'string' ? JSON.parse(claim.citations) : (claim.citations || []);
    } catch { return []; }
  })();

  return (
    <div className="bg-gray-50 border-t p-6">
      {/* Full claim text */}
      <div className="mb-4">
        <h4 className="text-xs uppercase tracking-wide text-gray-500 mb-1">{t('claim_text')}</h4>
        <p className="text-sm text-gray-800 leading-relaxed">{claim.text}</p>
      </div>

      {/* Explanation */}
      {claim.reason && (
        <div className="mb-4">
          <h4 className="text-xs uppercase tracking-wide text-gray-500 mb-1">{t('explanation')}</h4>
          <p className="text-sm text-gray-700">{claim.reason}</p>
        </div>
      )}

      {/* Evidence snippets */}
      {evidence.length > 0 && (
        <div className="mb-4">
          <h4 className="text-xs uppercase tracking-wide text-gray-500 mb-2">{t('evidence')}</h4>
          <div className="space-y-2">
            {evidence.map((ev, i) => (
              <div key={i} className="bg-white border rounded-lg p-3 text-sm">
                <div className="flex items-center gap-2 text-gray-400 text-xs mb-1">
                  <FileText size={12} />
                  <span>{t('source_page')}: {ev.source_page || 'N/A'}</span>
                  {ev.relevance_score && (
                    <span className="ml-auto text-accent font-medium">relevance: {(ev.relevance_score * 100).toFixed(0)}%</span>
                  )}
                </div>
                <p className="text-gray-700">{ev.snippet}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Citations */}
      {citations.length > 0 && (
        <div>
          <h4 className="text-xs uppercase tracking-wide text-gray-500 mb-2">{t('citations')}</h4>
          <ul className="space-y-1">
            {citations.map((c, i) => (
              <li key={i} className="flex items-center gap-2 text-sm text-primary-700">
                <ExternalLink size={12} />
                <span>{c}</span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}