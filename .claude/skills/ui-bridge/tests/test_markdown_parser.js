// tests/test_markdown_parser.js
// Run with: node tests/test_markdown_parser.js
const fs = require('fs')
eval(fs.readFileSync('canvas-app/markdown-parser.js', 'utf8'))

let passed = 0, failed = 0
function assert(label, actual, expected) {
  if (actual === expected) { console.log('  ✓', label); passed++ }
  else { console.error('  ✗', label, '\n    got:', actual, '\n    exp:', expected); failed++ }
}
function includes(label, actual, fragment) {
  if (actual.includes(fragment)) { console.log('  ✓', label); passed++ }
  else { console.error('  ✗', label, '\n    missing:', fragment, '\n    in:', actual); failed++ }
}

includes('h1', parseMarkdown('# Hello'), '<h1>Hello</h1>')
includes('h2', parseMarkdown('## World'), '<h2>World</h2>')
includes('bold', parseMarkdown('**bold**'), '<strong>bold</strong>')
includes('italic', parseMarkdown('*italic*'), '<em>italic</em>')
includes('inline code', parseMarkdown('`code`'), '<code>code</code>')
includes('unordered list', parseMarkdown('- item one'), '<li>item one</li>')
includes('link', parseMarkdown('[text](url)'), '<a href="url">text</a>')
includes('code block open', parseMarkdown('```\nfoo\n```'), '<pre><code>')
includes('paragraph', parseMarkdown('plain text'), '<p>plain text</p>')

console.log(`\n${passed} passed, ${failed} failed`)
if (failed) process.exit(1)
