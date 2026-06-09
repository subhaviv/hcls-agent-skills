import { useReducer, useEffect, useRef } from 'react';
import Header from './Header';
import MessageBubble from './MessageBubble';
import TypingIndicator from './TypingIndicator';

const initialState = {
  messages: [],
  isResponding: false,
  connected: false,
  agent: 'hcls',
};

function reducer(state, action) {
  switch (action.type) {
    case 'CONNECTED':
      return { ...state, connected: true };
    case 'DISCONNECTED':
      return { ...state, connected: false, isResponding: false };
    case 'USER_MESSAGE': {
      const userMsg = { role: 'user', content: action.text };
      const agentMsg = { role: 'assistant', segments: [{ type: 'text', content: '' }] };
      return { ...state, messages: [...state.messages, userMsg, agentMsg], isResponding: true };
    }
    case 'TEXT_CHUNK': {
      const msgs = [...state.messages];
      const last = { ...msgs[msgs.length - 1], segments: [...msgs[msgs.length - 1].segments] };
      const lastSeg = last.segments[last.segments.length - 1];
      if (lastSeg && lastSeg.type === 'text') {
        last.segments[last.segments.length - 1] = { ...lastSeg, content: lastSeg.content + action.content };
      } else {
        last.segments.push({ type: 'text', content: action.content });
      }
      msgs[msgs.length - 1] = last;
      return { ...state, messages: msgs };
    }
    case 'TOOL_CALL': {
      const msgs = [...state.messages];
      const last = { ...msgs[msgs.length - 1], segments: [...msgs[msgs.length - 1].segments] };
      last.segments.push({ type: 'tool', id: action.id, name: action.name, status: action.status || 'pending', params: action.params, subCategory: action.subCategory });
      msgs[msgs.length - 1] = last;
      return { ...state, messages: msgs };
    }
    case 'TOOL_UPDATE': {
      const msgs = [...state.messages];
      const last = { ...msgs[msgs.length - 1], segments: [...msgs[msgs.length - 1].segments] };
      const toolIdx = last.segments.findIndex(s => s.type === 'tool' && s.id === action.id);
      if (toolIdx !== -1) {
        last.segments[toolIdx] = { ...last.segments[toolIdx], status: action.status, duration: action.duration };
      } else {
        const subIdx = last.segments.findIndex(s => s.type === 'subagent' && s.id === action.id);
        if (subIdx !== -1) {
          const sub = { ...last.segments[subIdx], stages: [...(last.segments[subIdx].stages || [])] };
          sub.status = action.status;
          if (action.status === 'completed' || action.status === 'done') {
            sub.stages = sub.stages.map(s => ({ ...s, status: 'complete' }));
          }
          last.segments[subIdx] = sub;
        }
      }
      msgs[msgs.length - 1] = last;
      return { ...state, messages: msgs };
    }
    case 'SKILL_ACTIVATED': {
      const msgs = [...state.messages];
      const last = { ...msgs[msgs.length - 1], segments: [...msgs[msgs.length - 1].segments] };
      last.segments.push({ type: 'skill', name: action.name });
      msgs[msgs.length - 1] = last;
      return { ...state, messages: msgs };
    }
    case 'SUBAGENT_CALL': {
      const msgs = [...state.messages];
      const last = { ...msgs[msgs.length - 1], segments: [...msgs[msgs.length - 1].segments] };
      const stagesArr = (action.stages || []).map((s, i) => ({
        name: s.name || s.role || `stage-${i}`,
        role: s.role || '',
        segments: [{ type: 'text', content: '' }],
        status: i === 0 ? 'running' : 'pending'
      }));
      last.segments.push({ type: 'subagent', id: action.id, role: action.role, status: action.status || 'spawned', stages: stagesArr, task: action.task || '' });
      msgs[msgs.length - 1] = last;
      return { ...state, messages: msgs };
    }
    case 'SUBAGENT_CHUNK': {
      const msgs = [...state.messages];
      const last = { ...msgs[msgs.length - 1], segments: [...msgs[msgs.length - 1].segments] };
      const idx = last.segments.findIndex(s => s.type === 'subagent' && s.id === action.id);
      if (idx !== -1) {
        const sub = { ...last.segments[idx], stages: [...last.segments[idx].stages] };
        const si = action.stageIndex;
        if (si != null && sub.stages[si]) {
          const stage = { ...sub.stages[si], segments: [...sub.stages[si].segments] };
          if (stage.status === 'pending') stage.status = 'running';
          const lastSeg = stage.segments[stage.segments.length - 1];
          if (lastSeg?.type === 'text') {
            stage.segments[stage.segments.length - 1] = { ...lastSeg, content: lastSeg.content + action.text };
          } else {
            stage.segments.push({ type: 'text', content: action.text });
          }
          sub.stages[si] = stage;
        }
        last.segments[idx] = sub;
      }
      msgs[msgs.length - 1] = last;
      return { ...state, messages: msgs };
    }
    case 'SUBAGENT_EVENT': {
      const msgs = [...state.messages];
      const last = { ...msgs[msgs.length - 1], segments: [...msgs[msgs.length - 1].segments] };
      const idx = last.segments.findIndex(s => s.type === 'subagent' && s.id === action.id);
      if (idx !== -1) {
        const sub = { ...last.segments[idx], stages: [...last.segments[idx].stages] };
        const si = action.stageIndex;
        if (si != null && sub.stages[si]) {
          const stage = { ...sub.stages[si], segments: [...sub.stages[si].segments] };
          if (stage.status === 'pending') stage.status = 'running';
          if (action.event.type === 'tool_update') {
            const ti = stage.segments.findLastIndex(s => s.type === 'tool' && s.id === action.event.id);
            if (ti !== -1) stage.segments[ti] = { ...stage.segments[ti], status: action.event.status };
          } else {
            stage.segments.push(action.event);
          }
          sub.stages[si] = stage;
        }
        last.segments[idx] = sub;
      }
      msgs[msgs.length - 1] = last;
      return { ...state, messages: msgs };
    }
    case 'SUBAGENT_STAGE_DONE': {
      const msgs = [...state.messages];
      const last = { ...msgs[msgs.length - 1], segments: [...msgs[msgs.length - 1].segments] };
      const idx = last.segments.findIndex(s => s.type === 'subagent' && s.id === action.id);
      if (idx !== -1) {
        const sub = { ...last.segments[idx], stages: [...last.segments[idx].stages] };
        const si = action.stageIndex;
        if (si != null && sub.stages[si]) {
          sub.stages[si] = { ...sub.stages[si], status: 'complete' };
        }
        last.segments[idx] = sub;
      }
      msgs[msgs.length - 1] = last;
      return { ...state, messages: msgs };
    }
    case 'TASKLIST_COMPLETE': {
      const msgs = [...state.messages];
      const last = { ...msgs[msgs.length - 1], segments: [...msgs[msgs.length - 1].segments] };
      // Find the last task list create segment and merge completedIds
      let found = false;
      for (let i = last.segments.length - 1; i >= 0; i--) {
        if (last.segments[i].type === 'tool' && last.segments[i].params?.command === 'create') {
          last.segments[i] = { ...last.segments[i], params: { ...last.segments[i].params, completedIds: [...(last.segments[i].params.completedIds || []), ...action.completedIds] } };
          found = true;
          break;
        }
      }
      console.log('[reducer] TASKLIST_COMPLETE', { completedIds: action.completedIds, found, segCount: last.segments.length });
      msgs[msgs.length - 1] = last;
      return { ...state, messages: msgs };
    }
    case 'TURN_END':
      return { ...state, isResponding: false };
    case 'SET_AGENT':
      return { ...state, agent: action.agent };
    case 'NEW_CHAT':
      return { ...state, messages: [] };
    default:
      return state;
  }
}

export default function ChatPanel() {
  const [state, dispatch] = useReducer(reducer, initialState);
  const wsRef = useRef(null);
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);
  const reconnectTimer = useRef(null);

  const agentRef = useRef(state.agent);
  agentRef.current = state.agent;

  useEffect(() => {
    function connect() {
      const ws = new WebSocket('ws://localhost:3001');
      wsRef.current = ws;

      ws.onopen = () => {
        ws.send(JSON.stringify({ type: 'set_agent', agent: agentRef.current }));
      };

      ws.onmessage = (e) => {
        const msg = JSON.parse(e.data);
        switch (msg.type) {
          case 'ready': dispatch({ type: 'CONNECTED' }); break;
          case 'text_chunk': dispatch({ type: 'TEXT_CHUNK', content: msg.text }); break;
          case 'tool_call':
            if (msg.category === 'skill') {
              dispatch({ type: 'SKILL_ACTIVATED', name: msg.name });
            } else if (msg.category === 'subagent') {
              const stages = msg.params?.stages || [];
              const task = msg.params?.task || msg.params?.prompt_template || '';
              dispatch({ type: 'SUBAGENT_CALL', id: msg.id, role: msg.name, status: msg.status, stages, task });
            } else {
              if (msg.category === 'tasklist' && msg.params?.command === 'complete') {
                dispatch({ type: 'TASKLIST_COMPLETE', completedIds: msg.params.completed_task_ids || [] });
              } else {
                dispatch({ type: 'TOOL_CALL', id: msg.id, name: msg.name, status: msg.status, params: msg.params, subCategory: msg.subCategory });
              }
            }
            break;
          case 'tool_update': dispatch({ type: 'TOOL_UPDATE', id: msg.id, status: msg.status }); break;
          case 'subagent_chunk': dispatch({ type: 'SUBAGENT_CHUNK', id: msg.id, stageIndex: msg.stageIndex, text: msg.text }); break;
          case 'subagent_event': dispatch({ type: 'SUBAGENT_EVENT', id: msg.id, stageIndex: msg.stageIndex, event: msg.event }); break;
          case 'subagent_stage_done': dispatch({ type: 'SUBAGENT_STAGE_DONE', id: msg.id, stageIndex: msg.stageIndex }); break;
          case 'turn_end': dispatch({ type: 'TURN_END' }); break;
          case 'error': dispatch({ type: 'TURN_END' }); break;
        }
      };

      ws.onclose = () => {
        dispatch({ type: 'DISCONNECTED' });
        reconnectTimer.current = setTimeout(connect, 3000);
      };

      ws.onerror = () => ws.close();
    }

    connect();
    return () => {
      clearTimeout(reconnectTimer.current);
      wsRef.current?.close();
    };
  }, []);

  const scrollContainerRef = useRef(null);
  const isNearBottomRef = useRef(true);

  const handleScroll = () => {
    const el = scrollContainerRef.current;
    if (!el) return;
    isNearBottomRef.current = el.scrollHeight - el.scrollTop - el.clientHeight < 100;
  };

  useEffect(() => {
    if (isNearBottomRef.current) {
      messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }
  }, [state.messages, state.isResponding]);

  const handleSend = (text) => {
    if (!text.trim() || state.isResponding || !state.connected) return;
    dispatch({ type: 'USER_MESSAGE', text: text.trim() });
    wsRef.current?.send(JSON.stringify({ type: 'prompt', text: text.trim() }));
  };

  const handleCancel = () => {
    wsRef.current?.send(JSON.stringify({ type: 'cancel' }));
    dispatch({ type: 'TURN_END' });
  };

  const handleAgentChange = (agent) => {
    dispatch({ type: 'SET_AGENT', agent });
    agentRef.current = agent;
    if (wsRef.current?.readyState === 1) {
      wsRef.current.send(JSON.stringify({ type: 'set_agent', agent }));
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    handleSend(inputRef.current.value);
    inputRef.current.value = '';
    inputRef.current.style.height = 'auto';
  };

  return (
    <div className="flex flex-col h-screen">
      <Header connected={state.connected} onNewChat={() => dispatch({ type: 'NEW_CHAT' })} />
      <div ref={scrollContainerRef} onScroll={handleScroll} className="flex-1 overflow-y-auto px-4 py-4 space-y-4">
        {state.messages.map((msg, i) => (
          <MessageBubble key={i} message={msg} isResponding={state.isResponding} />
        ))}
        {state.isResponding && <TypingIndicator />}
        <div ref={messagesEndRef} />
      </div>
      <form onSubmit={handleSubmit} className="p-4 border-t border-slate-700 bg-slate-800">
        <div className="flex gap-2 max-w-4xl mx-auto items-center">
          <select
            value={state.agent}
            onChange={(e) => handleAgentChange(e.target.value)}
            disabled={state.isResponding}
            className="bg-slate-700 text-white text-sm rounded-lg px-2 py-2 border border-slate-600 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50"
            aria-label="Select agent"
          >
            <option value="hcls">hcls</option>
            <option value="hcls-multiagent">hcls-multiagent</option>
          </select>
          <textarea
            ref={inputRef}
            rows={1}
            placeholder={state.connected ? 'Ask about HCLS workflows...' : 'Connecting...'}
            disabled={state.isResponding || !state.connected}
            className="flex-1 bg-slate-700 text-white rounded-lg px-4 py-2 border border-slate-600 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50 placeholder-slate-400 resize-none overflow-hidden"
            aria-label="Message input"
            onInput={(e) => { e.target.style.height = 'auto'; e.target.style.height = e.target.scrollHeight + 'px'; }}
            onKeyDown={(e) => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); handleSubmit(e); } }}
          />
          {state.isResponding ? (
            <button
              type="button"
              onClick={handleCancel}
              className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-500 transition-colors"
              aria-label="Stop response"
            >
              Stop
            </button>
          ) : (
            <button
              type="submit"
              disabled={!state.connected}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              aria-label="Send message"
            >
              Send
            </button>
          )}
        </div>
      </form>
    </div>
  );
}
