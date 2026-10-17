"""Build an explicitly edited explainer from the latest SHP-006 trace (not live AI)."""
from __future__ import annotations
import json,subprocess
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[1]
c=next(c for c in json.loads((ROOT/'data'/'recorded_cases.json').read_text())['cases'] if c['id']=='SHP-006')
assert [e['review']['decision'] for e in c['agent_events'] if e['node']=='critic_resolution']==['REVISE','ACCEPT']
assert c['final_action']['revision_count']==1
font='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
bold='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
F=lambda n,b=False:ImageFont.truetype(bold if b else font,n)
slides=[
 ('THE CASE',('One exception.','Several decisions.'),('SHP-006 · October 17 recorded run','This is a documented replay, not a live AI system.')),
 ('01 / TRIAGE',('Check the signal.','Understand context.'),('Deterministic preprocessing and LangGraph routing','Operational inputs inform the specialist agents.')),
 ('02 / PROPOSE',('Resolution Agent','recommends action.'),('The first recommendation is captured in LangSmith.','Its rationale and operational instruction are retained.')),
 ('03 / REVIEW',('Independent Critic','requests REVISE.'),('The recorded objection explains the missing action.','Control returns to Resolution Agent.')),
 ('04 / REVISION',('The agent revises.','Critic ACCEPTS.'),('A new proposal addresses the recorded objection.','Both reviewer rationales are available in the demo.')),
 ('05 / CUSTOMER',('Draft. Review.','Never auto-send.'),('A Communication Critic assesses the customer draft.','No delivery or customer outreach was executed.')),
 ('FINAL / EVIDENCE',('One revision.','Recorded decision.'),(f"SHP-006 end-to-end trace: {c['metrics']['latency_seconds']:.2f} seconds.",'Video speed does not represent actual inference timing.')),
]
W,H,FPS,SEC=1024,576,10,4
out=ROOT/'assets'/'shp006_story.mp4'
proc=subprocess.Popen(['ffmpeg','-y','-hide_banner','-loglevel','error','-f','rawvideo','-vcodec','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','-','-an','-c:v','libx264','-preset','veryfast','-crf','27','-pix_fmt','yuv420p','-movflags','+faststart',str(out)],stdin=subprocess.PIPE,stderr=subprocess.PIPE)
try:
 for ix,(eyebrow,heads,sub) in enumerate(slides):
  for j in range(SEC*FPS):
   im=Image.new('RGB',(W,H),(49,29,61));d=ImageDraw.Draw(im)
   d.ellipse((760,-180,1220,200),outline=(78,48,90),width=75)
   d.rounded_rectangle((48,43,112,88),radius=10,fill=(235,112,77))
   d.text((58,58),'E/C',font=F(17,True),fill=(255,255,255))
   d.text((128,58),'EXCEPTION / CONTROL',font=F(17,True),fill=(228,212,225))
   d.text((50,126),eyebrow,font=F(22),fill=(247,195,131))
   for k,line in enumerate(heads):d.text((47,195+k*70),line,font=F(46,True),fill=(255,250,244))
   d.rounded_rectangle((44,382,978,482),radius=13,fill=(64,40,76))
   for k,line in enumerate(sub):d.text((66,403+k*37),line,font=F(20),fill=(231,214,224))
   d.text((48,527),'EDITED RECONSTRUCTION  /  OCT 2026 LANGSMITH TRACE',font=F(13),fill=(184,169,186))
   d.rectangle((0,H-6,W,H),fill=(88,58,95))
   d.rectangle((0,H-6,round(W*(ix+j/(SEC*FPS))/len(slides)),H),fill=(240,108,76))
   proc.stdin.write(im.tobytes())
 proc.stdin.close();err=proc.stderr.read();ret=proc.wait()
 if ret:raise RuntimeError(err.decode(errors='replace'))
finally:
 if proc.poll() is None:proc.kill()
print(out,out.stat().st_size)
