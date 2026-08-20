// canvas-app/minimap.js
// Frame thumbnails + viewport indicator + click navigation — Task 13
var Minimap = (() => {
  let _W, _H
  let _canvas, _ctx, _container, _canvasContainer

  function _getDims() {
    return window.innerWidth <= 1024
      ? { w: 120, h: 90 }
      : { w: 180, h: 140 }
  }

  function init() {
    _container      = document.getElementById('minimap-container')
    _canvasContainer = document.getElementById('canvas-container')
    const d = _getDims(); _W = d.w; _H = d.h
    _canvas = document.createElement('canvas')
    _canvas.id = 'minimap-canvas'
    _canvas.width = _W; _canvas.height = _H
    _canvas.style.display = 'block'
    _container.appendChild(_canvas)
    _ctx = _canvas.getContext('2d')
    document.addEventListener('canvas:transformed', render)
    _canvas.addEventListener('click', _onClick)

    // Resize: update canvas dimensions and re-render
    window.addEventListener('resize', () => {
      const nd = _getDims()
      if (nd.w !== _W) {
        _W = nd.w; _H = nd.h
        _canvas.width = _W; _canvas.height = _H
        render()
      }
    })
  }

  function render() {
    if (!_ctx) return
    const W = _W, H = _H
    const bounds = FrameManager.getAllBounds()
    if (!bounds.length) return
    _ctx.clearRect(0, 0, W, H)

    const minX = Math.min(...bounds.map(b => b.x))
    const minY = Math.min(...bounds.map(b => b.y))
    const maxX = Math.max(...bounds.map(b => b.x + b.w))
    const maxY = Math.max(...bounds.map(b => b.y + b.h))
    const pad = 8
    const scaleX = (W - pad*2) / (maxX - minX || 1)
    const scaleY = (H - pad*2) / (maxY - minY || 1)
    const s = Math.min(scaleX, scaleY)

    // store for click mapping
    _canvas._minX = minX; _canvas._minY = minY; _canvas._s = s; _canvas._pad = pad

    // draw frames
    _ctx.fillStyle = '#3b82f6'
    for (const b of bounds) {
      _ctx.fillRect(
        pad + (b.x - minX) * s,
        pad + (b.y - minY) * s,
        Math.max(2, b.w * s),
        Math.max(2, b.h * s)
      )
    }

    // draw viewport
    const { tx, ty, scale } = CanvasCore.getTransform()
    const cw = _canvasContainer.clientWidth
    const ch = _canvasContainer.clientHeight
    const vx1 = (-tx / scale - minX) * s + pad
    const vy1 = (-ty / scale - minY) * s + pad
    const vw  = (cw / scale) * s
    const vh  = (ch / scale) * s
    _ctx.strokeStyle = '#fbbf24'
    _ctx.lineWidth = 1.5
    _ctx.strokeRect(vx1, vy1, vw, vh)
  }

  function _onClick(e) {
    const r = _canvas.getBoundingClientRect()
    const mx = e.clientX - r.left, my = e.clientY - r.top
    const { _minX, _minY, _s, _pad } = _canvas
    if (_s === undefined) return
    const { scale } = CanvasCore.getTransform()
    const cx = (mx - _pad) / _s + _minX
    const cy = (my - _pad) / _s + _minY
    const cw = _canvasContainer.clientWidth
    const ch = _canvasContainer.clientHeight
    CanvasCore.animateTo(-cx * scale + cw/2, -cy * scale + ch/2, scale)
  }

  return { init, render }
})()
