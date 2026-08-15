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

if 'function getIsInApp() { return true; }' not in s: raise RuntimeError('App gate patch failed')
if '更换球员 · 免费∞' not in s: raise RuntimeError('Unlimited reroll patch failed')
if '30队免费任选' not in s: raise RuntimeError('Free team picker patch failed')
for i in range(1,9):
    if f'assets/data-{i}.js' not in s: raise RuntimeError(f'data {i} not localized')
(out/'index.html').write_text(s,encoding='utf-8')
print('patched',out/'index.html')
