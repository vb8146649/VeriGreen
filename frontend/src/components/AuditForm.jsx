import React, { useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { Upload, Link as LinkIcon, Loader2 } from 'lucide-react';
import { startAudit } from '../api/client';

export default function AuditForm() {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const fileRef = useRef(null);

  const [mode, setMode] = useState('file'); // 'file' | 'url'
  const [file, setFile] = useState(null);
  const [url, setUrl] = useState('');
  const [company, setCompany] = useState('');
  const [year, setYear] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [dragOver, setDragOver] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    if (!company.trim()) { setError('Company name is required'); return; }
    if (mode === 'file' && !file) { setError('Please select a PDF file'); return; }
    if (mode === 'url' && !url.trim()) { setError('Please enter a URL'); return; }

    setLoading(true);
    try {
      const formData = new FormData();
      formData.append('company_name', company);
      if (year) formData.append('report_year', year);
      if (mode === 'file') {
        formData.append('file', file);
      } else {
        formData.append('url', url);
      }
      const res = await startAudit(formData);
      navigate(`/audit/${res.audit_id}`);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to start audit');
    } finally {
      setLoading(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setDragOver(false);
    const dropped = e.dataTransfer.files[0];
    if (dropped && dropped.type === 'application/pdf') setFile(dropped);
  };

  return (
    <form onSubmit={handleSubmit} className="bg-white rounded-2xl shadow-lg p-8 max-w-2xl mx-auto">
      {/* Tab toggle */}
      <div className="flex gap-2 mb-6">
        <button type="button" onClick={() => setMode('file')}
          className={`flex items-center gap-2 px-4 py-2 rounded-lg font-medium transition ${mode === 'file' ? 'bg-primary-700 text-white' : 'bg-gray-100 text-gray-600 hover:bg-gray-200'}`}>
          <Upload size={18} /> {t('upload_pdf')}
        </button>
        <button type="button" onClick={() => setMode('url')}
          className={`flex items-center gap-2 px-4 py-2 rounded-lg font-medium transition ${mode === 'url' ? 'bg-primary-700 text-white' : 'bg-gray-100 text-gray-600 hover:bg-gray-200'}`}>
          <LinkIcon size={18} /> {t('enter_url')}
        </button>
      </div>

      {/* File upload / URL input */}
      {mode === 'file' ? (
        <div
          onClick={() => fileRef.current?.click()}
          onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
          onDragLeave={() => setDragOver(false)}
          onDrop={handleDrop}
          className={`border-2 border-dashed rounded-xl p-10 text-center cursor-pointer transition mb-4
            ${dragOver ? 'border-primary-500 bg-primary-50' : 'border-gray-300 hover:border-primary-500 hover:bg-primary-50'}`}>
          <Upload size={40} className="mx-auto mb-3 text-gray-400" />
          <p className="text-gray-500">{file ? file.name : t('drag_drop')}</p>
          <input ref={fileRef} type="file" accept=".pdf" className="hidden"
            onChange={(e) => setFile(e.target.files[0])} />
        </div>
      ) : (
        <input type="url" value={url} onChange={(e) => setUrl(e.target.value)}
          placeholder={t('url_placeholder')}
          className="w-full border border-gray-300 rounded-lg px-4 py-3 mb-4 focus:ring-2 focus:ring-primary-500 focus:outline-none" />
      )}

      {/* Company & Year */}
      <div className="grid grid-cols-2 gap-4 mb-6">
        <input type="text" value={company} onChange={(e) => setCompany(e.target.value)}
          placeholder={t('company_name')}
          className="border border-gray-300 rounded-lg px-4 py-3 focus:ring-2 focus:ring-primary-500 focus:outline-none" />
        <input type="text" value={year} onChange={(e) => setYear(e.target.value)}
          placeholder={t('report_year')}
          className="border border-gray-300 rounded-lg px-4 py-3 focus:ring-2 focus:ring-primary-500 focus:outline-none" />
      </div>

      {/* Error */}
      {error && <p className="text-red-600 text-sm mb-4">{error}</p>}

      {/* Submit */}
      <button type="submit" disabled={loading}
        className="w-full bg-primary-700 hover:bg-primary-900 text-white font-semibold py-3 rounded-lg transition flex items-center justify-center gap-2 disabled:opacity-50">
        {loading ? <><Loader2 size={20} className="animate-spin" /> {t('processing')}</> : t('start_audit')}
      </button>
    </form>
  );
}