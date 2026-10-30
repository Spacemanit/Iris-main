# Iris: a defensible research and publication strategy

Prepared 7 October 2026. Planning window: approximately two weeks, through 21 October 2026. This is a research advisory dossier, not a completed systematic review or a report of experiments. No new performance measurements or participant results were collected. Sources are linked at the claims they support; bibliographic entries are in `iris_references.bib`.

**Reading update, 13 October 2026:** concise, current research summaries are in `01_Novelty_and_Literature.md`, `02_Review_Standards_and_Risks.md`, and `03_Course_Submission_Strategy.md`. The date above was an approximate planning assumption, not a confirmed deadline. The longer agenda below includes optional work beyond the clarified submission-focused objective.

## Revised practical objective after the student's clarification

The immediate objective is a teacher-approved manuscript and genuine proof of submission within approximately two weeks. The student expects the course to end in about two months and considers later rejection an acceptable outcome. Acceptance and public publication are not the immediate target. The more ambitious research agenda below is optional background, not required work for this revised objective.

Prepare a modest focused narrative review, provisionally titled **A Focused Literature Review of Gaze and Visual Feedback in Low-Cost Interactive Companions**. Use established literature to compare face-position tracking, gaze behavior, visual processing feedback and implementation trade-offs. Describe Iris briefly as a course prototype motivating those choices. Claim a comparative synthesis only to the extent the completed paper provides one. No new algorithm, benchmark, human experiment or artificial novelty claim is needed for this manuscript format. Check that the chosen outlet actually accepts unsolicited reviews.

Practical deliverables: a readable manuscript following the selected venue's format, roughly 12–18 relevant references as a workload estimate, a checked comparison table, teacher approval, and the authentic submission acknowledgement/manuscript ID. Label the status **submitted** or **under review**, as appropriate. Submission does not establish acceptance or publication. Do not fabricate a submission, acceptance, result, or bibliography entry. Submit a coherent manuscript in good faith to a legitimate in-scope outlet; expected rejection is a possible outcome, not a result to manufacture.

### Google Scholar exposure

Google Scholar's official inclusion guidance concerns discoverable scholarly web content and requires accessible full text or an author-written abstract. It includes preprints and technical reports as well as journal articles. From these requirements, an ordinary private submission behind a journal's login does not itself generate a publicly crawlable Scholar entry. Rejection likewise does not by itself create such an entry. This conclusion assumes the outlet does not publicly post submissions and no public version has been posted elsewhere. Check for optional or automatic preprint posting when submitting. [Google Scholar inclusion guidance](https://scholar.google.com/intl/en/scholar/inclusion.html).

For the submission-only objective, keep the manuscript in the course submission system and the journal's private editorial system. A public Zenodo deposit, preprint posting or institutional repository deposit would create public exposure and therefore is not the default route. Public publication in a weak outlet could raise reputational concerns; the effect is evaluator-dependent. Deleting a profile entry does not erase a paper from the underlying Scholar index or from its publisher. [Google Scholar profiles](https://scholar.google.com/intl/en/scholar/citations.html).

The earlier repository-publication recommendation below addressed a different objective: guaranteeing a public citable output by the deadline. It is superseded for this submission-only plan. After an editorial decision, accurately report rejection or acceptance; if accepted, review the publication terms and discuss whether to proceed. Do not assume rejection, a particular review duration, or that every outlet separates submission from permission to publish.

## Earlier research recommendation — optional longer-term direction

Write a focused critical narrative review of **temporal responsiveness in low-cost embodied conversational interfaces**, using Iris as a motivating implementation. If time permits, add a separate, modest engineering benchmark of camera-data freshness during speech and language-model processing. Keep publication logistics separate from scientific claims.

Suggested review title:

**From Frame Rate to Responsive Attention: A Critical Review of Gaze, Processing Feedback, and Information Freshness in Low-Cost Embodied Assistants**

Suggested experimental title, only after collecting results:

**Measuring Visual-Attention Freshness in an ESP32 Display Companion During Local Speech and Language Inference**

The contribution can be a useful synthesis, a reporting framework, or evidence about a particular constrained system. It need not be a new face detector, language model, or robot category. But neither a synthesis nor a benchmark is automatically novel: the final paper must show exactly how it differs from the closest work.

The most promising question is: **What should designers measure and preserve when a companion appears animated but its visual reactions may be driven by stale camera information?** A display can continue blinking smoothly while its target position is old. Display animation rate, face-detection runtime, camera-to-control delay, response-onset delay, and the age of the information currently driving the display describe different properties.

## What Iris actually implements

The inspected source is more specific, and more defensible, than the original PRD:

| Aspect | Evidence in the workspace | Publication implication |
| --- | --- | --- |
| Hardware baseline | `SPEC.md` and hardware findings identify AI-Thinker ESP32-CAM, OV3660 and ST7735S 128×160 | Use the actual build, not the earlier OV2640/ST7789 shopping list |
| Visual sensing | `iris/vision.py` uses an OpenCV Haar face detector and the largest face bounding box | Describe face-position tracking. It does not estimate a person's eye-gaze direction or identify who is speaking |
| Display behavior | Firmware maps normalized position to pupil offsets of approximately ±10 pixels; renders expressions and blinking | Rendered gaze is a visual cue. Directional legibility and perceived eye contact remain untested |
| Compute location | Host runs vision and optional Whisper/Ollama/Coqui adapters | Describe a host-assisted embedded interface; record which models and hardware actually ran |
| Current audio path | The 13 October specification enables device microphone/speaker defaults, with laptop fallbacks; replacement hardware operation still needs confirmation | Host compute remains part of the system; distinguish configured audio from physically verified operation |
| Queue handling | `iris/server.py` retains one waiting frame and replaces it with newer input | This is an existing implementation feature that can be evaluated |
| Sender pacing | Firmware responds to `frame_ack` changes, normally permits one outstanding frame, and has a five-second probe fallback | Application pacing is present, but counters are not a complete timestamp/sequence tracing mechanism |
| Concurrency | Firmware separates network/capture from drawing; host sends vision and voice work to threads | Concurrency is implemented. Resource isolation and responsiveness must still be measured |
| Smoothing | Host uses a fixed coefficient per detected frame; device smooths per drawing iteration | Changing update rates changes the effective smoothing response |
| Measurements | Host records tracking duration and counters | Existing logs do not establish camera-to-pixel latency, data age, power, social presence, or clinical benefit |

The user reports that the assembled project works. The inspection here verifies implementation choices, not physical performance. Older documents contain stale hardware and integration notes; confirm the final build configuration when writing its methods.

## Correct the old literature claims before presenting them

`iris-prd.md` has numbered markers such as [29]–[47] without matching numbered reference entries. Its short appendix names real topics but is not a usable bibliography. Rebuild citations from the papers themselves.

| Old claim | Evidence check | Defensible wording |
| --- | --- | --- |
| Dynamic pupils defeat the Mona Lisa effect | Jung et al. used a rendered 3D virtual human, a 65-inch display and added virtual-camera rotation. This is not the Iris cartoon-pupil implementation | Directional gaze on flat displays presents perceptual challenges; Iris's cues require their own evaluation |
| Social gaze research proves inexpensive displays outperform mechanical systems | Admoni and Scassellati organize social-gaze research into human-, design- and technology-centered approaches. Their review is not a universal cost/performance superiority result | Social-gaze literature motivates explicit behavioral and perceptual evaluation |
| GazeGrasp establishes social-companion performance | Its ESP32 eye-tracking interface controls robotic grasping, a different task | It is adjacent implementation evidence, not evidence of Iris's social effectiveness |
| Sub-₹1500 AI companion | The old BOM does not establish final receipts or include host compute | Report device BOM, complete deployment requirements and reused-host assumptions separately |
| Under-200-ms gaze response / 30 FPS / under-5-ms drawing | These are targets in the documents, not results from this investigation | Label targets and report observed distributions separately |
| Thinking pupils demonstrate cognition | A rendered state is not a measurement of the user's cognition or the machine's mental state | Describe a visual processing-status cue |
| Reduces loneliness, anxiety, or improves classroom learning | No such study is available for Iris | Omit outcome claims; name possible future studies only if relevant |

Relevant primary sources: [Jung et al., 2023](https://ceur-ws.org/Vol-3467/paper4.pdf), [Admoni and Scassellati, 2017](https://publications.ri.cmu.edu/social-eye-gaze-human-robot-interaction-review), and [GazeGrasp, 2025 preprint](https://arxiv.org/abs/2501.07255).

## Closest work and what it means for novelty

These are verified seed references, not a completed exhaustive corpus. Full-text sections were inspected where available; access limitations are stated. Do not infer that an unmentioned feature is absent from a paper.

| Work | Relevant evidence | Consequence for Iris |
| --- | --- | --- |
| Admoni & Scassellati (2017), social-gaze review | Established organization of gaze research; institutional abstract and metadata checked | A general review of why robot eyes matter would add little |
| Al Moubayed, Edlund & Beskow (2012), *Taming Mona Lisa* | Studies gaze interpretation on 2D and 3D projection surfaces; full text available | Gaze appearance and observer viewpoint require evaluation |
| Jung, Kum & Lee (2023), *Breaking the Mona Lisa Effect* | Added visual-camera rotation improves directional judgments in its virtual-human setup | Simple tracking does not inherit this finding |
| Andrist et al. (2014), conversational gaze aversion | NAO study of purposeful gaze aversion, with 30 participants | Constant face following is not a complete conversational-gaze policy |
| Shiwa et al. (2009), response timing | Studies robot response delays and conversational fillers; institutional abstract checked | Fast visible acknowledgement and final spoken answer should be considered separately |
| Axelsson, Buschmeier & Skantze (2022), feedback review | Covers feedback in speech, gaze, gestures and facial expressions | Processing indicators belong to a broader communication problem |
| Yates et al. (2021), AoI survey | Formal literature on freshness of timestamped updates and queueing | Frame rate and low processing time are insufficient measures of freshness |
| Sun et al., *Update or Wait* | Acknowledgement-like zero-wait updating is not universally age-optimal; author preprint checked | Do not label Iris's pacing policy theoretically optimal |
| Hessels & Fang (2026), perceptual perspective | Distinguishes gaze functions and perceptual/individual limits | Face position should not be equated with attention or social understanding |
| Neuber et al. (2026), *Eyes ahead* | Explicitly identifies inadequate response-time and implementation reporting in robotic gaze following | Provides an independently documented reporting problem, in an adjacent setting |
| Rutatola et al. (2026), low-cost educational robot review | Reviews 34 designs and affordability choices | Avoid a broad new survey of inexpensive social robots |
| Wang et al. (2026), LLM-HRI review | Reports heterogeneous methods across 86 included articles; abstract and publisher search text checked | Avoid an equally broad review of LLMs in social robots |
| Kang et al. (2026), *Fluid-Xpress* | Already decouples nonverbal feedback from LLM processing; published short paper and methods checked | Fast/slow separation itself is not an invention of Iris |
| FluxGarage RoboEyes; XiaoZhi ESP32 | Public repositories already implement expressive eyes and ESP32 conversational/display capabilities | Treat these as practical prior art, not peer-reviewed social-effectiveness evidence |

Primary links: [Taming Mona Lisa](https://www.lri.fr/~anab/teaching/evaluation/papers/AlMoubayed2012_MonaLisaEffect.pdf), [gaze aversion](https://pages.cs.wisc.edu/~bilge/pubs/2014/HRI14-Andrist.pdf), [response timing](https://doi.org/10.1007/s12369-009-0012-8), [feedback review](https://doi.org/10.3389/fcomp.2022.744574), [AoI survey](https://user.eng.umd.edu/~ulukus/papers/journal/aoi-survey.pdf), [Update or Wait](https://arxiv.org/abs/1601.02284), [perceptual perspective](https://doi.org/10.3758/s13423-026-02902-x), [Eyes ahead](https://doi.org/10.3389/frobt.2025.1723527), [low-cost robot review](https://doi.org/10.3389/frobt.2026.1827676), [LLM-HRI review](https://arxiv.org/abs/2602.15063), [Fluid-Xpress](https://shura.shu.ac.uk/37180/1/Ma-Fluid-XpressEmotion-Aware%28VoR%29.pdf), [RoboEyes](https://github.com/FluxGarage/RoboEyes), [XiaoZhi](https://github.com/78/xiaozhi-esp32).

Important scope distinction: *Eyes ahead* addresses following the user's gaze toward objects, whereas Iris follows face position. Its reporting criticism motivates checking timing in Iris; it does not prove that the same gap exists throughout the specific low-cost display-companion literature. Its abstract and conclusion also differ in their study counts; avoid copying a count without resolving that discrepancy.

## Where a contribution is plausible

### 1. Critical review plus an evaluation framework — recommended

Bring together three specific questions: what the gaze/feedback behavior communicates, how it is perceived on a small display, and how current the sensor information remains during concurrent computation. Build an evidence matrix that separates those questions. The synthesis is useful if it shows why metrics often called “responsiveness” cannot be compared directly.

Suggested review questions:

1. Which capabilities are being evaluated: face following, human gaze estimation, gaze-target following, or perceived eye contact?
2. What timing endpoints are reported: model runtime, command receipt, display update, first acknowledgement, or completed speech?
3. How do compute placement, queue policy and filtering affect the age of the information driving visible behavior?
4. What minimum implementation and measurement details would make inexpensive systems reproducible?

Proposed original synthesis: a reporting framework with five dimensions—**behavioral function, perceptual setup, timing endpoints, execution/queue policy, and deployment cost/reproducibility**. This framework is a proposal from this investigation. Its novelty and usefulness must be demonstrated through the selected literature, not asserted from its name.

The final review should deliver a completed comparison table, explicit limits on transferring results between embodiments, and an actionable measurement protocol. A sequence of unrelated paper summaries is not enough.

### 2. Reproducible systems benchmark — strongest practical extension

Question: Under shared-host load, what are the trade-offs among continuous streaming, dropping old waiting frames, and acknowledgement-paced streaming?

This is an application/measurement contribution using established ideas. It becomes valuable through transparent measurement, fair baselines and reusable artifacts, even if no new algorithm emerges. A null or mixed result is legitimate; do not promise improvement before running it.

### 3. Small-display gaze perception — plausible, poor fit for the deadline

Question: Can observers distinguish intended pupil directions on the actual 128×160 cartoon face at specified distances and viewing angles?

A controlled comparison of pupil-only motion against an additional orientation cue could be relevant. It requires a justified experimental design, institutionally appropriate participant procedures and adequate uncertainty reporting. It should not be replaced by asking a few friends whether the device feels alive. This is a later project, not the dependency for the two-week review.

### Features that do not establish novelty by themselves

Adding emotion recognition, conversational memory, an LLM, Hinglish, another sensor, or “privacy” to the title does not establish a new research contribution. Each introduces its own baselines and evidence requirements. Local processing is a deployment property to document; it does not establish a complete privacy guarantee.

## A review method feasible for this team

Call the paper a **critical narrative review with a documented search**, unless you actually complete the stronger procedures needed for a systematic or scoping review. SANRA offers useful narrative-review checks—purpose, search description, referencing, evidence reasoning and endpoint data—but was developed in medical publishing; use it as writing guidance, not as a robotics validation standard. [SANRA](https://doi.org/10.1186/s41073-019-0064-8).

Use separate searches rather than requiring every paper to mention every theme:

- `(social robot OR embodied conversational agent OR virtual agent) AND (gaze OR eye contact OR nonverbal feedback) AND (latency OR timing OR response time)`
- `(low-cost OR affordable OR ESP32 OR Arduino OR Raspberry Pi) AND (companion OR social robot OR conversational interface) AND (display OR eyes OR gaze)`
- `(age of information OR information freshness) AND (vision OR status update OR queue OR edge computing)`
- `(language model OR LLM) AND (robot OR embodied agent) AND (latency OR asynchronous OR nonverbal)`

Search accessible IEEE/ACM records, Google Scholar and author/institutional repositories. Use Scopus/Web of Science only if the team really has access and actually searches them. Record database/interface, exact query, search date, date/language restrictions and any stopping rule. Treat Google Scholar results as ranked discovery, not an exhaustive reproducible census. Check cited and citing work from the seed references.

Include work that informs gaze perception/behavior, response feedback, timestamped-update freshness, or the relevant low-cost architecture. Maintain separate labels for empirical studies, reviews, theoretical papers, preprints and maker repositories. Exclude unrelated industrial eye-guided control from the core synthesis; GazeGrasp can remain adjacent background. For inaccessible full texts, record the limitation and avoid detailed methods claims.

Plan for roughly 15–25 genuinely relevant scholarly sources if the search supports that scope; this is a workload estimate, not an acceptance threshold or a fabricated inclusion count. Keep the seed list small enough to read properly. Deduplicate versions of the same paper.

For each included work record: citation; evidence type; embodiment/display; sensed quantity; gaze/feedback function; compute placement; temporal metric and endpoints; clock method; queue/filter policy if reported; concurrent workload; evaluation setup; uncertainty; deployment-cost boundary; code/material availability; and one transferable finding plus one limitation. Use **not reported in inspected full text**, **not applicable**, and **not verified** distinctly. Have a second teammate check critical claims and a subset of extraction rows, and describe what they actually checked.

Suggested paper structure: introduction and narrow question; search and selection method; terminology; perceptual/behavioral evidence; temporal and architectural evidence; cross-paper synthesis; proposed reporting framework; Iris as an illustrative case; limitations; conclusion. Keep the prototype to a modest portion of the review. Do not present planned experiments as completed evidence.

## Optional benchmark specification

### Fair comparisons

Compare three policies on the same hardware, input resolution, detector, smoothing, transport and nominal capture-rate limit:

| Policy | Definition |
| --- | --- |
| A: continuous bounded FIFO | Fixed-rate sender; a declared finite waiting queue with an explicit overflow policy |
| B: continuous latest frame | Same sender; one waiting frame overwritten by newer arrivals |
| C: paced latest frame | Iris's application acknowledgement pacing plus latest-frame retention |

A alone is a weak baseline. B is needed to distinguish sender pacing from an ordinary latest-frame fix. A reasonable small FIFO is sufficient; an unlimited queue creates an artificial straw man. Document upstream camera buffers, WebSocket/TCP buffering, rejected frames and reconnect behavior. TCP retransmissions and buffering remain possible even when the application queue has one slot.

Run each policy with warmed models under: vision only; vision plus actual STT/LLM/TTS workload; and a declared controlled processing-delay stress condition. Keep artificial delay results separate from real inference results. Use about five independent 60–120-second runs per condition as an initial engineering characterization, randomize order, and log model settings, host CPU/GPU, memory, network and camera configuration. This number is a practical pilot plan, not a claim of statistical power.

### Measure the right thing

Add a session identifier, frame sequence number and source timestamp for evaluation, and echo them in controls. This is proposed instrumentation, not existing telemetry. Verify what a camera-driver timestamp denotes; exposure start, capture completion and upload start are not interchangeable.

Define target-information age at device time `t` as `t - source_timestamp_of_latest_applied_target`. Measure it continuously or reconstruct its time-weighted history, including periods with no new updates. Its mean/p95, peak age and time above predeclared diagnostic thresholds can expose staleness that average FPS misses. A 200-ms threshold can be an engineering target, but is not an established universal human-perception limit.

Return the device's original timestamp and subtract on that same device clock after applying the corresponding control. This avoids subtracting unsynchronized host and ESP32 clocks. Host receive-to-detect and detect-to-send durations can be measured separately on the host's monotonic clock. Use session IDs and address rollover/reconnects. Returning a control is not proof that pixels have changed.

Track control adoption and display-transfer completion separately. Pupil smoothing mixes successive targets, so label information age as the age of the target commanding the renderer; it is not a complete account of the rendered pupil's trajectory. Measure motion response/settling separately, preferably with repeatable visual input and external video of input and display in the same view. Phone slow-motion has finite timing resolution and may have variable frame timing; state the actual method and uncertainty.

The existing `tracking_ms` starts after the host dequeues a frame. It excludes earlier camera/network/queue delay, outbound control delivery and drawing. It cannot support an end-to-end latency claim.

Also report fresh-target update rate; fraction and reason of drops; invalid frames; host load; and useful-motion error or response lag. Define a no-face policy and separately count failed detections. At stationary targets, an unchanged LCD image need not be retransferred; distinguish drawing-loop frequency, physical screen transfer rate and new target-information rate.

Summarize by independent run, retain raw timing logs, and show dispersion/intervals. Thousands of adjacent frames are not thousands of independent experimental replicates. Do not report simulated logs as hardware measurements or translate timing gains into engagement gains without a separate human study.

A narrow optional extension is to compare fixed-per-update smoothing with elapsed-time filtering, `alpha = 1 - exp(-dt/tau)`, at a matched nominal time constant. This is established filter mathematics, not a novel invention. It may expose a meaningful rate-dependence trade-off, but prioritize the main benchmark first.

## What other students report doing

The accounts below are self-reported community evidence, not representative surveys, verified institutional policies, or proof of your teacher's motives.

- A student with an AI voice-assistant project describes being required to publish despite seeing no invention in the work. The thread includes suggestions to find a narrower contribution and seek faculty help; the original poster later says they intend to publish. It does **not** verify an eventual publication. [Student voice-assistant account](https://www.reddit.com/r/india/comments/136rs28/college_forcing_to_publish_final_year_project_as/).
- A B.Tech student reports submission-confirmation requirements for marks and insufficient research training, despite doing literature reading, experiments and analysis. This shows why checking the exact assessed milestone matters. [Submission/marks account](https://www.reddit.com/r/IndianAcademia/comments/1qblori/is_it_normal_for_undergrad_students_to_be/).
- A Pune team reports pressure over IEEE publication, fees, scope and added authorship. Comments describe negotiating acceptance of other venues; some also suggest falsely reporting unsuccessful submissions. The latter is not a defensible solution. None of these comments establishes the policy of all affiliated colleges. [Pune account](https://www.reddit.com/r/pune/comments/1oxporr/our_college_is_forcing_us_to_publish_in_ieee/).

The useful adaptations are to establish the actual milestone, narrow the paper, seek concrete supervision, and use a proportionate publication outlet. Avoid buying a paper or inventing a novelty/result to satisfy a metric.

There is also published evidence of a more supportive approach: a University of Vermont engineering capstone case describes prior-art tutorials, workshops and project-specific librarian consultations, with improvements in research practices. This supports asking for specific research help rather than treating unfamiliarity with the field as a personal failure. [Sherriff & Rand, 2022](https://doi.org/10.29173/istl2598).

Ask the supervisor to make three concrete contributions: check the research question against the nearest papers, identify a suitable venue, and review the claim/evidence table. These requests move the conversation from “make it novel” to assessable work.

## Publication routes within the actual constraint

| Route | What it establishes | Fit for approximately two weeks |
| --- | --- | --- |
| Repository preprint/technical review with DOI | Public, citable manuscript; no journal peer-review claim | Most controllable route, **if the teacher explicitly counts it** |
| Institutional student journal or proceedings | Depends on the actual editorial/peer-review process | Possible only if a real issue/event is scheduled and the editor confirms suitability and timing |
| Undergraduate research journal | Genuine editorial/peer-review opportunity | Reasonable destination; acceptance/publication by the deadline is unverified |
| Specialist conference short paper | A narrow evaluated contribution | Good later target, tied to an event's deadlines and review |

Zenodo's official quick-start describes uploading, providing metadata and publishing a record with an assigned DOI. A DOI identifies the public record; it does not certify peer review. Use a truthful resource type such as preprint/report, proper authorship, a clearly labeled status and a complete checked manuscript. No upload was made in this task. [Zenodo quick-start](https://help.zenodo.org/docs/get-started/quickstart/).

One concrete journal to investigate is **Reinvention**, published at the University of Warwick. Warwick states that it accepts undergraduate research including literature reviews, is peer reviewed, charges authors no fee and normally publishes in April and October. It is a credible undergraduate-oriented possibility, not a guaranteed October or two-week slot. [Warwick's journal page](https://warwick.ac.uk/fac/cross_fac/iatl/research/reinvention/).

Its submission guidelines require an original manuscript, specify 2,000–5,000 words for research articles, and say assessed coursework is considered only after assessment is completed. They also require disclosure consistent with its AI/authorship policy. Check eligibility and ask the editor about preprint compatibility before assuming a Zenodo-first route can also go there. [Reinvention submissions](https://reinventionjournal.org/index.php/reinvention/about/submissions).

HRI's Late-Breaking Reports demonstrate that legitimate outlets exist for early-stage ideas and results, with a stated peer-review process. The linked 2026 event has already taken place; it is evidence of a publication format, not a live two-week destination. [HRI 2026 LBR](https://humanrobotinteraction.org/2026/late-breaking-reports/).

If the teacher insists on an accepted journal article within two weeks, no legitimate acceptance can be guaranteed. Obtain a concrete, suitable outlet and editorial timetable from the department rather than accepting an unspecified demand. An ISSN, DOI, Google Scholar appearance or the word “international” alone does not establish review quality. Evaluate editorial identity, actual relevant papers, stated review, transparent fees and archiving. Guarantees of acceptance or extremely short review are specifically flagged in the publishing industry's guidance. [Think. Check. Submit.](https://thinkchecksubmit.org/journals/).

## Google Scholar and reputation

A small, candid undergraduate paper is not automatically a reputational disaster. That is an assessment, not a guarantee about how every future evaluator will view it. The important distinction is between modest work that accurately states its contribution and work with unverifiable references, misleading measurements or exaggerated findings.

Google Scholar's profile documentation allows control over article updates and distinguishes profile edits from the underlying search index. Curating a profile does not erase a public publication. It also does not describe a journal-prestige score that a single student paper would “ruin.” Present a preprint as a preprint and a journal article as a journal article. [Google Scholar profile documentation](https://scholar.google.com/intl/en/scholar/citations.html).

## Fourteen-day plan

| Days | Concrete deliverable |
| --- | --- |
| 1–2 | Confirm whether DOI preprint, proceedings, submission, or accepted article counts; choose review scope and inspect nearest papers |
| 3–5 | Complete documented searches, read selected sources, deduplicate and fill extraction rows; teammate checks crucial claims |
| 6–7 | Write synthesis and reporting framework; create original tables/diagram and correct the prototype description |
| 8–10 | Optional benchmark only if instrumentation works; otherwise strengthen the review without inventing results |
| 11–12 | Supervisor reviews contribution, references and venue; verify cited claims in source text |
| 13 | Finalize abstract, manuscript, authorship, declarations and venue formatting |
| 14 | Deposit if an explicitly accepted repository route, or submit to the agreed journal/outlet; report the exact status |

If no accepted-publication route is agreed by day 2, treat that as a scheduling problem to resolve with the teacher, not a reason to manufacture scientific novelty. A complete manuscript is achievable within the window; independent editorial acceptance is outside the team's control.

## A defensible statement for the teacher

“Iris uses established sensing, rendering and language-model components. We propose a focused review of how low-cost embodied interfaces maintain timely visual attention during slower conversational processing. Our contribution will be a comparison of behavioral, perceptual and timing evidence, and a reproducible reporting framework. If time permits, we will use Iris to characterize camera-data freshness under shared-host load, with clearly defined baselines. We will distinguish implemented features, measured results and future hypotheses.”

Before external submission, the team must complete the documented corpus and evidence table. This dossier supplies a justified direction and verified starting references; it is not an already accepted paper or proof that no earlier work addresses the proposed question.
