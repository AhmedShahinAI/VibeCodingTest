// canvas-app/layers-panel.js
const LayersPanel = (() => {
  let _manifest, _state, _el

  function init(manifest, state) {
    _manifest = manifest; _state = state
    _el = document.getElementById('layers-content')
    render()
    document.addEventListener('layers:refresh', render)
  }

  function render() {
    if (!_el) return
    _el.innerHTML = ''
    _renderGroup('Pages', _manifest.pages, 'frame')
    _renderGroup('Flow Wires', _state.wires, 'wire')
    _renderGroup('Docs', _state.docs, 'doc')
  }

  function _renderGroup(label, items, type) {
    if (!items.length) return
    const vis = items.filter(i => i.visible !== false).length
    const header = document.createElement('div')
    header.className = 'layer-group-header'
    header.innerHTML = `<span>▾</span><span>${label}</span><span style="margin-left:auto;font-size:10px;font-weight:400">${vis}/${items.length}</span>`
    _el.appendChild(header)

    const list = document.createElement('div')
    for (const item of items) {
      const row = document.createElement('div')
      row.className = 'layer-item'
      const isVisible = item.visible !== false
      const label = item.title ?? item.label ?? item.id
      row.innerHTML = `<button class="eye-btn" title="Toggle visibility">${isVisible ? '👁' : '⊘'}</button><span>${label}</span>`
      row.querySelector('.eye-btn').addEventListener('click', e => {
        e.stopPropagation()
        const newVis = item.visible === false
        if (type === 'frame') FrameManager.setVisible(item.id, newVis)
        else { item.visible = newVis; render() }
      })
      row.addEventListener('click', () => {
        if (type === 'frame') FrameManager.focusFrame(item.id)
      })
      list.appendChild(row)
    }
    _el.appendChild(list)
  }

  function refresh() { render() }

  return { init, refresh }
})()
