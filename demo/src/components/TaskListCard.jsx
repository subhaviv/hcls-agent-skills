export default function TaskListCard({ params = {}, status, isActive }) {
  const command = params.command;
  const tasks = params.tasks || [];
  const description = params.task_list_description || '';

  const completedIds = params.completedIds || [];

  if (command === 'create' && tasks.length > 0) {
    return (
      <div className={`my-2 rounded-lg border border-amber-600/50 bg-slate-800/80 px-3 py-2 ${isActive ? 'sticky top-0 z-10 bg-slate-900/95 backdrop-blur shadow-lg' : ''}`}>
        <div className="flex items-center gap-2 text-xs text-amber-400 font-medium mb-1">
          <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"/>
          </svg>
          {description || 'Task List'}
        </div>
        <ul className="space-y-0.5">
          {tasks.map((t, i) => {
            const done = completedIds.includes(String(i + 1));
            return (
              <li key={i} className={`flex items-start gap-2 text-xs ${done ? 'text-emerald-400 line-through' : 'text-slate-300'}`}>
                <span className="text-slate-500 mt-0.5 font-mono">{i + 1}.</span>
                <span>{t.task_description}</span>
              </li>
            );
          })}
        </ul>
      </div>
    );
  }

  if (command === 'complete' && completedIds.length > 0) {
    return (
      <div className="my-1 inline-flex items-center gap-1 text-xs text-emerald-400">
        <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7"/>
        </svg>
        Completed {completedIds.length} task{completedIds.length > 1 ? 's' : ''}
      </div>
    );
  }

  return null;
}
