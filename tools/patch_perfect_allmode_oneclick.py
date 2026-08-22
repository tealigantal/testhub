#!/usr/bin/env python3
from pathlib import Path
import sys

if len(sys.argv) != 2:
    raise SystemExit('usage: patch_perfect_allmode_oneclick.py INDEX_HTML')

path = Path(sys.argv[1])
s = path.read_text(encoding='utf-8')

js = r'''
<script id="allmode-oneclick-v3">
(function(){
  function ocIsLegend(){
    return !!(window.STATE && (STATE.mode === 'legend' || STATE.draftMode === 'historical'));
  }

  function ocRoster(team){
    if (ocIsLegend()) {
      var hist = (typeof NBA2K_ALLTIME_DATA !== 'undefined' && NBA2K_ALLTIME_DATA && NBA2K_ALLTIME_DATA[team + '_HIST']) || [];
      if (hist && hist.length) return hist;
    }
    return (typeof NBA2K_DATA !== 'undefined' && NBA2K_DATA && NBA2K_DATA[team]) || [];
  }

  // Rectangular Hungarian algorithm. Rows=13 attributes, columns=unique players.
  // Minimises cost; used here to maximise weighted adjusted attribute value.
  function ocHungarian(cost){
    var n=cost.length, m=cost[0].length;
    var u=new Array(n+1).fill(0), v=new Array(m+1).fill(0);
    var p=new Array(m+1).fill(0), way=new Array(m+1).fill(0);
    for(var i=1;i<=n;i++){
      p[0]=i;
      var j0=0, minv=new Array(m+1).fill(Infinity), used=new Array(m+1).fill(false);
      do{
        used[j0]=true;
        var i0=p[j0], delta=Infinity, j1=0;
        for(var j=1;j<=m;j++) if(!used[j]){
          var cur=cost[i0-1][j-1]-u[i0]-v[j];
          if(cur<minv[j]){minv[j]=cur;way[j]=j0;}
          if(minv[j]<delta){delta=minv[j];j1=j;}
        }
        for(var j2=0;j2<=m;j2++){
          if(used[j2]){u[p[j2]]+=delta;v[j2]-=delta;}
          else if(j2>0) minv[j2]-=delta;
        }
        j0=j1;
      }while(p[j0]!==0);
      do{
        var prev=way[j0];
        p[j0]=p[prev];
        j0=prev;
      }while(j0!==0);
    }
    var ans=new Array(n).fill(-1);
    for(var jj=1;jj<=m;jj++) if(p[jj]>0 && p[jj]<=n) ans[p[jj]-1]=jj-1;
    return ans;
  }

  function ocOptimalBuild(pos){
    var teams=(typeof NBA2K_TEAMS !== 'undefined' && NBA2K_TEAMS) ? NBA2K_TEAMS.slice() : [];
    var attrs=(typeof ATTR_KEYS !== 'undefined' && ATTR_KEYS) ? ATTR_KEYS.slice() : [];
    if(!teams.length || !attrs.length) return null;

    // One column per player name because the game itself forbids reusing a player name.
    // If the same legend appears on multiple historical teams, keep that player's best
    // team/version independently for each attribute.
    var byName={};
    teams.forEach(function(team){
      var roster=ocRoster(team);
      roster.forEach(function(player){
        var name=player && (player.name || player.nameEN || player.cname);
        if(!name) return;
        if(!byName[name]) byName[name]={name:name,best:{}};
        var mainPos=getPlayerMainPos(player);
        attrs.forEach(function(key){
          var raw=parseInt(player[key],10);
          if(!isFinite(raw)) raw=50;
          var penalty=getPosPenalty(pos,mainPos,key);
          var val=Math.round(raw*penalty);
          var old=byName[name].best[key];
          if(!old || val>old.value){
            byName[name].best[key]={player:player,team:team,value:val,raw:raw,penalty:penalty};
          }
        });
      });
    });

    var players=Object.keys(byName).map(function(k){return byName[k];});
    if(players.length<attrs.length) return null;
    var weights=(SIM_CONFIG && SIM_CONFIG.OVR_WEIGHTS && SIM_CONFIG.OVR_WEIGHTS[pos]) || {};
    var cost=[];
    for(var ai=0;ai<attrs.length;ai++){
      var key=attrs[ai];
      var w=(weights[key] != null) ? weights[key] : 0.07;
      var row=[];
      for(var pi=0;pi<players.length;pi++){
        var cand=players[pi].best[key];
        var score=(cand ? cand.value : 0)*w;
        row.push(100000-Math.round(score*1000));
      }
      cost.push(row);
    }
    var assignment=ocHungarian(cost);
    var result={};
    for(var i=0;i<attrs.length;i++){
      var col=assignment[i];
      if(col<0 || !players[col] || !players[col].best[attrs[i]]) return null;
      result[attrs[i]]=players[col].best[attrs[i]];
    }
    return result;
  }

  window.applyBestBuild=function(pos){
    pos=pos || STATE.position || 'PG';
    var spec=ocOptimalBuild(pos);
    if(!spec){alert('当前模式最强建模数据尚未加载完成');return;}

    STATE.position=pos;
    STATE.attrs={};
    STATE.attrSlots={};
    STATE.lockedCount=0;
    STATE.usedPlayers=[];
    STATE._mustLockAfterSpin=false;
    STATE.currentTeam=null;
    STATE.currentRoster=[];
    STATE._shownThisTeam=[];
    STATE._teamsVisited=[];
    STATE.selectedPlayer=null;
    STATE._locking=false;
    STATE.finalOVR=0;
    STATE.finalPosition=null;
    STATE.finalArchetype=null;

    var missing=[];
    ATTR_KEYS.forEach(function(key){
      var pick=spec[key];
      var player=pick && pick.player;
      if(!player){missing.push(key);return;}
      STATE.attrs[key]=pick.value;
      STATE.attrSlots[key]={
        player:player.name || player.nameEN || player.cname,
        team:pick.team,
        value:pick.value,
        raw:pick.raw,
        penalty:pick.penalty
      };
      STATE.lockedCount++;
      STATE.usedPlayers.push(player.name || player.nameEN || player.cname);
      if(STATE._teamsVisited.indexOf(pick.team)===-1) STATE._teamsVisited.push(pick.team);
    });
    if(missing.length){alert('一键最强缺少属性：'+missing.join(', '));return;}

    STATE.finalOVR=calcOVR(STATE.attrs,pos);
    STATE.finalPosition=pos;
    revealPlayer();
  };

  // Expose a tiny marker for CI/runtime diagnosis.
  window.PERFECT_PLAYER_ONECLICK_V3={
    allModes:true,
    legendPool:'NBA2K_ALLTIME_DATA[*_HIST]',
    currentPool:'NBA2K_DATA',
    optimizer:'hungarian'
  };
})();
</script>
'''

if 'id="allmode-oneclick-v3"' in s:
    raise RuntimeError('v3 all-mode patch already present')
if '</body>' not in s:
    raise RuntimeError('body end not found')
s = s.replace('</body>', js + '\n</body>', 1)
path.write_text(s, encoding='utf-8')
print('added all-mode one-click optimizer:', path)
