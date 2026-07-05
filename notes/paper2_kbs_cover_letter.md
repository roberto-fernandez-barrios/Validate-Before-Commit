# Cover letter — Knowledge-Based Systems

> Editable draft. Fill affiliation and any funding; adjust tone to taste.

Dear Editor-in-Chief,

We are pleased to submit our manuscript, *"Validate Before Commit: Label-Efficient Safe Readaptation for
Adaptive Network Intrusion Detection under Concept Drift,"* for consideration in *Knowledge-Based Systems*.

Machine-learning detectors deployed in changing environments are periodically retrained to cope with concept
drift, and the field treats the decision of *when* to retrain as a drift-detection problem. Our central
finding is that this is the wrong control variable. Whether retraining a deployed model helps is governed
almost entirely by how much that model has already degraded — a quantity that correlates with the model's
no-adaptation accuracy at r ≈ −0.82 to −0.89 across four downstream classifiers, and which drift detectors,
by construction, cannot observe. As a consequence, drift-triggered retraining ranges from strongly beneficial
to net-harmful across three public benchmarks, and the choice of detector is not the operative lever.

We reframe readaptation as a cost-aware decision and contribute a deployable, label-efficient *intelligent
decision method* — a validate-before-commit gate that retrains a candidate model but commits it only if it
beats the incumbent on a small labeled probe. The method needs only tens of labeled instances, tolerates
label latency, and fails safe under adversarial (poisoned) validation labels; it is pre-registered and
evaluated with 30-seed confidence intervals across two detectors and four downstream classifiers, and we
report honest negatives (simple confirmation/cooldown policies and a zero-label variant both fail) that
delimit the method. All results are reproducible from a public artifact.

We believe this work fits squarely within the scope of *Knowledge-Based Systems*, whose leading topics
include machine-learning methodology and intelligent decision-support systems: the paper contributes a
methodological reframing and a practical decision method for the safe management of deployed intelligent
detection systems under non-stationarity, with rigorous empirical validation.

The manuscript is original, has not been published previously, and is not under consideration elsewhere. All
authors approve the submission and declare no competing interests. The datasets used are public and cited;
our code and protocols are released as a citable artifact. Highlights and a graphical abstract are provided.

Thank you for considering our submission.

Sincerely,
Roberto Fernández-Barrios, on behalf of all authors
(Iker Pastor-López, Amaia Pikatza-Huerga, Pablo García Bringas)
Faculty of Engineering, University of Deusto, Bilbao, Spain
Corresponding author: roberto.fernandez.b@deusto.es
