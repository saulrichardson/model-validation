const workflowStages = [
  {
    phase: "Stage 01",
    title: "Discovery",
    body:
      "Inventory the package as it exists: code, documents, datasets, metrics, model artifacts, notebooks, configs, and runtime evidence.",
  },
  {
    phase: "Stage 02",
    title: "Playbook Resolution",
    body:
      "Resolve which validation modules are executable, partial, or blocked based on the evidence that is actually present.",
  },
  {
    phase: "Stage 03",
    title: "Tool Execution",
    body:
      "Run the supported subset through local evidence tools and bounded sidecar calls instead of pretending unsupported checks happened.",
  },
  {
    phase: "Stage 04",
    title: "Bank-Facing Report",
    body:
      "Draft a memo with findings, recommended actions, coverage rationale, evidence requests, and a clear boundary around unsupported scope.",
  },
];

const reviewTracks = [
  {
    title: "Material Change Revalidation",
    summary:
      "For packages that include baseline and candidate versions, runnable code, metrics, and supporting documentation.",
    notes: [
      "Supports a full material-change revalidation memo.",
      "Designed around baseline-versus-candidate comparison.",
      "Includes sensitivity and stress-ready artifacts in the seeded path.",
    ],
  },
  {
    title: "Documentation-Led Conceptual Review",
    summary:
      "For documentation-heavy submissions where the implementation is missing, incomplete, or not runnable.",
    notes: [
      "Focuses on conceptual readiness and documentation consistency.",
      "Surfaces evidence gaps instead of manufacturing coverage.",
      "Benchmarks rubric-style readiness before final synthesis.",
    ],
  },
  {
    title: "Vendor Black-Box Behavioral Review",
    summary:
      "For opaque vendor packages where a runtime harness exists but conceptual internals remain unavailable.",
    notes: [
      "Supports partial validation rather than false completeness.",
      "Uses executable runtime behavior as the primary review surface.",
      "Highlights missing design evidence and reason-code issues explicitly.",
    ],
  },
];

const outputSurfaces = [
  "Normalized case record",
  "Playbook decisions by module",
  "Agent stage summaries",
  "Tool-call ledger",
  "Evidence ledger",
  "Key findings",
  "Coverage boundary and memo",
];

const evidenceTypes = [
  "Code",
  "Documents",
  "Datasets",
  "Metrics",
  "Models",
  "Notebooks",
  "Configs",
  "Containers",
];

export default function Home() {
  return (
    <main className="site-shell">
      <header className="site-header">
        <a className="brand-mark" href="#top">
          <span className="brand-mark__chip">MV</span>
          <span className="brand-mark__text">
            <strong>Model Validation</strong>
            <span>Artifact-first workbench</span>
          </span>
        </a>
        <nav className="site-nav" aria-label="Primary">
          <a href="#workflow">Workflow</a>
          <a href="#tracks">Review Modes</a>
          <a href="#deliverables">Deliverables</a>
        </nav>
      </header>

      <section className="hero" id="top">
        <div className="hero-copy">
          <p className="eyebrow">Bank Model Validation</p>
          <h1>Validation for the package you actually received.</h1>
          <p className="hero-body">
            Upload the messy mix of artifacts that landed on your desk. The workbench discovers
            what is present, resolves which checks are defensibly supported, executes the supported
            subset, and drafts a bank-facing memo with explicit coverage boundaries.
          </p>
          <div className="hero-actions">
            <a className="button button--primary" href="#workflow">
              See the workflow
            </a>
            <a className="button button--ghost" href="#tracks">
              Review supported paths
            </a>
          </div>
          <dl className="hero-metrics" aria-label="Platform highlights">
            <div>
              <dt>04</dt>
              <dd>staged phases from discovery to report</dd>
            </div>
            <div>
              <dt>03</dt>
              <dd>implemented review paths in the seeded demos</dd>
            </div>
            <div>
              <dt>01</dt>
              <dd>bank-facing memo with a stated coverage boundary</dd>
            </div>
          </dl>
        </div>

        <div className="hero-board" aria-label="Operator board">
          <div className="board-note board-note--signal">
            <span className="board-note__label">Intake</span>
            <h2>Messy evidence in</h2>
            <p>
              Model packages arrive incomplete, inconsistent, and mixed across code, documents,
              metrics, and runtime artifacts.
            </p>
          </div>

          <div className="board-stack">
            <article className="board-card">
              <span className="board-card__kicker">Supported evidence</span>
              <div className="token-row">
                {evidenceTypes.map((item) => (
                  <span key={item} className="token">
                    {item}
                  </span>
                ))}
              </div>
            </article>

            <article className="board-card">
              <span className="board-card__kicker">Output discipline</span>
              <ul className="compact-list">
                <li>Executable modules are separated from partial and blocked scope.</li>
                <li>Coverage ratio and rationale are surfaced, not hidden.</li>
                <li>Evidence requests stay attached to the final memo.</li>
              </ul>
            </article>

            <article className="board-card board-card--memo">
              <span className="board-card__kicker">Final deliverable</span>
              <h3>Coverage Boundary</h3>
              <p>
                The report states what was reviewed, what was executed, what was blocked, and what
                still needs evidence.
              </p>
            </article>
          </div>
        </div>
      </section>

      <section className="signal-strip" aria-label="Proof points">
        <p>Artifact-first intake</p>
        <p>Executable, partial, or blocked modules</p>
        <p>Evidence ledger and tool trace</p>
        <p>Bank-facing memo with recommended actions</p>
      </section>

      <section className="statement-grid">
        <article className="statement-card">
          <p className="eyebrow">Why This Surface Exists</p>
          <h2>Not a generic chatbot. A staged analyst workflow.</h2>
          <p>
            The underlying platform already models discovery, playbook resolution, execution, and
            reporting as separate stages. The homepage should therefore sell disciplined workflow,
            evidence handling, and explicit limits instead of vague AI automation.
          </p>
        </article>

        <article className="statement-card statement-card--accent">
          <p className="eyebrow">Current Positioning</p>
          <h2>Built for bank operators working through evidence gaps.</h2>
          <p>
            The current repo artifacts support three concrete review paths: full material-change
            revalidation, documentation-led conceptual review, and vendor black-box behavioral
            review.
          </p>
        </article>
      </section>

      <section className="section-shell" id="workflow">
        <div className="section-heading">
          <p className="eyebrow">Workflow</p>
          <h2>Four stages, each with a narrower claim than the last.</h2>
          <p>
            The workbench earns confidence by reducing ambiguity at each step instead of skipping
            directly to a polished conclusion.
          </p>
        </div>

        <div className="workflow-grid">
          {workflowStages.map((stage) => (
            <article className="workflow-card" key={stage.title}>
              <p className="workflow-card__phase">{stage.phase}</p>
              <h3>{stage.title}</h3>
              <p>{stage.body}</p>
            </article>
          ))}
        </div>
      </section>

      <section className="section-shell section-shell--dense" id="tracks">
        <div className="section-heading">
          <p className="eyebrow">Review Modes</p>
          <h2>Three public-facing use cases already grounded in demo artifacts.</h2>
          <p>
            These modes map directly to the seeded packages currently represented in the project,
            which makes them safer homepage claims than hypothetical future features.
          </p>
        </div>

        <div className="tracks-grid">
          {reviewTracks.map((track) => (
            <article className="track-card" key={track.title}>
              <h3>{track.title}</h3>
              <p>{track.summary}</p>
              <ul className="track-list">
                {track.notes.map((note) => (
                  <li key={note}>{note}</li>
                ))}
              </ul>
            </article>
          ))}
        </div>
      </section>

      <section className="deliverables" id="deliverables">
        <div className="deliverables-copy">
          <p className="eyebrow">Deliverables</p>
          <h2>Operator surfaces stay close to the evidence.</h2>
          <p>
            The current workbench UI and report schema already expose the outputs below. A public
            front page should frame these as evidence products, not decorative dashboards.
          </p>
          <ul className="deliverables-list">
            {outputSurfaces.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
        </div>

        <article className="memo-preview" aria-label="Memo preview">
          <div className="memo-preview__topline">
            <span>Validation Memo</span>
            <span>Coverage stated explicitly</span>
          </div>
          <h3>Partial validation is still useful when the boundary is honest.</h3>
          <p>
            The reporting layer already carries scope, modules executed, modules blocked, findings,
            evidence requests, key metrics, and recommended actions into a single bank-facing memo.
          </p>
          <div className="memo-preview__grid">
            <div>
              <strong>Scope</strong>
              <p>Only supported checks are executed.</p>
            </div>
            <div>
              <strong>Findings</strong>
              <p>Each finding keeps evidence references attached.</p>
            </div>
            <div>
              <strong>Boundary</strong>
              <p>Unsupported modules remain visible and named.</p>
            </div>
            <div>
              <strong>Next Actions</strong>
              <p>Evidence requests and follow-ups stay in the report.</p>
            </div>
          </div>
        </article>
      </section>

      <section className="boundary-banner">
        <div>
          <p className="eyebrow">Coverage Discipline</p>
          <h2>When the evidence is thin, the system should narrow scope, not bluff.</h2>
        </div>
        <div className="boundary-banner__badges">
          <span>Executable</span>
          <span>Partial</span>
          <span>Blocked</span>
        </div>
      </section>
    </main>
  );
}
