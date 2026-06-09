function inlineFormat(text) {
  return text
    .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
    .replace(/`([^`]+)`/g, '<code class="bg-slate-900 px-1 rounded text-sm font-mono">$1</code>')
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.+?)\*/g, '<em>$1</em>');
}

export function renderMarkdown(text) {
  if (!text) return '';

  const codeBlocks = [];
  let processed = text.replace(/```(\w*)\n([\s\S]*?)```/g, (_, lang, code) => {
    const escaped = code.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
    codeBlocks.push(`<pre class="bg-slate-900 rounded p-3 my-2 overflow-x-auto font-mono text-sm"><code>${escaped}</code></pre>`);
    return `\x00CODEBLOCK${codeBlocks.length - 1}\x00`;
  });

  const blocks = processed.split(/\n{2,}/);
  const rendered = blocks.map(block => {
    const lines = block.split('\n');

    // Table - find table within block (may have preceding text)
    const tableStart = lines.findIndex((l, idx) => 
      l.trim().startsWith('|') && lines[idx + 1]?.trim().match(/^\|[\s:|-]+\|$/)
    );
    if (tableStart !== -1) {
      const before = lines.slice(0, tableStart);
      const tableLines = lines.slice(tableStart).filter(l => l.trim().startsWith('|'));
      const parseRow = (line) => line.split('|').slice(1, -1).map(c => c.trim());
      const headers = parseRow(tableLines[0]);
      const rows = tableLines.slice(2).map(parseRow);
      let html = '';
      if (before.length) html += `<p class="my-1">${before.map(l => inlineFormat(l)).join('<br/>')}</p>`;
      html += '<table class="border-collapse my-2 text-sm w-full"><thead><tr>';
      headers.forEach(h => { html += `<th class="border border-slate-700 px-3 py-1 bg-slate-700 font-semibold text-left">${inlineFormat(h)}</th>`; });
      html += '</tr></thead><tbody>';
      rows.forEach((row, i) => {
        html += `<tr class="${i % 2 === 0 ? 'bg-slate-800' : 'bg-[#2d3748]'}">`;
        row.forEach(cell => { html += `<td class="border border-slate-700 px-3 py-1">${inlineFormat(cell)}</td>`; });
        html += '</tr>';
      });
      return html + '</tbody></table>';
    }

    // Headers
    if (block.match(/^#{1,3} /)) {
      const match = block.match(/^(#{1,3}) (.+)$/m);
      if (match) {
        const level = match[1].length;
        const sizes = { 1: 'text-xl font-bold', 2: 'text-lg font-semibold', 3: 'text-base font-semibold' };
        return `<h${level} class="${sizes[level]} my-2">${inlineFormat(match[2])}</h${level}>`;
      }
    }

    // Ordered list
    if (lines.every(l => l.match(/^\d+\.\s/) || l.trim() === '')) {
      const items = lines.filter(l => l.match(/^\d+\.\s/)).map(l => `<li class="ml-4">${inlineFormat(l.replace(/^\d+\.\s/, ''))}</li>`);
      return `<ol class="list-decimal my-1">${items.join('')}</ol>`;
    }

    // Unordered list
    if (lines.every(l => l.match(/^[-*]\s/) || l.trim() === '')) {
      const items = lines.filter(l => l.match(/^[-*]\s/)).map(l => `<li class="ml-4">${inlineFormat(l.replace(/^[-*]\s/, ''))}</li>`);
      return `<ul class="list-disc my-1">${items.join('')}</ul>`;
    }

    // Paragraph
    return `<p class="my-1">${lines.map(l => inlineFormat(l)).join('<br/>')}</p>`;
  });

  let html = rendered.join('');
  html = html.replace(/\x00CODEBLOCK(\d+)\x00/g, (_, i) => codeBlocks[i]);
  return html;
}
