// canvas-app/wiring.js
var Wiring = (() => {
  let _svg, _manifest, _state, _navVisible = true
  const FLOW_COLORS = ['#3b82f6','#10b981','#f59e0b','#ef4444','#8b5cf6','#ec4899']
  let _colorIndex = 0

  function init(manifest, state) {
    _manifest = manifest; _state = state
    _svg = document.getElementById('wires-svg')
    FrameManager.setWireRefreshCallback(updatePositions)
    renderAll()
    const navBtn = document.getElementById('toggle-nav-wires')
    if (navBtn) navBtn.classList.add('active')  // visible by default
    navBtn?.addEventListener('click', e => {
      _navVisible = !_navVisible
      e.target.classList.toggle('active', _navVisible)
      renderAll()
    })
  }

  function renderAll() {
    // remove all existing wire paths and labels (keep defs)
    _svg.querySelectorAll('.wire-path, .wire-label').forEach(e => e.remove())
    if (_navVisible) _renderNavWires()
    _renderFlowWires()
    _resizeSVG()
  }

  function _renderNavWires() {
    for (const w of _manifest.nav_wires ?? []) {
      _drawWire(w.from, w.to, '', '#94a3b8', 1.5, true, 'arrow-nav')
    }
  }

  function _renderFlowWires() {
    for (const w of _state.wires ?? []) {
      if (!w.visible) continue
      _drawWire(w.from, w.to, w.label ?? '', w.color, 2.5, false, 'arrow-flow', w.id)
    }
  }

  let _wireMode = false, _wireSource = null

  function enterWireMode() {
    _wireMode = true
    _wireSource = null
    document.getElementById('canvas-container').style.cursor = 'crosshair'
    document.dispatchEvent(new CustomEvent('wire:mode-on'))
    // clicking a frame sets source; clicking another frame completes the wire
    document.addEventListener('click', _onWireClick)
  }

  function exitWireMode() {
    _wireMode = false
    _wireSource = null
    document.getElementById('canvas-container').style.cursor = ''
    document.removeEventListener('click', _onWireClick)
    document.dispatchEvent(new CustomEvent('wire:mode-off'))
  }

  function _onWireClick(e) {
    const card = e.target.closest('.frame-card')
    if (!card) return
    const id = card.dataset.id
    if (!_wireSource) {
      _wireSource = id
      card.style.outline = '2px solid #3b82f6'
    } else {
      if (id === _wireSource) { card.style.outline = ''; _wireSource = null; return }
      const label = prompt('Wire label (optional):') ?? ''
      card.style.outline = ''
      document.querySelector(`[data-id="${_wireSource}"]`).style.outline = ''
      addFlowWire(_wireSource, id, label)
      exitWireMode()
      document.getElementById('tool-wire')?.classList.remove('active')
      document.getElementById('tool-select')?.classList.add('active')
    }
  }

  function addFlowWire(fromId, toId, label) {
    const wire = {
      id:      'wire_' + Math.random().toString(16).slice(2, 8),
      from:    fromId,
      to:      toId,
      label:   label,
      type:    'flow',
      color:   nextColor(),
      visible: true,
    }
    StateManager.addFlowWire(wire)
    renderAll()
    LayersPanel.refresh()
  }

  function _drawWire(fromId, toId, label, color, width, dashed, markerId, wireId) {
    const from = _centerOf(fromId), to = _centerOf(toId)
    if (!from || !to) return

    const dx = to.x - from.x
    const path = document.createElementNS('http://www.w3.org/2000/svg', 'path')
    path.classList.add('wire-path')
    if (wireId) path.dataset.wireId = wireId
    const cp = Math.abs(dx) * 0.5 + 80
    path.setAttribute('d', `M${from.x},${from.y} C${from.x+cp},${from.y} ${to.x-cp},${to.y} ${to.x},${to.y}`)
    path.setAttribute('stroke', color)
    path.setAttribute('stroke-width', width)
    path.setAttribute('fill', 'none')
    path.setAttribute('marker-end', `url(#${markerId})`)
    if (dashed) path.setAttribute('stroke-dasharray', '5 3')
    _svg.appendChild(path)

    if (label) {
      const mx = (from.x + to.x) / 2, my = (from.y + to.y) / 2
      const g = document.createElementNS('http://www.w3.org/2000/svg', 'g')
      g.classList.add('wire-label')
      const rect = document.createElementNS('http://www.w3.org/2000/svg', 'rect')
      rect.setAttribute('x', mx - label.length * 3 - 6)
      rect.setAttribute('y', my - 10)
      rect.setAttribute('width', label.length * 6 + 12)
      rect.setAttribute('height', 18)
      rect.setAttribute('rx', 4)
      rect.setAttribute('fill', color)
      const text = document.createElementNS('http://www.w3.org/2000/svg', 'text')
      text.setAttribute('x', mx); text.setAttribute('y', my + 4)
      text.setAttribute('text-anchor', 'middle')
      text.setAttribute('fill', '#fff')
      text.setAttribute('font-size', '10')
      text.textContent = label
      g.appendChild(rect); g.appendChild(text)
      _svg.appendChild(g)
    }
  }

  function _centerOf(id) {
    const bounds = FrameManager.getAllBounds().find(b => b.id === id)
    if (!bounds) return null
    return { x: bounds.x + bounds.w / 2, y: bounds.y + bounds.h / 2 }
  }

  function _resizeSVG() {
    const bounds = FrameManager.getAllBounds()
    if (!bounds.length) return
    const maxX = Math.max(...bounds.map(b => b.x + b.w)) + 200
    const maxY = Math.max(...bounds.map(b => b.y + b.h)) + 200
    _svg.setAttribute('width', maxX); _svg.setAttribute('height', maxY)
  }

  function updatePositions() { renderAll() }

  function setNavWiresVisible(v) { _navVisible = v; renderAll() }

  function nextColor() {
    const c = FLOW_COLORS[_colorIndex % FLOW_COLORS.length]
    _colorIndex++
    return c
  }

  return { init, renderAll, setNavWiresVisible, updatePositions, nextColor, enterWireMode, exitWireMode, addFlowWire }
})()
