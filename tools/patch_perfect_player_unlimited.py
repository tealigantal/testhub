#!/usr/bin/env python3
from pathlib import Path
import re
import sys

if len(sys.argv) != 3:
    raise SystemExit('usage: patch_perfect_player_unlimited.py SOURCE_HTML ANDROID_ASSETS_DIR')

source = Path(sys.argv[1])
assets = Path(sys.argv[2])
assets.mkdir(parents=True, exist_ok=True)
s = source.read_text(encoding='utf-8')

# Independent identity.
s = re.sub(r'<title>.*?</title>', '<title>完美球员 · 无限重选</title>', s, count=1, flags=re.S)

# Remove external runtime/advertising SDKs. The page contains its own local Colorbox fallbacks.
s = re.sub(r'<script src="https://gosspublic\.alicdn\.com/aliyun-oss-sdk-[^"]+"></script>\s*', '', s)
s = re.sub(r'<script src="https://activity-static\.hoopchina\.com\.cn/colorbox-activities/js/kaleido-fed-sdk\.js"></script>\s*', '', s)
s = re.sub(r'<script src="https://activity-static\.hoopchina\.com\.cn/hupu-web-guard\.js"[^>]*></script>\s*', '', s)
s = re.sub(r'<script src="https://activity-static\.hoopchina\.com\.cn/games/static/colorbox-ai/colorbox-ai_v[^\"]+\.js"[^>]*></script>\s*', '', s)
# VA reward-video dynamic loader in the head.
s = re.sub(r'\s*<!-- VA H5 SDK — 激励视频任务 -->\s*<script>\s*\(function\(\) \{.*?\}\)\(\);\s*</script>', '', s, count=1, flags=re.S)

# Package the eight gameplay/data scripts locally.
remote = [
    'https://activity-static.hoopchina.com.cn/files/2678-58zyeprc-upload-1783508428855-12.js',
    'https://activity-static.hoopchina.com.cn/files/2678-5hu3djrc-upload-1783494754597-12.js',
    'https://activity-static.hoopchina.com.cn/files/2678-gd4jvxrc-upload-1783494754597-15.js',
    'https://activity-static.hoopchina.com.cn/files/2678-456sfprc-upload-1783494754597-18.js',
    'https://activity-static.hoopchina.com.cn/files/2678-mdo4zerc-upload-1783494754597-21.js',
    'https://activity-static.hoopchina.com.cn/files/2678-qlg35lrc-upload-1783494754597-24.js',
    'https://activity-static.hoopchina.com.cn/files/26630-uq56cnrc-upload-1782786826635-12.js',
    'https://activity-static.hoopchina.com.cn/files/26716-pz0d55rc-upload-1784184998973-30.js',
]
for i, url in enumerate(remote, 1):
    s = s.replace(url, f'assets/data-{i}.js')

# No Hupu App gate.
s = s.replace(
    'function getIsInApp() {\n  return /kanqiu|huputiyu/i.test(window.navigator.userAgent || "");\n}',
    'function getIsInApp() { return true; }'
)

# Make any legacy counter effectively irrelevant too.
s = s.replace('_rerollsLeft: 3,', '_rerollsLeft: 999999,')

# Always-free reroll button.
pattern = r'function getRerollButtonHtml\(\) \{.*?\n\}\n\nfunction updateSlotButtons\(\)'
replacement = '''function getRerollButtonHtml() {
  var hasTeam = !!STATE.currentTeam;
  return '<button class="btn btn-sm slot-btn" onclick="rerollTeamPlayers()"' +
    (hasTeam ? '' : ' disabled style="opacity:0.3;"') +
    '>👥 更换球员 · 免费∞</button>';
}

function updateSlotButtons()'''
s, n = re.subn(pattern, replacement, s, count=1, flags=re.S)
if n != 1:
    raise RuntimeError('getRerollButtonHtml block changed upstream')

# Put direct team selection beside random in BOTH build-stage action renders.
selector_btn = '''<button class="btn btn-sm slot-btn" onclick="showBuildTeamPicker()"
        style="background:var(--bg-card);color:var(--text);">
        🎯 选择球队
      </button>
      ${getRerollButtonHtml()}'''
count = s.count('${getRerollButtonHtml()}')
if count < 2:
    raise RuntimeError('expected two build reroll button insertion points')
s = s.replace('${getRerollButtonHtml()}', selector_btn, 2)
s = s.replace('<div class="br-slot-label">🎰 随机选队</div>', '<div class="br-slot-label">🎰 随机 / 自选球队</div>', 1)

# Add full 30-team picker for BUILD stage.
insert_before = 'let _slotSpinning = false;'
if insert_before not in s:
    raise RuntimeError('build slot insertion point missing')
build_picker = r'''
function showBuildTeamPicker() {
  var old = document.getElementById('build-team-picker-overlay');
  if (old) old.remove();
  var teams = [...NBA2K_TEAMS].sort();
  var gridHtml = '';
  teams.forEach(function(t) {
    var cn = SIM_CONFIG.TEAM_NAMES[t] || t;
    var city = window.TEAM_CITY[t] || '';
    gridHtml += '<div class="team-pick-card" data-team="' + t + '" onclick="selectBuildTeamFromPicker(\'' + t + '\')">' +
      getTeamLogo(t, 36) +
      '<span class="tpc-abbr">' + cn + '</span>' +
      '<span class="tpc-name">' + city + '</span>' +
      '</div>';
  });
  var overlay = document.createElement('div');
  overlay.className = 'team-picker-overlay';
  overlay.id = 'build-team-picker-overlay';
  overlay.innerHTML = '<div class="team-picker-modal">' +
    '<div class="team-picker-header"><span>🎯 选择球员所属球队 · 30队任选</span>' +
    '<button class="team-picker-close" onclick="closeBuildTeamPicker()">✕</button></div>' +
    '<div class="team-picker-grid">' + gridHtml + '</div></div>';
  overlay.addEventListener('click', function(e) { if (e.target === overlay) closeBuildTeamPicker(); });
  document.body.appendChild(overlay);
}

function closeBuildTeamPicker() {
  var el = document.getElementById('build-team-picker-overlay');
  if (el) el.remove();
}

function selectBuildTeamFromPicker(team) {
  closeBuildTeamPicker();
  if (_slotSpinning || STATE._mustLockAfterSpin) return;
  STATE.currentTeam = team;
  if (STATE._teamsVisited.indexOf(team) === -1) STATE._teamsVisited.push(team);
  STATE.selectedPlayer = null;
  STATE._shownThisTeam = [];
  STATE._mustLockAfterSpin = true;
  renderLeftAttrs();
  updateSlotButtons();
  showTeamRoster(team);
}

'''
s = s.replace(insert_before, build_picker + insert_before, 1)

# Infinite player reroll: never decrements, and recycle the team's pool after every player has appeared.
pattern = r'/\*\* 当前球队内换一批球员 \*/\s*function rerollTeamPlayers\(\) \{.*?\n\}\n\nfunction pickPlayer\(name\)'
replacement = r'''/** 当前球队内无限免费换一批球员 */
function rerollTeamPlayers() {
  if (!STATE.currentTeam) return;
  const players = NBA2K_DATA[STATE.currentTeam] || [];
  const available = players.filter(p => !STATE.usedPlayers.includes(p.name));
  if (!available.length) return;

  let notShown = available.filter(p => !STATE._shownThisTeam.includes(p.name));
  if (!notShown.length) {
    STATE._shownThisTeam = [];
    notShown = available.slice();
  }
  const shuffled = shuffleArr([...notShown]);
  const shown = shuffled.slice(0, Math.min(5, shuffled.length));
  shown.forEach(p => {
    if (!STATE._shownThisTeam.includes(p.name)) STATE._shownThisTeam.push(p.name);
  });
  STATE.selectedPlayer = null;
  renderLeftAttrs();
  updateSlotButtons();
  renderRosterPlayers(STATE.currentTeam, shown, available);
}

function pickPlayer(name)'''
s, n = re.subn(pattern, replacement, s, count=1, flags=re.S)
if n != 1:
    raise RuntimeError('rerollTeamPlayers block changed upstream')

# Career random team uses all 30 teams instead of only teams visited during player building.
s = s.replace("var pool = STATE._teamsVisited.length > 0 ? STATE._teamsVisited : [...NBA2K_TEAMS].sort();", "var pool = [...NBA2K_TEAMS].sort();")

# Career direct picker: always all 30 teams, no ad / counter restriction.
pattern = r'function showCareerTeamPicker\(teamList\) \{.*?\n\}\n\nfunction closeCareerTeamPicker\(\)'
replacement = r'''function showCareerTeamPicker(teamList) {
  var old = document.getElementById('team-picker-overlay');
  if (old) old.remove();
  var allTeams = [...NBA2K_TEAMS].sort();
  var gridHtml = '';
  allTeams.forEach(function(t) {
    var cn = SIM_CONFIG.TEAM_NAMES[t] || t;
    var city = window.TEAM_CITY[t] || '';
    gridHtml += '<div class="team-pick-card" data-team="' + t + '" onclick="selectCareerTeamFromPicker(\'' + t + '\')">' +
      getTeamLogo(t, 36) +
      '<span class="tpc-abbr">' + cn + '</span>' +
      '<span class="tpc-name">' + city + '</span></div>';
  });
  var overlay = document.createElement('div');
  overlay.className = 'team-picker-overlay';
  overlay.id = 'team-picker-overlay';
  overlay.innerHTML = '<div class="team-picker-modal">' +
    '<div class="team-picker-header"><span>🎯 选择生涯球队 · 30队任选</span>' +
    '<button class="team-picker-close" onclick="closeCareerTeamPicker()">✕</button></div>' +
    '<div class="team-picker-grid">' + gridHtml + '</div></div>';
  overlay.addEventListener('click', function(e) { if (e.target === overlay) closeCareerTeamPicker(); });
  document.body.appendChild(overlay);
}

function closeCareerTeamPicker()'''
s, n = re.subn(pattern, replacement, s, count=1, flags=re.S)
if n != 1:
    raise RuntimeError('showCareerTeamPicker block changed upstream')

# Remove the reward-video block entirely; achievement module immediately after it is kept.
s = re.sub(
    r'<!-- ====== 激励视频自选球队（VA H5 SDK · activityId 318）====== -->.*?(?=<!-- ====== 成就系统模块)',
    '', s, count=1, flags=re.S
)

# Visible independent-build marker.
s = s.replace('打造我的传奇球星', '打造我的完美球员 · FREE ∞', 1)

# Validation.
for i in range(1, 9):
    if f'assets/data-{i}.js' not in s:
        raise RuntimeError(f'local data script {i} missing')
if '更换球员 · 免费∞' not in s:
    raise RuntimeError('infinite free reroll marker missing')
if '选择球员所属球队 · 30队任选' not in s:
    raise RuntimeError('build-stage team selector missing')
if '选择生涯球队 · 30队任选' not in s:
    raise RuntimeError('career team selector missing')
if '看广告换球员' in s or '看视频自选球队' in s:
    raise RuntimeError('ad-gated controls still present')
if 'if (!getIsInApp())' in s:
    # getIsInApp is forced true, but strip the gate anyway for safety.
    s = re.sub(r'\s*if \(!getIsInApp\(\)\) \{\s*showDownloadModal\(\);\s*return;\s*\}', '', s)
remote_scripts = re.findall(r'<script[^>]+src="https://', s)
if remote_scripts:
    raise RuntimeError(f'remote executable script remains: {remote_scripts[:5]}')

(assets / 'index.html').write_text(s, encoding='utf-8')
print('Patched:', assets / 'index.html')
