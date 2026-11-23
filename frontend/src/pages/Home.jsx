import React, { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Leaf, CheckCircle, XCircle } from 'lucide-react';
import AuditForm from '../components/AuditForm';
import { getHealth } from '../api/client';

export default function Home() {
  const { t } = useTranslation();
  const [health, setHealth] = useState(null);

  useEffect(() => {
    getHealth().then(setHealth).catch(() => setHealth(null));
  }, []);

  return (
    <div className="max-w-4xl mx-auto">
      {/* Hero */}
      <div className="text-center mb-10">
        <div className="flex items-center justify-center gap-3 mb-4">
          <Leaf size={48} className="text-primary-700" />
          <h1 className="text-4xl font-black text-gray-900">{t('app_name')}</h1>
        </div>
        <p className="text-lg text-gray-500">{t('tagline')}</p>

        {/* Health indicator */}
        {health !== null && (
          <div className="mt-4 inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-white shadow text-sm">
            {health?.api === 'ok' ? (
              <><CheckCircle size={16} className="text-green-500" /> <span className="text-green-700">{t('health_ok')}</span></>
            ) : (
              <><XCircle size={16} className="text-red-500" /> <span className="text-red-700">{t('health_error')}</span></>
            )}
          </div>
        )}
      </div>

      {/* Audit Form */}
      <AuditForm />
    </div>
  );
}