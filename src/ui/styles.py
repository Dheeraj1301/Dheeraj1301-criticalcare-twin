CSS = """
<style>
:root { --bg:#071015; --panel:#0d1920; --panel2:#111f27; --line:#20343d; --text:#e7f0f2; --muted:#8fa5ad; --cyan:#45d6c7; --amber:#ffbd59; --red:#ff6376; }
.stApp { background: radial-gradient(circle at 80% 0%, #10252c 0%, var(--bg) 32%); color:var(--text); }
[data-testid="stSidebar"] { background:#09141a; border-right:1px solid var(--line); }
.block-container { max-width:1500px; padding-top:1.4rem; }
h1,h2,h3 { font-family:Inter,system-ui,sans-serif; letter-spacing:-.02em; }
h1 { color:#f1fbfb; font-size:2.15rem !important; }
.eyebrow { color:var(--cyan); text-transform:uppercase; letter-spacing:.18em; font:700 .72rem monospace; }
.disclaimer { background:#281a0d; border:1px solid #6a4920; color:#ffd99c; padding:.72rem 1rem; border-radius:8px; font-size:.86rem; }
.statusbar { display:flex; gap:14px; flex-wrap:wrap; margin:.6rem 0 1rem; }
.statuspill { background:#10242a; border:1px solid #24515a; border-radius:99px; padding:.35rem .72rem; color:#bceee9; font:600 .75rem monospace; }
.metric-card { background:linear-gradient(145deg,#102029,#0a161c); border:1px solid var(--line); border-radius:10px; padding:.85rem; min-height:125px; box-shadow:0 10px 30px #0003; }
.metric-name { color:var(--muted); text-transform:uppercase; letter-spacing:.08em; font-size:.7rem; }
.metric-value { color:#f4fbfb; font:700 1.55rem monospace; margin:.32rem 0; }
.metric-meta { color:#9eb0b7; font:.72rem monospace; line-height:1.55; }
.badge { border:1px solid #2e6467; color:#8ff0e4; border-radius:4px; padding:.12rem .35rem; font-size:.62rem; }
.flow { display:flex; align-items:center; gap:8px; flex-wrap:wrap; margin:1rem 0; }
.flow-node { background:#0d2027; border:1px solid #285260; padding:.7rem .8rem; border-radius:7px; font:700 .72rem monospace; color:#bdd5dc; }
.flow-arrow { color:var(--cyan); }
.event { padding:.38rem .6rem; border-left:2px solid var(--cyan); margin:.25rem 0; background:#0c171d; font:.72rem monospace; color:#b8cbd0; }
.live-flow { display:grid; grid-template-columns:repeat(6,minmax(110px,1fr)); gap:10px; margin:1rem 0 1.2rem; }
.live-stage { position:relative; background:#0b181e; border:1px solid #203943; border-radius:10px; padding:.75rem .7rem; min-height:72px; color:#829aa2; font:700 .68rem monospace; text-align:center; letter-spacing:.04em; }
.live-stage .stage-num { display:block; color:#49656d; font-size:.58rem; margin-bottom:.35rem; }
.live-stage.done { border-color:#29675f; color:#a8ddd7; background:#0c211f; }
.live-stage.active { border-color:var(--cyan); color:#e8fffc; background:#10302e; box-shadow:0 0 0 1px #45d6c755,0 0 28px #45d6c72b; animation:pulse 1.3s ease-in-out infinite; }
.live-stage.active:after { content:''; position:absolute; left:15%; right:15%; bottom:-2px; height:3px; border-radius:3px; background:var(--cyan); }
@keyframes pulse { 0%,100%{transform:translateY(0)} 50%{transform:translateY(-2px)} }
.signal-panel { background:#09161c; border:1px solid var(--line); border-radius:12px; padding:1rem; min-height:220px; }
.signal-title { color:#789098; font:700 .66rem monospace; letter-spacing:.12em; margin-bottom:.8rem; }
.signal-row { display:grid; grid-template-columns:1.5fr 1fr .7fr; padding:.42rem 0; border-bottom:1px solid #172a31; font:.76rem monospace; }
.signal-row:last-child { border:0; }
.signal-value { color:#efffff; text-align:right; }
.signal-delta { color:#55d8cb; text-align:right; }
.engine-core { border:1px solid #2f6d69; background:radial-gradient(circle at center,#123331,#0a171c 68%); border-radius:50%; width:190px; height:190px; margin:.9rem auto; display:flex; flex-direction:column; justify-content:center; align-items:center; box-shadow:0 0 45px #45d6c719; }
.engine-core .version { color:#f1fffd; font:800 2rem monospace; }
.engine-core .label { color:#65d9ce; font:700 .64rem monospace; letter-spacing:.14em; }
.output-chip { display:flex; justify-content:space-between; align-items:center; padding:.7rem .8rem; border:1px solid var(--line); background:#0a171d; border-radius:8px; margin:.45rem 0; font:.72rem monospace; color:#8fa5ad; }
.output-chip strong { color:#e8f7f6; font-size:.95rem; }
@media (max-width:900px){ .live-flow{grid-template-columns:repeat(2,1fr);} }
.research-note { color:#91a7ae; font-size:.82rem; }
[data-testid="stMetric"] { background:#0d1c23; border:1px solid var(--line); padding:.7rem; border-radius:8px; }
[data-testid="stDataFrame"] { border:1px solid var(--line); border-radius:8px; }
</style>
"""
