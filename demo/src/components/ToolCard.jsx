import { useState } from 'react';

const statusIcons = {
  pending: <span className="w-4 h-4 border-2 border-yellow-400 border-t-transparent rounded-full animate-spin inline-block" />,
  running: <span className="w-4 h-4 border-2 border-blue-400 border-t-transparent rounded-full animate-spin inline-block" />,
  completed: <svg className="w-4 h-4 text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7"/></svg>,
  failed: <svg className="w-4 h-4 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12"/></svg>,
};

export default function ToolCard({ name, status = 'pending', params, duration }) {
  const [expanded, setExpanded] = useState(false);

  return (
    <div className="my-1 rounded bg-slate-700 border border-slate-600 text-sm">
      <button
        onClick={() => setExpanded(!expanded)}
        className="w-full flex items-center gap-2 px-3 py-1.5 text-left"
        aria-expanded={expanded}
      >
        {statusIcons[status] || statusIcons.pending}
        <span className="text-slate-200 font-mono text-xs">{name}</span>
        {duration && <span className="ml-auto text-xs text-slate-400">{duration}ms</span>}
        <svg className={`w-3 h-3 text-slate-400 transition-transform ${expanded ? 'rotate-180' : ''}`} fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7"/></svg>
      </button>
      {expanded && params && (
        <pre className="px-3 py-2 text-xs text-slate-400 border-t border-slate-600 overflow-x-auto font-mono">
          {typeof params === 'string' ? params : JSON.stringify(params, null, 2)}
        </pre>
      )}
    </div>
  );
}
