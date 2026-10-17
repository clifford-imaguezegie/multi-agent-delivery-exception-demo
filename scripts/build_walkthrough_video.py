"""Produce a silent, captioned storyboard video from the original SHP-004 record.

Explicitly an edited educational reconstruction, not a recording of live inference.
Requires Pillow and ffmpeg only for authorship; the deployed Streamlit app requires neither.
"""
from __future__ import annotations
import json
import subprocess
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT=Path(__file__).resolve().parents[1]
cases=json.loads((ROOT/"data"/"recorded_cases.json").read_text(encoding="utf-8"))["cases"]
c=next(x for x in cases if x["id"]=="SHP-004")
assert c["final_action"]["revision_count"]==2
assert c["final_action"]["escalated"] is True
assert c["final_action"]["resolution"]=="REPLACE"
assert c["metrics"]["latency_seconds"]==28.58

OUT=ROOT/"assets"/"shp004_story.mp4"
W,H=1024,576
FPS=12
SEC=4.5
PLUM=(48,27,59); PLUM_LIGHT=(72,43,83); CREAM=(255,248,240)
CORAL=(243,112,76); GOLD=(247,195,131); LAV=(223,201,220); MUTED=(190,168,189)
FONT_PATH="/usr/share/fonts/opentype/inter/Inter-Regular.otf"
BOLD_PATH="/usr/share/fonts/opentype/inter/Inter-Bold.otf"
font_s=ImageFont.truetype(FONT_PATH,20)
font_xs=ImageFont.truetype(BOLD_PATH,15)
font_t=ImageFont.truetype(BOLD_PATH,49)
font_m=ImageFont.truetype(FONT_PATH,25)
font_b=ImageFont.truetype(BOLD_PATH,23)
font_foot=ImageFont.truetype(FONT_PATH,15)
slides=[
    {"step":"THE EXCEPTION","title":["One damaged parcel.","Several decisions."],"body":["SHP-004 · damaged fragile package · VIP customer", "From incident report to a reviewed replacement decision."],"bottom":"ORIGINAL RECORDED CASE · EDITED RECONSTRUCTION"},
    {"step":"01 / SIGNAL","title":["A delivery issue", "needs triage."],"body":["The preprocessor normalises the delivery event.","The case is routed as an actionable exception."],"bottom":"CAPTURED PREPROCESSING AND ORCHESTRATOR EVENTS"},
    {"step":"02 / CONTEXT","title":["Not just the event.","The full context."],"body":["Delivery notes · package attributes · customer profile", "Operational tools and the playbook inform the resolution."],"bottom":"ORIGINAL WORKFLOW: TOOLS + RAG POLICY RETRIEVAL"},
    {"step":"03 / RESOLUTION","title":["The agent proposes", "a replacement."],"body":["Recorded recommendation: REPLACE", "Handling instruction: REMOVE_FROM_ROUTE_AND_HOLD"],"bottom":"RESOLUTION AGENT · GEMMA 4 26B A4B IT"},
    {"step":"04 / INDEPENDENT REVIEW","title":["The Critic requests", "two revisions."],"body":["Decision 1: REVISE · Decision 2: REVISE", "A bounded review loop prevents indefinite retries."],"bottom":"RESOLUTION CRITIC · GEMMA 4 31B IT"},
    {"step":"05 / HUMAN OVERSIGHT","title":["The revision limit", "triggers escalation."],"body":["Maximum two resolution revisions reached.", "Supervisor review is required; no real shipment change occurs."],"bottom":"RECORDED ORCHESTRATOR: FORCED ESCALATION"},
    {"step":"06 / COMMUNICATION","title":["Customer messaging", "is checked too."],"body":["A FORMAL customer communication draft is generated.","The Communication Critic recorded ACCEPT."],"bottom":"DRAFT ONLY · NOT SENT"},
    {"step":"FINAL / RECORDED RESULT","title":["REPLACE.","Escalate to human."],"body":["2 resolution revisions · final escalation YES", "Original end-to-end run: 28.58 seconds."],"bottom":"FILM DURATION IS NOT MODEL PROCESSING TIME"},
]

def draw_frame(i, frame_number):
    slide=slides[i]
    fr=Image.new("RGB",(W,H),PLUM)
    d=ImageDraw.Draw(fr)
    d.ellipse((756,-215,1160,187),outline=PLUM_LIGHT,width=72)
    d.ellipse((828,310,1160,644),outline=PLUM_LIGHT,width=51)
    d.rounded_rectangle((47,43,108,84),radius=11,fill=CORAL)
    d.text((58,55),"E / C",font=font_xs,fill=CREAM)
    d.text((125,55),"EXCEPTION / CONTROL",font=font_xs,fill=LAV)
    d.text((48,129),slide["step"],font=font_s,fill=GOLD,stroke_width=0)
    d.line((48,174,85,174),fill=CORAL,width=5)
    y=205
    for line in slide["title"]:
        d.text((48,y),line,font=font_t,fill=CREAM,stroke_width=0)
        y+=62
    d.rounded_rectangle((46,371,975,490),radius=16,fill=(63,39,73),outline=(89,61,100),width=2)
    y=390
    for line in slide["body"]:
        d.text((67,y),line,font=font_m,fill=LAV)
        y+=42
    d.text((48,529),slide["bottom"],font=font_foot,fill=MUTED)
    d.text((885,529),f"{i+1:02d} / {len(slides):02d}",font=font_foot,fill=MUTED)
    # Progress indicator makes it clear this is an edited film.
    frac=(i+frame_number/(SEC*FPS))/len(slides)
    d.rectangle((0,H-5,W,H),fill=(101,66,108))
    d.rectangle((0,H-5,max(1,round(W*frac)),H),fill=CORAL)
    return fr

if __name__=="__main__":
    OUT.parent.mkdir(parents=True,exist_ok=True)
    cmd=["ffmpeg","-y","-hide_banner","-loglevel","error","-f","rawvideo","-vcodec","rawvideo","-pix_fmt","rgb24","-s",f"{W}x{H}","-r",str(FPS),"-i","-","-an","-c:v","libx264","-preset","fast","-crf","25","-pix_fmt","yuv420p","-movflags","+faststart",str(OUT)]
    proc=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=subprocess.PIPE)
    try:
        for i in range(len(slides)):
            for j in range(round(SEC*FPS)):
                proc.stdin.write(draw_frame(i,j).tobytes())
        proc.stdin.close()
        err=proc.stderr.read()
        ret=proc.wait()
        if ret:
            raise RuntimeError(err.decode(errors='replace'))
    finally:
        if proc.poll() is None:proc.kill()
    print("Built",OUT,OUT.stat().st_size,"bytes")
