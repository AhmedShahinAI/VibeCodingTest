// canvas-app/doc-cards.js
// Markdown doc cards — Task 16
var DocCards = (() => {
  let _manifest, _state, _viewport
  const _cards = new Map()  // docId → {el, docState}

  function init(manifest, state) {
    _manifest = manifest; _state = state
    _viewport = document.getElementById('canvas-viewport')
    renderAll()
    _setupToolbar()
  }

  function renderAll() {
    for (const docState of _state.docs) {
      if (!_cards.has(docState.id)) _createCard(docState)
    }
  }

  function addCard(docId) {
    const existing = _state.docs.find(d => d.id === docId)
    if (existing) { _scrollToDoc(docId); return }
    const { tx, ty, scale } = CanvasCore.getTransform()
    const cont = document.getElementById('canvas-container')
    const docState = {
      id: docId,
      x: -tx / scale + cont.clientWidth / (scale * 2),
      y: -ty / scale + 40,
      width: 400,
      visible: true
    }
    StateManager.addDocCard(docState)
    _createCard(docState)
    LayersPanel.refresh()
  }

  function _scrollToDoc(docId) {
    const entry = _cards.get(docId)
    if (!entry) return
    const { docState } = entry
    const cont = document.getElementById('canvas-container')
    const { scale } = CanvasCore.getTransform()
    const tx = cont.clientWidth / 2 - docState.x * scale
    const ty = cont.clientHeight / 2 - docState.y * scale
    CanvasCore.animateTo(tx, ty, scale)
  }

  function _createCard(docState) {
    const docMeta = _manifest.docs.find(d => d.id === docState.id)
    if (!docMeta) return
    const el = document.createElement('div')
    el.className = 'doc-card'
    el.dataset.docId = docState.id
    el.style.transform = `translate(${docState.x}px,${docState.y}px)`
    el.style.width = (docState.width || 400) + 'px'
    el.innerHTML = `
      <div class="doc-card-title-bar">
        <span class="doc-card-title">📄 ${docMeta.title}</span>
        <button class="frame-close" style="color:#9ca3af" title="Close">×</button>
      </div>
      <div class="doc-card-body">Loading…</div>`

    el.querySelector('.frame-close').addEventListener('click', () => {
      el.remove()
      _cards.delete(docState.id)
      _state.docs = _state.docs.filter(d => d.id !== docState.id)
      LayersPanel.refresh()
    })

    _bindDocDrag(el, docState)
    _viewport.appendChild(el)
    _cards.set(docState.id, { el, docState })

    // fetch and render markdown
    fetch(docMeta.file)
      .then(r => r.text())
      .then(md => {
        el.querySelector('.doc-card-body').innerHTML = parseMarkdown(md)
      })
      .catch(() => {
        el.querySelector('.doc-card-body').textContent = 'Could not load ' + docMeta.file
      })
  }

  function _bindDocDrag(el, docState) {
    const titleBar = el.querySelector('.doc-card-title-bar')
    let dragging = false, startMX, startMY, startX, startY

    titleBar.addEventListener('mousedown', e => {
      if (e.button !== 0) return
      e.stopPropagation()
      dragging = true
      startMX = e.clientX; startMY = e.clientY
      startX = docState.x; startY = docState.y
      window.addEventListener('mousemove', onMove)
      window.addEventListener('mouseup', onUp)
    })

    function onMove(e) {
      if (!dragging) return
      const { scale } = CanvasCore.getTransform()
      docState.x = startX + (e.clientX - startMX) / scale
      docState.y = startY + (e.clientY - startMY) / scale
      el.style.transform = `translate(${docState.x}px,${docState.y}px)`
      StateManager.updateDocPosition(docState.id, docState.x, docState.y)
    }

    function onUp() {
      dragging = false
      window.removeEventListener('mousemove', onMove)
      window.removeEventListener('mouseup', onUp)
    }
  }

  function _setupToolbar() {
    const btn = document.getElementById('tool-add-doc')
    if (!btn) return
    btn.addEventListener('click', () => {
      if (!_manifest.docs || !_manifest.docs.length) {
        alert('No docs available in this project.')
        return
      }
      const opts = _manifest.docs.map((d, i) => `${i + 1}. ${d.title}`).join('\n')
      const input = prompt('Add doc card:\n' + opts + '\n\nEnter number:')
      if (!input) return
      const idx = parseInt(input) - 1
      if (idx >= 0 && idx < _manifest.docs.length) addCard(_manifest.docs[idx].id)
    })
  }

  return { init, addCard, renderAll }
})()
