"""Trace-faithful playback events for the public recorded-replay UI.

One event per retained LangSmith workflow node. Node elapsed durations use
recorded start/end timestamps; animation pace is illustrative.
"""
from __future__ import annotations
import json
from html import escape
from decision_package import decision_package
from review_evidence import review_annotations

NODE_BY_PREFIX = {
    "preprocessor": "preprocessor",
    "orchestrator": "orchestrator",
    "resolution_agent": "resolution_agent",
    "critic_resolution": "resolution_critic",
    "communication_agent": "communication_agent",
    "critic_communication": "communication_critic",
    "finalize": "finalizer",
}
NODE_NAMES = {
    "preprocessor": "Preprocessor",
    "orchestrator": "Orchestrator",
    "resolution_agent": "Resolution Agent",
    "resolution_critic": "Resolution Critic",
    "communication_agent": "Communication Agent",
    "communication_critic": "Communication Critic",
    "finalizer": "Finalisation",
}


def trace_steps(case: dict) -> list[dict]:
    """One event per traced LangGraph stage, with measured stage elapsed time."""
    if case.get('agent_events'):
        steps=[]
        for e in case['agent_events']:
            node={'critic_resolution':'resolution_critic','critic_communication':'communication_critic','finalize':'finalizer'}.get(e['node'], e['node'])
            preview=e.get('summary','')
            if e.get('review',{}).get('rationale'):
                note=e['review']['rationale']
            elif e.get('proposal',{}).get('rationale'):
                note=e['proposal']['rationale']
            elif e.get('draft',{}).get('communication_message'):
                note=e['draft']['communication_message']
            else: note=''
            steps.append({'index':e['index'],'node':node,'agent':NODE_NAMES[node],
                'source': f"{e['node']}: {preview}", 'message':preview,
                'is_revision':e.get('review',{}).get('decision')=='REVISE',
                'is_escalation':e.get('review',{}).get('decision')=='ESCALATE',
                'evidence_note':note,
                'timing':e['duration_seconds'],'offset':e['start_offset_seconds']})
        return steps
    return []


def build_replay_html(case: dict) -> str:
    payload = {
        "id":case["id"], "title":case["title"],
        "latency":case["metrics"]["latency_seconds"],
        "steps":trace_steps(case), "decision": decision_package(case),
    }
    # Prevent HTML/script injection even if replay text gains other input later.
    js_payload = json.dumps(payload, ensure_ascii=False).replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026")
    return HTML.replace("__REPLAY_DATA__", js_payload)


HTML = r'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1" />
<style>
:root{--ink:#281a2e;--plum:#321e3d;--coral:#ef6d4b;--peach:#fff0e4;--edge:#e9d8cb;--cream:#fffbf6;--muted:#786877}
*{box-sizing:border-box} html,body{margin:0;background:transparent;color:var(--ink);font-family:system-ui,-apple-system,"Segoe UI",sans-serif}
.shell{border:1px solid var(--edge);border-radius:19px;background:var(--cream);overflow:hidden}
.toolbar{display:flex;gap:14px;align-items:center;justify-content:space-between;flex-wrap:wrap;padding:18px 22px;background:var(--plum);color:white}
.toolbar .name{font-family:Georgia,serif;font-size:1.3rem}.toolbar .meta{font-size:12px;opacity:.8;margin-top:3px}
.buttons{display:flex;gap:7px;align-items:center;flex-wrap:wrap}
button{background:#fff9f3;color:var(--plum);border:none;border-radius:8px;padding:9px 14px;cursor:pointer;font:600 13px system-ui}
button:disabled{opacity:.35;cursor:not-allowed}button.play{background:var(--coral);color:white}
button:focus-visible{outline:3px solid #ffbc82;outline-offset:2px}
select{border:1px solid #dcc9da;background:white;color:var(--ink);border-radius:7px;padding:8px;font:13px system-ui}
.graphwrap{overflow-x:auto;padding:2px 6px 0;background:linear-gradient(135deg,#fffcf9,#fff6ef)}
.graph{height:365px;min-width:980px;position:relative;max-width:1120px;margin:0 auto}
.network{position:absolute;inset:0;width:100%;height:100%}
.edge{fill:none;stroke:#ceb9c8;stroke-width:2;stroke-dasharray:5 7;opacity:.7}
#travel{fill:none;stroke:var(--coral);stroke-width:4;stroke-linecap:round;filter:drop-shadow(0px 0px 4px #ef6d4b77)}
#orb{fill:#ff764e;stroke:white;stroke-width:3;filter:drop-shadow(0px 0px 6px #ef6d4b99)}
.node{position:absolute;transform:translate(-50%,-50%);width:177px;height:78px;padding:12px 10px;border:2px solid #dfd1df;border-radius:13px;background:white;box-shadow:0 5px 15px #3320360c;text-align:center;transition:background .2s, border-color .2s,box-shadow .2s}
.node .icon{font-size:19px;display:block;line-height:1.1}.node .title{font-size:13px;font-weight:750;margin-top:5px}
.node .small{font-size:10px;color:var(--muted);margin-top:2px}.node.active{background:#fff1e6;border-color:var(--coral);box-shadow:0 2px 23px #ed684840}
.node.done{border-color:#b6c9ae}
.bottom{display:grid;grid-template-columns:1.05fr .95fr;gap:0;border-top:1px solid var(--edge);min-height:205px}
.panel{padding:18px 22px}.panel+ .panel{border-left:1px solid var(--edge);background:white}
.kicker{font-size:10px;letter-spacing:.16em;font-weight:850;color:#b24c37;text-transform:uppercase;margin-bottom:9px}
#evidence-note{font-size:12px;line-height:1.5;background:#fff1e7;border-left:3px solid #df795b;padding:7px 10px;margin-top:11px;max-height:112px;overflow-y:auto;white-space:pre-wrap;display:none}
#out-title{font-weight:800;font-size:17px;margin-bottom:7px}#out-line{font-size:14px;line-height:1.48;overflow-wrap:anywhere;max-height:110px;overflow-y:auto;white-space:pre-wrap}
#activity{font-size:12px;color:#655568;overflow-y:auto;max-height:117px;line-height:1.7}
#activity div{padding:4px 0;border-bottom:1px solid #f3eee8}#activity span{font-weight:800;color:#a74e39;margin-right:9px}
.status{display:flex;flex-wrap:wrap;gap:7px 16px;padding:10px 22px;background:#fff0e2;border-top:1px solid var(--edge);font-size:12px;color:#594653}
.status strong{color:#422646} .progress{height:5px;background:#e6d7dc}.fill{height:5px;background:var(--coral);width:0%;transition:width .2s}
.disclaimer{padding:9px 21px;background:#fcf3e8;font-size:11px;color:#796576;line-height:1.4}
@media(max-width:700px){.bottom{display:block}.panel+.panel{border-left:none;border-top:1px solid var(--edge)}.toolbar{padding:13px}.toolbar .name{font-size:1.12rem}}
@media(prefers-reduced-motion:reduce){.node,.fill{transition:none}}
</style></head><body>
<script id="replay-source" type="application/json">__REPLAY_DATA__</script>
<div class="shell">
 <div class="toolbar">
  <div><div class="name">Agent execution map</div><div class="meta" id="scenario"></div></div>
  <div class="buttons"><button id="prev" aria-label="Previous recorded trace event">← Back</button><button class="play" id="play" aria-label="Play recorded workflow">▶ Play</button><button id="next" aria-label="Next recorded trace event">Next →</button><button id="reset" aria-label="Replay from first trace event">↺ Reset</button>
  <label style="font-size:12px" for="speed">Replay pace</label><select id="speed" aria-label="Replay pace"><option value="1800">Slow</option><option value="1150" selected>Normal</option><option value="600">Fast</option></select></div>
 </div>
 <div class="graphwrap"><div class="graph">
  <svg class="network" viewBox="0 0 1100 365" preserveAspectRatio="xMidYMid meet" aria-label="Seven agent and workflow nodes with animated event transitions" role="img">
  <defs><marker id="arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="5" markerHeight="5" orient="auto-start-reverse"><path d="M0 0 L10 5 L0 10Z" fill="#ceb9c8"/></marker></defs>
  <path class="edge" marker-end="url(#arrow)" d="M 225 100 L 288 100"/>
  <path class="edge" marker-end="url(#arrow)" d="M 455 100 L 514 100"/>
  <path class="edge" marker-end="url(#arrow)" d="M 686 100 L 792 100"/>
  <path class="edge" marker-end="url(#arrow)" d="M 875 138 Q 905 14 695 31 Q 595 26 598 60"/>
  <path class="edge" marker-end="url(#arrow)" d="M 369 140 Q 414 228 600 251"/>
  <path class="edge" marker-end="url(#arrow)" d="M 688 285 L 790 285"/>
  <path class="edge" marker-end="url(#arrow)" d="M 794 324 Q 640 358 457 306"/>
  <path class="edge" marker-end="url(#arrow)" d="M 369 141 L 369 246"/>
  <path id="travel" d=""/><circle id="orb" r="10" cx="140" cy="100" />
  </svg>
  <div class="node" id="preprocessor" style="left:12.73%;top:27.4%"><span class="icon">⬡</span><div class="title">Preprocessor</div><div class="small">Triage · guardrails</div></div>
  <div class="node" id="orchestrator" style="left:33.55%;top:27.4%"><span class="icon">◎</span><div class="title">Orchestrator</div><div class="small">Route · loops</div></div>
  <div class="node" id="resolution_agent" style="left:54.55%;top:27.4%"><span class="icon">◈</span><div class="title">Resolution Agent</div><div class="small">Recommend</div></div>
  <div class="node" id="resolution_critic" style="left:79.55%;top:27.4%"><span class="icon">◇</span><div class="title">Resolution Critic</div><div class="small">Accept / revise</div></div>
  <div class="node" id="finalizer" style="left:33.55%;top:78.1%"><span class="icon">✓</span><div class="title">Finalisation</div><div class="small">Recorded decision</div></div>
  <div class="node" id="communication_agent" style="left:54.55%;top:78.1%"><span class="icon">✎</span><div class="title">Communication Agent</div><div class="small">Draft (not sent)</div></div>
  <div class="node" id="communication_critic" style="left:79.55%;top:78.1%"><span class="icon">◇</span><div class="title">Communication Critic</div><div class="small">Validate draft</div></div>
 </div></div>
 <div class="progress"><div class="fill" id="fill"></div></div>
 <div class="bottom"><div class="panel"><div class="kicker" id="stepcount">REPLAY EVENT</div><div id="out-title" aria-live="polite"></div><div id="out-line" aria-live="polite"></div><div id="evidence-note" aria-live="polite"></div></div>
  <div class="panel"><div class="kicker">RECORDED EVENT HISTORY</div><div id="activity"></div></div></div>
 <div class="status"><span><strong id="stepmeta"></strong></span><span>Recorded end-to-end: <strong id="duration"></strong></span><span>Node timing: <strong id="stage-time">—</strong></span></div>
 <div class="disclaimer">Animated movement and playback speed illustrate the <b>actual recorded event order</b>, not real-time execution. Event text and elapsed node timings are taken from an anonymised October 2026 LangSmith trace; no models or logistics actions are invoked.</div>
</div>
<script>
(() => {
  'use strict';
  const data = JSON.parse(document.getElementById('replay-source').textContent);
  const loc = {preprocessor:[140,100],orchestrator:[369,100],resolution_agent:[600,100],resolution_critic:[875,100],communication_agent:[600,285],communication_critic:[875,285],finalizer:[369,285]};
  const $ = id => document.getElementById(id);
  const steps = data.steps;
  let index = 0,playing = false, timer = null, frame = null, lastNode = 'preprocessor';
  $('scenario').textContent = data.id+' · '+data.title+' · '+steps.length+' recorded events';
  $('duration').textContent = Number(data.latency).toFixed(2)+' seconds';
  function setActive(node){Object.keys(loc).forEach(n=>{$(n).classList.toggle('active',n===node)});}
  function stop(){playing=false; clearTimeout(timer); cancelAnimationFrame(frame);$('play').textContent='▶ Play';}
  function position(node){let p=loc[node]||loc.preprocessor;$('orb').setAttribute('cx',p[0]);$('orb').setAttribute('cy',p[1]);$('travel').setAttribute('d','');}
  function animate(from,to,done){
    const [x0,y0]=loc[from]||loc.preprocessor, [x1,y1]=loc[to]||loc.preprocessor;
    if(from===to){position(to);done();return;}
    const dx=x1-x0,dy=y1-y0;
    const bend=(from==='resolution_critic'&&to==='resolution_agent')?-100:(Math.abs(dx)>400 ? -45 : 0);
    const cx=(x0+x1)/2,cy=(y0+y1)/2+bend;
    const path=$('travel');path.setAttribute('d',`M${x0},${y0} Q${cx},${cy} ${x1},${y1}`);
    const length=path.getTotalLength();const start=performance.now();const speed=Number($('speed').value);const animLength=Math.min(760,Math.max(260,speed*.54));
    function animateFrame(now){let pct=Math.min(1,(now-start)/animLength);let pt=path.getPointAtLength(length*(pct*pct*(3-2*pct)));$('orb').setAttribute('cx',pt.x);$('orb').setAttribute('cy',pt.y);
      if(pct<1){frame=requestAnimationFrame(animateFrame)}else{path.setAttribute('d','');done()}
    }
    if(window.matchMedia('(prefers-reduced-motion: reduce)').matches){position(to);done()}else{frame=requestAnimationFrame(animateFrame)}
  }
  function render(){
    const s=steps[index];const prev=lastNode;lastNode=s.node;setActive(s.node);
    $('stepcount').textContent=`TRACE EVENT ${s.index} / ${steps.length}`;
    $('out-title').textContent=s.agent;
    $('out-line').textContent=s.message||s.source;
    $('evidence-note').textContent=s.evidence_note||'';
    $('evidence-note').style.display=s.evidence_note?'block':'none';
    $('stepmeta').textContent='Event '+(index+1)+' of '+steps.length; $('stage-time').textContent=Number(s.timing).toFixed(3)+' s · started at +'+Number(s.offset).toFixed(3)+' s';
    $('fill').style.width=((index+1)/steps.length*100).toFixed(1)+'%';
    const recent=steps.slice(Math.max(0,index-3),index+1);
    $('activity').replaceChildren(...recent.map(r=>{const row=document.createElement('div');const lbl=document.createElement('span');lbl.textContent=String(r.index).padStart(2,'0')+' · '+r.agent;row.append(lbl, document.createTextNode(' '+r.message));return row;}));
    $('prev').disabled=index===0;$('next').disabled=index===steps.length-1;
    animate(prev,s.node,()=>{});
  }
  function go(i){cancelAnimationFrame(frame);index=Math.max(0,Math.min(steps.length-1,i));render()}
  function queue(){if(!playing)return;timer=setTimeout(()=>{if(index+1>=steps.length){stop();return;}go(index+1);queue();},Number($('speed').value));}
  $('play').addEventListener('click',()=>{if(playing){stop();return}if(index>=steps.length-1){go(0)}playing=true;$('play').textContent='Ⅱ Pause';queue();});
  $('prev').addEventListener('click',()=>{stop();go(index-1)});
  $('next').addEventListener('click',()=>{stop();go(index+1)});
  $('reset').addEventListener('click',()=>{stop();lastNode='preprocessor';go(0)});
  $('speed').addEventListener('change',()=>{if(playing){clearTimeout(timer);queue()}});
  position('preprocessor');render();
})();
</script></body></html>'''
