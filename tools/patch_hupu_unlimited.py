#!/usr/bin/env python3
from pathlib import Path
import hashlib
import re
import sys
import urllib.request

if len(sys.argv) != 3:
    raise SystemExit("usage: patch_hupu_unlimited.py SOURCE_HTML ANDROID_ASSETS_DIR")

source = Path(sys.argv[1])
assets_root = Path(sys.argv[2])
assets_root.mkdir(parents=True, exist_ok=True)
logo_dir = assets_root / "assets" / "logos"
logo_dir.mkdir(parents=True, exist_ok=True)

s = source.read_text(encoding="utf-8")

# Standalone identity / no App gate.
s = s.replace(
    "<title>挑战传奇 — 挑战历史最强NBA球队 - 虎扑</title>",
    "<title>挑战传奇 · 无限刷新</title>",
)
s = s.replace(
    'function getIsInApp(){return /kanqiu|huputiyu/i.test(window.navigator.userAgent||"");}',
    'function getIsInApp(){return true;}',
)
s = s.replace('  if(!getIsInApp()){showOutsideGate();return;}\n', '')

# Remove runtime integrations that are not part of the game itself.
s = re.sub(r'<script src="https://activity-static\.hoopchina\.com\.cn/hupu-web-guard\.js"[^>]*></script>\s*', '', s)
s = re.sub(r'<script src="https://activity-static\.hoopchina\.com\.cn/games/static/colorbox-ai/colorbox-ai_v2\.1\.71\.js"[^>]*></script>\s*', '', s)
s = re.sub(r'<link[^>]+fonts\.googleapis\.com[^>]*>\s*', '', s)
s = re.sub(r'<link[^>]+fonts\.gstatic\.com[^>]*>\s*', '', s)

# Five runtime datasets are packaged with the APK.
remote_data = [
    'https://activity-static.hoopchina.com.cn/files/26727-wbtxxnrc-upload-1785124598386-52.js',
    'https://activity-static.hoopchina.com.cn/files/26721-9gnnmcrc-upload-1784627950810-12.js',
    'https://activity-static.hoopchina.com.cn/files/26721-0njiyprc-upload-1784627950810-27.js',
    'https://activity-static.hoopchina.com.cn/files/26723-ds5k1jrc-upload-1784794258625-12.js',
    'https://activity-static.hoopchina.com.cn/files/26721-htvdrrrc-upload-1784631261470-12.js',
]
for i, url in enumerate(remote_data, 1):
    s = s.replace(url, f'assets/data-{i}.js')

# Bundle all team logos referenced by the game so gameplay stays local/offline.
logo_urls = sorted(set(re.findall(r'https://activity-static\.hoopchina\.com\.cn/files/[^"\']+\.png', s)))
headers = {'User-Agent': 'Mozilla/5.0 (Linux; Android 16) AppleWebKit/537.36 Chrome/138 Mobile Safari/537.36'}
for url in logo_urls:
    name = hashlib.sha1(url.encode('utf-8')).hexdigest()[:12] + '.png'
    dest = logo_dir / name
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=30) as r:
        dest.write_bytes(r.read())
    s = s.replace(url, f'assets/logos/{name}')

# Remove Hupu-brand corner logo and its poster preloader in this independent build.
s = re.sub(r'<img class="hp-logo-corner"[^>]*>', '', s)
s = re.sub(
    r'// 预加载虎扑logo供海报使用\s*let _hpLogo=null;\s*\(function\(\)\{.*?\}\)\(\);',
    'let _hpLogo=null;',
    s,
    count=1,
    flags=re.S,
)

# Remove the two unreachable Hupu/ad-only overlays.
s = re.sub(r'<div class="overlay hidden" id="outsideModal">.*?</div>\s*</div>\s*', '', s, count=1, flags=re.S)
s = re.sub(r'<!-- 重新随机选择弹窗 -->\s*<div class="overlay hidden" id="respinChoiceOverlay">.*?</div>\s*</div>\s*', '', s, count=1, flags=re.S)

# Free / unlimited re-roll: no budget charge and no ad branch.
s = s.replace(
    '<button class="btn ghost" id="respinBtn" style="display:none">重新随机 -$10M</button>',
    '<button class="btn ghost" id="respinBtn" style="display:none">重新随机 · 免费∞</button>',
)
old_render = '''  const rbtn=$("respinBtn");
  if(rbtn){
    const canFree=respinFreeAvailable();
    const firstFree=firstFreeRespinAvailable();
    rbtn.style.display=(anySelectable&&(canFree||remaining>=RESPIN_COST))?"":"none";
    if(canFree&&remaining<RESPIN_COST){rbtn.textContent="重新随机-看广告免费随机";}
    else if(firstFree){rbtn.textContent="重新随机-$10M/看广告免费";}
    else{rbtn.textContent="重新随机 -"+fmtM(RESPIN_COST);}
    rbtn.disabled=false;
    rbtn.onclick=reSpinCurrentTeam;
  }
}'''
new_render = '''  const rbtn=$("respinBtn");
  if(rbtn){
    rbtn.style.display=anySelectable?"":"none";
    rbtn.textContent="重新随机 · 免费∞";
    rbtn.disabled=false;
    rbtn.onclick=reSpinCurrentTeam;
  }
}'''
if old_render not in s:
    raise RuntimeError('reroll render block changed upstream')
s = s.replace(old_render, new_render)

old_free = '''function doFreeRespin(){
  if(spinning||!currentGroup)return;
  respinFirstFreeUsed=true;
  usedKeys.add(currentGroup.key);currentGroup=null;
  $("landed").classList.add("hidden");
  updateHud();spin();
}'''
new_free = '''function doFreeRespin(){
  if(spinning||!currentGroup)return;
  usedKeys.add(currentGroup.key);currentGroup=null;
  $("landed").classList.add("hidden");
  updateHud();spin();
}'''
if old_free not in s:
    raise RuntimeError('doFreeRespin changed upstream')
s = s.replace(old_free, new_free)

old_reroll = '''function reSpinCurrentTeam(){
  window.ColorboxAI?.track({act:"click",blk:"BMC018",pos:"TC7",label:"重抽"});
  if(spinning||!currentGroup)return;
  if(firstFreeRespinAvailable()){
    // 剩余不足10M：无法花钱，直接看广告免费随机（不再弹窗选择）
    if(remaining<RESPIN_COST){runAdRespin();}
    else{openRespinChoice();}
    return;
  }
  if(lowBudgetRespinAvailable()){
    runAdRespin();
    return;
  }
  doPaidRespin();
}'''
new_reroll = '''function reSpinCurrentTeam(){
  if(spinning||!currentGroup)return;
  doFreeRespin();
}'''
if old_reroll not in s:
    raise RuntimeError('reSpinCurrentTeam changed upstream')
s = s.replace(old_reroll, new_reroll)

# Results are local: keep replay, remove Hupu post/share navigation.
s = re.sub(
    r"html\+='<div class=\"res-actions\".*?</div>';",
    "html+='<div class=\"res-actions\"><button class=\"btn\" onclick=\"playAgain()\">再来一局</button></div>';",
    s,
    count=1,
)

# Remove bottom OSS/Kaleido/reward-video SDK injection.
s = re.sub(r'<!-- SDK脚本移到内联逻辑之后.*?</script>\s*</body>', '</body>', s, count=1, flags=re.S)

# Visible marker for this independent build.
s = s.replace(
    '<div class="subtitle">Against Legendary</div>',
    '<div class="subtitle">Against Legendary · FREE ∞</div>',
    1,
)

# Disable the leftover landing URL even though the gate is removed.
s = s.replace(
    "const HUPU_APP_LANDING_URL='https://games.mobileapi.hupu.com/landing?auto_install=yes&channel=739';",
    "const HUPU_APP_LANDING_URL='#';",
)

# Core validation: no remote executable scripts, local datasets, free reroll, no App gate.
remote_script = re.findall(r'<script[^>]+src="https://', s)
if remote_script:
    raise RuntimeError(f'remote scripts remain: {remote_script}')
for i in range(1, 6):
    if f'assets/data-{i}.js' not in s:
        raise RuntimeError(f'dataset {i} missing')
if '重新随机 · 免费∞' not in s or 'function reSpinCurrentTeam(){\n  if(spinning||!currentGroup)return;\n  doFreeRespin();\n}' not in s:
    raise RuntimeError('free unlimited reroll patch missing')
if 'if(!getIsInApp())' in s:
    raise RuntimeError('Hupu App gate still active')

(assets_root / 'index.html').write_text(s, encoding='utf-8')
print(f'Patched standalone game: {assets_root / "index.html"}')
print(f'Bundled team logos: {len(logo_urls)}')
