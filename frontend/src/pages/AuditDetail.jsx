import React, { useEffect, useState, useRef } from 'react';
import { useParams } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { Loader2, Download } from 'lucide-react';
import { getAudit, getClaims, downloadReport } from '../api/client';
import ScoreCard from '../components/ScoreCard';
import ClaimsTable from '../components/ClaimsTable';

export default function AuditDetail() {
  const { id } = useParams();
  const { t } = useTranslation();

  const [audit, setAudit] = useState(null);
  const [claims, setClaims] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const pollRef = useRef(null);

  useEffect(() => {
    const fetchAudit = async () => {
      try {
        const data = await getAudit(id);
        setAudit(data);

        if (data.status === 'done' || data.status === 'error') {
          clearInterval(pollRef.current);
          setLoading(false);
          if (data.status === 'done') {
            const c = await getClaims(id);
            setClaims(c);
          }
        }
      } catch (err) {
        setError(err.response?.data?.detail || 'Failed to load audit');
        clearInterval(pollRef.current);
        setLoading(false);
      }
    };

    fetchAudit();
    pollRef.current = setInterval(fetchAudit, 3000);
    return () => clearInterval(pollRef.current);
  }, [id]);

  const handleDownloadReport = async () => {
    try {
      const blob = await downloadReport(id);
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url; a.download = `esg_report_${id}.pdf`; a.click();
      URL.revokeObjectURL(url);
    } catch { /* ignore */ }
  };

  if (error) {
    return <div className="text-center py-20 text-red-500">{error}</div>;
  }

  if (loading || !audit || audit.status === 'processing' || audit.status === 'pending') {
    return (
      <div className="flex flex-col items-center justify-center py-20">
        <Loader2 size={48} className="animate-spin text-primary-700 mb-4" />
        <p className="text-lg text-gray-500">{t('processing')}</p>
        <p className="text-sm text-gray-400 mt-1">Audit ID: {id}</p>
      </div>
    );
  }

  if (audit.status === 'error') {
    return <div className="text-center py-20 text-red-500">Audit failed. Please try again.</div>;
  }

  return (
    <div className="max-w-5xl mx-auto">
      {/* Score Card */}
      <ScoreCard
        summary={audit.summary || {}}
        company={audit.company_name || audit.company || ''}
        year={audit.report_year || ''}
      />

      {/* Download Report */}
      <div className="flex justify-end mb-4">
        <button onClick={handleDownloadReport}
          className="flex items-center gap-2 bg-accent hover:bg-amber-700 text-white font-medium px-5 py-2.5 rounded-lg transition">
          <Download size={18} /> {t('download_report')}
        </button>
      </div>

      {/* Claims Table */}
      <ClaimsTable claims={claims} />
    </div>
  );
}