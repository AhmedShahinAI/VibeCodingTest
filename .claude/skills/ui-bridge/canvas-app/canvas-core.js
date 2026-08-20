// canvas-app/canvas-core.js
// Infinite pan + zoom engine — Task 10
var CanvasCore = (() => {
  let tx = 0, ty = 0, scale = 1
  const MIN_ZOOM = 0.1, MAX_ZOOM = 3.0
  let _container, _viewport, _zoomDisplay

  function init() {
    _container   = document.getElementById('canvas-container')
    _viewport    = document.getElementById('canvas-viewport')
    _zoomDisplay = document.getElementById('zoom-display')
    _bindEvents()
  }

  let _vpSaveTimer = null
  function applyTransform(animate = false) {
    if (animate) {
      _viewport.style.transition = 'transform 300ms ease-in-out'
      setTimeout(() => { _viewport.style.transition = '' }, 320)
    }
    _viewport.style.transform = `translate(${tx}px,${ty}px) scale(${scale})`
    if (_zoomDisplay) _zoomDisplay.textContent = `${Math.round(scale * 100)}%`
    document.dispatchEvent(new CustomEvent('canvas:transformed'))
    // Save viewport to localStorage (debounced so it doesn't fire every pixel)
    clearTimeout(_vpSaveTimer)
    _vpSaveTimer = setTimeout(() => {
      if (typeof StateManager !== 'undefined') StateManager.saveViewport(tx, ty, scale)
    }, 500)
  }

  function zoom(delta, originX, originY) {
    const newScale = Math.min(MAX_ZOOM, Math.max(MIN_ZOOM, scale * (1 + delta)))
    tx = originX - (originX - tx) * (newScale / scale)
    ty = originY - (originY - ty) * (newScale / scale)
    scale = newScale
    applyTransform()
  }

  function pan(dx, dy) { tx += dx; ty += dy; applyTransform() }

  function screenToCanvas(sx, sy) {
    return { x: (sx - tx) / scale, y: (sy - ty) / scale }
  }

  function canvasToScreen(cx, cy) {
    return { x: cx * scale + tx, y: cy * scale + ty }
  }

  function fitAll(frames) {
    if (!frames || !frames.length) return
    const vis = frames.filter(f => f.visible !== false)
    if (!vis.length) return
    const minX = Math.min(...vis.map(f => f.x))
    const minY = Math.min(...vis.map(f => f.y))
    const maxX = Math.max(...vis.map(f => f.x + f.width))
    const maxY = Math.max(...vis.map(f => f.y + f.height))
    const pad = 60
    const cw = _container.clientWidth
    const ch = _container.clientHeight
    scale = Math.min(MAX_ZOOM, Math.max(MIN_ZOOM,
      Math.min((cw - pad * 2) / (maxX - minX), (ch - pad * 2) / (maxY - minY))
    ))
    tx = pad - minX * scale + (cw - (maxX - minX) * scale) / 2
    ty = pad - minY * scale + (ch - (maxY - minY) * scale) / 2
    applyTransform()
  }

  function animateTo(x, y, z) {
    tx = x; ty = y; scale = z
    applyTransform(true)
    return new Promise(r => setTimeout(r, 320))
  }

  function getTransform() { return { tx, ty, scale } }

  function _bindEvents() {
    let panning = false, startX = 0, startY = 0

    function _canStartPan(target) {
      return target === _container || target === _viewport ||
             target.classList.contains('interaction-blocker')
    }

    _container.addEventListener('mousedown', e => {
      if (!_canStartPan(e.target) || e.button !== 0) return
      panning = true; startX = e.clientX; startY = e.clientY
      _container.style.cursor = 'grabbing'
    })

    window.addEventListener('mousemove', e => {
      if (!panning) return
      pan(e.clientX - startX, e.clientY - startY)
      startX = e.clientX; startY = e.clientY
    })

    window.addEventListener('mouseup', () => {
      panning = false; _container.style.cursor = ''
    })

    // Ctrl/Cmd + scroll → zoom; plain scroll → pan (trackpad two-finger scroll)
    _container.addEventListener('wheel', e => {
      e.preventDefault()
      if (e.ctrlKey || e.metaKey) {
        const r = _container.getBoundingClientRect()
        zoom(-e.deltaY * 0.01, e.clientX - r.left, e.clientY - r.top)
      } else {
        pan(-e.deltaX, -e.deltaY)
      }
    }, { passive: false })

    // Touch: single-finger pan, two-finger pinch+pan
    let _t1x = 0, _t1y = 0, _td = 0, _tmx = 0, _tmy = 0
    _container.addEventListener('touchstart', e => {
      e.preventDefault()
      if (e.touches.length === 1) {
        _t1x = e.touches[0].clientX; _t1y = e.touches[0].clientY; _td = 0
      } else if (e.touches.length === 2) {
        _td = Math.hypot(e.touches[0].clientX - e.touches[1].clientX,
                         e.touches[0].clientY - e.touches[1].clientY)
        _tmx = (e.touches[0].clientX + e.touches[1].clientX) / 2
        _tmy = (e.touches[0].clientY + e.touches[1].clientY) / 2
      }
    }, { passive: false })

    _container.addEventListener('touchmove', e => {
      e.preventDefault()
      if (e.touches.length === 1) {
        pan(e.touches[0].clientX - _t1x, e.touches[0].clientY - _t1y)
        _t1x = e.touches[0].clientX; _t1y = e.touches[0].clientY
      } else if (e.touches.length === 2) {
        const nd = Math.hypot(e.touches[0].clientX - e.touches[1].clientX,
                              e.touches[0].clientY - e.touches[1].clientY)
        const mx = (e.touches[0].clientX + e.touches[1].clientX) / 2
        const my = (e.touches[0].clientY + e.touches[1].clientY) / 2
        const r = _container.getBoundingClientRect()
        if (_td > 0) zoom(nd / _td - 1, mx - r.left, my - r.top)
        pan(mx - _tmx, my - _tmy)
        _td = nd; _tmx = mx; _tmy = my
      }
    }, { passive: false })

    _container.addEventListener('touchend', () => { _td = 0 }, { passive: false })

    document.addEventListener('keydown', e => {
      if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return
      if (e.key === '=' || e.key === '+') zoom(0.1, _container.clientWidth / 2, _container.clientHeight / 2)
      if (e.key === '-') zoom(-0.1, _container.clientWidth / 2, _container.clientHeight / 2)
      if ((e.ctrlKey || e.metaKey) && e.key === '0') {
        e.preventDefault()
        fitAll(typeof StateManager !== 'undefined' ? StateManager.state?.frames : [])
      }
    })

    document.getElementById('zoom-in')?.addEventListener('click',
      () => zoom(0.1, _container.clientWidth / 2, _container.clientHeight / 2))
    document.getElementById('zoom-out')?.addEventListener('click',
      () => zoom(-0.1, _container.clientWidth / 2, _container.clientHeight / 2))
  }

  return { init, zoom, pan, screenToCanvas, canvasToScreen, fitAll, animateTo, getTransform, applyTransform }
})()
