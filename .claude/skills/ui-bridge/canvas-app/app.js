// canvas-app/app.js
async function main() {
  const [manifest, rawState] = await Promise.all([
    fetch(MANIFEST_URL).then(r => r.json()),
    fetch(STATE_URL).then(r => r.json()).catch(() => null)
  ])

  // Merge: start with canvas-state.json, then overlay any localStorage changes on top.
  // localStorage is keyed per-project so different projects don't share state.
  const lsKey  = 'canvas:state:' + (manifest.project || 'default')
  const lsRaw  = (() => { try { return JSON.parse(localStorage.getItem(lsKey)) } catch(_) { return null } })()
  const baseState = rawState ?? StateManager.generateDefaultLayout(manifest)
  // If localStorage has a newer version of state for this project, prefer it
  const state = StateManager.migrateState(lsRaw ?? baseState)
  // Stamp project name onto state (used by storage keys)
  state.project = manifest.project || 'default'
  StateManager.state = state

  CanvasCore.init()
  FrameManager.init(manifest, state)
  LayersPanel.init(manifest, state)
  Wiring.init(manifest, state)
  DocCards.init(manifest, state)
  Minimap.init()
  Presentation.init()
  PageModal.init()

  // Card size toggle (S / M / L)
  const SIZES = ['s', 'm', 'l']
  function _applySize(size) {
    FrameManager.setCardSize(size)
    SIZES.forEach(s => document.getElementById(`size-${s}`)?.classList.toggle('active', s === size))
    if (state.card_size !== size) { state.card_size = size; StateManager.markDirty() }
  }
  SIZES.forEach(s => document.getElementById(`size-${s}`)?.addEventListener('click', () => _applySize(s)))
  // Restore saved size from state
  _applySize(state.card_size ?? 'm')

  // Toolbar mode buttons
  const modes = ['select','pan','wire']
  modes.forEach(m => {
    document.getElementById(`tool-${m}`)?.addEventListener('click', () => {
      modes.forEach(x => document.getElementById(`tool-${x}`)?.classList.remove('active'))
      document.getElementById(`tool-${m}`)?.classList.add('active')
      if (m === 'wire') Wiring.enterWireMode()
      else Wiring.exitWireMode?.()
    })
  })

  // Save button: tries POST /save (local server) first, falls back to download.
  // Run `python server.py` in ui-preview/ to enable the server write path.
  const saveBtn = document.getElementById('save-btn')

  async function _saveToServer() {
    try {
      const r = await fetch('/save', {
        method:  'POST',
        headers: { 'Content-Type': 'application/json' },
        body:    JSON.stringify(StateManager.state),
      })
      return r.ok
    } catch (_) { return false }
  }

  saveBtn?.addEventListener('click', async () => {
    _setSaveLabel('Saving…')
    const ok = await _saveToServer()
    if (ok) {
      _setSaveLabel('Saved to disk ✓')
    } else {
      StateManager.saveDownload()
      _setSaveLabel('Downloaded ✓')
    }
  })

  // Autosave indicator: briefly shows "●" in Save button after each auto-save
  document.addEventListener('state:autosaved', () => _setSaveLabel('● Auto-saved'))
  function _setSaveLabel(text) {
    if (!saveBtn) return
    saveBtn.textContent = text
    clearTimeout(saveBtn._t)
    saveBtn._t = setTimeout(() => { saveBtn.textContent = 'Save' }, 2000)
  }

  // Restore saved viewport (pan/zoom) — only if localStorage has one
  const savedVP = StateManager.loadViewport()
  if (savedVP) {
    CanvasCore.animateTo(savedVP.tx, savedVP.ty, savedVP.scale)
  } else {
    setTimeout(() => CanvasCore.fitAll(state.frames), 100)
  }

  // Onboarding banner (dismiss after first view; key is per-project)
  const _storageKey = 'canvas:onboarded:' + (manifest.project || 'default').toLowerCase().replace(/\s+/g, '-')
  if (!localStorage.getItem(_storageKey)) {
    const banner = document.createElement('div')
    banner.style.cssText = 'position:fixed;top:52px;left:50%;transform:translateX(-50%);background:#1e40af;color:#fff;padding:10px 20px;border-radius:6px;font-size:12px;z-index:999;cursor:pointer;max-width:90vw;text-align:center;'
    banner.textContent = '💡 Deploy this folder to a web server or GitHub Pages to share it with your team. Click to dismiss.'
    banner.addEventListener('click', () => { banner.remove(); localStorage.setItem(_storageKey, '1') })
    document.body.appendChild(banner)
  }
}

main().catch(console.error)
