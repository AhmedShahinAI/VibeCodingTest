// canvas-app/state-manager.js
// Global StateManager IIFE — no imports/exports
// Use var so eval() in test harness exposes it to the calling scope
var StateManager = (() => {
  let _state = null
  let _saveTimer = null

  // Keys are project-scoped so different projects don't share localStorage state
  const _lsStateKey    = () => 'canvas:state:'    + ((_state && _state.project) || 'default')
  const _lsViewportKey = () => 'canvas:viewport:' + ((_state && _state.project) || 'default')

  // Debounced auto-save — fires 600ms after the last mutation
  function _scheduleAutoSave() {
    clearTimeout(_saveTimer)
    _saveTimer = setTimeout(() => {
      try {
        localStorage.setItem(_lsStateKey(), JSON.stringify(_state))
        document.dispatchEvent(new CustomEvent('state:autosaved'))
      } catch (_) {}
    }, 600)
  }

  function saveViewport(tx, ty, scale) {
    try { localStorage.setItem(_lsViewportKey(), JSON.stringify({ tx, ty, scale })) } catch (_) {}
  }

  function loadViewport() {
    try { return JSON.parse(localStorage.getItem(_lsViewportKey())) } catch (_) { return null }
  }

  function migrateState(s) {
    if (!s.version || s.version < 1) {
      s.version     = 1
      s.story_stops = s.story_stops ?? []
      s.docs        = s.docs        ?? []
      s.wires       = s.wires       ?? []
    }
    s.card_size = s.card_size ?? 'm'
    return s
  }

  function generateDefaultLayout(manifest) {
    const FRAME_W = 380, FRAME_H = 480, GAP_Y = 40, GAP_X = 120
    const groups = {}, order = []
    for (const p of manifest.pages) {
      const g = p.group ?? 'Other'
      if (!groups[g]) { groups[g] = []; order.push(g) }
      groups[g].push(p)
    }
    const frames = []
    let colX = 0
    for (const g of order) {
      let y = 0
      for (const p of groups[g]) {
        frames.push({ id: p.id, x: colX, y, width: FRAME_W, height: FRAME_H, visible: true })
        y += FRAME_H + GAP_Y
      }
      colX += FRAME_W + GAP_X
    }
    return { version: 1, frames, wires: [], docs: [], story_stops: [] }
  }

  function getState() { return _state }

  function updateFramePosition(id, x, y) {
    const f = _state.frames.find(f => f.id === id)
    if (f) { f.x = x; f.y = y; _scheduleAutoSave() }
  }

  function setFrameVisible(id, visible) {
    const f = _state.frames.find(f => f.id === id)
    if (f) { f.visible = visible; _scheduleAutoSave() }
  }

  function addFlowWire(wire) { _state.wires.push(wire); _scheduleAutoSave() }

  function removeWire(id) {
    _state.wires = _state.wires.filter(w => w.id !== id)
    _scheduleAutoSave()
  }

  function addDocCard(doc) {
    if (!_state.docs.find(d => d.id === doc.id)) { _state.docs.push(doc); _scheduleAutoSave() }
  }

  function updateDocPosition(id, x, y) {
    const d = _state.docs.find(d => d.id === id)
    if (d) { d.x = x; d.y = y; _scheduleAutoSave() }
  }

  function addStoryStop(stop) { _state.story_stops.push(stop); _scheduleAutoSave() }

  function removeStoryStop(id) {
    _state.story_stops = _state.story_stops.filter(s => s.id !== id)
    _scheduleAutoSave()
  }

  // Expose auto-save for external callers (e.g. card size change)
  function markDirty() { _scheduleAutoSave() }

  function saveDownload() {
    const blob = new Blob([JSON.stringify(_state, null, 2)], { type: 'application/json' })
    const a = document.createElement('a')
    a.href = URL.createObjectURL(blob)
    a.download = 'canvas-state.json'
    a.click()
    URL.revokeObjectURL(a.href)
  }

  function applyImported(raw) {
    _state = migrateState(raw)
    document.dispatchEvent(new CustomEvent('state:loaded', { detail: _state }))
  }

  // Guard drag-drop listeners so Node.js test stubs don't crash
  if (typeof document !== 'undefined' && typeof document.addEventListener === 'function') {
    document.addEventListener('dragover', e => e && typeof e.preventDefault === 'function' && e.preventDefault())
    document.addEventListener('drop', e => {
      const file = e && e.dataTransfer && e.dataTransfer.files && e.dataTransfer.files[0]
      if (!file || !file.name || !file.name.endsWith('.json')) return
      file.text().then(t => applyImported(JSON.parse(t)))
    })
  }

  return {
    get state() { return _state },
    set state(v) { _state = v },
    migrateState, generateDefaultLayout, getState,
    updateFramePosition, setFrameVisible,
    addFlowWire, removeWire,
    addDocCard, updateDocPosition,
    addStoryStop, removeStoryStop,
    saveDownload, applyImported,
    saveViewport, loadViewport, markDirty,
  }
})()
