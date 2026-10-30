# Gaze and Visual Feedback in Low-Cost Interactive Companions: A Focused Narrative Review

**Working manuscript, 13 October 2026.** Author names, affiliations, final declarations and venue formatting remain to be supplied. This draft requires the authors' source verification and substantive revision before external submission.

## Abstract

Interactive companions can combine a camera, an animated face and a conversational interface without reproducing the mechanical complexity of a humanoid robot. However, implementing these features does not establish that users perceive appropriate gaze or meaningful feedback. This focused narrative review examines selected literature on social gaze, facial displays, conversational feedback and information freshness to identify design considerations for inexpensive companions. The synthesis distinguishes face-position tracking from human gaze estimation, spatial gaze interpretation from perceived eye contact, and visible activity from feedback about system state. Empirical findings from projected faces, virtual humans and embodied robots are compared with attention to differences in representation, task and evaluation. Information freshness provides an additional engineering perspective on visual responses during computationally demanding speech processing. The resulting design questions concern perceptual clarity, conversational meaning, temporal relevance and the cost of the complete system. The review offers a bounded synthesis for prototype designers rather than a systematic inventory or evidence that a particular companion improves engagement.

**Keywords:** human-robot interaction; social gaze; animated faces; conversational feedback; low-cost companions; information freshness

## 1. Introduction

A small device that looks toward a person, blinks and answers questions can provide a useful introduction to interactive systems. Its apparent simplicity conceals several different problems. The camera must provide usable observations; the displayed eyes must communicate a direction; changes in expression must correspond to an interaction state; and speech processing must coexist with these visual behaviors. A successful demonstration of the assembled device addresses integration, but does not by itself answer how people interpret its behavior.

Social gaze is already an established research area. Admoni and Scassellati [1] distinguish human-focused, design-focused and technology-focused investigations, emphasizing that gaze systems are studied with different platforms and measures. This distinction is useful for inexpensive companions: implementing an eye movement is a technology decision, whereas showing that the movement communicates attention requires evidence about people. Treating these as separate questions prevents an implementation feature from being presented as a demonstrated social outcome.

Recent reviews also limit the scope of a plausible contribution. Neuber et al. [2] examine technologies through which humanoid robots follow human gaze, while Rutatola et al. [4] review affordable educational robot designs. This article does not attempt to replace those broader accounts. Its purpose is narrower: to connect selected findings about visual representation and conversational feedback with engineering choices in camera-equipped companions whose facial behavior is displayed on a screen.

The guiding question is: **What design considerations follow from the literature when a low-cost companion uses an animated face to respond visually while also processing speech?** The contribution is a comparison organized around four questions: whether the visual cue can be interpreted, what it communicates, how current its input is, and what resources support the complete system. These questions are offered as a practical synthesis, not as a validated model of engagement or a claim that the underlying techniques are new.

## 2. Review approach

This is a focused narrative review using purposive selection. An initial set of references was assembled through AI-assisted web discovery on 7 October 2026 and revisited on 13 October 2026. The latter search included the queries `"screen-based" "robot" gaze latency low cost` and `"social eye gaze" "low-cost" "review"`, followed by targeted retrieval of named publications from publisher websites, proceedings and author or institutional repositories. Eleven technical publications and one methodological paper were retained in this draft. This number describes the cited selection; it is not a screening yield from a systematic search.

Sources were chosen for relevance to social gaze, facial representation, conversational feedback, affordability or the freshness of sensor-driven updates. Laboratory studies and review articles were used for different purposes: studies supplied bounded findings, and reviews supplied terminology and broader context. The synthesis compared representation, task, participant sample where applicable, reported outcome and limits of transfer. Industrial manipulation without a relevant visual communication component, and clinical effectiveness claims, were outside the intended scope.

No systematic search of subscription databases, independent duplicate screening, formal risk-of-bias assessment or meta-analysis was conducted. The selection favors accessible English-language material and therefore may omit relevant work. SANRA, a narrative-review appraisal scale developed in a medical publishing context, informed the emphasis on explicit aims, search description, referencing and scientific reasoning [5]. It is used here as an editorial aid, not as a robotics reporting standard or evidence of publishability. AI assisted discovery, comparison and prose drafting; the present document remains an author-verification draft.

## 3. Distinguishing the capabilities

Terms that sound similar can describe different input and output requirements. A face detector provides a location or bounding box in an image. Mapping its center to displayed pupil positions can produce face-directed behavior, but does not estimate where that person is looking. Human gaze estimation requires additional information about eye direction or a justified approximation from head orientation. Gaze following then connects an estimated direction to a possible target in the environment. These distinctions are consistent with the technology scope examined by Neuber et al. [2].

Mutual gaze additionally concerns reciprocal orientation between partners; directing the device toward a detected face alone does not establish reciprocity [1]. Consequently, a prototype should describe the quantity it actually detects before claiming eye contact or joint attention. The distinction matters even if users casually describe the device as following their eyes.

Hessels and Fang [3] further caution against equating gaze with attention. Gaze participates in both perception and communication, and its interpretation depends on context and human perceptual constraints. Their perspective concerns anthropomorphic gaze and should not be assumed to establish the same effects for every stylized character. For a small display, a conservative evaluation question is whether observers can identify the intended target or state, rather than whether the device has reproduced human social understanding.

Table 1 summarizes the distinctions used in this review. The final column identifies evidence that a designer would need; it does not state that any particular prototype already has that evidence.

**Table 1. Capability claims and the evidence they require.**

| Claim | Operational meaning | Evidence needed |
|---|---|---|
| Face-position tracking | Display behavior responds to a detected face location | Detection and mapping checks across positions and failure cases |
| Human gaze estimation | System estimates a person's looking direction | Comparison with an appropriate gaze reference |
| Gaze following | System identifies a target along that direction | Target identification in a defined environment |
| Perceived eye contact | Observer interprets the displayed gaze as directed at them | Observer judgments under specified viewing conditions |
| Joint attention | Partners coordinate attention toward a common referent | An interaction task demonstrating shared reference |

## 4. Visual representation and spatial interpretation

Replacing moving eyes with a display changes the representation problem. Screen animation allows pupil shape, position and expression to be altered without additional facial actuators. However, a two-dimensional image does not provide the same viewing geometry as a physical face. A visually convincing animation can therefore remain ambiguous about whom it addresses.

Al Moubayed et al. [6] compared gaze judgments for an animated face projected onto a flat surface and a three-dimensional facial mask. Five observers judged stimuli from different positions. The three-dimensional condition supported more consistent interpretation of gaze targets in the surrounding physical space. This supports a representation-specific distinction, rather than a general claim that every curved or embodied display produces accurate eye contact. The small observer sample and controlled geometry also constrain transfer to a handheld companion.

Jung et al. [7] investigated a different response to display ambiguity: small changes in the rendering viewpoint of virtual humans. Their study involved 30 participants, a 65-inch display and a viewing distance of 2.4 metres. The intervention improved gaze-direction judgments in the tested narrow-angle condition. The measured outcome was direction recognition; improved long-term engagement was not established. Differences in screen size, background and character realism make direct application to a small pair of cartoon eyes an open design question.

Krüger et al. [8] provide another approach in Mirror Eyes, where the displayed eyes show reflection-like images of the attended region. A 33-participant study used a robot with head movement, speech and pick-and-place tasks. Participants reported greater information-processing awareness and detected erroneous actions earlier with mirroring enabled. This is evidence about a particular referential aid during brief task exposure. It neither establishes affordability nor shows that the same overlay would remain legible on a miniature display.

Together, these studies suggest that representation should be selected for the intended communication task. A companion meant only to orient toward one nearby person faces a different requirement from a robot that must distinguish several objects or interlocutors. Increasing facial detail may not solve ambiguity if the relevant target cannot be inferred. Designers can instead begin with a simple discrimination task: ask observers whom or what the character appears to address from several specified positions. This proposed check isolates the interpretation problem before broader claims about social presence are attempted.

## 5. Conversational meaning of visual behavior

Correctly indicating a target is only one function of gaze. Andrist et al. [9] evaluated conversational gaze aversion with 30 participants interacting with NAO robots. Appropriately timed aversions influenced perceived thoughtfulness and conversational floor holding; the study did not find the predicted increase in participant disclosure. Both the positive and null findings matter. Looking away can have a useful conversational role, while a favorable result on one measure does not establish improvement in every social outcome.

Axelsson et al. [10] review feedback across speech, head gestures, gaze and facial expression. Their account distinguishes feedback about contact, perception, understanding and acceptance. For a companion, this provides a reason to distinguish an indication that input is being received from an indication that its meaning has been understood. A repeated blink can keep the character visually active, but activity alone does not communicate which stage of processing has succeeded.

Kang et al. [11] explicitly separate nonverbal reactions from language generation in Fluid-Xpress. Their micro-loop handles facial reactions while a macro-loop handles verbal reasoning. The accompanying eight-participant pilot provides preliminary evidence, including increased awareness of expression changes, rather than a general validation of emotion understanding or therapeutic benefit. The architecture is relevant here because it demonstrates prior work on visual responsiveness during slower language processing; that separation should not be claimed as an invention of a new student prototype.

A cautious design interpretation is to give each visible state a clear, limited meaning. A listening cue can indicate that capture is enabled. A processing cue can indicate that a response is pending. A speaking cue can accompany playback. An error cue can explain that the system could not complete a request. These mappings should be documented and checked with observers. In particular, a cheerful reaction after an unrecognized utterance could imply successful understanding when the system has none. Conversely, a processing animation that continues after a failed request can conceal a failure. Designing the transition and recovery behavior is therefore part of designing the feedback, rather than an incidental implementation detail.

**Table 2. Selected empirical evidence and boundaries of transfer.**

| Study | Setting and sample | Relevant finding | Boundary for a small companion |
|---|---|---|---|
| Al Moubayed et al. [6] | Flat and three-dimensional facial projections; five observers | Three-dimensional presentation supported more consistent spatial gaze judgments | Specific projection geometry; small sample |
| Jung et al. [7] | Large-display virtual humans; 30 participants | Rendering viewpoint cue improved tested gaze judgments | Direction-recognition task, not sustained conversation |
| Andrist et al. [9] | NAO conversation; 30 participants | Timed aversion helped selected conversational measures; disclosure result was null | Head-mediated behavior may differ from animated pupils |
| Krüger et al. [8] | Robot manipulation task; 33 participants | Mirroring supported awareness and earlier error detection | Brief exposure; larger display and actuated head |
| Kang et al. [11] | Dual-loop expressive robot; pilot with eight participants | Preliminary improvement in expression awareness | Small pilot does not establish clinical or general social benefit |

The table supports comparison of study conditions, not an effectiveness ranking. The interventions and outcomes differ, so their results cannot be treated as interchangeable measurements of engagement.

## 6. Temporal relevance and information freshness

A responsive animation can still use outdated observations. Yates et al. [12] define Age of Information around the elapsed time since generation of the newest received status update. This perspective distinguishes freshness from packet delay or throughput: sending more observations can also create waiting and congestion. It supplies a useful engineering concept, but its networking results are not themselves evidence about perceived gaze in HRI.

For a camera-driven display, a corresponding design question concerns the age of the observation represented by the visible eyes. If an old frame waits behind other work, rapid rendering of the resulting command does not make the observation current. Likewise, an animation can run smoothly while the selected face position remains unchanged because the tracking worker is delayed. Rendering rate, tracking update rate and observation-to-display delay should therefore be reported separately.

A latest-observation queue is one possible response when only the current position is needed. It exchanges completeness for freshness by replacing pending observations. However, dropping observations is unsuitable when the algorithm requires a motion history unless that history is maintained separately. This is a design hypothesis to evaluate under the intended workload, rather than an assertion that discarding frames universally improves interaction.

Neuber et al. [2] identify incomplete response-time reporting in much of the gaze-following literature. A future companion evaluation could make its timing endpoints explicit: observation acquisition, completion of analysis, command receipt and visible display change. Measurements beginning only at host receipt would omit earlier acquisition and transfer delay. Comparisons across devices also require an explained timestamp or clock-alignment method. Such reporting would permit more useful comparisons without introducing an unsupported universal latency threshold.

## 7. Synthesis for inexpensive companions

The reviewed evidence suggests four design questions that should be assessed separately. **Perceptual clarity** asks whether observers can identify the intended target or state. **Conversational meaning** asks whether a cue represents the interaction stage accurately. **Temporal relevance** asks whether the visual response still corresponds to the current observation or event. **System affordability** asks what resources are required to deliver those behaviors reliably. Improvement in one dimension should not be assumed to establish improvement in the others.

The cost dimension requires care. Rutatola et al. [4] found diverse designs across 34 studies of low-cost educational robots and used a contextual definition of affordability rather than a universal price threshold. This makes a bare board-price comparison insufficient. A host-assisted companion should state whether its reported cost includes the computer used for vision and speech, audio components, power supply and enclosure. Reusing an existing laptop can be appropriate for a course prototype, but a device-only cost and a complete deployment cost answer different questions.

These questions also help separate an engineering report from an interaction claim. A prototype can establish that its components exchange data and recover from interruptions. To claim that a displayed state is recognizable, it needs an observer task. To claim improved engagement, it needs an appropriately defined interaction outcome and comparison. The review therefore favors explicit claims linked to a suitable form of evidence. Adding more features without clarifying those claims would make evaluation more difficult, even if the demonstration becomes more entertaining.

## 8. Illustrative application to Iris

Iris illustrates these distinctions without providing a new experimental result. Inspection of the project specification and vision implementation on 13 October 2026 shows an ESP32-CAM and small facial display connected to host-side vision and speech processing. The vision code selects the largest detected face and maps its center into normalized display coordinates. This is face-position tracking rather than estimation of the user's eye-gaze direction. The implementation also separates display rendering from host-side speech work and retains a latest video observation.

These choices make Iris a concrete setting in which to consider the review's questions. They do not demonstrate accurate perceived eye contact, a measured latency advantage, emotion recognition, educational improvement or therapeutic effectiveness. Those outcomes remain untested in this article. A follow-up evaluation could first check direction and state recognition, then measure observation-to-display behavior with and without speech workload. The proposed evaluation is future work; no participant results or timing measurements are reported here. Iris serves as an illustration of design reasoning, not as evidence validating the synthesis.

## 9. Limitations and conclusion

This review is selective and interpretive. Accessible sources and the prototype-oriented question influenced selection, and no claim of exhaustive coverage is made. Evidence spans facial projections, virtual humans, humanoids and expressive robots with different tasks and measures. Several selected studies use brief laboratory encounters or small samples. Their findings cannot establish long-term effects for an inexpensive companion, and the proposed four questions have not been evaluated as a measurement instrument. The use of a methodological appraisal tool from medicine also does not substitute for field-specific peer review.

The selected literature supports a cautious conclusion: useful visual interaction involves more than detecting a face and animating eyes. Designers must consider what observers can infer, what a cue actually signifies, how current its supporting observation is, and what resources the behavior requires. A low-cost companion can provide a practical platform for exploring these questions. Establishing social benefits, however, requires evaluation beyond a functioning demonstration. The contribution of this review is that bounded connection between perception, feedback and engineering, rather than a claim of a new gaze algorithm or a validated social intervention.

## AI-use statement for this working draft

Codex by OpenAI assisted with literature discovery, source comparison, organization, prose drafting and manuscript formatting throughout this document. It was not used to generate experimental observations or participant data. Author source checking, substantive revision and approval of the final manuscript remain pending. Before submission, this statement must be updated to describe the completed workflow accurately and placed where the selected venue requires it.

## References

[1] Admoni, H. and Scassellati, B. (2017). Social eye gaze in human-robot interaction: A review. *Journal of Human-Robot Interaction*, 6(1), 25-63. [https://doi.org/10.5898/JHRI.6.1.Admoni](https://doi.org/10.5898/JHRI.6.1.Admoni).

[2] Neuber, L., Culemann, W., Ingendoh, R. M. and Heine, A. (2026). Eyes ahead: A scoping review of technologies enabling humanoid robots to follow human gaze. *Frontiers in Robotics and AI*, 12, 1723527. [https://doi.org/10.3389/frobt.2025.1723527](https://doi.org/10.3389/frobt.2025.1723527). Published 16 January 2026; the publisher labels the volume 2025.

[3] Hessels, R. S. and Fang, Y. (2026). A visual perceptual perspective on gaze in social robotics. *Psychonomic Bulletin & Review*, 33, article 131. [https://doi.org/10.3758/s13423-026-02902-x](https://doi.org/10.3758/s13423-026-02902-x).

[4] Rutatola, E. P., Msonge, F. C., Proesmans, R., Stroeken, K. and Belpaeme, T. (2026). Low-cost social robot designs for education: A review. *Frontiers in Robotics and AI*, 13, 1827676. [https://doi.org/10.3389/frobt.2026.1827676](https://doi.org/10.3389/frobt.2026.1827676).

[5] Baethge, C., Goldbeck-Wood, S. and Mertens, S. (2019). SANRA - A scale for the quality assessment of narrative review articles. *Research Integrity and Peer Review*, 4, article 5. [https://doi.org/10.1186/s41073-019-0064-8](https://doi.org/10.1186/s41073-019-0064-8).

[6] Al Moubayed, S., Edlund, J. and Beskow, J. (2012). Taming Mona Lisa: Communicating gaze faithfully in 2D and 3D facial projections. *ACM Transactions on Interactive Intelligent Systems*, 1(2), article 11. [https://doi.org/10.1145/2070719.2070724](https://doi.org/10.1145/2070719.2070724).

[7] Jung, S., Kum, J. and Lee, M. (2023). Breaking the Mona Lisa effect: Enhancing eye contact with virtual humans in 2D display environments. *Proceedings of the 15th Asia-Pacific Workshop on Mixed and Augmented Reality*, CEUR Workshop Proceedings, 3467. [https://ceur-ws.org/Vol-3467/paper4.pdf](https://ceur-ws.org/Vol-3467/paper4.pdf).

[8] Krüger, M., Tanneberg, D., Wang, C., Hasler, S. and Gienger, M. (2025). Mirror Eyes: Explainable human-robot interaction at a glance. Author preprint, arXiv:2506.18466v1, associated with the 34th IEEE International Conference on Robot and Human Interactive Communication. [https://arxiv.org/abs/2506.18466](https://arxiv.org/abs/2506.18466). Related published DOI: [https://doi.org/10.1109/RO-MAN63969.2025.11217810](https://doi.org/10.1109/RO-MAN63969.2025.11217810).

[9] Andrist, S., Tan, X. Z., Gleicher, M. and Mutlu, B. (2014). Conversational gaze aversion for humanlike robots. *Proceedings of the 2014 ACM/IEEE International Conference on Human-Robot Interaction*, 25-32. [https://doi.org/10.1145/2559636.2559666](https://doi.org/10.1145/2559636.2559666).

[10] Axelsson, A., Buschmeier, H. and Skantze, G. (2022). Modeling feedback in interaction with conversational agents - A review. *Frontiers in Computer Science*, 4, 744574. [https://doi.org/10.3389/fcomp.2022.744574](https://doi.org/10.3389/fcomp.2022.744574).

[11] Kang, C., Alitai, M., Wang, Y., Cai, X., Ma, R., Cangelosi, A. and Shangguan, Z. (2026). Fluid-Xpress: Emotion-aware dual-loop framework for empathic facial reaction in HRI. *Companion Proceedings of the 21st ACM/IEEE International Conference on Human-Robot Interaction*, 425-429. [https://doi.org/10.1145/3776734.3794429](https://doi.org/10.1145/3776734.3794429).

[12] Yates, R. D., Sun, Y., Brown, D. R., III, Kaul, S. K., Modiano, E. and Ulukus, S. (2021). Age of information: An introduction and survey. *IEEE Journal on Selected Areas in Communications*, 39(5), 1183-1210. [https://doi.org/10.1109/JSAC.2021.3065072](https://doi.org/10.1109/JSAC.2021.3065072).
