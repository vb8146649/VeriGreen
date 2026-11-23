import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { Clock, ExternalLink, Loader2 } from 'lucide-react';
import { getAudits } from '../api/client';

export default function History() {
  const { t } = useTranslation();
  const [audits, setAudits] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    getAudits()
      .then(setAudits)
      .catch((err) => setError(err.response?.data?.detail || 'Could not load audit history.'))
      .finally(() => setLoading(false));
  }, []);

  // Placeholder — in a full implementation this would fetch from GET /audits
  return (
    <div className="max-w-4xl mx-auto">
      <h1 className="text-2xl font-bold text-gray-800 mb-6">{t('nav_history')}</h1>
      {loading ? (
        <div className="flex justify-center py-16 text-primary-700"><Loader2 className="animate-spin" /></div>
      ) : error ? (
        <div className="rounded-xl bg-red-50 p-5 text-red-700">{error}</div>
      ) : audits.length === 0 ? (
        <div className="bg-white rounded-2xl shadow-lg p-10 text-center">
          <Clock size={48} className="mx-auto mb-4 text-gray-300" />
          <p className="text-gray-400">{t('no_audits')}</p>
        </div>
      ) : (
        <div className="overflow-hidden rounded-xl bg-white shadow-sm">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead className="bg-gray-50 text-xs uppercase text-gray-500">
                <tr>
                  <th className="px-5 py-3">{t('company_name')}</th>
                  <th className="px-5 py-3">{t('report_year')}</th>
                  <th className="px-5 py-3">{t('status')}</th>
                  <th className="px-5 py-3">{t('date')}</th>
                  <th className="px-5 py-3"></th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {audits.map((audit) => (
                  <tr key={audit.id} className="hover:bg-gray-50">
                    <td className="px-5 py-4 font-medium text-gray-800">{audit.company}</td>
                    <td className="px-5 py-4 text-gray-600">{audit.report_year || '—'}</td>
                    <td className="px-5 py-4 capitalize text-gray-600">{audit.status}</td>
                    <td className="px-5 py-4 text-gray-600">{audit.created_at ? new Date(audit.created_at).toLocaleString() : '—'}</td>
                    <td className="px-5 py-4 text-right">
                      <Link to={`/audit/${audit.id}`} className="inline-flex items-center gap-1 font-medium text-primary-700 hover:text-primary-900">
                        {t('view')} <ExternalLink size={14} />
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
