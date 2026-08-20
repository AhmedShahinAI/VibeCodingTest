function parseMarkdown(md) {
  const lines = md.split('\n')
  const html = []
  let inCode = false, inList = false

  for (let i = 0; i < lines.length; i++) {
    let line = lines[i]

    if (line.startsWith('```')) {
      if (!inCode) { if (inList) { html.push('</ul>'); inList = false } html.push('<pre><code>'); inCode = true }
      else          { html.push('</code></pre>'); inCode = false }
      continue
    }
    if (inCode) { html.push(escHtml(line)); continue }

    if (line.startsWith('# '))      { if (inList) { html.push('</ul>'); inList = false } html.push(`<h1>${inline(line.slice(2))}</h1>`); continue }
    if (line.startsWith('## '))     { if (inList) { html.push('</ul>'); inList = false } html.push(`<h2>${inline(line.slice(3))}</h2>`); continue }
    if (line.startsWith('### '))    { if (inList) { html.push('</ul>'); inList = false } html.push(`<h3>${inline(line.slice(4))}</h3>`); continue }
    if (line.startsWith('#### '))   { if (inList) { html.push('</ul>'); inList = false } html.push(`<h4>${inline(line.slice(5))}</h4>`); continue }
    if (line.startsWith('- ') || line.startsWith('* ')) {
      if (!inList) { html.push('<ul>'); inList = true }
      html.push(`<li>${inline(line.slice(2))}</li>`)
      continue
    }
    if (inList) { html.push('</ul>'); inList = false }
    if (line.trim() === '') { html.push('<br>'); continue }
    html.push(`<p>${inline(line)}</p>`)
  }
  if (inList) html.push('</ul>')
  if (inCode) html.push('</code></pre>')
  return html.join('\n')
}

function inline(text) {
  return text
    .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
    .replace(/`([^`]+)`/g, '<code>$1</code>')
    .replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>')
    .replace(/\*([^*]+)\*/g, '<em>$1</em>')
    .replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2">$1</a>')
}

function escHtml(s) {
  return s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;')
}
