"""Build the illustrated cloud-edge architecture report from real local artifacts."""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (BaseDocTemplate, Frame, Image, KeepTogether, PageBreak,
                               PageTemplate, Paragraph, Spacer, Table, TableStyle)

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw" / "patient" / "dataset.csv"
META = ROOT / "models" / "hospital_mortality_metadata.json"
OUT = ROOT / "output" / "pdf" / "CRITICALCARE_TWIN_Cloud_Edge_Architecture.pdf"
TMP = ROOT / "tmp" / "pdfs"
NAVY, PANEL, CYAN, AMBER, RED, TEXT, MUTED = "#071015", "#102029", "#45d6c7", "#ffbd59", "#ff6376", "#e7f0f2", "#617982"


def savefig(fig, name):
    path = TMP / name
    fig.savefig(path, dpi=180, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return path


def architecture_figure():
    fig, ax = plt.subplots(figsize=(12, 5.5)); ax.set_xlim(0, 12); ax.set_ylim(0, 6); ax.axis("off")
    boxes = [
        (0.2,2.3,1.6,1.1,"Patient /\nDemo source",CYAN), (2.2,2.0,2.2,1.7,"EDGE NODE\nValidation\nDigital twin\nLocal analytics",CYAN),
        (4.9,3.4,1.8,1.0,"Offline outbox\nSQLite",AMBER), (4.9,.9,1.8,1.0,"Local dashboard\nLow latency",CYAN),
        (7.2,2.0,2.0,1.7,"CLOUD API\nIdempotent sync\nPseudonymous key",RED),
        (9.7,3.4,1.9,1.0,"Cloud twin store",RED), (9.7,.9,1.9,1.0,"Fleet / latest-state\nquery APIs",RED),
    ]
    for x,y,w,h,label,color in boxes:
        ax.add_patch(plt.Rectangle((x,y),w,h,facecolor=PANEL,edgecolor=color,linewidth=2,joinstyle="round"))
        ax.text(x+w/2,y+h/2,label,ha="center",va="center",color="white",fontsize=9,fontweight="bold")
    arrows=[((1.8,2.85),(2.2,2.85),"observation"),((4.4,3.0),(4.9,3.9),"durable"),((4.4,2.4),(4.9,1.4),"state"),((6.7,3.9),(7.2,3.0),"HTTPS"),((9.2,3.0),(9.7,3.9),"store"),((10.65,3.4),(10.65,1.9),"query")]
    for start,end,label in arrows:
        ax.annotate("",xy=end,xytext=start,arrowprops=dict(arrowstyle="->",color=MUTED,lw=2)); ax.text((start[0]+end[0])/2,(start[1]+end[1])/2+.18,label,ha="center",fontsize=7,color=MUTED)
    ax.text(3.3,5.5,"EDGE DOMAIN",ha="center",fontsize=11,fontweight="bold",color=CYAN)
    ax.text(9.3,5.5,"CLOUD DOMAIN",ha="center",fontsize=11,fontweight="bold",color=RED)
    fig.patch.set_facecolor(NAVY); ax.set_facecolor(NAVY)
    return savefig(fig,"architecture.png")


def dataset_figures(df, metadata):
    paths=[]
    fig,axs=plt.subplots(1,2,figsize=(11,4.2))
    counts=df.hospital_death.value_counts().sort_index(); axs[0].bar(["Survived","Hospital death"],counts.values,color=[CYAN,RED]); axs[0].set_title("Documented outcome balance"); axs[0].set_ylabel("Encounters")
    for outcome,color,label in [(0,CYAN,"Survived"),(1,RED,"Hospital death")]: axs[1].hist(df.loc[df.hospital_death==outcome,"age"].dropna(),bins=25,alpha=.55,density=True,color=color,label=label)
    axs[1].set_title("Age distribution by outcome"); axs[1].set_xlabel("Age (years)"); axs[1].legend(); fig.suptitle("Figure 2. ICU cohort and documented outcome (n=91,713)",fontweight="bold"); paths.append(savefig(fig,"cohort.png"))
    fig,axs=plt.subplots(2,2,figsize=(11,7)); specs=[("heart_rate_apache","Heart rate (bpm)"),("map_apache","MAP (mmHg)"),("resprate_apache","Respiratory rate"),("temp_apache","Temperature (C)")]
    for ax,(col,label) in zip(axs.flat,specs):
        for outcome,color,name in [(0,CYAN,"Survived"),(1,RED,"Hospital death")]: ax.hist(df.loc[df.hospital_death==outcome,col].dropna(),bins=35,alpha=.48,density=True,color=color,label=name)
        ax.set_xlabel(label); ax.set_ylabel("Density"); ax.legend(fontsize=7)
    fig.suptitle("Figure 3. Observed ICU admission physiology by outcome",fontweight="bold"); paths.append(savefig(fig,"vitals.png"))
    missing=(df.isna().mean()*100).sort_values(ascending=False).head(18).sort_values()
    fig,ax=plt.subplots(figsize=(10,6)); ax.barh(missing.index,missing.values,color=AMBER); ax.set_xlabel("Missing values (%)"); ax.set_title("Figure 4. Highest missingness in the ICU source"); paths.append(savefig(fig,"missingness.png"))
    cols=["age","bmi","heart_rate_apache","map_apache","resprate_apache","temp_apache","d1_spo2_min","d1_glucose_max","hospital_death"]
    corr=df[cols].corr(numeric_only=True)
    fig,ax=plt.subplots(figsize=(8,7)); im=ax.imshow(corr,cmap="RdBu_r",vmin=-1,vmax=1); ax.set_xticks(range(len(cols)),[c.replace("_apache","") for c in cols],rotation=45,ha="right",fontsize=8); ax.set_yticks(range(len(cols)),[c.replace("_apache","") for c in cols],fontsize=8); fig.colorbar(im,ax=ax,shrink=.75); ax.set_title("Figure 5. Pairwise correlations (descriptive, not causal)"); paths.append(savefig(fig,"correlation.png"))
    candidates=metadata["candidates"]
    fig,axs=plt.subplots(1,2,figsize=(11,4.2))
    names=list(candidates); x=np.arange(len(names)); width=.25
    for i,key in enumerate(["roc_auc","pr_auc","brier"]): axs[0].bar(x+(i-1)*width,[candidates[n][key] for n in names],width,label=key.upper())
    axs[0].set_xticks(x,[n.replace("_","\n") for n in names]); axs[0].set_ylim(0,1); axs[0].legend(); axs[0].set_title("Internal model comparison")
    for n,color in zip(names,[CYAN,RED]):
        roc=candidates[n]["roc_curve"]; axs[1].plot(roc["fpr"],roc["tpr"],label=n,color=color,lw=2)
    axs[1].plot([0,1],[0,1],"--",color=MUTED); axs[1].set_xlabel("False-positive rate"); axs[1].set_ylabel("True-positive rate"); axs[1].set_title("ROC curves"); axs[1].legend(fontsize=8)
    fig.suptitle("Figure 6. Model test-set evidence",fontweight="bold"); paths.append(savefig(fig,"models.png"))
    return paths


def build():
    TMP.mkdir(parents=True,exist_ok=True); OUT.parent.mkdir(parents=True,exist_ok=True)
    df=pd.read_csv(RAW); metadata=json.loads(META.read_text(encoding="utf-8"))
    arch=architecture_figure(); charts=dataset_figures(df,metadata)
    styles=getSampleStyleSheet()
    styles.add(ParagraphStyle(name="TitleWhite",parent=styles["Title"],textColor=colors.HexColor(TEXT),fontSize=27,leading=32,alignment=TA_CENTER,spaceAfter=18))
    styles.add(ParagraphStyle(name="SubWhite",parent=styles["Normal"],textColor=colors.HexColor("#b5c9ce"),fontSize=12,leading=18,alignment=TA_CENTER))
    styles.add(ParagraphStyle(name="H1x",parent=styles["Heading1"],textColor=colors.HexColor("#0b5f59"),fontSize=20,leading=24,spaceBefore=10,spaceAfter=10))
    styles.add(ParagraphStyle(name="H2x",parent=styles["Heading2"],textColor=colors.HexColor("#174d58"),fontSize=14,leading=18,spaceBefore=8,spaceAfter=6))
    styles.add(ParagraphStyle(name="Bodyx",parent=styles["BodyText"],fontSize=9.5,leading=14,spaceAfter=7))
    styles.add(ParagraphStyle(name="Smallx",parent=styles["BodyText"],fontSize=7.8,leading=11,textColor=colors.HexColor("#465a60")))
    story=[]
    story += [Spacer(1,1.0*inch),Paragraph("CRITICALCARE-TWIN",styles["TitleWhite"]),Paragraph("Cloud-Edge Patient Digital Twin Architecture",styles["SubWhite"]),Spacer(1,.35*inch),Image(str(arch),width=7.2*inch,height=3.3*inch),Spacer(1,.25*inch),Paragraph("Detailed technical architecture, real dataset evidence, test results, deployment model, and scientific limitations",styles["SubWhite"]),Spacer(1,.6*inch),Paragraph("Research and educational software prototype - not clinically validated",styles["SubWhite"]),PageBreak()]
    def h1(t): story.append(Paragraph(t,styles["H1x"]))
    def h2(t): story.append(Paragraph(t,styles["H2x"]))
    def p(t): story.append(Paragraph(t,styles["Bodyx"]))
    def bullets(items):
        for item in items: story.append(Paragraph("- "+item,styles["Bodyx"]))
    h1("1. Executive summary"); p("CRITICALCARE-TWIN is a patient-specific digital twin research prototype split across an edge domain and a cloud domain. The edge node accepts timestamped observations, validates them, updates the persistent physiological state, runs low-latency analytics, and records an auditable snapshot. A durable outbox then transfers a deliberately reduced, pseudonymous state summary to the cloud service. The cloud stores versioned summaries and exposes latest-state and fleet-level query endpoints.")
    p("This separation is intentional. Immediate state synchronization does not depend on network availability. Cloud connectivity adds longitudinal retention and multi-edge aggregation, but a network outage cannot stop the local twin. In the current free local demonstration, the cloud boundary is executed as a second FastAPI process. The API contract is deployable to a cloud host without changing edge behavior; this document does not claim that a commercial cloud account is configured.")
    h2("What changed"); bullets(["Added a deployable FastAPI cloud service with health, sync, latest-state, and fleet-summary endpoints.","Added an offline-safe SQLite edge outbox and explicit synchronization audit.","Pseudonymized the source patient identifier before any cloud payload is built.","Integrated cloud synchronization into every real twin snapshot while preventing scenario clones from publishing.","Consolidated eight dashboard pages into seven by merging data provenance and model evaluation into Evidence Lab."])
    h1("2. System context and trust boundaries"); story.append(Image(str(arch),width=7.2*inch,height=3.3*inch)); p("Figure 1. The edge domain owns raw observations, direct patient identifiers, state estimation, and low-latency behavior. The cloud domain receives only a pseudonymous patient key, twin ID, version, state vector, derived values, risk output, uncertainty, provenance class, and timestamps. The local demonstration uses HTTP on loopback; a real deployment must terminate TLS and authenticate edge sites.")
    h2("Edge responsibilities"); bullets(["Ingest and validate observations against configured physiological bounds.","Maintain X(t-1), X(t), delta X, rolling state history, baseline B, and uncertainty.","Run model inference, anomaly scoring, and short-horizon forecasting locally.","Persist patient, observation, event, risk, and snapshot records in SQLite.","Queue cloud envelopes when the service is unavailable and retry in order."])
    h2("Cloud responsibilities"); bullets(["Accept idempotent messages keyed by message_id and preserve twin version.","Store pseudonymous longitudinal state summaries across sessions and edge sites.","Expose the latest state for one pseudonymous key and aggregate fleet counts.","Remain independent of the Streamlit presentation layer."])
    h1("3. End-to-end lifecycle"); p("At time t the source produces observation Y_t. The edge validates Y_t, then computes X_t = F(X_(t-1), Y_t, q_t), where q_t is measurement quality. Derived features Z_t = G(X_t, B, history) feed the supervised hospital-death model, the independent anomaly detector, and the forecast. A snapshot is written locally before a cloud envelope is attempted. If the API accepts it, an audit row records success. If not, the unchanged JSON envelope is placed in the durable outbox.")
    lifecycle=[["Step","Component","Output"],["1","Telemetry / source adapter","Timestamped Observation"],["2","Edge validation","Range/type decision"],["3","State estimator","Filtered X_t and delta X"],["4","Feature engine","Derived Z_t"],["5","Analytics","Risk, anomaly, forecast"],["6","Local repository","Durable snapshot and events"],["7","Edge gateway","Pseudonymous cloud envelope"],["8","Cloud API","Accepted versioned state"],["9","Cloud store","Latest-state and fleet queries"]]
    table=Table(lifecycle,colWidths=[.45*inch,2.0*inch,4.4*inch],repeatRows=1); table.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,0),colors.HexColor("#0b5f59")),("TEXTCOLOR",(0,0),(-1,0),colors.white),("GRID",(0,0),(-1,-1),.35,colors.HexColor("#b7c7ca")),("FONTSIZE",(0,0),(-1,-1),8),("VALIGN",(0,0),(-1,-1),"TOP"),("ROWBACKGROUNDS",(0,1),(-1,-1),[colors.white,colors.HexColor("#eef5f5")]) ])); story += [table,PageBreak()]
    h1("4. Dataset evidence"); p("The primary source is the downloaded ICU encounter table from mitishaagarwal/patient. It contains 91,713 rows and 85 columns. It is cross-sectional at encounter level: first-hour and first-day minima/maxima are summaries, not an ordered bedside time series. The other downloaded datasets are kept separate because no scientifically defensible common patient identifier exists.")
    story += [Image(str(charts[0]),width=7.2*inch,height=2.75*inch),Paragraph("The documented hospital_death positive rate is {:.2%}. Class imbalance motivates PR-AUC alongside ROC-AUC.".format(df.hospital_death.mean()),styles["Smallx"]),PageBreak(),Image(str(charts[1]),width=7.2*inch,height=4.6*inch),Paragraph("Distributions are descriptive views of observed source columns. They do not establish clinical thresholds or causal relationships.",styles["Smallx"]),PageBreak(),Image(str(charts[2]),width=7.0*inch,height=4.2*inch),Paragraph("Missingness is preserved during preprocessing and median-imputed inside the model pipeline. Twin uncertainty separately reflects missing observations.",styles["Smallx"]),PageBreak(),Image(str(charts[3]),width=6.4*inch,height=5.5*inch),Paragraph("Correlations are descriptive and may reflect treatment, selection, site, and coding effects.",styles["Smallx"]),PageBreak()]
    h1("5. Model and test-set evidence"); p("The downstream supervised task predicts the source field hospital_death. Logistic regression and a class-balanced random forest use a fixed 80/20 stratified encounter split. APACHE mortality probabilities, patient/encounter identifiers, and target-adjacent fields are excluded. The selected random forest reached ROC-AUC {:.3f} and PR-AUC {:.3f}; these are internal metrics only.".format(metadata["candidates"][metadata["selected_model"]]["roc_auc"],metadata["candidates"][metadata["selected_model"]]["pr_auc"])); story += [Image(str(charts[4]),width=7.2*inch,height=2.75*inch)]
    h2("Interpretation limits"); bullets(["Random splitting does not establish future-site or temporal generalization.","Feature importance and displayed contributions are associations, not causal effects.","The model output is hospital-death probability for the dataset task, not a clinical diagnosis.","Replay telemetry is simulated and is never used to fabricate training labels."])
    h1("6. Cloud API and edge synchronization contract");
    api=[["Endpoint","Purpose"],["GET /health","Service mode and stored snapshot count"],["POST /v1/twins/sync","Idempotently accept one CloudTwinEnvelope"],["GET /v1/twins/{patient_key}/latest","Return latest version for a pseudonymous patient"],["GET /v1/fleet/summary","Count snapshots, pseudonymous patients, and sites"]]
    table=Table(api,colWidths=[2.6*inch,4.25*inch],repeatRows=1); table.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,0),colors.HexColor("#0b5f59")),("TEXTCOLOR",(0,0),(-1,0),colors.white),("GRID",(0,0),(-1,-1),.35,colors.HexColor("#b7c7ca")),("FONTSIZE",(0,0),(-1,-1),8),("VALIGN",(0,0),(-1,-1),"TOP") ])); story += [table]
    p("The edge derives patient_key as the first 20 hexadecimal characters of SHA-256(salt:patient_id). This is pseudonymization, not anonymization. Production use would require managed secrets, key rotation, authenticated transport, access control, audit retention, and formal privacy review. Scenario clones explicitly remove their edge gateway so experimental branches cannot enter the cloud record.")
    h1("7. Persistence and failure behavior"); bullets(["Local twin SQLite: patients, twins, observations, snapshots, events, risk predictions, simulations, model metadata.","Edge outbox SQLite: unsent immutable envelopes plus successful-sync audit.","Cloud SQLite demo: idempotent messages indexed by patient_key and observed time.","Offline behavior: local synchronization continues; outbound messages queue; flush retries in chronological order.","Duplicate behavior: cloud INSERT OR IGNORE on message_id makes retransmission idempotent."])
    h1("8. Dashboard simplification"); p("The former Twin Architecture page is replaced by Cloud & Edge, which combines live service health, queue depth, sync count, deployment boundary, and architecture. Data & Provenance and Model Lab are merged into Evidence Lab tabs. This removes redundant navigation while preserving scientifically important evidence. Command Center, Live Twin, State Explorer, Risk & Explainability, What-If Lab, Cloud & Edge, and Evidence Lab remain.")
    h1("9. Verification"); bullets(["Unit tests cover initialization, validation, state transitions, history, event generation, features, persistence, and scenario isolation.","Cloud tests verify sync acceptance, latest-state retrieval, fleet aggregation, offline buffering, and absence of raw patient IDs in outbound JSON.","Dashboard AppTest renders all seven pages and runs a what-if scenario without mutating the actual twin.","The full stack is smoke-tested with the FastAPI service on port 8000 and Streamlit on port 8501."])
    h1("10. Deployment guide"); p("Development uses two processes so edge and cloud failure modes are observable. Start the cloud boundary with python scripts/run_cloud.py, then start the edge/dashboard with python -m streamlit run app.py. The edge target defaults to http://127.0.0.1:8000. A deployment can replace this URL with a TLS endpoint while retaining the same envelope and retry behavior.")
    h2("Production hardening required"); bullets(["Mutual TLS or signed service credentials per edge site.","Secret-managed HMAC or tokenization instead of a code-default salt.","Managed database with encryption, backups, retention policy, and row-level access control.","Schema versioning, dead-letter queues, observability, rate limits, and disaster recovery.","Clinical governance, external validation, safety case, and regulatory assessment."])
    h1("11. Scientific and ethical limitations"); p("This system is a research and educational prototype. It is not a medical device and has no clinical validation. The cloud service does not change that status. Synthetic replay is a demonstrative time-indexed stream around an observed baseline, not real telemetry. The anomaly score, instability metric, forecast, and uncertainty layer are prototype methods. No output should diagnose, prescribe, triage, or manage a patient.")
    story.append(PageBreak())
    h1("12. Traceability"); trace=[["Concern","Implementation"],["Twin state","src/twin/state.py, patient_twin.py"],["Synchronization","src/twin/synchronizer.py"],["Edge outbox","src/edge/gateway.py"],["Cloud API","src/cloud/service.py"],["Persistence","src/twin/repository.py"],["Dashboard","app.py, src/ui"],["Dataset audit","reports/DATASET_AUDIT.md"],["Model evidence","reports/MODEL_EVALUATION.md"],["Tests","tests/"]]
    table=Table(trace,colWidths=[2.0*inch,4.8*inch],repeatRows=1); table.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,0),colors.HexColor("#0b5f59")),("TEXTCOLOR",(0,0),(-1,0),colors.white),("GRID",(0,0),(-1,-1),.35,colors.HexColor("#b7c7ca")),("FONTSIZE",(0,0),(-1,-1),8)])); story += [table]
    def page(canvas,doc):
        canvas.saveState()
        if doc.page == 1:
            canvas.setFillColor(colors.HexColor(NAVY)); canvas.rect(0,0,A4[0],A4[1],fill=1,stroke=0)
            footer = colors.HexColor("#9bb0b5")
        else:
            footer = colors.HexColor("#60777d")
        canvas.setFont("Helvetica",7); canvas.setFillColor(footer); canvas.drawString(36,22,"CRITICALCARE-TWIN | Cloud-edge architecture report"); canvas.drawRightString(A4[0]-36,22,f"Page {doc.page}"); canvas.restoreState()
    doc=BaseDocTemplate(str(OUT),pagesize=A4,rightMargin=36,leftMargin=36,topMargin=38,bottomMargin=34,title="CRITICALCARE-TWIN Cloud-Edge Architecture")
    frame=Frame(doc.leftMargin,doc.bottomMargin,doc.width,doc.height,id="normal")
    doc.addPageTemplates([PageTemplate(id="main",frames=frame,onPage=page)])
    doc.build(story)
    print(f"Wrote {OUT}")


if __name__ == "__main__": build()
