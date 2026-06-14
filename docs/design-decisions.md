# Design Decisions

This document explains the thinking behind the legal-intake MCP server: what
it is, the principles that shaped it, and the choices that a reader evaluating
the work should understand. The code shows what was built; this explains why.

The goal here is candor, not promotion. The server is a proof of concept with
real strengths and real, stated limitations. Where a choice involved a
tradeoff, the tradeoff is named.

## 1. What this is, and why intake

This is a Model Context Protocol (MCP) server for legal matter intake, built
for the context an alternative legal services provider (ALSP) works in:
serving the in-house legal, compliance, and operations functions of corporate
clients, often at high volume. It is not a law-firm conflicts-and-engagement
system; the client relationship is the stable unit, and the matters flowing
through it are recurring work within an ongoing engagement.

Intake is a good demonstration vehicle for an MCP server because it is a
genuine agentic workflow, not a single function call. A new matter arrives as
free text. Answering "what is this, have we done it before, who should handle
it, and does it need to go back to the client" requires composing several
distinct operations over structured firm data — exactly the kind of
multi-step reasoning that MCP exists to enable, with the language model as the
orchestrator and the server as the source of grounded, structured facts.

## 2. The core principle: tools surface, the model reasons, the human decides

The single most important design choice runs through every tool: each tool
*surfaces structured signals* rather than *returning a verdict*. The language
model reasons over those signals. A human makes the consequential decision.

This is not an accident of implementation; it is the governing principle, and
it is what makes the system appropriate for legal work. An intake tool that
returned "assign this to Lawyer X" or "this is cleared, proceed" would be
substituting a brittle automated judgment for a professional one. Instead,
`suggest_staffing` returns ranked candidates *with the data behind the
ranking* — seniority, capacity, expertise areas — so that the reasoning layer
can weigh them, and a human can overrule.

A live run of the server demonstrated this working exactly as intended. Asked
to staff a patent in-licensing matter, the staffing tool ranked a
high-availability associate first on its capacity-after-seniority logic. The
model, reading the expertise data the tool also returned, recognized that the
top-ranked associate's expertise was vendor/procurement while a slightly
busier senior lawyer specialized in licensing and had led the near-identical
prior matter — and recommended the specialist instead, stating explicitly that
it was overriding the capacity ranking on expertise grounds and that the final
call belonged to the user. That override is the whole design in one moment:
the tool surfaced, the model reasoned, the human decides.

The implication for tool design is concrete. Tools expose their raw inputs to
judgment rather than collapsing them into a single score. A staffing tool that
hid expertise behind one ranking number would have produced a worse outcome,
because the model would have had nothing to reason against. Surfacing beats
deciding.

## 3. Mechanical-first classification

`classify_matter` performs deterministic, keyword-based classification with no
language-model call inside the tool. It scans the matter description for
signal phrases mapped to matter types, using word-boundary matching, and
returns ranked candidates with confidence scores and the specific phrases that
matched.

The choice to make the classifier mechanical rather than LLM-based is
deliberate, and it mirrors the philosophy of a companion project — a
[hallucination detector](https://github.com/david-yamin-esq/agentic-hallucination-detector)
that prioritizes mechanical detection over LLM self-grading wherever possible.
Three reasons:

- **Explainability.** A mechanical match can be shown: "this was classified as
  an MSA Review because the phrases 'master services agreement' and 'msa'
  appeared." A model-produced classification can only be asserted.
- **Determinism.** The same description always classifies the same way. That
  is a precondition for any kind of audit or regression testing.
- **Division of labor.** The host model is already a powerful reasoner. Putting
  a second model call *inside* the tool would be redundant and would move
  judgment into a place where it cannot be inspected. The mechanical tool
  surfaces; the host model reasons.

The tradeoff is real and worth naming: keyword matching is length-sensitive
and literal. A short description that mentions "licensing" once will match the
matter type but not pick up complexity. In the live run referenced above, the
classifier scored a substantively complex licensing matter as "Routine"
because the short description contained no complexity signal — and the model
correctly distrusted that score, noting that the substance and a near-identical
precedent both pointed to "Complex," and proceeded on that basis. This is the
intended behavior: the deterministic layer is a triage aid, explicitly framed
as such in the tool description, and the reasoning layer is expected to
override it when context warrants. A classifier that pretended to more
certainty than keyword matching can support would be worse, not better.

## 4. Why the escalation tool refuses to decide

`flag_for_escalation` is the tool that most clearly expresses the project's
governance stance, because of what it deliberately does not do: it does not
escalate, and it does not clear. It scans for escalation signals (novel
issues, liability above norm, IP exposure, regulatory exposure, material
commitments), reports the client's own stated escalation threshold when a
client is given, names the escalation contact, and then explicitly returns a
recommendation framed as a flag for human judgment.

The reason is that escalation is a decision that belongs to the client's
in-house team, and an intake system must never silently absorb a decision that
belongs to someone else. The cost structure is asymmetric: a matter wrongly
escalated wastes a little time; a matter wrongly *not* escalated can mean an
ALSP takes a substantive position on something the client needed to decide.
The tool therefore leans toward surfacing, states "when in doubt, escalate" in
its own output, and reports the client's threshold alongside its own signal
detection so the two can be weighed together rather than collapsed.

In the live run, the tool flagged a licensing matter that contained two of the
client's explicitly forbidden terms, mapped that against the client's stated
threshold ("any IP assignment, licensing term, or publication restriction"),
and named the General Counsel as the contact — while still framing the call as
the human's to make. That is the correct behavior for a tool operating at the
boundary of a professional judgment.

## 5. Structured outputs as explainability

Every tool returns structured data that includes the basis for its output, not
just the output. `classify_matter` returns the matched signal phrases.
`find_similar_matters` returns the matched matter types and how ranking was
done. `suggest_staffing` returns seniority fit, capacity, and expertise for
each candidate. `flag_for_escalation` returns the triggered signals and the
client threshold.

This is a defensibility choice. In legal services, "the system recommended X"
is not good enough; "the system recommended X because of these specific,
inspectable facts" is. Returning the basis alongside the result means any
recommendation can be reconstructed and challenged, and it means the reasoning
layer has real material to work with rather than a verdict to rubber-stamp.

## 6. Why these six tools

The server exposes six intake tools plus a liveness check (`ping`):
classification (`classify_matter`), precedent retrieval
(`find_similar_matters`), client context (`check_client_history`), detail
retrieval (`get_matter_history`), staffing (`suggest_staffing`), and escalation
assessment (`flag_for_escalation`).

The selection answers the four questions a real intake process asks — what is
this, have we done it before and how does this client want it handled, who
should do it, and does it need to go back to the client — with one or two tools
each. Choosing which operations to expose is itself the design work: an intake
system could expose twenty tools, and a sprawling surface would make the
workflow harder for a model to compose, not easier. The discipline is to
expose the operations that compose into the actual workflow and stop there.

Some things were deliberately left out of this version:

- **No conflicts-checking tool.** In the ALSP-to-in-house context, conflicts
  are resolved at the engagement level, not per matter. A firm-side intake
  system would need this; this one replaces it with `check_client_history`,
  which answers the question that actually recurs here ("have we done this
  before for this client").
- **No write operations.** Every tool reads and recommends. Nothing creates,
  assigns, or escalates as a side effect. Intake is advisory by nature, and
  keeping the tools read-only keeps the human-in-the-loop boundary clean.
- **No automated remediation or drafting.** The server triages; it does not
  produce the work product.

## 7. Data model choices

The data model is ALSP-specific in a way that matters. The stable entity is
`client_companies`, each carrying a standing preferences profile — preferred
paper, playbook variant, redlining style, approval thresholds, required and
forbidden clauses, escalation threshold, communication norms. Matters are
recurring work within those ongoing relationships, not one-off engagements.
This is the structural difference between an ALSP serving in-house departments
and a law firm taking outside matters, and it shapes which questions the tools
answer.

The mock data uses three clients with deliberately contrasting profiles — a
high-governance financial-services client that escalates readily, a
high-throughput logistics client that runs on templates and tolerates light
redlining, and an IP-sensitive biotech client whose matters need senior
staffing and careful escalation. The contrast is what lets the demonstration
show client-specific behavior: the same matter type is handled differently
depending on whose standing preferences apply.

Storage is the standard-library `sqlite3` module with list- and dict-valued
fields stored as JSON-encoded text columns. This is a pragmatic choice for a
single-file demonstration database: it keeps the schema flat and dependency
count at zero, at the cost of not being able to query inside the JSON columns
at the SQL level. For the demonstration's scale (three clients, sixty-nine
matters) this is the right tradeoff; a production system with millions of
contracts would use a real relational schema or a document store.

The mock matters are generated, not hand-authored, by a deterministic seeded
generator that instantiates scenario templates across the clients eligible for
each kind of work, creating multiple instances of high-volume contract types
to mirror how managed contract review actually recurs. The generator is itself
part of the design: it produces realistic clustering (several near-identical
prior matters for a given client and type) that makes precedent retrieval
meaningful, and it is reproducible, so the demonstration data is stable across
runs.

## 8. Limitations, and what a production version would need

This is a proof of concept. It demonstrates architecture and judgment, not
production readiness. The boundaries are worth stating plainly:

- **Mock data only.** Three fictional clients and sixty-nine generated
  matters. The patterns are realistic; the volume is a demonstration scale,
  not a production one.
- **Single-user, local, no authentication.** The server runs locally over
  stdio for a single user via a desktop MCP client. A production deployment
  would need authentication, multi-tenant isolation, access controls, and
  monitoring — none of which is in scope here.
- **Classifier length-sensitivity.** As discussed in section 3, the
  keyword-based classifier under-reads complexity from short descriptions.
  This is mitigated by the reasoning layer in practice, but a production
  classifier would supplement keyword matching with additional signals.
- **No write path, by design.** The server cannot create, assign, or escalate.
  That is the correct boundary for a triage aid, but a production intake system
  would eventually need governed, audited write operations with the same
  human-in-the-loop discipline applied to each.
- **Staffing is capacity-and-seniority, not full optimization.** Expertise is
  surfaced for the reasoning layer to weigh, deliberately, rather than folded
  into the ranking. A production version might add expertise scoring — but
  only carefully, since the live run showed that leaving expertise to the
  reasoning layer produced better staffing than a single ranking number would
  have.

The throughline of these limitations is the same as the throughline of the
design: the system is built to surface structured, inspectable signals to a
reasoning layer and a human, and to refuse to make the decisions that belong to
people. A production version would scale the data, harden the deployment, and
add governed write paths — but it would keep that principle, because in legal
work the principle is the point.
