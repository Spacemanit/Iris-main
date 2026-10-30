# Gaze and visual feedback in low-cost interactive companions: A narrative review

Eklavya Nathani, Manit Bisht, and Anis Fatema

## Abstract
Camera-equipped companions can display animated eyes and converse through speech while using a small embedded device and a separate computing host. A functioning implementation, however, leaves open how people interpret its gaze and whether its visible responses reflect current observations. This focused narrative review examines literature on social gaze, facial displays, conversational feedback, information freshness, and affordable robot design. It compares findings across projected faces, virtual humans, and embodied robots, with attention to task, representation, sample, and outcome. The synthesis separates face-position tracking from gaze estimation, target discrimination from perceived eye contact, and processing activity from evidence of understanding. It also distinguishes rendering rate, observation age, and spoken-response timing. These distinctions support a proposed reporting checklist and a research agenda for small display-based companions. Iris illustrates the implementation decisions that the checklist would expose; no new performance measurements or participant results are reported. The main unresolved questions concern miniature-display legibility, interpretation of feedback during failures, visual freshness under concurrent speech work, and complete deployment cost. Addressing these questions would support more precise design choices and claims without assuming that findings from larger robots transfer directly.


Keywords:
Human-robot interaction, social gaze, conversational feedback, information freshness, low-cost companions.


## Introduction
An interactive companion can combine a camera, a small facial display, and speech processing to respond to nearby people. Its eyes may move toward a detected face while a separate process prepares a spoken answer. This arrangement creates several evaluation problems. Detecting a face does not establish that the displayed character appears to address its owner. A processing animation does not establish that the system understood an utterance. Smooth drawing does not establish that the observation driving the eyes is current.

Admoni and Scassellati distinguish research into human responses, gaze design, and computational implementation [@admoni2017]. These categories help separate an engineering demonstration from an interaction result. The distinction matters for inexpensive companions, where a successful exchange of camera frames and display commands can be mistaken for evidence of social presence.

Related reviews already cover broad parts of this problem. Neuber et al. examine technologies for humanoid robots to follow human gaze [@neuber2026]; Rutatola et al. examine affordable educational robot designs [@rutatola2026]. The abstract of Wang et al.'s review describes heterogeneous methods and outcomes in language-model-based interaction research [@wang2026]. Together, these accounts motivate a narrower comparison of visual communication and the computing conditions that support it.

The question addressed here is which design and evaluation considerations follow from existing evidence when a low-cost companion displays an animated face while processing speech. The review connects perceptual interpretation, conversational meaning, temporal relevance, and deployment resources. Its contribution is a bounded synthesis and a proposed reporting checklist. The checklist does not introduce a new gaze algorithm or a validated measure of engagement. Iris, a host-assisted display companion, provides an illustrative application rather than experimental evidence.

## Review approach
This focused narrative review uses purposive selection. The project research dossier, existing manuscript, bibliography, and supplied review-writing guidance provided the starting material. On 13 October 2026, targeted web searches and direct retrieval from publisher websites, proceedings, and author or institutional repositories revisited those sources. Searches included `"low-cost" "companion" "gaze" display latency`, `"screen-based" robot gaze visual feedback latency`, `"age of information" vision queue latest frame`, and `"language model" robot "nonverbal" "Fluid-Xpress"`. Named-title searches resolved publication identity and versions. Ordinary web discovery was used; subscription databases were not directly searched.

Sources qualified if they informed social-gaze terminology, display interpretation, conversational feedback, update freshness, or the resource requirements of affordable companions. Empirical studies, conceptual reviews, and theoretical networking work supplied different kinds of evidence. Fifteen scholarly sources were retained, alongside two software repositories used only for implementation context. This count describes the final selection, not a systematic screening yield. Industrial gaze-controlled manipulation without a visual-communication role, publication logistics, and clinical-effectiveness claims were outside the technical synthesis.

Extraction recorded representation, task, participant sample where relevant, outcome, access level, and limits of transfer. Full-text passages supported the detailed empirical comparisons. Shiwa et al. and Wang et al. were used only at abstract level [@shiwa2009; @wang2026]. Mirror Eyes was inspected in its author-preprint version; the published metadata for Update or Wait was checked separately from its author text. The evidence ledger records these distinctions. Narrative-review checks concerning aims, search description, citations, reasoning, and endpoint data drew on SANRA [@sanra2019]. Its medical-domain origin limits its use here to editorial guidance.

No independent duplicate screening, formal risk-of-bias scoring, preregistered protocol, or quantitative pooling was performed. Source accessibility and the project question shaped selection. The findings therefore characterize the reviewed material and its transfer to small companions, rather than the prevalence of practices throughout the field.

## Capabilities and claims
### Sensing and displayed behavior
A face detector locates a face in an image. Mapping its bounding-box center to pupil offsets creates face-position tracking. Human gaze estimation instead estimates where a person is looking. Gaze following adds a mapping from that estimated direction to a target in the environment [@neuber2026]. These operations have different inputs, failure cases, and reference measurements. A camera that detects an approaching person need not resolve that person's eye direction.

Mutual gaze concerns reciprocal orientation between partners. Admoni and Scassellati distinguish it from unreciprocated face-directed gaze and from joint attention toward a shared referent [@admoni2017]. A device can therefore implement face following without establishing either mutual gaze or joint attention. Table \ref{tab:claims} associates common capability claims with the evidence they would require.

\begin{table}[t]
\caption{Capability claims and appropriate evidence}
\label{tab:claims}
\centering
\footnotesize
\begin{tabularx}{\columnwidth}{@{}p{0.30\columnwidth}Y@{}}
\toprule
Capability & Evidence required \\
\midrule
Face-position tracking & Detection and coordinate-mapping checks, including multiple faces and detection loss. \\
Human gaze estimation & Looking-direction estimates compared with an appropriate gaze reference. \\
Gaze following & Correct environmental-target identification in a defined scene. \\
Perceived eye contact & Observer judgments under specified display and viewing conditions. \\
Joint attention & An interaction task showing coordination toward a shared referent. \\
\bottomrule
\end{tabularx}
\end{table}

### Perception and attention
Hessels and Fang challenge the assumption that looking direction and visual attention are interchangeable [@hessels2026]. Their account emphasizes perceptual constraints, context, and individual differences, and explicitly limits its scope to humanoid and anthropomorphic gaze. Stylized eyes on a tiny screen require their own assessment. A conservative first question is whether observers can identify the intended target; an inference about attention or social understanding requires further evidence.

This separation also clarifies evaluation order. A participant may recognize that a character faces left without believing that it addresses a particular person. Conversely, an image may seem to make eye contact while providing poor target discrimination. Direction recognition, perceived address, and shared attention should be measured separately when a design claims more than one capability.

## Facial representation and spatial interpretation
### Geometry and additional cues
The spatial interpretation of displayed gaze depends on more than the pupil coordinates. Al Moubayed et al. compared a flat facial projection with a three-dimensional facial mask using five observers [@almoubayed2012]. The three-dimensional presentation supported more consistent interpretation of gaze in physical space. Their controlled projection geometry and small sample constrain generalization to other faces. The result provides a reason to test observer viewpoint, rather than a guarantee that adding physical depth will solve every gaze problem.

Jung et al. examined an additional rendering cue on a flat display [@jung2023]. Thirty participants judged gaze from virtual humans on a 65-inch screen at 2.4 metres. Small virtual-camera rotations improved left/right recognition in the tested narrow-angle arrangement. The character also provided body, head, and environmental information. The study tested gaze judgments without dialogue, and the broader-angle condition always preceded the narrow-angle condition. Its result consequently supports the tested cue and geometry, while leaving conversation and miniature-display transfer unresolved.

These studies address a common difficulty through different interventions. One changes the projection surface; the other changes the rendered viewpoint. Neither establishes that moving two cartoon pupils on a small panel resolves ambiguity between observers. For such a panel, the relevant comparison is whether an additional cue improves identification of the intended target at the actual viewing distance and angle.

### Referential content and task outcomes
Mirror Eyes adds reflection-like imagery of the attended region to screen eyes on an actuated robot head [@mirror2025]. In a 33-participant pick-and-place study, mirroring increased subjective information-processing awareness and enabled earlier interruption of erroneous actions. The visual intervention supplied information about a referent, rather than simply changing the realism of the eyes. Its task outcome therefore differs from gaze-direction recognition.

The distinction explains why richer rendering is not an effectiveness scale. Projection geometry can support spatial judgments; a rendering cue can distinguish nearby interlocutors; imagery can expose which object the robot has selected. These designs solve different communication problems. Mirror Eyes also involved brief exposure and a larger, moving embodiment. The reviewed evidence does not establish whether useful target imagery remains readable inside miniature eyes.

Table \ref{tab:studies} compares the selected empirical studies. The rows describe interventions and transfer limits, not a ranking. Different tasks, samples, and outcomes prevent numerical pooling into a single estimate of engagement.

\begin{table*}[t]
\caption{Selected empirical findings and limits of transfer to small display companions}
\label{tab:studies}
\centering
\footnotesize
\setlength{\tabcolsep}{5pt}
\renewcommand{\arraystretch}{1.15}
\begin{tabularx}{\textwidth}{@{}p{0.14\textwidth}p{0.23\textwidth}Y Y@{}}
\toprule
Study & Representation and sample & Relevant finding & Transfer limit \\
\midrule
Al Moubayed et al. [@almoubayed2012] & Flat and 3D facial projections; five observers. & The 3D condition supported more consistent spatial gaze interpretation. & Small sample and a particular projection geometry; miniature pixel eyes were not tested. \\
Jung et al. [@jung2023] & Virtual humans on a 65-inch screen; 30 participants. & Viewpoint rotation improved narrow-angle gaze judgments. & Constrained observer positions and no dialogue; screen scale differs from Iris. \\
Mirror Eyes [@mirror2025] & Screen eyes, actuated head, and manipulation task; 33 participants. & Mirroring supported processing awareness and earlier error interruption. & Brief exposure and task-specific imagery; small-display legibility remains open. \\
Andrist et al. [@andrist2014] & NAO conversation; 30 participants. & Timed aversion improved selected conversation measures; disclosure did not increase. & Head movement and scripted timing differ from pupil-only rendering. \\
Fluid-Xpress [@kang2026] & Dual-loop expressive robot; eight female university students. & Expression awareness increased; between-condition valence change was not significant. & Small, homogeneous pilot; no general or lasting emotional benefit follows. \\
\bottomrule
\end{tabularx}
\end{table*}

## Conversational meaning and processing feedback
### Gaze as a timed conversational action
Continuous face following is a simple orientation policy, but conversation may require changes in gaze. Andrist et al. compared appropriately timed, poorly timed, and absent gaze aversion in a 30-participant NAO study [@andrist2014]. Well-timed aversion improved thoughtfulness judgments and helped the robot hold the conversational floor. The predicted increase in disclosure, measured through response word count, did not occur. The null finding limits any interpretation that gaze aversion improves interaction uniformly.

For a display companion, the transferable point is to examine the timing and function of a movement together. A gaze shift during response preparation and the same shift during listening need not communicate the same thing. Copying an animation without its transition policy would omit part of the intervention. Whether pupil motion can express the relevant function as clearly as head movement remains an empirical question.

### Activity, understanding, and recovery
Axelsson et al. distinguish feedback about contact, perception, understanding, and attitude or acceptance [@axelsson2022]. These levels provide a useful interpretation of visible processing states. A listening animation can indicate that capture is enabled; it cannot by itself confirm successful speech recognition. A response-pending animation can indicate work in progress; it cannot confirm understanding. Designers need to specify the evidence that triggers a state and the event that ends it.

This reasoning also applies to failures. If recognition fails while a cheerful animation continues, the cue may communicate success unsupported by the system state. If processing ends through a timeout, a perpetual thinking animation leaves the user unable to distinguish delay from failure. Checking transitions, error messages, and recovery is therefore part of evaluating feedback meaning. These are design implications of the review, rather than measured outcomes of Iris.

Shiwa et al.'s abstract reports a one-second peak in spoken-response preferences in its first robot experiment and discusses conversational fillers that signal intent to respond [@shiwa2009]. This supports treating acknowledgement and substantive reply as separate events. The abstract-level evidence does not establish a universal timing threshold, and its spoken-response endpoint should not be applied to camera-driven gaze motion.

### Concurrent nonverbal and verbal work
Fluid-Xpress separates nonverbal facial reactions from verbal reasoning through concurrent processing loops [@kang2026]. Its eight-participant pilot found increased expression awareness, while the between-condition change in valence was not significant. The short encounters and homogeneous sample make the findings preliminary. Neither sustained well-being nor an end-to-end visual-latency advantage for other devices follows from them.

The architecture nevertheless establishes relevant prior work on keeping visual reactions active during language processing. A new companion should identify how its scheduling and feedback differ, then evaluate those differences. Concurrency alone does not establish independent resources: vision and speech workers can still share processor capacity, memory, and network access. The intended benefit must be measured under the workload that creates the contention.

## Temporal relevance and information freshness
### Different meanings of responsiveness
Yates et al. define Age of Information using the elapsed time since generation of the freshest delivered update [@yates2021]. Unlike throughput or individual packet delay, it describes freshness at the receiver over time. In a camera-driven interface, this distinction exposes how an animation can remain smooth while reacting to an old observation.

For a proposed companion evaluation, let $s_i$ be the source timestamp of a camera observation and $a_i$ the time its target estimate is adopted by the device. Define $j(t)$ as the index of the newest source observation represented by an adopted target at time $t$. Its target-information age is
\begin{equation}
\Delta_{\mathrm{target}}(t)=t-s_{j(t)}.
\label{eq:age}
\end{equation}
This adapts the established age concept to a renderer target. It does not fully characterize the visible pupil trajectory, because filtering can combine old and new estimates. The timestamp must also identify a declared acquisition event. Exposure start, capture completion, and upload start are different endpoints.

An observation-to-adoption delay, $a_i-s_i$, describes one delivered update. Equation \ref{eq:age} continues increasing between updates, including stalls. A useful report would therefore state delay distributions, time-weighted target age, fresh-target update rate, and the frequency of stale periods separately. Render-loop rate and actual display-transfer rate should also be distinguished. None is a direct measure of perceived responsiveness without an observer study.

### Queue policy and paced updates
Age research shows that update policy affects freshness [@yates2021]. Sun et al. demonstrate that sending a fresh update immediately after the previous delivery is not always age-optimal in their channel model [@sun2017]. Thus, acknowledgement pacing in a companion should not be described as theoretically optimal without establishing the relevant assumptions.

A latest-frame queue replaces an unprocessed observation when a newer one arrives. For position following, this can reduce the amount of outdated work waiting for analysis. It sacrifices completeness and does not remove upstream camera buffering, network waiting, or a frame already in inference. Its consequences also differ for algorithms that require a motion history. The relevant engineering question is which policy preserves useful target information under the actual workload, rather than which policy processes the most frames.

### Endpoints and clocks
Neuber et al. identify incomplete response-time reporting in the humanoid gaze-following studies they review [@neuber2026]. Their finding motivates clearer endpoints in adjacent companion evaluations without establishing a field-wide gap for every face-following display.

An evaluation should identify acquisition, host receipt, analysis completion, command adoption, and visible pixel change. Returning a source timestamp to the originating device permits an acquisition-to-adoption interval on one clock; host-stage durations can use the host's monotonic clock. Direct subtraction across device and host clocks requires synchronization or an explicit uncertainty bound. Display adoption and transfer completion still differ from observed pixel change. External video of a repeatable input and the display can supplement internal timestamps if its frame timing and resolution are documented.

## Affordability and reproducibility
Rutatola et al. describe varied computing and display arrangements across 34 educational robot designs and discuss affordability in relation to resources and continuing infrastructure [@rutatola2026]. Their review supports reporting the deployment boundary rather than applying a universal board-price threshold. A separate host may reduce the embedded device's computing requirements while moving cost, energy use, and maintenance elsewhere.

For a host-assisted companion, the device bill of materials and the complete deployment cost answer different questions. A reproducible report should name the host, required peripherals, power supply, enclosure, network, software versions, and model configuration. It should state whether the host is newly purchased, reused, or shared. This accounting supports a practical comparison of deployments; it does not imply that every prototype must include a newly purchased computer in its marginal cost.

RoboEyes documents animated eyes on OLED displays, and XiaoZhi ESP32 documents embedded conversational-device capabilities [@roboeyes; @xiaozhi]. These repositories show that expressive display and conversational components are established practical building blocks. Their documentation does not provide peer-reviewed evidence of social benefit. Including them prevents a feature combination from being treated as novelty while preserving the distinction between software availability and interaction evidence.

## Illustrative application to Iris
### Implemented design choices
The Iris specification and source inspected on 13 October 2026 describe an AI-Thinker ESP32-CAM, an OV3660 camera, and an ST7735S display with a resolution of $128\times160$ pixels. The Python host uses an OpenCV Haar detector, selects the largest detected face, and maps its center into normalized display coordinates. It does not estimate eye direction, identify a speaker, or infer emotion. The interpretation justified by this implementation is face-position tracking.

The host retains one waiting camera frame, replacing it with newer input. Firmware uses application acknowledgements to pace camera transmission and separates capture/network work from drawing. Host-side speech adapters run separately from the receive loop. Device microphone and speaker paths are enabled in the current specification, with laptop alternatives. These are implementation and configuration observations. The present review does not certify physical audio operation or measured performance.

The reporting distinctions expose several limits of the existing diagnostics. The host's tracking duration starts after a frame leaves the waiting queue; it omits earlier camera and network delay, outbound command delivery, and display change. A drawing-rate target does not measure the frequency of fresh gaze information. Fixed smoothing per update also makes the effective motion response depend on update frequency. Acquisition timestamps, frame identity, and display-application timing would be needed for the proposed age measurements.

### What an evaluation would resolve
The literature supports using Iris to test specific claims rather than assigning it social benefits from its architecture. A target-discrimination task would establish whether the actual pupil motion communicates whom the device addresses. A state-identification task would test the meanings of listening, processing, playback, and failure cues. Instrumented workload comparisons would characterize visual freshness during speech processing. None has been completed in this review, and the historical latency and cost figures in the project planning documents remain targets rather than results.

## Evidence gaps and a research agenda
### Where transfer remains uncertain
The selected literature is sufficient to identify design considerations, but it is incomplete for validating the miniature-display implementation. The following gaps refer to this corpus and the evidence needed for Iris. They do not establish that no relevant work exists elsewhere. Table \ref{tab:gaps} pairs each uncertainty with research that would resolve it and the design decision it would inform.

The clearest perceptual gap is scale. Projection masks, large virtual-human displays, and actuated heads establish representation-dependent results [@almoubayed2012; @jung2023; @mirror2025]. They do not establish the direction-recognition accuracy of a $128\times160$ cartoon face. Controlled judgments at specified distances and off-axis positions would reveal where its pupil offsets remain legible. Comparing pupil-only motion with an extra orientation cue would test whether additional rendering earns its complexity.

A second gap concerns interpretation during incomplete or failed processing. Conversational-gaze and feedback research show why function and timing matter [@andrist2014; @axelsson2022]. However, the proposed Iris states have no observer validation. Scripted successful and failed utterances could test state recognition, inappropriate success inference, and the ability to recover. Such research would determine which states require a clearer animation or a spoken explanation.

The engineering gap is the relationship between concurrent workload and current visual behavior. Fluid-Xpress provides an architectural precedent, while information-age work supplies a timing concept [@kang2026; @yates2021; @sun2017]. Neither supplies measurements for the Iris hardware and network. A timestamped benchmark could compare continuous bounded first-in-first-out processing, continuous latest-frame processing, and paced latest-frame processing. Holding the detector, resolution, smoothing, transport, and capture ceiling constant would distinguish the effect of pacing from ordinary frame replacement. Vision-only, actual speech-processing, and separately labeled artificial-delay conditions would show where each policy helps or harms.

\begin{table*}[t]
\caption{Evidence gaps in the reviewed corpus and research that would inform Iris}
\label{tab:gaps}
\centering
\footnotesize
\setlength{\tabcolsep}{5pt}
\renewcommand{\arraystretch}{1.15}
\begin{tabularx}{\textwidth}{@{}p{0.16\textwidth}Y Y Y@{}}
\toprule
Area & Unresolved evidence & Research and outcome & How the result would help \\
\midrule
Small-display gaze & Transfer of larger-face results to tiny cartoon eyes. & Controlled target judgments across distance and angle; accuracy and confusion by condition. & Choose pupil offsets, extra orientation cues, and a justified viewing range. \\
State interpretation & Whether users distinguish input capture, processing, playback, and failure. & Scripted successful and failed interactions; state recognition and recovery success. & Map visible cues to observable events and expose misunderstood transitions. \\
Visual freshness & Observation age and motion response during concurrent speech work. & Matched queue/pacing baselines; source-to-display delay, target age, drop rate, and settling response. & Select scheduling and buffering on measured trade-offs, without assuming pacing is optimal. \\
Complete affordability & Cost and resource needs when the host and peripherals are counted. & Reproducible component inventory and workload/resource measurements, with reuse assumptions. & Separate marginal device cost from a repeatable standalone deployment. \\
Repeated use and diverse users & Persistence of benefits and variation outside brief laboratory encounters. & Repeated-session comparisons with defined interaction outcomes and justified recruitment. & Test sustained utility and reveal whose needs the visual policy fails to meet. \\
\bottomrule
\end{tabularx}
\end{table*}

### Reporting and priorities
Five reporting fields would make these studies easier to interpret. The behavioral field identifies the sensed quantity and the gaze or feedback function. The perceptual field specifies display geometry, cue size, observer positions, and task. The temporal field names endpoints, clocks, and delay or age statistics. The execution field describes buffers, filtering, dropped observations, compute placement, and concurrent workload. The deployment field gives the cost boundary and the materials needed to reproduce the system. These fields are a proposal from this synthesis, not an externally validated standard.

Timing summaries should treat independent runs as experimental units and preserve variation across runs. Adjacent frames share system state and should not be counted as independent replicates merely because many were logged. Reports should also distinguish detection loss, discarded waiting frames, invalid input, and stalled display updates. An engineering threshold may define a diagnostic target, but a universal human-perception limit would require separate evidence.

For Iris, the first priorities are miniature-display discrimination, feedback interpretation, and a basic timestamped workload benchmark. They address claims closest to the implementation. Repeated-use studies and comparisons across cultural, age, or accessibility needs would then test broader transfer. Brief laboratory results and the conceptual cautions about individual variation justify these questions [@mirror2025; @kang2026; @hessels2026]; they do not justify an existing claim of improved learning, reduced loneliness, or therapeutic effectiveness.

## Limitations
Purposive selection and accessible English-language material limit coverage. Two sources supplied only abstract-level evidence, and inspected author versions remain explicitly identified. The empirical studies differ in embodiment, task, sample, and outcome, so the synthesis cannot estimate a common effect size. Reviews provide context and conceptual distinctions rather than direct evidence for Iris. The suggested information-age adaptation concerns a renderer target, and smoothing limits its correspondence to visible motion. The reporting checklist and proposed studies have not been validated. No new participant, timing, cost, or power data were collected.

## Conclusion
The reviewed literature supports evaluating small companions through distinct claims about gaze interpretation, feedback meaning, visual freshness, and deployment resources. Geometry and added cues affect particular spatial judgments; timed gaze behavior affects particular conversational measures; update policy affects the freshness of observations. These results support specific design questions while limiting transfer between systems.

For Iris, the next research step is to connect its face-position tracking and display states to defined perceptual and temporal outcomes. Small-display judgments would establish a usable viewing range, failure-inclusive feedback tests would clarify state meanings, and timestamped workload comparisons would expose stale visual responses. Until those measurements exist, the project provides a concrete integration setting and the review provides a reasoned evaluation agenda.

## Data availability and AI assistance
No original experimental data were generated. The accompanying evidence ledger and search log document the review sources and extraction decisions. Codex by OpenAI assisted literature discovery, source extraction and comparison, organization, prose drafting, and LaTeX formatting across the manuscript. It did not generate participant observations or performance measurements.

## References

- **admoni2017**: H. Admoni and B. Scassellati, "Social eye gaze in human-robot interaction: A review," *Journal of Human-Robot Interaction*, vol. 6, no. 1, pp. 25--63, 2017. https://doi.org/10.5898/JHRI.6.1.Admoni.

- **neuber2026**: L. Neuber, W. Culemann, R. M. Ingendoh, and A. Heine, "Eyes ahead: A scoping review of technologies enabling humanoid robots to follow human gaze," *Frontiers in Robotics and AI*, vol. 12, Art. no. 1723527, Jan. 2026. https://doi.org/10.3389/frobt.2025.1723527.

- **rutatola2026**: E. P. Rutatola, F. C. Msonge, R. Proesmans, K. Stroeken, and T. Belpaeme, "Low-cost social robot designs for education: A review," *Frontiers in Robotics and AI*, vol. 13, Art. no. 1827676, 2026. https://doi.org/10.3389/frobt.2026.1827676.

- **wang2026**: Y. Wang, Y. Xu, A. Nikolova, Y. Wang, J. Wang, C. Wang, and X. Tong, "How do we research human-robot interaction in the age of large language models? A systematic review," author preprint, arXiv:2602.15063v1, 2026. [Online]. Available: https://arxiv.org/abs/2602.15063v1. Related publication: https://doi.org/10.1145/3772318.3790920.

- **shiwa2009**: T. Shiwa, T. Kanda, M. Imai, H. Ishiguro, and N. Hagita, "How quickly should a communication robot respond? Delaying strategies and habituation effects," *International Journal of Social Robotics*, vol. 1, no. 2, pp. 141--155, 2009. https://doi.org/10.1007/s12369-009-0012-8.

- **sanra2019**: C. Baethge, S. Goldbeck-Wood, and S. Mertens, "SANRA---a scale for the quality assessment of narrative review articles," *Research Integrity and Peer Review*, vol. 4, Art. no. 5, 2019. https://doi.org/10.1186/s41073-019-0064-8.

- **hessels2026**: R. S. Hessels and Y. Fang, "A visual perceptual perspective on gaze in social robotics," *Psychonomic Bulletin & Review*, vol. 33, Art. no. 131, 2026. https://doi.org/10.3758/s13423-026-02902-x.

- **almoubayed2012**: S. Al Moubayed, J. Edlund, and J. Beskow, "Taming Mona Lisa: Communicating gaze faithfully in 2D and 3D facial projections," *ACM Transactions on Interactive Intelligent Systems*, vol. 1, no. 2, Art. no. 11, 25 pp., Jan. 2012. https://doi.org/10.1145/2070719.2070724.

- **jung2023**: S. Jung, J. Kum, and M. Lee, "Breaking the Mona Lisa effect: Enhancing eye contact with virtual humans in 2D display environments," in *Proc. 15th Asia-Pacific Workshop on Mixed and Augmented Reality*, *CEUR Workshop Proceedings*, vol. 3467, 2023. [Online]. Available: https://ceur-ws.org/Vol-3467/paper4.pdf.

- **mirror2025**: M. Kr\"uger, D. Tanneberg, C. Wang, S. Hasler, and M. Gienger, "Mirror Eyes: Explainable human-robot interaction at a glance," author preprint, arXiv:2506.18466v1, 2025. [Online]. Available: https://arxiv.org/abs/2506.18466v1. Related RO-MAN publication: https://doi.org/10.1109/RO-MAN63969.2025.11217810.

- **andrist2014**: S. Andrist, X. Z. Tan, M. Gleicher, and B. Mutlu, "Conversational gaze aversion for humanlike robots," in *Proc. ACM/IEEE International Conference on Human-Robot Interaction*, 2014, pp. 25--32. https://doi.org/10.1145/2559636.2559666.

- **kang2026**: C. Kang, M. Alitai, Y. Wang, X. Cai, R. Ma, A. Cangelosi, and Z. Shangguan, "Fluid-Xpress: Emotion-aware dual-loop framework for empathic facial reaction in HRI," in *Companion Proc. 21st ACM/IEEE International Conference on Human-Robot Interaction*, 2026, pp. 425--429. https://doi.org/10.1145/3776734.3794429.

- **axelsson2022**: A. Axelsson, H. Buschmeier, and G. Skantze, "Modeling feedback in interaction with conversational agents---a review," *Frontiers in Computer Science*, vol. 4, Art. no. 744574, 2022. https://doi.org/10.3389/fcomp.2022.744574.

- **yates2021**: R. D. Yates, Y. Sun, D. R. Brown III, S. K. Kaul, E. Modiano, and S. Ulukus, "Age of information: An introduction and survey," *IEEE Journal on Selected Areas in Communications*, vol. 39, no. 5, pp. 1183--1210, 2021. https://doi.org/10.1109/JSAC.2021.3065072.

- **sun2017**: Y. Sun, E. Uysal-Biyikoglu, R. D. Yates, C. E. Koksal, and N. B. Shroff, "Update or wait: How to keep your data fresh," *IEEE Transactions on Information Theory*, vol. 63, no. 11, pp. 7492--7508, 2017. https://doi.org/10.1109/TIT.2017.2735804. Author version: https://arxiv.org/abs/1601.02284v9.

- **roboeyes**: FluxGarage, "RoboEyes," software repository, accessed Oct. 13, 2026. [Online]. Available: https://github.com/FluxGarage/RoboEyes.

- **xiaozhi**: XiaoZhi ESP32 contributors, "XiaoZhi ESP32," software repository, accessed Oct. 13, 2026. [Online]. Available: https://github.com/78/xiaozhi-esp32.
