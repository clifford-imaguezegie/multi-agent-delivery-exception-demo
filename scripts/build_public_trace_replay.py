"""PRIVATE authoring utility. Builds a tightly allowlisted public dataset from LangSmith exports.
Never publish the private ZIP, raw spans, internal PDF excerpts, or this utility's inputs.
Usage: python scripts/build_public_trace_replay.py /path/private_traces.zip
Perform human privacy and policy-content review before public upload.
"""
from __future__ import annotations
import json, re, sys, zipfile
from pathlib import Path
from datetime import datetime
from collections import Counter

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'data'/'recorded_cases.json'
NODES={'preprocessor','orchestrator','resolution_agent','critic_resolution','communication_agent','critic_communication','finalize'}
NO_IDENTIFIERS=['customer_profile_full','raw_rows','playbook_context','inputs','outputs','tool_calls_log','locker_availability','customer_profile','consolidated_event','prompt','api_key','trace_id','run_id','dotted_order']

def parse(t): return datetime.fromisoformat(t.replace('Z','+00:00'))
def elapsed(s,e):return round(max(0,(parse(e)-parse(s)).total_seconds()),3)

def build_redactor(runs):
    names=set()
    for r in runs:
        o=r.get('outputs') or {}
        if not isinstance(o,dict):continue
        cp=o.get('customer_profile_full') or o.get('customer_profile') or {}
        if isinstance(cp,dict):
            for key in ('name','full_name','customer_name','first_name','last_name'):
                v=cp.get(key)
                if isinstance(v,str) and len(v.strip())>2: names.add(v.strip())
    names={n for n in names if n.lower() not in {'vip','standard','casual','formal','unknown','none'}}
    def clean(value):
        if value is None:return ''
        text=str(value)
        for name in sorted(names,key=len,reverse=True):
            text=re.sub(r'(?<!\w)'+re.escape(name)+r'(?!\w)','[CUSTOMER]',text,flags=re.I)
        text=re.sub(r'\b[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}\b','[EMAIL REDACTED]',text)
        text=re.sub(r'(?<!\w)\+?\d[\d ()-]{8,}\d(?!\w)','[PHONE REDACTED]',text)
        text=re.sub(r'(?i)\b(?:CUST|CUSTOMER|ACC|ACCOUNT)[-_#:]?\d{2,}\b','[CUSTOMER ID REDACTED]',text)
        text=re.sub(r'\b\d{1,5}\s+(?:[A-Z][\w-]+\s+){0,4}(?:Street|Road|Avenue|Lane|Drive|Boulevard|Close|Court|Way|Place|St|Rd|Ave)\b[.,]?','[ADDRESS REDACTED]',text,flags=re.I)
        text=re.sub(r'(?i)\b(?:dear|hello|hi)\s+(?:mr\.?|ms\.?|mrs\.?)?\s*[A-Z][a-z]+(?:\s+[A-Z][a-z]+)?\s*[,!:]',lambda m: m.group(0).split()[0]+' [CUSTOMER],',text)
        text=re.sub(r'(?i)\b(?:[A-Z]{1,2}\d[A-Z\d]?\s*\d[A-Z]{2})\b','[POSTCODE REDACTED]',text)
        return text
    return clean

def public_build(private_zip):
    original=json.loads(BASE.read_text(encoding='utf8'))
    base={c['id']:c for c in original['cases']}
    cases=[]
    with zipfile.ZipFile(private_zip) as z:
        for i in range(1,11):
            shipment=f'SHP-{i:03}'
            runs=json.loads(z.read(f'{shipment}/trace.json'))['runs']
            manifest=json.loads(z.read(f'{shipment}/manifest.json'))
            clean=build_redactor(runs)
            assert all(not r.get('error') for r in runs)
            root=next(r for r in runs if r['name']=='delivery_exception_case')
            stages=[r for r in runs if r['name'] in NODES and not r['name'].endswith('_node')]
            stages.sort(key=lambda r:(r['start_time'],r.get('dotted_order','')))
            # Authoritative final decision is in finalizer state, not root final_action (None).
            finalizer=next(r for r in reversed(stages) if r['name']=='finalize')
            fo=finalizer.get('outputs') or {}
            fa=(fo.get('final_actions') or [])[-1]
            resolution=fo.get('resolution_output') or {}
            resolution_critic=fo.get('critic_resolution_output') or {}
            communication=fo.get('communication_output') or {}
            communication_critic=fo.get('critic_communication_output') or {}
            def safe_res(d):return {k:clean(d.get(k)) for k in ('is_exception','resolution','operational_action','rationale') if d.get(k) is not None}
            def safe_critic(d):return {k:clean(d.get(k)) for k in ('decision','rationale') if d.get(k) is not None}
            def safe_comm(d):return {k:clean(d.get(k)) for k in ('tone_label','communication_message') if d.get(k) is not None}
            now_proposal={}
            now_draft={}
            events=[]
            timeline=[]
            for r in stages:
                n=r['name'];o=r.get('outputs') or {}
                dur=elapsed(r['start_time'],r['end_time'])
                ev={'index':len(events)+1,'node':n,'start_offset_seconds':round((parse(r['start_time'])-parse(root['start_time'])).total_seconds(),3), 'duration_seconds':dur}
                if n=='resolution_agent':
                    p=safe_res(o.get('resolution_output') or {})
                    now_proposal=p
                    ev['proposal']=p
                    ev['summary']='Proposed '+p.get('resolution','unknown').replace('_',' ').lower()+' · '+p.get('operational_action','handling not recorded').replace('_',' ').lower()
                elif n=='critic_resolution':
                    rev=safe_critic(o.get('critic_resolution_output') or {})
                    ev['review']=rev
                    ev['reviewed_proposal']=dict(now_proposal)
                    ev['summary']='Resolution Critic: '+rev.get('decision','unavailable')
                elif n=='communication_agent':
                    now_draft=safe_comm(o.get('communication_output') or {})
                    ev['draft']=now_draft
                    ev['summary']='Prepared an unsent customer draft'
                elif n=='critic_communication':
                    rev=safe_critic(o.get('critic_communication_output') or {})
                    ev['review']=rev
                    ev['reviewed_draft']=dict(now_draft)
                    ev['summary']='Communication Critic: '+rev.get('decision','unavailable')
                elif n=='preprocessor': ev['summary']='Normalised event; '+('routine event' if fa.get('is_exception')=='NO' else 'exception identified')
                elif n=='orchestrator':
                    route=clean(o.get('next_agent') or 'routing recorded')
                    ev['summary']='Routes to '+route.replace('_',' ')
                else: ev['summary']='Recorded final decision · '+str(fa.get('resolution') or 'N/A').replace('_',' ')
                events.append(ev)
                timeline.append(n+': '+ev['summary'])
            all_reviews=[ev for ev in events if ev['node'] in ('critic_resolution','critic_communication')]
            review_count=sum(ev.get('review',{}).get('decision')=='REVISE' for ev in events if ev['node']=='critic_resolution')
            assert fa['revision_count']==review_count or (fa['revision_count']==2 and review_count==2),(shipment,fa['revision_count'],review_count)
            c=base[shipment]
            # Strict data allowlist. No state copies, prompts, retrieved documents or private identifiers.
            case={
              'id':shipment,'title':c['title'],
              'event':c['event'],'customer':c['customer'],
              'escalation_signals':{'triggers':[clean(x) for x in (fo.get('escalation_signals') or {}).get('triggers',[]) if isinstance(x,str)],'resolution_constraints':[], 'operational_constraints':[]},
              'ground_truth':c['ground_truth'],
              'final_action':{k:fa.get(k) for k in ('is_exception','resolution','escalated','tone','revision_count','guardrail_blocked')},
              'resolution_agent':safe_res(resolution),
              'resolution_critic':safe_critic(resolution_critic),
              'communication_agent':safe_comm(communication),
              'communication_critic':safe_critic(communication_critic),
              'metrics':{'latency_seconds':elapsed(root['start_time'],root['end_time'])},
              'trajectory':timeline,
              'agent_events':events,
              'trace_summary':{'spans_recorded':len(runs),'root_completed':bool(root.get('end_time')),'source':'LangSmith per-case trace export','captured_at':'2026-10-17'},
              'tool_calls':[f"{r['name']} · {elapsed(r['start_time'],r['end_time']):.3f}s (recorded tool span; arguments hidden)" for r in runs if r.get('run_type')=='tool' and r.get('name') in ('lookup_customer_profile','check_locker_availability','search_playbook','check_escalation_rules')], 'playbook_references':[], 'citation_pages':[],
            }
            cases.append(case)
    agg={'cases':10,'exception_cases':sum(c['final_action']['is_exception']=='YES' for c in cases),
         'complete_traces':10,
         'total_spans':sum(c['trace_summary']['spans_recorded'] for c in cases),
         'mean_latency_seconds':round(sum(c['metrics']['latency_seconds'] for c in cases)/10,2),
         'mean_exception_latency_seconds':round(sum(c['metrics']['latency_seconds'] for c in cases if c['final_action']['is_exception']=='YES')/8,2),
         'legacy_evaluation_not_reattached':True}
    data={'dataset_label':'October 17 2026 LangSmith replay capture','source':'Redacted allowlisted LangSmith spans from 10 rerun scenarios', 'replay_mode':True,
       'privacy':'Allowlist transform; requires manual privacy review before public release',
       'aggregate':agg, 'cases':cases}
    return data

if __name__=='__main__':
    if len(sys.argv)!=2:raise SystemExit('Pass PRIVATE LangSmith ZIP path')
    out=public_build(sys.argv[1]);p=ROOT/'data'/'recorded_cases.json';p.write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf8')
    print('Built',p,'with',out['aggregate'])
