import { useState } from 'react';
import SkillBadge from './SkillBadge';
import ToolCard from './ToolCard';
import TaskListCard from './TaskListCard';
import SubagentCard from './SubagentCard';
import { renderMarkdown } from './markdown';

function chipLabel(seg) {
  const name = seg.name || '';
  if (seg.subCategory === 'file_read') return name.replace(/^Reading\s+/i, '').replace(/^Read\s+/i, '');
  if (seg.subCategory === 'search') return name.replace(/^Searching for\s+/i, '🔍 ').replace(/^Finding\s+/i, '🔍 ');
  if (seg.subCategory === 'shell') {
    const cmd = name.replace(/^Running:\s*/i, '');
    return '⚡ ' + (cmd.length > 40 ? cmd.slice(0, 40) + '…' : cmd);
  }
  return name.length > 40 ? name.slice(0, 40) + '…' : name;
}

function ToolChips({ tools }) {
  const [expanded, setExpanded] = useState(false);
  const MAX_VISIBLE = 4;
  const hasMore = tools.length > MAX_VISIBLE;
  const visible = expanded ? tools : tools.slice(0, MAX_VISIBLE);

  return (
    <div className="my-1">
      <div className="flex flex-wrap gap-1 items-center">
        {visible.map(t => (
          <span key={t.id} className="inline-flex items-center gap-1 px-1.5 py-0.5 rounded bg-slate-700/60 text-[11px] text-slate-400 max-w-[280px]">
            {t.status === 'completed' ? (
              <svg className="w-2.5 h-2.5 text-emerald-400 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7"/></svg>
            ) : t.status === 'failed' ? (
              <svg className="w-2.5 h-2.5 text-red-400 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12"/></svg>
            ) : (
              <span className="w-2.5 h-2.5 border border-blue-400 border-t-transparent rounded-full animate-spin inline-block shrink-0" />
            )}
            <span className="truncate">{chipLabel(t)}</span>
          </span>
        ))}
        {hasMore && !expanded && (
          <button onClick={() => setExpanded(true)} className="px-1.5 py-0.5 rounded bg-slate-700/40 text-[11px] text-slate-500 hover:text-slate-300">
            +{tools.length - MAX_VISIBLE} more
          </button>
        )}
        {hasMore && expanded && (
          <button onClick={() => setExpanded(false)} className="px-1.5 py-0.5 rounded bg-slate-700/40 text-[11px] text-slate-500 hover:text-slate-300">
            less
          </button>
        )}
      </div>
    </div>
  );
}

export { ToolChips };

export default function MessageBubble({ message, isResponding }) {
  if (message.role === 'user') {
    return (
      <div className="flex justify-end">
        <div className="max-w-[75%] rounded-lg px-4 py-2 bg-blue-600 text-white">
          <p className="whitespace-pre-wrap">{message.content}</p>
        </div>
      </div>
    );
  }

  const segments = message.segments || [];

  // Group consecutive segments for rendering
  const rendered = [];
  let i = 0;
  while (i < segments.length) {
    const seg = segments[i];

    // Collect ALL consecutive tool calls (except tasklist) into inline chips
    if (seg.type === 'tool' && seg.subCategory && seg.subCategory !== 'other') {
      const tools = [];
      while (i < segments.length && segments[i].type === 'tool' && segments[i].subCategory && segments[i].subCategory !== 'other') {
        tools.push(segments[i]);
        i++;
      }
      rendered.push(<ToolChips key={`chips-${tools[0].id}`} tools={tools} />);
      continue;
    }

    // Everything else
    if (seg.type === 'text' && seg.content) {
      rendered.push(
        <div key={i} className="prose prose-invert prose-sm max-w-none" dangerouslySetInnerHTML={{ __html: renderMarkdown(seg.content) }} />
      );
    } else if (seg.type === 'skill') {
      rendered.push(<SkillBadge key={i} name={seg.name} />);
    } else if (seg.type === 'tool') {
      if (seg.name?.toLowerCase().includes('todo') || seg.name?.toLowerCase().includes('task list')) {
        rendered.push(<TaskListCard key={seg.id || i} params={seg.params} status={seg.status} isActive={isResponding} />);
      } else {
        rendered.push(<ToolCard key={seg.id || i} name={seg.name} status={seg.status} params={seg.params} duration={seg.duration} />);
      }
    } else if (seg.type === 'subagent') {
      rendered.push(<SubagentCard key={seg.id || i} role={seg.role} status={seg.status} stages={seg.stages} task={seg.task} />);
    }
    i++;
  }

  return (
    <div className="flex justify-start">
      <div className="max-w-[85%] rounded-lg px-4 py-3 bg-slate-800 text-slate-100">
        {rendered}
      </div>
    </div>
  );
}
