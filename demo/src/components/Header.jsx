export default function Header({ connected, onNewChat }) {
  return (
    <header className="flex items-center justify-between px-6 py-3 bg-slate-800 border-b border-slate-700">
      <h1 className="text-lg font-semibold text-white">HCLS Agent Skills</h1>
      <div className="flex items-center gap-3">
        <button
          onClick={onNewChat}
          className="px-3 py-1 text-sm bg-slate-700 text-slate-300 rounded hover:bg-slate-600 hover:text-white transition-colors"
        >
          + New Chat
        </button>
        <div className="flex items-center gap-2 text-sm text-slate-400">
          <span className={`w-2 h-2 rounded-full ${connected ? 'bg-emerald-500' : 'bg-red-500'}`} aria-label={connected ? 'Connected' : 'Disconnected'} />
          {connected ? 'Connected' : 'Disconnected'}
        </div>
      </div>
    </header>
  );
}
