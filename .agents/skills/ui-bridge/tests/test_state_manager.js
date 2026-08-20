// tests/test_state_manager.js
// Run with: node tests/test_state_manager.js
const fs = require('fs')
// provide browser stubs
global.document = { addEventListener: () => {} }
global.fetch = () => {}
eval(fs.readFileSync('canvas-app/state-manager.js', 'utf8'))

let passed = 0, failed = 0
function ok(label, cond) {
  if (cond) { console.log('  ✓', label); passed++ }
  else { console.error('  ✗', label); failed++ }
}

// migrateState: add version + story_stops to old file
const old = { frames: [], wires: [], docs: [] }
const migrated = StateManager.migrateState(old)
ok('migration adds version=1', migrated.version === 1)
ok('migration adds story_stops', Array.isArray(migrated.story_stops))

// generateDefaultLayout from manifest
const manifest = { pages: [{ id: 'page_a', group: 'G' }], docs: [] }
const layout = StateManager.generateDefaultLayout(manifest)
ok('default layout has frames', layout.frames.length === 1)
ok('default layout version', layout.version === 1)

// updateFramePosition
StateManager.state = { frames: [{ id: 'page_a', x: 0, y: 0, width: 380, height: 620, visible: true }], wires: [], docs: [], story_stops: [] }
StateManager.updateFramePosition('page_a', 55, 77)
ok('updateFramePosition x', StateManager.state.frames[0].x === 55)
ok('updateFramePosition y', StateManager.state.frames[0].y === 77)

// setFrameVisible
StateManager.setFrameVisible('page_a', false)
ok('setFrameVisible false', StateManager.state.frames[0].visible === false)

console.log(`\n${passed} passed, ${failed} failed`)
if (failed) process.exit(1)
