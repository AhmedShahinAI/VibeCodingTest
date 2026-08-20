#!/usr/bin/env node
/**
 * install.js - Skill installer for ui-generate-from-plan
 *
 * Invoked by:
 *   npx skills add rakymat-plugins/ui-gernreate-from-plan --all
 *   node scripts/install.js
 *   npm run install-skill
 */

'use strict';

const fs = require('fs');
const path = require('path');
const os = require('os');
const { execSync } = require('child_process');

const SKILL_ROOT = path.resolve(__dirname, '..');
const SKILL_NAME = 'ui-gernreate-from-plan';
const CLAUDE_GLOBAL = path.join(os.homedir(), '.claude');
const CODEX_GLOBAL = process.env.CODEX_HOME || path.join(os.homedir(), '.codex');
const SKILL_DEST = path.join(CLAUDE_GLOBAL, 'skills', SKILL_NAME);
const CODEX_SKILL_DEST = path.join(CODEX_GLOBAL, 'skills', SKILL_NAME);
const CMD_DEST = path.join(CLAUDE_GLOBAL, 'commands');
const INIT_CWD = process.env.INIT_CWD ? path.resolve(process.env.INIT_CWD) : process.cwd();

function ok(msg) {
  console.log('  OK ' + msg);
}

function warn(msg) {
  console.log('  WARN ' + msg);
}

function info(msg) {
  console.log(msg);
}

function mkdirp(dir) {
  if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });
}

function copyFile(src, dest) {
  mkdirp(path.dirname(dest));
  fs.copyFileSync(src, dest);
}

function copyDir(src, dest) {
  if (!fs.existsSync(src)) return;
  mkdirp(dest);
  for (const entry of fs.readdirSync(src, { withFileTypes: true })) {
    const srcPath = path.join(src, entry.name);
    const destPath = path.join(dest, entry.name);
    if (entry.isDirectory()) {
      copyDir(srcPath, destPath);
    } else if (entry.isFile()) {
      copyFile(srcPath, destPath);
    }
  }
}

function globFiles(dir, ext) {
  if (!fs.existsSync(dir)) return [];
  return fs.readdirSync(dir)
    .filter((f) => f.endsWith(ext))
    .map((f) => path.join(dir, f));
}

function checkCommand(cmd) {
  try {
    execSync(cmd + ' --version', { stdio: 'ignore' });
    return true;
  } catch (_) {
    return false;
  }
}

function getPythonVersion() {
  for (const cmd of ['python', 'python3']) {
    try {
      const output = execSync(cmd + ' --version 2>&1').toString().trim();
      if (/^Python\s+\d+\.\d+/.test(output)) return output;
    } catch (_) {
      // Try the next executable name.
    }
  }
  return null;
}

function copySkillFiles(dest) {
  mkdirp(dest);

  for (const f of ['SKILL.md', 'README.md', 'requirements.txt', 'package.json']) {
    const src = path.join(SKILL_ROOT, f);
    if (fs.existsSync(src)) copyFile(src, path.join(dest, f));
  }

  for (const d of ['scripts', 'subskills', 'references', 'templates', 'schemas', 'agents', '.claude', '.codex']) {
    copyDir(path.join(SKILL_ROOT, d), path.join(dest, d));
  }
}

info('');
info('Installing ui-generate-from-plan skill...');
info('');

copySkillFiles(SKILL_DEST);
ok('Claude skill files copied to ' + SKILL_DEST);

copySkillFiles(CODEX_SKILL_DEST);
ok('Codex skill files copied to ' + CODEX_SKILL_DEST);

const cmdSrc = path.join(SKILL_ROOT, '.claude', 'commands');
mkdirp(CMD_DEST);
for (const f of globFiles(cmdSrc, '.md')) {
  copyFile(f, path.join(CMD_DEST, path.basename(f)));
}
ok('Claude commands installed to ' + CMD_DEST);

if (INIT_CWD !== SKILL_ROOT) {
  const localCmdDir = path.join(INIT_CWD, '.claude', 'commands');
  mkdirp(localCmdDir);
  for (const f of globFiles(cmdSrc, '.md')) {
    copyFile(f, path.join(localCmdDir, path.basename(f)));
  }
  ok('Project Claude commands installed to ' + localCmdDir);
}

const codexAliasSrc = path.join(SKILL_ROOT, '.codex', 'skills');
const codexAliasDest = path.join(CODEX_GLOBAL, 'skills');
copyDir(codexAliasSrc, codexAliasDest);
ok('Codex alias skills installed to ' + codexAliasDest);

if (INIT_CWD !== SKILL_ROOT) {
  const localCodexAliasDest = path.join(INIT_CWD, '.codex', 'skills');
  copyDir(codexAliasSrc, localCodexAliasDest);
  ok('Project Codex alias skills installed to ' + localCodexAliasDest);
}

info('');
info('Checking dependencies...');

const pythonVersion = getPythonVersion();
if (pythonVersion) {
  ok('Python found: ' + pythonVersion);
} else {
  warn('python3 not found - inference scripts will not run');
  warn('Install Python 3.8+ from https://python.org');
}

info('');
info('Checking Impeccable...');
if (checkCommand('npx') || checkCommand('npx.cmd')) {
  const npxBin = checkCommand('npx') ? 'npx' : 'npx.cmd';
  try {
    execSync(npxBin + ' impeccable --version', { stdio: 'ignore', timeout: 5000 });
    ok('Impeccable already installed');
  } catch (_) {
    info('  Installing Impeccable...');
    try {
      execSync(npxBin + ' impeccable install --providers=claude', {
        stdio: 'inherit',
        timeout: 30000,
      });
      ok('Impeccable installed');
    } catch (_) {
      warn('Impeccable install failed - HTML validation will run in internal-only mode');
    }
  }
} else {
  warn('npx not found - Impeccable CLI validation disabled');
}

info('');
info('Done! ui-generate-from-plan is installed.');
info('');
info('Restart your agent, then use:');
info('  /ui-plan or $ui-plan');
info('  /ui-implement or $ui-implement');
info('  /ui-link-html-to-plan or $ui-link-html-to-plan');
info('');
info('Full docs: https://github.com/rakymat-plugins/ui-gernreate-from-plan');
info('');
