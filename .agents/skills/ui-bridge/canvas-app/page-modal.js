// canvas-app/page-modal.js
// Full-page preview modal — opens on double-click or expand button
var PageModal = (() => {
  let _modal, _iframe, _title

  function init() {
    _modal  = document.getElementById('page-modal')
    _iframe = document.getElementById('page-modal-iframe')
    _title  = document.getElementById('page-modal-title')

    document.getElementById('page-modal-backdrop')?.addEventListener('click', close)
    document.getElementById('page-modal-close')?.addEventListener('click', close)
    document.addEventListener('keydown', e => {
      if (e.key === 'Escape' && _modal && !_modal.hidden) close()
    })
  }

  function open(page) {
    if (!_modal) return
    _title.textContent = page.title
    _iframe.src = page.file
    _iframe.title = page.title || ''
    _modal.hidden = false
  }

  function close() {
    if (!_modal) return
    _modal.hidden = true
    _iframe.src = ''  // unload page so it stops running in background
  }

  return { init, open, close }
})()
