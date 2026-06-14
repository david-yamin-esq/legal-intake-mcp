# legal-intake-mcp

*A Model Context Protocol server for legal matter intake that knows what not to decide.*

A corporate legal department routes a stream of work to its managed-services
provider: "review this in-licensing agreement, the counterparty wants
assignment of improvements." Every incoming matter has to be triaged before it
reaches a lawyer: *what is this, have we handled it before for this client, who
on the bench should take it, and does it need to go back to the client's own
in-house team?* This server exposes that triage as MCP tools, so a language
model in Claude Desktop (or any MCP client) can run it against the provider's
structured data, routing each matter to the right team and escalating the ones
that need a client decision back to the GC.

The design rests on one principle: **the tools surface structured signals, the
model reasons over them, and a human makes the call.** No tool in this server
decides anything.

![Surface, reason, decide](docs/intake-pipeline.svg)

## See it work

Here is a single real intake request, run end to end through the live server.
The annotations point out the moments that matter.

**The request:**

> New intake from Vertex Biosciences: review an in-licensing agreement for a
> patented assay. The counterparty wants assignment of improvements and a broad
> license grant. Run full intake: classify it, check what we know about this
> client, find similar past matters, suggest staffing, and tell me whether it
> needs escalation.

The model chained five tools (`classify_matter`, `check_client_history`,
`find_similar_matters`, `suggest_staffing`, `flag_for_escalation`) and produced
a full intake. Three moments are worth slowing down on.

### 1. It distrusted a tool's output when the substance warranted

> *Matter type: Licensing Agreement Review. One caveat worth flagging: the
> automated classifier scored complexity as Routine because it only
> pattern-matched the word "licensing." Don't trust that number here. The
> substance — assignment of licensee improvements plus a broad grant — and the
> near-identical prior matter both point to Complex.*

The classifier is deterministic keyword matching, and a short description gave
it nothing to read complexity from. The model caught that, said so plainly,
and corrected the assessment on the substance. The deterministic layer is a
triage aid; the reasoning layer is expected to overrule it when context
warrants, and here it did.

### 2. It overrode the staffing recommendation on expertise grounds

> *The system's top capacity pick is James O'Brien, but his expertise is
> vendor/procurement, not licensing — so I'd override on expertise grounds:
> Recommended lead: Marcus Webb, Senior Counsel. He led the near-identical
> prior matter, and his expertise areas are MSA, licensing, and indemnification
> — a direct fit. Final call is yours.*

This is the design in one moment. `suggest_staffing` ranked O'Brien first on
its capacity-after-seniority logic, but it also *returned each candidate's
expertise areas* rather than hiding them behind a single score. The model read
that data, recognized the better substantive fit, cross-referenced the
near-identical prior matter that Webb had led, and recommended Webb instead,
explicitly flagging that it was overriding the ranking and that the decision
belonged to the user. A tool that had collapsed expertise into one number would
have produced a worse answer. Surfacing beats deciding.

### 3. It flagged escalation against the client's own stated threshold

> *Yes — escalation recommended. The tool flagged IP exposure, and that maps
> directly onto Vertex's own threshold of any IP assignment or licensing term.
> Escalate to Dr. Helena Voss, General Counsel. The deal as described contains
> two of the client's explicitly forbidden terms — this isn't a borderline
> call. In-house should be looped in before we take substantive positions.*

`flag_for_escalation` does not escalate and does not clear. It surfaces the
triggered signals, reports the client's *own* standing escalation threshold,
names the contact, and frames the recommendation as a human call. Here it
caught that the deal tripped two of Vertex's explicitly forbidden terms and
mapped that against the client's stated threshold, but it still left the
decision where it belongs.

## The principle: surface, reason, decide

Every tool returns structured signals *and the basis for them*: matched
keywords, ranked candidates with their underlying data, triggered escalation
signals alongside the client's stated threshold. Nothing returns a bare
verdict. This is what lets the reasoning layer do real work instead of
rubber-stamping, and it is what makes any recommendation inspectable and
defensible after the fact: not "the system said so," but "the system surfaced
these specific facts, and here is the reasoning over them."

## The tools

| Tool | Surfaces |
|---|---|
| `classify_matter` | ranked candidate matter types, with the signal phrases that matched |
| `find_similar_matters` | comparable past matters, ranked by type-match and same-client boost |
| `check_client_history` | client profile, standing preferences, recent matters, applicable templates |
| `get_matter_history` | full detail on a specific past matter |
| `suggest_staffing` | ranked lead-lawyer candidates **and the seniority, capacity, and expertise behind the ranking** |
| `flag_for_escalation` | triggered escalation signals **alongside the client's own stated threshold**: a flag for human judgment, never a decision |

A seventh tool, `ping`, is a liveness check.

## How it's built

```
server.py                     thin MCP surface, one wrapper per tool
legal_intake/
    taxonomy.py               service categories, matter types, keyword signals
    db.py                     SQLite storage; JSON-encoded columns for list/dict fields
    classifier.py             deterministic, word-boundary keyword classification
    queries.py                read tools (similar matters, client history, matter detail)
    staffing.py               judgment tools (staffing, escalation)
    seed_data.py              reference data: clients, teams, lawyers, templates
    matters_data.py           matter scenario pool
    seed.py                   deterministic seed generator
docs/
    design-decisions.md       why the system is built the way it is
```

Tool logic lives in the `legal_intake` package and is testable independently
of MCP; `server.py` is a thin wrapper that exposes each as a tool with a
description written for the model that reads it. The classifier is mechanical
by design: keyword matching with word boundaries, no model call inside the
tool, chosen for explainability, determinism, and a clean division of labor
with the reasoning layer. The rationale for that and every other significant
choice is in [`docs/design-decisions.md`](docs/design-decisions.md).

## The demo data

The server includes a deterministic, seeded mock dataset modeled on an ALSP
serving corporate in-house departments:

- **3 client companies** with deliberately contrasting profiles: a
  high-governance financial-services client that escalates readily, a
  high-throughput logistics client that runs on templates, and an IP-sensitive
  biotech client whose matters need senior staffing. The contrast is what lets
  the same matter type be handled differently depending on whose standing
  preferences apply.
- **69 matters** across those clients, generated to cluster realistically
  (several near-identical prior matters per client and type), which is what
  makes precedent retrieval meaningful.
- **6 service teams, 22 lawyers, 14 templates.**

The data is fictional. The patterns are not.

## Run it

Prerequisites: Python 3.11+, [Claude Desktop](https://claude.ai/download).

```bash
# 1. Clone and enter the project
git clone https://github.com/david-yamin-esq/legal-intake-mcp.git
cd legal-intake-mcp

# 2. Create and activate a virtual environment
python -m venv .venv
# macOS/Linux:
source .venv/bin/activate
# Windows (PowerShell):
.\.venv\Scripts\Activate.ps1

# 3. Install the MCP SDK
pip install "mcp[cli]"

# 4. Build the demo database
python -m legal_intake.seed
```

Then register the server with Claude Desktop. The standard way:

```bash
mcp install server.py --name "Legal Intake"
```

If that is unavailable in your environment, register it manually by adding this
to Claude Desktop's `claude_desktop_config.json` (use absolute paths, and on
Windows double every backslash):

```json
{
  "mcpServers": {
    "legal-intake": {
      "command": "/absolute/path/to/.venv/bin/python",
      "args": ["/absolute/path/to/server.py"]
    }
  }
}
```

Restart Claude Desktop, then try:

> *A new matter came in: review a master services agreement for a SaaS vendor,
> counterparty paper, expedited. Run full intake.*

## Status and scope

This is a proof of concept. It demonstrates architecture and judgment, not
production readiness: mock data, single-user, local over stdio, no
authentication, every tool read-only by design. A production version would
scale the data, harden the deployment, and add governed, audited write paths,
but it would keep the principle that the tools surface and people decide,
because in legal work that principle is the point. The boundaries are stated
plainly in [`docs/design-decisions.md`](docs/design-decisions.md).

It is a companion to a related project, an
[agentic hallucination detector](https://github.com/david-yamin-esq/agentic-hallucination-detector)
for legal AI output, which shares the same mechanical-first philosophy:
prefer deterministic, inspectable detection over model self-grading wherever
the problem allows it.

## License

MIT.
