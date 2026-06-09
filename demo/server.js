import { WebSocketServer } from 'ws';
import { spawn } from 'child_process';
import { createInterface } from 'readline';
import { fileURLToPath } from 'url';
import path from 'path';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const REPO_ROOT = process.env.DEMO_CWD || path.resolve(__dirname, '..');
const PORT = 3001;

const wss = new WebSocketServer({ port: PORT });
console.log(`[server] WebSocket listening on port ${PORT}`);

wss.on('connection', (ws) => {
  console.log('[server] Client connected');
  let session = null;

  function startSession(agent) {
    if (session) killSession(session);
    session = createSession(agent, ws);
  }

  ws.on('message', (data) => {
    let msg;
    try { msg = JSON.parse(data); } catch { return; }

    if (msg.type === 'set_agent') {
      startSession(msg.agent);
    } else if (msg.type === 'prompt' && session?.ready) {
      sendPrompt(session, msg.text);
    } else if (msg.type === 'cancel' && session) {
      // ACP doesn't support cancel - just tell frontend to stop showing output
      session.muted = true;
      send(ws, { type: 'turn_end' });
    }
  });

  ws.on('close', () => {
    console.log('[server] Client disconnected');
    if (session) killSession(session);
    session = null;
  });
});

function createSession(agent, ws) {
  const args = ['acp', '--trust-all-tools'];
  if (agent) args.push('--agent', agent);

  console.log(`[server] Spawning: kiro-cli ${args.join(' ')}`);
  const proc = spawn('kiro-cli', args, { cwd: REPO_ROOT, stdio: ['pipe', 'pipe', 'pipe'] });

  const ctx = { proc, ws, nextId: 1, sessionId: null, ready: false, pending: new Map(), childSessions: new Map(), subagentToolCallId: null, subagentStages: [] };

  const rl = createInterface({ input: proc.stdout });
  rl.on('line', (line) => handleLine(ctx, line));

  proc.stderr.on('data', (chunk) => console.error(`[stderr] ${chunk.toString().trim()}`));

  proc.on('exit', (code) => {
    console.log(`[server] Subprocess exited (code=${code})`);
    if (!ctx.ready || code !== 0) {
      send(ws, { type: 'error', message: `Subprocess exited (code=${code})` });
    }
    ctx.ready = false;
  });

  sendRpc(ctx, 'initialize', {
    protocolVersion: 1,
    clientCapabilities: {},
    clientInfo: { name: 'hcls-chatbot', version: '0.1.0' }
  });

  return ctx;
}

function handleLine(ctx, line) {
  let msg;
  try { msg = JSON.parse(line); } catch { return; }

  if ('id' in msg) {
    const id = msg.id;
    const handler = ctx.pending.get(id);
    ctx.pending.delete(id);

    if (msg.error) {
      console.error(`[server] RPC error (id=${id}):`, msg.error);
      send(ctx.ws, { type: 'error', message: msg.error.message || 'RPC error' });
      return;
    }

    if (handler) handler(msg.result);
  } else if (msg.method) {
    if (msg.method.startsWith('_kiro.dev/')) return;
    handleNotification(ctx, msg);
  }
}

function handleNotification(ctx, msg) {
  if (msg.method !== 'session/update') return;
  const update = msg.params?.update;
  if (!update) return;

  const notifSessionId = msg.params?.sessionId;
  const isChildSession = notifSessionId && notifSessionId !== ctx.sessionId;

  // Track new child sessions and assign stageIndex
  if (isChildSession && !ctx.childSessions.has(notifSessionId)) {
    const idx = ctx.childSessions.size;
    ctx.childSessions.set(notifSessionId, idx);
    console.log(`[debug] New child session #${idx}: ${notifSessionId} → stage: ${ctx.subagentStages[idx]?.name || 'unknown'}`);
  }

  const type = update.sessionUpdate;

  // Unmute on turn_end (previous response finished)
  if (type === 'turn_end' && !isChildSession) {
    ctx.muted = false;
  }

  // Skip sending if muted (user cancelled)
  if (ctx.muted && !isChildSession) return;

  // --- Child session notifications: route to subagent tabs ---
  if (isChildSession) {
    const stageIndex = ctx.childSessions.get(notifSessionId);

    if (type === 'agent_message_chunk') {
      send(ctx.ws, { type: 'subagent_chunk', id: ctx.subagentToolCallId, stageIndex, text: update.content?.text || '' });
    } else if (type === 'tool_call') {
      const name = update.title || update.name || '';
      const params = update.rawInput || update.params || {};
      const category = classifyTool(name);

      if (category === 'skill') {
        let skillName = null;
        const paths = params.operations?.map(o => o.path) || (params.path ? [params.path] : []);
        for (const p of paths) {
          const match = p?.match(/skills\/([^/]+)/);
          if (match) { skillName = match[1]; break; }
        }
        if (!skillName) skillName = params.__tool_use_purpose || name;
        send(ctx.ws, { type: 'subagent_event', id: ctx.subagentToolCallId, stageIndex, event: { type: 'skill', name: skillName } });
      } else {
        send(ctx.ws, { type: 'subagent_event', id: ctx.subagentToolCallId, stageIndex, event: { type: 'tool', id: update.toolCallId, name, status: update.status, params, subCategory: classifyToolSub(name) } });
      }
    } else if (type === 'tool_call_update') {
      send(ctx.ws, { type: 'subagent_event', id: ctx.subagentToolCallId, stageIndex, event: { type: 'tool_update', id: update.toolCallId, status: update.status } });
    } else if (type === 'turn_end') {
      send(ctx.ws, { type: 'subagent_stage_done', id: ctx.subagentToolCallId, stageIndex });
    }
    return;
  }

  // --- Parent session notifications ---
  if (type === 'tool_call') {
    const name = update.title || update.name || '';
    const params = update.rawInput || update.params || {};
    const category = classifyTool(name);

    if (category === 'subagent') {
      ctx.subagentToolCallId = update.toolCallId;
      ctx.subagentStages = params.stages || [];
      ctx.childSessions = new Map();
      console.log(`[debug] Subagent tool_call: id=${update.toolCallId} stages=${JSON.stringify(ctx.subagentStages.map(s => ({ name: s.name, role: s.role })))}`);
    } else if (category === 'tasklist') {
      console.log(`[debug] Tasklist tool_call: name="${name}" params.command="${params.command}" params=`, JSON.stringify(params).slice(0, 200));
    }

    let skillName = null;
    if (category === 'skill') {
      const paths = params.operations?.map(o => o.path) || (params.path ? [params.path] : []);
      for (const p of paths) {
        const match = p?.match(/skills\/([^/]+)/);
        if (match) { skillName = match[1]; break; }
      }
      if (!skillName) skillName = params.__tool_use_purpose || name;
    }

    send(ctx.ws, {
      type: 'tool_call',
      id: update.toolCallId,
      name: skillName || name,
      status: update.status,
      params,
      category,
      subCategory: category === 'tool' ? classifyToolSub(name) : undefined
    });
  } else if (type === 'tool_call_update') {
    const updateStatus = update.status;
    if (!updateStatus) return;

    // Subagent completing: mark all stages done, then clear tracking
    if (update.toolCallId === ctx.subagentToolCallId && (updateStatus === 'completed' || updateStatus === 'failed')) {
      // Mark all stages as complete
      for (let i = 0; i < ctx.subagentStages.length; i++) {
        send(ctx.ws, { type: 'subagent_stage_done', id: ctx.subagentToolCallId, stageIndex: i });
      }
      ctx.childSessions = new Map();
      ctx.subagentToolCallId = null;
      ctx.subagentStages = [];
    }

    send(ctx.ws, { type: 'tool_update', id: update.toolCallId, status: updateStatus });
  } else if (type === 'agent_message_chunk') {
    send(ctx.ws, { type: 'text_chunk', text: update.content?.text || '' });
  } else if (type === 'turn_end') {
    send(ctx.ws, { type: 'turn_end' });
  }
}

function classifyTool(name) {
  const lower = name.toLowerCase();
  if (lower.includes('skill') || lower.includes('reading skill')) return 'skill';
  if (lower.includes('subagent') || lower.includes('delegate') || lower.includes('spawn')) return 'subagent';
  if (lower.includes('todo') || lower.includes('task list') || lower.includes('completing #')) return 'tasklist';
  return 'tool';
}

function classifyToolSub(name) {
  const lower = name.toLowerCase();
  if (lower.startsWith('reading ') || lower.startsWith('read ')) return 'file_read';
  if (lower.startsWith('finding ') || lower.startsWith('searching ') || lower.startsWith('searching the web')) return 'search';
  if (lower.startsWith('running:') || lower.startsWith('running ')) return 'shell';
  if (lower.startsWith('fetching ')) return 'search';
  return 'other';
}

function sendPrompt(ctx, text) {
  sendRpc(ctx, 'session/prompt', {
    sessionId: ctx.sessionId,
    prompt: [{ type: 'text', text }]
  }, () => {
    send(ctx.ws, { type: 'turn_end' });
  });
}

function sendRpc(ctx, method, params, onResult) {
  const id = ctx.nextId++;
  const msg = { jsonrpc: '2.0', id, method, params };

  ctx.pending.set(id, (result) => {
    if (method === 'initialize') {
      console.log('[server] Initialized');
      sendRpc(ctx, 'session/new', { cwd: REPO_ROOT, mcpServers: [] });
    } else if (method === 'session/new') {
      ctx.sessionId = result?.sessionId;
      ctx.ready = true;
      console.log(`[server] Session ready: ${ctx.sessionId}`);
      send(ctx.ws, { type: 'ready' });
    }
    if (onResult) onResult(result);
  });

  ctx.proc.stdin.write(JSON.stringify(msg) + '\n');
  console.log(`[server] → ${method} (id=${id})`);
}

function killSession(ctx) {
  ctx.ready = false;
  try { ctx.proc.stdin.end(); } catch {}
  setTimeout(() => {
    try { ctx.proc.kill('SIGTERM'); } catch {}
    setTimeout(() => {
      try { ctx.proc.kill('SIGKILL'); } catch {}
    }, 2000);
  }, 500);
}

function send(ws, msg) {
  if (ws.readyState === 1) ws.send(JSON.stringify(msg));
}
