#!/usr/bin/env python3
from pathlib import Path
import re, sys

if len(sys.argv) != 3:
    raise SystemExit('usage: patch_perfect_player_apk.py SOURCE_HTML ASSETS_DIR')
src=Path(sys.argv[1]); out=Path(sys.argv[2]); out.mkdir(parents=True,exist_ok=True)
s=src.read_text(encoding='utf-8')

s=s.replace('<title>我创造的完美球员 - 虎扑</title>','<title>我创造的完美球员 · FREE ∞</title>')
s=s.replace('function getIsInApp() {\n  return /kanqiu|huputiyu/i.test(window.navigator.userAgent || "");\n}', 'function getIsInApp() { return true; }')

remote=[
'https://activity-static.hoopchina.com.cn/files/2678-58zyeprc-upload-1783508428855-12.js',
'https://activity-static.hoopchina.com.cn/files/2678-5hu3djrc-upload-1783494754597-12.js',
'https://activity-static.hoopchina.com.cn/files/2678-gd4jvxrc-upload-1783494754597-15.js',
'https://activity-static.hoopchina.com.cn/files/2678-456sfprc-upload-1783494754597-18.js',
'https://activity-static.hoopchina.com.cn/files/2678-mdo4zerc-upload-1783494754597-21.js',
'https://activity-static.hoopchina.com.cn/files/2678-qlg35lrc-upload-1783494754597-24.js',
'https://activity-static.hoopchina.com.cn/files/26630-uq56cnrc-upload-1782786826635-12.js',
'https://activity-static.hoopchina.com.cn/files/26716-pz0d55rc-upload-1784184998973-30.js',
]
for i,u in enumerate(remote,1): s=s.replace(u,f'assets/data-{i}.js')

# Unlimited free player rerolls.
s=re.sub(r"function getRerollButtonHtml\(\) \{.*?\n\}", '''function getRerollButtonHtml() {
  var hasTeam=!!STATE.currentTeam;
  return '<button class="btn btn-sm slot-btn" onclick="rerollTeamPlayers()"'+(hasTeam?'':' disabled style="opacity:0.3;"')+'>👥 更换球员 · 免费∞</button>';
}''', s, count=1, flags=re.S)
s=re.sub(r"function rerollTeamPlayers\(\) \{.*?\n\}\n\nfunction pickPlayer", '''function rerollTeamPlayers() {
  if (!STATE.currentTeam) return;
  const players=NBA2K_DATA[STATE.currentTeam];
  const available=players.filter(p=>!STATE.usedPlayers.includes(p.name));
  if (!available.length) return;
  let pool=available.filter(p=>!STATE._shownThisTeam.includes(p.name));
  if (!pool.length) { STATE._shownThisTeam=[]; pool=available.slice(); }
  const shuffled=shuffleArr([...pool]);
  const shown=shuffled.slice(0,Math.min(5,shuffled.length));
  shown.forEach(p=>{if(!STATE._shownThisTeam.includes(p.name))STATE._shownThisTeam.push(p.name);});
  STATE.selectedPlayer=null;
  renderLeftAttrs(); updateSlotButtons(); renderRosterPlayers(STATE.currentTeam,shown,available);
}

function pickPlayer''', s, count=1, flags=re.S)

# Career team picker: all 30 teams, free; remove reward-video button.
s=s.replace("function showCareerTeamPicker(teamList) {\n  var isFull = Array.isArray(teamList);", "function showCareerTeamPicker(teamList) {\n  teamList=[...NBA2K_TEAMS];\n  var isFull=true;")
s=s.replace("'<button id=\"adTeamPickBtn\" onclick=\"watchAdToPickTeam()\" style=\"min-height:30px;padding:5px 10px;border:none;border-radius:8px;background:linear-gradient(135deg,#ff6b35,#ff8a5c);color:#fff;font-family:var(--font-display);font-size:11px;font-weight:600;cursor:pointer;box-shadow:0 2px 0 #c94d1e;\">📺 看视频自选球队</button>' +", "'<span style=\"font-size:11px;color:var(--orange);font-weight:700;\">30队免费任选</span>' +")
s=s.replace("subLine = '🎉 看视频获得 · 全 ' + allTeams.length + ' 队任选';", "subLine = '🎉 免费 · 全 ' + allTeams.length + ' 队任选';")

# Independent-build marker.
s=s.replace('Spin the wheel · Build your player','Spin the wheel · Build your player · FREE ∞',1)

# One-click strongest builds. Each mapping is the globally optimal 13-attribute
# assignment under the game's own cross-position penalty and OVR weights,
# with each source player used at most once.
best_build_js = r'''

const BEST_BUILDS = {
  PG: {
    threePT:{team:'GSW',name:'Stephen Curry'}, MID:{team:'DAL',name:'Kyrie Irving'},
    FIN:{team:'BOS',name:'Payton Pritchard'}, DNK:{team:'POR',name:'Ja Morant'},
    HAN:{team:'BOS',name:'Jayson Tatum'}, PAS:{team:'OKC',name:'Shai Gilgeous-Alexander'},
    PDEF:{team:'OKC',name:'Luguentz Dort'}, IDEF:{team:'SAC',name:'Adam Flagler'},
    BLK:{team:'BOS',name:'Derrick White'}, REB:{team:'CHI',name:'Josh Giddey'},
    ATH:{team:'DET',name:'Ausar Thompson'}, STR:{team:'CHA',name:'Sion James'},
    CLU:{team:'BKN',name:'Noah Clowney'}
  },
  SG: {
    threePT:{team:'GSW',name:'Stephen Curry'}, MID:{team:'DEN',name:'Tim Hardaway Jr.'},
    FIN:{team:'BOS',name:'Payton Pritchard'}, DNK:{team:'MIN',name:'Anthony Edwards'},
    HAN:{team:'BOS',name:'Jayson Tatum'}, PAS:{team:'DEN',name:'Nikola Jokic'},
    PDEF:{team:'OKC',name:'Luguentz Dort'}, IDEF:{team:'HOU',name:'Amen Thompson'},
    BLK:{team:'BOS',name:'Derrick White'}, REB:{team:'CHI',name:'Josh Giddey'},
    ATH:{team:'DET',name:'Ausar Thompson'}, STR:{team:'CHA',name:'Sion James'},
    CLU:{team:'MEM',name:'Cedric Coward'}
  },
  SF: {
    threePT:{team:'GSW',name:'Stephen Curry'}, MID:{team:'HOU',name:'Marcus Smart'},
    FIN:{team:'BOS',name:'Payton Pritchard'}, DNK:{team:'MIN',name:'Anthony Edwards'},
    HAN:{team:'GSW',name:'Jimmy Butler'}, PAS:{team:'DEN',name:'Nikola Jokic'},
    PDEF:{team:'DET',name:'Ausar Thompson'}, IDEF:{team:'NOP',name:'Herbert Jones'},
    BLK:{team:'BOS',name:'Derrick White'}, REB:{team:'CHI',name:'Josh Giddey'},
    ATH:{team:'OKC',name:'Alex Caruso'}, STR:{team:'CHA',name:'Sion James'},
    CLU:{team:'TOR',name:'Kawhi Leonard'}
  },
  PF: {
    threePT:{team:'GSW',name:'Stephen Curry'}, MID:{team:'LAC',name:'Rui Hachimura'},
    FIN:{team:'BOS',name:'Payton Pritchard'}, DNK:{team:'MIN',name:'Anthony Edwards'},
    HAN:{team:'BOS',name:'Jayson Tatum'}, PAS:{team:'DEN',name:'Nikola Jokic'},
    PDEF:{team:'OKC',name:'Luguentz Dort'}, IDEF:{team:'CLE',name:'Evan Mobley'},
    BLK:{team:'ORL',name:'Jonathan Isaac'}, REB:{team:'ATL',name:'Jalen Johnson'},
    ATH:{team:'DET',name:'Ausar Thompson'}, STR:{team:'MIA',name:'Giannis Antetokounmpo'},
    CLU:{team:'BKN',name:'Noah Clowney'}
  },
  C: {
    threePT:{team:'MIA',name:'Bobby Portis'}, MID:{team:'LAC',name:'Rui Hachimura'},
    FIN:{team:'ATL',name:'Jock Landale'}, DNK:{team:'MIN',name:'Anthony Edwards'},
    HAN:{team:'NYK',name:'Karl-Anthony Towns'}, PAS:{team:'DEN',name:'Nikola Jokic'},
    PDEF:{team:'MIA',name:'Bam Adebayo'}, IDEF:{team:'CLE',name:'Evan Mobley'},
    BLK:{team:'DAL',name:'Moussa Cisse'}, REB:{team:'SAS',name:'Victor Wembanyama'},
    ATH:{team:'TOR',name:'Collin Murray-Boyles'}, STR:{team:'HOU',name:'Steven Adams'},
    CLU:{team:'TOR',name:'Kawhi Leonard'}
  }
};

function applyBestBuild(pos) {
  pos = pos || STATE.position;
  const spec = BEST_BUILDS[pos];
  if (!spec) return;

  STATE.position = pos;
  STATE.attrs = {};
  STATE.attrSlots = {};
  STATE.lockedCount = 0;
  STATE.usedPlayers = [];
  STATE._mustLockAfterSpin = false;
  STATE.currentTeam = null;
  STATE.currentRoster = [];
  STATE._shownThisTeam = [];
  STATE._teamsVisited = [];
  STATE.selectedPlayer = null;
  STATE._locking = false;
  STATE.finalOVR = 0;
  STATE.finalPosition = null;
  STATE.finalArchetype = null;

  const missing = [];
  ATTR_KEYS.forEach(function(key) {
    const pick = spec[key];
    const roster = (pick && NBA2K_DATA[pick.team]) || [];
    const player = roster.find(function(p) { return p.name === pick.name; });
    if (!player) { missing.push(key + ':' + (pick ? pick.name : '?')); return; }
    const rawVal = parseInt(player[key]) || 50;
    const playerPos = getPlayerMainPos(player);
    const penalty = getPosPenalty(pos, playerPos, key);
    const adjustedVal = Math.round(rawVal * penalty);
    STATE.attrs[key] = adjustedVal;
    STATE.attrSlots[key] = { player: player.name, team: pick.team, value: adjustedVal, raw: rawVal, penalty: penalty };
    STATE.lockedCount++;
    STATE.usedPlayers.push(player.name);
    if (STATE._teamsVisited.indexOf(pick.team) === -1) STATE._teamsVisited.push(pick.team);
  });

  if (missing.length) {
    alert('一键最强数据缺失：' + missing.join(', '));
    return;
  }
  STATE.finalOVR = calcOVR(STATE.attrs, pos);
  STATE.finalPosition = pos;
  revealPlayer();
}
'''
anchor='// ==================== 2. 位置选择 ===================='
if anchor not in s: raise RuntimeError('position anchor missing')
s=s.replace(anchor, best_build_js+'\n\n'+anchor, 1)

old_render = r'''function renderPositionSelect() {
  const grid = html('pos-grid');
  grid.innerHTML = '';
  
  const icons = { PG: '🎯', SG: '🔥', SF: '🏃', PF: '💪', C: '🧱' };
  SIM_CONFIG.POS_LIST.forEach(pos => {
    const card = document.createElement('div');
    card.className = 'pos-card';
    card.innerHTML = `
      <div class="pos-label">${SIM_CONFIG.POSITIONS[pos]}</div>
      <div class="pos-en">${icons[pos] || ''} ${pos}</div>
    `;
    card.onclick = () => {
      $$('.pos-card').forEach(c => c.classList.remove('selected'));
      card.classList.add('selected');
      STATE.position = pos;
    };
    grid.appendChild(card);
  });
}'''
new_render = r'''function renderPositionSelect() {
  const grid = html('pos-grid');
  grid.innerHTML = '';
  
  const icons = { PG: '🎯', SG: '🔥', SF: '🏃', PF: '💪', C: '🧱' };
  SIM_CONFIG.POS_LIST.forEach(pos => {
    const card = document.createElement('div');
    card.className = 'pos-card';
    card.innerHTML = `
      <div class="pos-label">${SIM_CONFIG.POSITIONS[pos]}</div>
      <div class="pos-en">${icons[pos] || ''} ${pos}</div>
      <button type="button" class="pos-best-btn" style="margin-top:9px;padding:7px 10px;border:0;border-radius:9px;background:var(--orange);color:#fff;font-family:var(--font-display);font-size:11px;font-weight:800;box-shadow:0 2px 0 #c94d1e;">⚡ 一键最强</button>
    `;
    card.onclick = (e) => {
      if (e.target && e.target.closest && e.target.closest('.pos-best-btn')) return;
      $$('.pos-card').forEach(c => c.classList.remove('selected'));
      card.classList.add('selected');
      STATE.position = pos;
    };
    const bestBtn = card.querySelector('.pos-best-btn');
    bestBtn.onclick = (e) => {
      e.stopPropagation();
      STATE.position = pos;
      applyBestBuild(pos);
    };
    grid.appendChild(card);
  });
}'''
if old_render not in s: raise RuntimeError('renderPositionSelect upstream changed')
s=s.replace(old_render,new_render,1)

s=s.replace('<div class="sub">现役模式 · 自选位置</div>', '<div class="sub">点位置正常建模 · 点「一键最强」直接生成</div>', 1)
s=s.replace(
    '<div id="build-pos-indicator" style="text-align:center;padding:4px 0 2px;font-family:var(--font-display);font-size:13px;color:var(--text-dim);letter-spacing:0.5px;"></div>\n    <div id="build-progress-area"></div>',
    '<div id="build-pos-indicator" style="text-align:center;padding:4px 0 2px;font-family:var(--font-display);font-size:13px;color:var(--text-dim);letter-spacing:0.5px;"></div>\n    <div style="display:flex;justify-content:center;padding:6px 0 8px;"><button type="button" class="btn btn-sm" onclick="applyBestBuild(STATE.position)" style="background:var(--orange);color:#fff;border-color:var(--orange);font-weight:800;">⚡ 一键最强（当前位置）</button></div>\n    <div id="build-progress-area"></div>',
    1,
)

if 'function getIsInApp() { return true; }' not in s: raise RuntimeError('App gate patch failed')
if '更换球员 · 免费∞' not in s: raise RuntimeError('Unlimited reroll patch failed')
if '30队免费任选' not in s: raise RuntimeError('Free team picker patch failed')
if 'const BEST_BUILDS = {' not in s or '⚡ 一键最强' not in s or 'function applyBestBuild(pos)' not in s:
    raise RuntimeError('One-click strongest build patch failed')
for i in range(1,9):
    if f'assets/data-{i}.js' not in s: raise RuntimeError(f'data {i} not localized')
(out/'index.html').write_text(s,encoding='utf-8')
print('patched',out/'index.html')
