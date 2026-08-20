// canvas-app/frame-manager.js
// Frame cards — iframe, interaction blocker, drag reposition, focus animation — Task 11
var FrameManager = (() => {
  const _frames = new Map()  // id → {el, page, state}
  let _viewport, _container
  let _wireRefresh = null   // set by Wiring after init
  let _frameScale  = 1.0   // S=0.65, M=1.0, L=1.5

  // Build the transform string used on every frame-card.
  // Scale is included here (not via CSS) so it composes correctly with translate:
  // translate(x,y) happens first (positions in canvas), then scale from top-left.
  function _tf(x, y) { return `translate(${x}px,${y}px) scale(${_frameScale})` }

  function init(manifest, state) {
    _viewport  = document.getElementById('canvas-viewport')
    _container = document.getElementById('canvas-container')
    const stateMap = Object.fromEntries(state.frames.map(f => [f.id, f]))
    for (const page of manifest.pages) {
      const fs = stateMap[page.id]
      if (!fs) continue
      const el = createFrame(page, fs)
      _viewport.appendChild(el)
      _frames.set(page.id, { el, page, state: fs })
    }
    _container.addEventListener('click', e => {
      if (e.target === _container || e.target === _viewport) _clearFocus()
    })
    document.addEventListener('keydown', e => {
      if (e.key === 'Escape') _clearFocus()
    })
  }

  function createFrame(page, fs) {
    const el = document.createElement('div')
    el.className = 'frame-card preview-mode'  // preview mode on by default
    el.dataset.id = page.id
    if (!fs.visible) el.style.display = 'none'
    el.style.transform = _tf(fs.x, fs.y)
    el.style.width  = fs.width  + 'px'
    el.style.height = fs.height + 'px'

    el.innerHTML = `
      <div class="frame-title-bar">
        <span class="frame-title">${page.title}</span>
        <span class="frame-group-badge">${page.group}</span>
        <button class="frame-expand" title="Full view (double-click)">⛶</button>
        <button class="frame-close" title="Hide">×</button>
      </div>
      <div class="frame-body">
        <iframe src="${page.file}" loading="lazy" title="${page.title}"></iframe>
        <div class="interaction-blocker"></div>
      </div>
      <button class="preview-toggle">Exit Preview</button>`

    el.querySelector('.frame-close').addEventListener('click', e => {
      e.stopPropagation()
      setVisible(page.id, false)
    })
    el.querySelector('.frame-expand').addEventListener('click', e => {
      e.stopPropagation()
      PageModal.open(page)
    })
    el.querySelector('.preview-toggle').addEventListener('click', e => {
      e.stopPropagation()
      el.classList.toggle('preview-mode')
      e.target.textContent = el.classList.contains('preview-mode') ? 'Exit Preview' : 'Preview Mode'
    })

    // Title bar double-click = open modal.
    // NOTE: body double-click CANNOT work in preview mode — clicks go into the iframe
    // document and never bubble back to the frame-card. Title bar and ⛶ button are
    // the only reliable dblclick / click targets outside the iframe.
    el.querySelector('.frame-title-bar').addEventListener('dblclick', e => {
      e.stopPropagation()
      PageModal.open(page)
    })
    // Fallback: body dblclick works when interaction-blocker IS visible (non-preview mode)
    el.addEventListener('dblclick', e => {
      if (e.target.closest('.frame-title-bar')) return  // handled above
      if (e.target.classList.contains('interaction-blocker')) PageModal.open(page)
    })

    _bindDrag(el, page.id, fs)
    return el
  }

  function _bindDrag(el, id, fs) {
    const titleBar = el.querySelector('.frame-title-bar')
    let dragging = false, startMX, startMY, startFX, startFY

    // Mouse drag
    // Critical: disable pointer-events on ALL iframes on drag start so mousemove
    // events don't get swallowed by iframe documents when the cursor crosses them.
    titleBar.addEventListener('mousedown', e => {
      if (e.button !== 0) return
      e.stopPropagation()
      dragging = true
      startMX = e.clientX; startMY = e.clientY
      startFX = fs.x; startFY = fs.y
      document.querySelectorAll('.frame-body iframe').forEach(f => f.style.pointerEvents = 'none')
      window.addEventListener('mousemove', onMove)
      window.addEventListener('mouseup', onUp)
    })

    // Touch drag — stopPropagation prevents canvas pan from also firing
    // Tap (no movement > 4px) → focus frame; drag (movement) → reposition frame
    let _touchMoved = false
    titleBar.addEventListener('touchstart', e => {
      if (e.touches.length !== 1) return
      e.stopPropagation()
      dragging = true; _touchMoved = false
      startMX = e.touches[0].clientX; startMY = e.touches[0].clientY
      startFX = fs.x; startFY = fs.y
    }, { passive: true })

    titleBar.addEventListener('touchmove', e => {
      if (!dragging || e.touches.length !== 1) return
      e.stopPropagation()
      const dx = e.touches[0].clientX - startMX
      const dy = e.touches[0].clientY - startMY
      if (Math.abs(dx) > 4 || Math.abs(dy) > 4) _touchMoved = true
      const { scale } = CanvasCore.getTransform()
      fs.x = startFX + dx / scale
      fs.y = startFY + dy / scale
      el.style.transform = _tf(fs.x, fs.y)
      StateManager.updateFramePosition(id, fs.x, fs.y)
      if (_wireRefresh) _wireRefresh()
    }, { passive: true })

    titleBar.addEventListener('touchend', e => {
      if (!_touchMoved) { e.stopPropagation(); focusFrame(id) }  // tap = focus frame
      dragging = false; _touchMoved = false
    }, { passive: true })

    function onMove(e) {
      if (!dragging) return
      const { scale } = CanvasCore.getTransform()
      const dx = (e.clientX - startMX) / scale
      const dy = (e.clientY - startMY) / scale
      fs.x = startFX + dx
      fs.y = startFY + dy
      el.style.transform = _tf(fs.x, fs.y)
      StateManager.updateFramePosition(id, fs.x, fs.y)
      if (_wireRefresh) _wireRefresh()
    }

    function onUp() {
      dragging = false
      document.querySelectorAll('.frame-body iframe').forEach(f => f.style.pointerEvents = '')
      window.removeEventListener('mousemove', onMove)
      window.removeEventListener('mouseup', onUp)
    }
  }

  function focusFrame(id) {
    _clearFocus()
    const entry = _frames.get(id)
    if (!entry) return
    entry.el.classList.add('focused')
    const fs = entry.state
    const cont = document.getElementById('canvas-container')
    const padX = 80, padY = 80
    // Account for current card scale so the focus zoom fits the visual card size
    const vW = fs.width  * _frameScale
    const vH = fs.height * _frameScale
    const zoom = Math.min(3, Math.max(0.2,
      Math.min((cont.clientWidth  - padX * 2) / vW,
               (cont.clientHeight - padY * 2) / vH)
    ))
    const tx = (cont.clientWidth  - vW * zoom) / 2 - fs.x * zoom
    const ty = (cont.clientHeight - vH * zoom) / 2 - fs.y * zoom
    CanvasCore.animateTo(tx, ty, zoom)
  }

  function _clearFocus() {
    _frames.forEach(e => e.el.classList.remove('focused'))
  }

  function setVisible(id, visible) {
    const entry = _frames.get(id)
    if (!entry) return
    entry.state.visible = visible
    entry.el.style.display = visible ? '' : 'none'
    StateManager.setFrameVisible(id, visible)
    document.dispatchEvent(new CustomEvent('layers:refresh'))
  }

  function getAllBounds() {
    return Array.from(_frames.values())
      .filter(e => e.state.visible !== false)
      .map(e => ({
        id: e.page.id,
        x: e.state.x, y: e.state.y,
        // Report visual size (scaled) so fitAll and minimap match what the user sees
        w: e.state.width  * _frameScale,
        h: e.state.height * _frameScale
      }))
  }

  // Change card size: 's' = 0.65×, 'm' = 1× (default), 'l' = 1.5×
  // Re-applies transform to all existing frames so the change is immediate.
  function setCardSize(size) {
    const SCALES = { s: 0.65, m: 1.0, l: 1.5 }
    _frameScale = SCALES[size] ?? 1.0
    _frames.forEach(({ el, state: fs }) => {
      el.style.transform = _tf(fs.x, fs.y)
    })
    if (_wireRefresh) _wireRefresh()
  }

  function setWireRefreshCallback(fn) { _wireRefresh = fn }

  return { init, createFrame, focusFrame, setVisible, getAllBounds, setWireRefreshCallback, setCardSize }
})()
