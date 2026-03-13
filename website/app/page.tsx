type ModuleState = "active" | "partial" | "inactive";

type WorkflowModule = {
  name: string;
  state: ModuleState;
};

type ReviewOutput = {
  title: string;
  coverage: string;
  findings: string;
  notes: string[];
};

type ReviewCase = {
  id: string;
  label: string;
  thesis: string;
  artifacts: string[];
  modules: WorkflowModule[];
  output: ReviewOutput;
};

const heroArtifacts = [
  "Source code",
  "Runtime asset",
  "Methodology docs",
  "Sample data",
  "Prior memo",
  "Reason-code mapping",
];

const heroModules: WorkflowModule[] = [
  { name: "Discovery", state: "active" },
  { name: "Runtime review", state: "active" },
  { name: "Evidence resolution", state: "active" },
  { name: "Benchmarking", state: "partial" },
  { name: "Final memo", state: "active" },
];

const heroOutput: ReviewOutput = {
  title: "Validation opinion",
  coverage: "74% supported scope",
  findings: "05 findings",
  notes: [
    "Review path selected from the evidence supplied.",
    "Coverage stays explicit where the package is incomplete.",
  ],
};

const stages = [
  {
    title: "Upload",
    sentence: "Accepts mixed model artifacts from bank teams and vendors.",
  },
  {
    title: "Discover",
    sentence: "Identifies code, runtime assets, data, docs, baselines, and gaps.",
  },
  {
    title: "Resolve",
    sentence: "Selects the validation modules the evidence actually supports.",
  },
  {
    title: "Execute",
    sentence: "Runs the review and produces findings, coverage, and a memo.",
  },
];

const reviewCases: ReviewCase[] = [
  {
    id: "full-revalidation",
    label: "Full revalidation",
    thesis:
      "A comprehensive package resolves into a nearly complete revalidation workflow.",
    artifacts: [
      "src/model/",
      "runtime/model-image.tar",
      "test_sample.parquet",
      "baseline_metrics.json",
      "methodology.pdf",
    ],
    modules: [
      { name: "Change review", state: "active" },
      { name: "Runtime reproduction", state: "active" },
      { name: "Baseline comparison", state: "active" },
      { name: "Benchmark checks", state: "active" },
      { name: "Documentation alignment", state: "active" },
      { name: "Final memo generation", state: "active" },
    ],
    output: {
      title: "Full revalidation memo",
      coverage: "92% supported scope",
      findings: "07 findings",
      notes: [
        "Runtime and baseline evidence support a full memo.",
        "Coverage is nearly complete, with limited residual gaps.",
      ],
    },
  },
  {
    id: "black-box-review",
    label: "Black-box behavioral review",
    thesis:
      "An opaque runtime package narrows into behavioral review with explicit limits.",
    artifacts: [
      "runtime/scorer.tar",
      "run_harness.sh",
      "sample_inputs.csv",
      "output_schema.json",
      "method_note.pdf",
    ],
    modules: [
      { name: "Runtime replay", state: "active" },
      { name: "Output profiling", state: "active" },
      { name: "Segment analysis", state: "active" },
      { name: "Documentation review", state: "partial" },
      { name: "Baseline comparison", state: "inactive" },
      { name: "Final memo generation", state: "active" },
    ],
    output: {
      title: "Partial validation report",
      coverage: "58% supported scope",
      findings: "04 findings",
      notes: [
        "Runtime behavior can be profiled and segmented.",
        "Internal model evidence was not supplied.",
      ],
    },
  },
  {
    id: "conceptual-review",
    label: "Conceptual review",
    thesis:
      "A documentation-heavy package produces a conceptual review and a gap report.",
    artifacts: [
      "methodology.pdf",
      "model_card.pdf",
      "prior_validation.docx",
      "feature_dictionary.xlsx",
      "sample_data.parquet",
      "reason_codes.csv",
    ],
    modules: [
      { name: "Methodology review", state: "active" },
      { name: "Document consistency checks", state: "active" },
      { name: "Data profiling", state: "active" },
      { name: "Reason-code assessment", state: "active" },
      { name: "Runtime review", state: "inactive" },
      { name: "Gap report", state: "active" },
    ],
    output: {
      title: "Conceptual review memo",
      coverage: "63% supported scope",
      findings: "05 findings",
      notes: [
        "Documents, mappings, and sample data can be reconciled.",
        "Execution-based review remains blocked pending runnable artifacts.",
      ],
    },
  },
];

const outputCards = [
  {
    title: "Validation memo",
    copy: "The review document itself: scope, coverage, findings, and actions.",
  },
  {
    title: "Coverage summary",
    copy: "What ran, what stayed partial, and why.",
  },
  {
    title: "Findings log",
    copy: "Named observations tied to modules and evidence.",
  },
  {
    title: "Gap report",
    copy: "The missing artifacts required for deeper review.",
  },
];

const comparisons = [
  {
    left: "Most systems help teams track model reviews.",
    right: "This platform helps them run them.",
  },
  {
    left: "Most systems expect clean inputs.",
    right: "This platform starts with messy real-world packages.",
  },
  {
    left: "Most systems standardize workflows.",
    right: "This platform adapts the workflow to the evidence available.",
  },
];

function StatePill({ state }: { state: ModuleState }) {
  return <span className={`state-pill state-pill--${state}`}>{state}</span>;
}

function FlowVisual({
  artifacts,
  modules,
  output,
  labels,
}: {
  artifacts: string[];
  modules: WorkflowModule[];
  output: ReviewOutput;
  labels: {
    left: string;
    center: string;
    right: string;
  };
}) {
  return (
    <div className="flow-visual">
      <article className="flow-column">
        <p className="flow-column__label">{labels.left}</p>
        <ul className="flow-list">
          {artifacts.map((artifact) => (
            <li key={artifact} className="flow-row">
              {artifact}
            </li>
          ))}
        </ul>
      </article>

      <article className="flow-column">
        <p className="flow-column__label">{labels.center}</p>
        <div className="module-list">
          {modules.map((module) => (
            <div key={module.name} className="module-row">
              <span>{module.name}</span>
              <StatePill state={module.state} />
            </div>
          ))}
        </div>
      </article>

      <article className="flow-column flow-column--output">
        <p className="flow-column__label">{labels.right}</p>
        <h3>{output.title}</h3>
        <div className="output-stats">
          <div>
            <span>Coverage</span>
            <strong>{output.coverage}</strong>
          </div>
          <div>
            <span>Findings</span>
            <strong>{output.findings}</strong>
          </div>
        </div>
        <ul className="output-notes">
          {output.notes.map((note) => (
            <li key={note}>{note}</li>
          ))}
        </ul>
      </article>
    </div>
  );
}

export default function Home() {
  return (
    <main className="page-shell">
      <header className="topbar">
        <a className="brand" href="#top">
          <span className="brand__mark">AMV</span>
          <span className="brand__copy">
            <strong>Agentic Model Validation</strong>
            <span>Bank model review software</span>
          </span>
        </a>

        <nav className="topbar__nav" aria-label="Primary">
          <a href="#workflow">How it works</a>
          <a href="#proof">Proof</a>
          <a href="#outputs">Outputs</a>
        </nav>
      </header>

      <section className="hero" id="top">
        <div className="hero__copy">
          <p className="eyebrow">Model review software</p>
          <h1>From model package to validation opinion</h1>
          <p className="hero__subhead">
            Banks upload code, containers, docs, data, or vendor artifacts. The platform
            discovers what&apos;s there, runs the applicable validation workflow, and produces a
            defensible review.
          </p>

          <div className="hero__actions">
            <a className="button button--primary" href="#proof">
              See three review paths
            </a>
            <a className="button button--secondary" href="#outputs">
              View example outputs
            </a>
          </div>
        </div>

        <div className="hero__band">
          <p className="hero__band-note">
            One engine decides what review the package supports.
          </p>
          <FlowVisual
            artifacts={heroArtifacts}
            modules={heroModules}
            output={heroOutput}
            labels={{
              left: "Package signals",
              center: "Review path",
              right: "Opinion out",
            }}
          />
        </div>
      </section>

      <div className="trust-line">
        Code. Containers. Docs. Data. Vendor packages. One review engine.
      </div>

      <section className="section section--workflow" id="workflow">
        <div className="section__intro">
          <p className="eyebrow">How it works</p>
          <h2>A review engine, not a workflow form</h2>
          <p>
            It reads the package, determines what the evidence supports, and runs the review that
            can actually be defended.
          </p>
        </div>

        <div className="stage-rail">
          {stages.map((stage, index) => (
            <article className="stage-row" key={stage.title}>
              <span className="stage-row__index">0{index + 1}</span>
              <h3>{stage.title}</h3>
              <p>{stage.sentence}</p>
            </article>
          ))}
        </div>
      </section>

      <section className="section section--proof" id="proof">
        <div className="section__intro">
          <p className="eyebrow">Proof</p>
          <h2>Same platform. Different reviews.</h2>
          <p>
            The workflow changes with the evidence. Same engine, different review paths.
          </p>
        </div>

        <div className="proof-stack">
          {reviewCases.map((reviewCase, index) => (
            <section className="proof-chapter" key={reviewCase.id}>
              <div className="proof-chapter__header">
                <span className="proof-chapter__index">0{index + 1}</span>
                <div>
                  <h3>{reviewCase.label}</h3>
                  <p>{reviewCase.thesis}</p>
                </div>
              </div>

              <FlowVisual
                artifacts={reviewCase.artifacts}
                modules={reviewCase.modules}
                output={reviewCase.output}
                labels={{
                  left: "Package",
                  center: "Workflow",
                  right: "Output",
                }}
              />
            </section>
          ))}
        </div>
      </section>

      <section className="section" id="outputs">
        <div className="section__intro">
          <p className="eyebrow">Outputs</p>
          <h2>The output is a review, not a transcript</h2>
          <p>The system produces work product a validation team can use.</p>
        </div>

        <div className="output-grid">
          {outputCards.map((card) => (
            <article className="output-summary" key={card.title}>
              <h3>{card.title}</h3>
              <p>{card.copy}</p>
            </article>
          ))}
        </div>
      </section>

      <section className="section">
        <div className="section__intro">
          <p className="eyebrow">Positioning</p>
          <h2>Execution, not just oversight</h2>
        </div>

        <div className="comparison-list">
          {comparisons.map((comparison) => (
            <article className="comparison-row" key={comparison.left}>
              <p>{comparison.left}</p>
              <strong>{comparison.right}</strong>
            </article>
          ))}
        </div>
      </section>

      <section className="cta">
        <div className="cta__copy">
          <p className="eyebrow">Explore the product</p>
          <h2>See the platform on three model packages</h2>
          <p>Software that turns messy bank model packages into validation opinions.</p>
        </div>

        <div className="cta__actions">
          <a className="button button--primary" href="#proof">
            See the platform on three model packages
          </a>
          <a className="button button--secondary" href="#outputs">
            View example outputs
          </a>
        </div>
      </section>
    </main>
  );
}
