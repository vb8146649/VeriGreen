import React, { useState } from 'react';
import { Routes, Route, Link, useLocation } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { Leaf, Home as HomeIcon, Clock, Globe } from 'lucide-react';
import HomePage from './pages/Home';
import AuditDetail from './pages/AuditDetail';
import History from './pages/History';

export default function App() {
  const { t, i18n } = useTranslation();
  const location = useLocation();
  const [lang, setLang] = useState(i18n.language);

  const toggleLang = () => {
    const next = lang === 'en' ? 'hi' : 'en';
    i18n.changeLanguage(next);
    setLang(next);
  };

  const navLink = (to, icon, label) => {
    const active = location.pathname === to;
    return (
      <Link to={to}
        className={`flex items-center gap-3 px-4 py-2.5 rounded-lg text-sm font-medium transition
          ${active ? 'bg-primary-700 text-white' : 'text-gray-300 hover:bg-[#1e3d2b] hover:text-white'}`}>
        {icon} {label}
      </Link>
    );
  };

  return (
    <div className="flex min-h-screen bg-[#FAF8F5]">
      {/* Sidebar */}
      <nav className="w-64 bg-[#13261B] flex flex-col p-5 shrink-0">
        {/* Logo */}
        <div className="flex items-center gap-2 mb-10 px-2">
          <Leaf size={28} className="text-primary-500" />
          <span className="text-xl font-black text-white tracking-tight">VeriGreen</span>
          <span className="text-xs text-accent font-mono mt-1">AI</span>
        </div>

        {/* Nav links */}
        <div className="space-y-1 flex-1">
          {navLink('/', <HomeIcon size={18} />, t('nav_home'))}
          {navLink('/history', <Clock size={18} />, t('nav_history'))}
        </div>

        {/* Language toggle */}
        <button onClick={toggleLang}
          className="flex items-center gap-2 px-4 py-2.5 rounded-lg text-sm font-medium text-gray-300 hover:bg-[#1e3d2b] hover:text-white transition mt-4">
          <Globe size={18} />
          {lang === 'en' ? 'हिंदी' : 'English'}
        </button>
      </nav>

      {/* Main content */}
      <main className="flex-1 p-8 overflow-auto">
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/audit/:id" element={<AuditDetail />} />
          <Route path="/history" element={<History />} />
        </Routes>
      </main>
    </div>
  );
}