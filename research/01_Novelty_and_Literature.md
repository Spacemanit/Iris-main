# Iris: novelty and literature findings

Research summary updated 13 October 2026. This is advice about possible contributions, not a paper, completed systematic review or report of experiments.

## Main conclusion

Iris is a credible integration project. The inspected implementation does not yet support a claim of a new gaze algorithm, a new conversational architecture or demonstrated social benefits. The most defensible course-paper direction is a **focused narrative review comparing gaze representation, conversational feedback and visual responsiveness in inexpensive companions**.

The possible contribution belongs to the comparison and interpretation of existing evidence. Its novelty remains modest and must be judged against related reviews. No search can certify that a proposed angle has never been covered.

## What the project actually supports

- The vision code tracks the center of the largest detected face. This is **face-position tracking**, not estimation of where the user's eyes are looking.
- The display renders eyes and interaction states. Accurate perceived eye contact, readable gaze direction and understandable state cues require observer evaluation.
- Vision, display and speech work are separated in the implementation. That is an engineering choice, not evidence of a measured responsiveness advantage.
- The current specification enables device microphone and speaker paths, with host-side vision and speech models. A complete-system cost must account for the host and peripherals. Physical operation of replacement audio hardware still needs confirmation.
- There are no research measurements here establishing camera-to-display delay, information freshness, power, engagement, learning or therapeutic benefit.

These conclusions come from the current project specification and vision implementation inspected on 13 October. Older planning documents contain targets and stale configuration details.

## Closest literature and its implications

| Work | What matters for Iris |
|---|---|
| [Admoni and Scassellati, 2017](https://publications.ri.cmu.edu/storage/publications/2018/01/admoni2017jhri.pdf) | Social-gaze research already separates technological implementation, design and human responses. Moving pupils alone do not establish a social effect. |
| [Al Moubayed et al., 2012](https://www.lri.fr/~anab/teaching/evaluation/papers/AlMoubayed2012_MonaLisaEffect.pdf) | Flat and three-dimensional facial projections communicate spatial gaze differently. Its five-observer study does not validate a small cartoon-eye display. |
| [Jung et al., 2023](https://ceur-ws.org/Vol-3467/paper4.pdf) | A viewpoint cue improved gaze judgments with large-display virtual humans. The 30-participant direction-recognition study does not demonstrate sustained engagement or validate Iris's pupils. |
| [Andrist et al., 2014](https://pages.cs.wisc.edu/~bilge/pubs/2014/HRI14-Andrist.pdf) | Timed gaze aversion had useful conversational effects in a 30-participant NAO study; the predicted disclosure improvement was not found. Constant face following is not a complete gaze policy. |
| [Axelsson et al., 2022](https://doi.org/10.3389/fcomp.2022.744574) | Feedback can concern contact, perception, understanding or acceptance. An animation indicating activity need not indicate successful understanding. |
| [Kang et al., 2026: Fluid-Xpress](https://shura.shu.ac.uk/37180/1/Ma-Fluid-XpressEmotion-Aware%28VoR%29.pdf) | Nonverbal reactions already run separately from language reasoning. An eight-participant pilot is preliminary evidence; fast/slow separation is not new to Iris. |
| [Krüger et al., 2025: Mirror Eyes](https://arxiv.org/html/2506.18466v1) | Screen eyes can carry explicit referential information. Its 33-participant manipulation study supports particular awareness/error-detection outcomes, not affordability or transfer to miniature displays. Author preprint inspected; published version linked by arXiv. |
| [Hessels and Fang, 2026](https://doi.org/10.3758/s13423-026-02902-x) | Gaze and attention are not interchangeable; perceptual and contextual limits matter. Findings about anthropomorphic gaze need caution when applied to stylized eyes. |
| [Neuber et al., 2026](https://doi.org/10.3389/frobt.2025.1723527) | A gaze-following review identifies incomplete response-time reporting. Its scope is humanoids following human gaze, so it does not prove a gap throughout face-tracking companions. |
| [Rutatola et al., 2026](https://doi.org/10.3389/frobt.2026.1827676) | A review of 34 affordable educational robot designs already covers that broad territory. Affordability is contextual, rather than a universal board-price threshold. |
| [Yates et al., 2021](https://user.eng.umd.edu/~ulukus/papers/journal/aoi-survey.pdf) | Age of Information supplies an established way to think about stale observations. Applying it to a display is a design interpretation, not a new networking metric or demonstrated social benefit. |

## Three possible directions

1. **Focused comparative review: best fit for this course.** Compare what gaze cues mean, how studies evaluate them, and what transfers to small companions. A checked comparison table and bounded design conclusions are the useful output.
2. **Timing benchmark: stronger engineering evidence, optional.** Measure observation-to-display behavior during speech workload with defined comparisons. This requires instrumentation and actual results; it is unnecessary if the assignment accepts a review.
3. **Small-display perception study: possible later work.** Test direction or state recognition with observers. Participant recruitment, ethics requirements and study design make this less convenient within a short deadline.

Avoid claiming a breakthrough from ESP32 hardware, local language models, animated eyes, concurrency or combining these features. Established maker projects such as [RoboEyes](https://github.com/FluxGarage/RoboEyes) and [XiaoZhi ESP32](https://github.com/78/xiaozhi-esp32) are also relevant practical prior art, although they do not supply peer-reviewed evidence of social effectiveness.

## Suggested scope

Working topic: **Gaze and visual feedback in low-cost interactive companions**.

Central question: *Which design and evaluation considerations follow from existing evidence when a companion uses a small animated face while also processing speech?*

Compare perceptual clarity, conversational meaning, temporal relevance and complete-system cost. Treat these as organizing questions, not a validated framework. Iris can motivate the review without becoming an invented experiment.

Fuller background and the original reference shortlist remain in [Iris_Research_Strategy.md](Iris_Research_Strategy.md) and [iris_references.bib](iris_references.bib). This summary supersedes older implementation details where they differ.
