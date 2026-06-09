import { useState, useEffect } from 'react';
import SkillBadge from './SkillBadge';
import ToolCard from './ToolCard';
import TaskListCard from './TaskListCard';
import { ToolChips } from './MessageBubble';
import { renderMarkdown } from './markdown';

function TaskField({ task }) {
  const [showFull, setShowFull] = useState(false);
  const isLong = task.length > 120;

  return (
    <div className="px-3 py-1.5 border-t border-slate-700/50 text-xs text-slate-400">
      <span className="text-slate-500 font-medium">Task: </span>
      <span>{isLong && !showFull ? task.slice(0, 120) + '...' : task}</span>
      {isLong && (
        <button onClick={() => setShowFull(!showFull)} className="ml-1 text-indigo-400 hover:text-indigo-300">
          {showFull ? 'less' : 'more'}
        </button>
      )}
    </div>
  );
}

export default function SubagentCard({ stages = [], role, status = 'spawned', task = '' }) {
  const [activeTab, setActiveTab] = useState(0);
  const [expanded, setExpanded] = useState(true);

  const isComplete = status === 'completed' || status === 'done';
  const isFailed = status === 'failed';

  // Auto-switch to next running tab when current completes
  useEffect(() => {
    if (stages[activeTab]?.status === 'complete') {
      const next = stages.findIndex((s, i) => i > activeTab && s.status === 'running');
      if (next !== -1) setActiveTab(next);
    }
  }, [stages, activeTab]);

  const activeStage = stages[activeTab];
  const hasContent = activeStage?.segments?.some(s => s.type !== 'text' || s.content);

  return (
    <div className="my-2 rounded-lg border border-indigo-600/50 bg-slate-800/80 overflow-hidden">
      {/* Header */}
      <button
        onClick={() => setExpanded(!expanded)}
        className="w-full flex items-center gap-2 px-3 py-2 text-sm hover:bg-slate-700/30 transition-colors text-left"
        aria-expanded={expanded}
      >
        <svg className="w-4 h-4 text-indigo-400 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0z"/>
        </svg>
        <div className="flex items-center gap-1.5 flex-wrap min-w-0">
          {stages.length > 0 ? stages.map((s, i) => (
            <span key={i} className="text-slate-200 text-xs bg-slate-700 px-2 py-0.5 rounded">
              {s.name}{s.role ? <span className="text-slate-400 ml-1">({s.role})</span> : ''}
            </span>
          )) : (
            <span className="text-slate-200 text-xs">{role || 'sub-agent'}</span>
          )}
        </div>
        <span className={`ml-auto text-xs font-medium shrink-0 ${isComplete ? 'text-emerald-400' : isFailed ? 'text-red-400' : 'text-blue-400'}`}>
          {isComplete ? 'Complete' : isFailed ? 'Failed' : 'Running...'}
        </span>
        <svg className={`w-3 h-3 text-slate-500 transition-transform shrink-0 ${expanded ? 'rotate-180' : ''}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7"/>
        </svg>
      </button>

      {/* Task */}
      {task && (
        <TaskField task={task} />
      )}

      {expanded && (
        <>
          {/* Tabs */}
          {stages.length > 0 && (
            <div className="flex border-t border-slate-700/50 overflow-x-auto" role="tablist">
              {stages.map((stage, i) => (
                <button
                  key={i}
                  role="tab"
                  aria-selected={i === activeTab}
                  onClick={() => setActiveTab(i)}
                  className={`flex items-center gap-1.5 px-3 py-1.5 text-xs whitespace-nowrap border-b-2 transition-colors ${
                    i === activeTab
                      ? 'border-indigo-400 text-indigo-300 bg-slate-700/40'
                      : 'border-transparent text-slate-400 hover:text-slate-200 hover:bg-slate-700/20'
                  }`}
                >
                  <span className={`w-1.5 h-1.5 rounded-full shrink-0 ${
                    stage.status === 'complete' ? 'bg-emerald-400' :
                    stage.status === 'running' ? 'bg-blue-400 animate-pulse' :
                    'bg-slate-500'
                  }`} />
                  {stage.name}
                  <span className={`text-[10px] ${
                    stage.status === 'complete' ? 'text-emerald-400' :
                    stage.status === 'running' ? 'text-blue-400' :
                    'text-slate-500'
                  }`}>
                    {stage.status === 'complete' ? '✓' : ''}
                  </span>
                </button>
              ))}
            </div>
          )}

          {/* Active tab content */}
          {hasContent && (
            <div className="border-t border-slate-700/50 px-3 py-2 max-h-96 overflow-y-auto text-sm text-slate-200">
              {(() => {
                const segs = activeStage.segments;
                const items = [];
                let i = 0;
                while (i < segs.length) {
                  const seg = segs[i];
                  if (seg.type === 'tool' && seg.subCategory && seg.subCategory !== 'other') {
                    const tools = [];
                    while (i < segs.length && segs[i].type === 'tool' && segs[i].subCategory && segs[i].subCategory !== 'other') {
                      tools.push(segs[i]);
                      i++;
                    }
                    items.push(<ToolChips key={`chips-${i}`} tools={tools} />);
                    continue;
                  }
                  if (seg.type === 'text' && seg.content) {
                    items.push(<div key={i} className="prose prose-invert prose-sm max-w-none" dangerouslySetInnerHTML={{ __html: renderMarkdown(seg.content) }} />);
                  } else if (seg.type === 'skill') {
                    items.push(<SkillBadge key={i} name={seg.name} />);
                  } else if (seg.type === 'tool') {
                    if (seg.params?.command === 'create' && seg.params?.tasks?.length) {
                      items.push(<TaskListCard key={seg.id || i} params={seg.params} status={seg.status} isActive={!isComplete} />);
                    } else if (!(seg.params?.command === 'complete')) {
                      items.push(<ToolCard key={seg.id || i} name={seg.name} status={seg.status} params={seg.params} />);
                    }
                  }
                  i++;
                }
                return items;
              })()}
            </div>
          )}
        </>
      )}
    </div>
  );
}
