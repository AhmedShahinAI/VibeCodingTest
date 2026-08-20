// canvas-app/presentation.js
const Presentation = (() => {
  let _active = false, _current = 0

  function init() {
    document.getElementById('present-btn')?.addEventListener('click', enter)
    document.getElementById('add-stop-btn')?.addEventListener('click', addStop)
    document.getElementById('prev-stop')?.addEventListener('click', prev)
    document.getElementById('next-stop')?.addEventListener('click', next)
    document.addEventListener('keydown', e => {
      if (_active && e.key === 'ArrowRight') next()
      if (_active && e.key === 'ArrowLeft')  prev()
      if (_active && e.key === 'Escape')     exit()
      if (!_active && e.key === 'F5') { e.preventDefault(); enter() }
    })

    // Touch swipe: left = next, right = prev
    let _sx = 0, _sy = 0
    document.addEventListener('touchstart', e => {
      if (!_active) return
      _sx = e.touches[0].clientX
      _sy = e.touches[0].clientY
    }, { passive: true })
    document.addEventListener('touchend', e => {
      if (!_active) return
      const dx = e.changedTouches[0].clientX - _sx
      const dy = e.changedTouches[0].clientY - _sy
      if (Math.abs(dx) > 48 && Math.abs(dx) > Math.abs(dy)) {
        if (dx < 0) next(); else prev()
      }
    }, { passive: true })
  }

  function enter() {
    const stops = StateManager.state.story_stops
    if (!stops.length) { alert('No story stops yet.\n\nArrange the canvas view and click "+ Stop" to add one.'); return }
    _active = true
    _current = 0
    document.body.classList.add('presenting')
    document.getElementById('presentation-bar').hidden = false
    document.documentElement.requestFullscreen?.().catch(() => {})
    _showStop(_current)
  }

  function exit() {
    _active = false
    document.body.classList.remove('presenting')
    document.getElementById('presentation-bar').hidden = true
    document.exitFullscreen?.().catch(() => {})
  }

  function addStop() {
    const { tx, ty, scale } = CanvasCore.getTransform()
    const label = prompt('Story stop label:')
    if (!label) return
    const stop = {
      id:       'stop_' + Math.random().toString(16).slice(2, 8),
      label,
      viewport: { x: tx, y: ty, zoom: scale }
    }
    StateManager.addStoryStop(stop)
    LayersPanel.refresh()
  }

  function goTo(i) {
    const stops = StateManager.state.story_stops
    if (!stops.length) return
    _current = Math.max(0, Math.min(stops.length - 1, i))
    _showStop(_current)
  }

  function _showStop(i) {
    const stops = StateManager.state.story_stops
    if (!stops[i]) return
    const s = stops[i]
    CanvasCore.animateTo(s.viewport.x, s.viewport.y, s.viewport.zoom)
    document.getElementById('stop-label').textContent   = s.label
    document.getElementById('stop-counter').textContent = `${i+1} / ${stops.length}`
    Wiring.setNavWiresVisible(false)
  }

  function next() { goTo(_current + 1) }
  function prev() { goTo(_current - 1) }

  return { init, enter, exit, addStop, goTo, next, prev }
})()
