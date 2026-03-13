type MapColumn = {
  label: string;
  title: string;
  items: string[];
};

type StackRow = {
  label: string;
  nodes: string[];
};

const heroMap: MapColumn[] = [
  {
    label: "Inputs",
    title: "Messy model package",
    items: ["Code", "Containers", "Docs", "Data", "Prior reviews", "Vendor artifacts"],
  },
  {
    label: "Engine",
    title: "Review resolution layer",
    items: ["Evidence graph", "Workflow resolver", "Coverage boundary", "Execution fabric"],
  },
  {
    label: "Output",
    title: "Validation opinion",
    items: ["Memo", "Findings", "Coverage", "Gap report"],
  },
];

const thesisPoints = [
  {
    title: "Messy inputs are the norm",
    copy:
      "Model validation does not begin with a perfect handoff. It begins with whatever the bank team or vendor can actually produce.",
  },
  {
    title: "The workflow should be inferred",
    copy:
      "The platform determines what kind of review can be defended from the evidence instead of forcing every model through the same checklist.",
  },
  {
    title: "The output should be decision-grade",
    copy:
      "The end state is not a transcript or an activity log. It is a memo, findings, coverage, and explicit gaps.",
  },
];

const operatingModel: MapColumn[] = [
  {
    label: "01",
    title: "Intake",
    items: ["Secure upload boundary", "Artifact inventory", "Provenance retained"],
  },
  {
    label: "02",
    title: "Discovery",
    items: ["Asset typing", "Scope mapping", "Runnable evidence", "Gap detection"],
  },
  {
    label: "03",
    title: "Resolution",
    items: ["Review mode selected", "Modules activated", "Coverage boundary set"],
  },
  {
    label: "04",
    title: "Execution",
    items: ["Runtime checks", "Document analysis", "Data profiling", "Benchmarking"],
  },
  {
    label: "05",
    title: "Work product",
    items: ["Validation memo", "Findings log", "Coverage summary", "Gap report"],
  },
];

const operatingNarrative = [
  {
    index: "01",
    title: "Intake the package as-is",
    copy:
      "The system accepts mixed packages from bank teams and vendors without requiring the inputs to be normalized first.",
  },
  {
    index: "02",
    title: "Build the evidence view",
    copy:
      "Artifacts are classified, linked to model scope, and evaluated for whether they support runtime, conceptual, or comparative review.",
  },
  {
    index: "03",
    title: "Resolve the applicable review path",
    copy:
      "The control plane decides which validation modules can actually be defended from the package supplied.",
  },
  {
    index: "04",
    title: "Run the modules",
    copy:
      "Execution services perform the specific review work the package supports, from runtime reproduction to documentation analysis and reason-code review.",
  },
  {
    index: "05",
    title: "Issue structured work product",
    copy:
      "The result is assembled into review-grade outputs with findings, coverage, and explicit evidence limits.",
  },
];

const architectureRows: StackRow[] = [
  {
    label: "External package",
    nodes: ["Bank team artifacts", "Vendor package", "Prior memos", "Data extracts"],
  },
  {
    label: "Control plane",
    nodes: ["Artifact intake", "Evidence graph", "Review planner", "Coverage ledger"],
  },
  {
    label: "Execution plane",
    nodes: ["Runtime sandbox", "Doc analysis", "Data profiling", "Benchmark service", "Reason-code review"],
  },
  {
    label: "Output layer",
    nodes: ["Validation memo", "Findings log", "Coverage summary", "Gap report"],
  },
];

const architectureNotes = [
  {
    title: "Control plane",
    copy:
      "Maps the package, determines what evidence is usable, and selects the review plan that can be defended.",
  },
  {
    title: "Execution plane",
    copy:
      "Runs the actual validation modules in isolated services rather than treating review as a workflow-only exercise.",
  },
  {
    title: "Output layer",
    copy:
      "Packages the result into structured work product with explicit scope and evidence boundaries.",
  },
];

const reviewModes = [
  {
    title: "Execution review",
    trigger: "When code or a runnable environment is present.",
    copy:
      "Supports reproduction, baseline comparison, benchmark checks, and execution-backed findings.",
  },
  {
    title: "Behavioral review",
    trigger: "When the package is opaque but still scorable.",
    copy:
      "Supports replay, profiling, segmentation, and explicit coverage limits without pretending the black box is transparent.",
  },
  {
    title: "Conceptual review",
    trigger: "When the package is primarily documentary.",
    copy:
      "Supports methodology assessment, consistency checks, data-level review, and a clear gap report for deeper execution-based review.",
  },
];

const outputCards = [
  {
    title: "Validation memo",
    copy: "The formal opinion: scope, conclusion, findings, and required actions.",
  },
  {
    title: "Coverage summary",
    copy: "A structured statement of what was supported, partial, or blocked by the package.",
  },
  {
    title: "Findings log",
    copy: "Named observations linked to the module that produced them and the evidence behind them.",
  },
  {
    title: "Gap report",
    copy: "The missing artifacts required to move from conceptual or behavioral review into fuller validation.",
  },
];

const comparisons = [
  {
    left: "Most systems help teams administer model review.",
    right: "This system is built to execute model review.",
  },
  {
    left: "Most systems assume the inputs are already clean.",
    right: "This system starts from the package the institution actually has.",
  },
  {
    left: "Most systems standardize process.",
    right: "This system resolves process from the evidence.",
  },
];

function ColumnMap({
  columns,
  className,
}: {
  columns: MapColumn[];
  className?: string;
}) {
  return (
    <div className={`column-map ${className ?? ""}`.trim()}>
      {columns.map((column) => (
        <article className="column-map__column" key={`${column.label}-${column.title}`}>
          <p className="column-map__label">{column.label}</p>
          <h3>{column.title}</h3>
          <ul className="column-map__list">
            {column.items.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
        </article>
      ))}
    </div>
  );
}

function StackDiagram({ rows }: { rows: StackRow[] }) {
  return (
    <div className="stack-diagram">
      {rows.map((row) => (
        <div className="stack-diagram__row" key={row.label}>
          <div className="stack-diagram__label">{row.label}</div>
          <div className="stack-diagram__nodes">
            {row.nodes.map((node) => (
              <div className="stack-diagram__node" key={node}>
                {node}
              </div>
            ))}
          </div>
        </div>
      ))}
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
            <span>Validation infrastructure for banks</span>
          </span>
        </a>

        <nav className="topbar__nav" aria-label="Primary">
          <a href="#operating-model">Operating model</a>
          <a href="#architecture">Architecture</a>
          <a href="#outputs">Outputs</a>
        </nav>
      </header>

      <section className="hero" id="top">
        <div className="hero__copy">
          <p className="eyebrow">Validation infrastructure for banks</p>
          <h1>From model package to validation opinion</h1>
          <p className="hero__subhead">
            Software that ingests messy model packages, resolves the review path the evidence
            supports, and produces decision-grade validation work product.
          </p>

          <div className="hero__actions">
            <a className="button button--primary" href="#operating-model">
              See the operating model
            </a>
            <a className="button button--secondary" href="#architecture">
              Review the architecture
            </a>
          </div>

          <p className="hero__aside">
            Not AI governance. Not workflow tracking. Software that performs model review work.
          </p>
        </div>

        <div className="hero__visual">
          <ColumnMap columns={heroMap} className="column-map--hero" />
        </div>
      </section>

      <div className="trust-line">
        Code. Containers. Docs. Data. Vendor packages. One review engine.
      </div>

      <section className="section section--thesis">
        <div className="section__intro">
          <p className="eyebrow">Thesis</p>
          <h2>Software that does the review</h2>
          <p>
            The wedge is narrow and concrete: turn an uneven model package into a defensible
            validation opinion.
          </p>
        </div>

        <div className="thesis-grid">
          {thesisPoints.map((point) => (
            <article className="thesis-card" key={point.title}>
              <h3>{point.title}</h3>
              <p>{point.copy}</p>
            </article>
          ))}
        </div>
      </section>

      <section className="section" id="operating-model">
        <div className="section__intro">
          <p className="eyebrow">Operating model</p>
          <h2>A review engine, not a system of record</h2>
          <p>
            The operating model is simple: ingest the package, build the evidence view, resolve
            the review path, execute the modules, and issue structured work product.
          </p>
        </div>

        <ColumnMap columns={operatingModel} />

        <div className="narrative-list">
          {operatingNarrative.map((step) => (
            <article className="narrative-row" key={step.index}>
              <span className="narrative-row__index">{step.index}</span>
              <h3>{step.title}</h3>
              <p>{step.copy}</p>
            </article>
          ))}
        </div>
      </section>

      <section className="section" id="architecture">
        <div className="section__intro">
          <p className="eyebrow">Architecture</p>
          <h2>Built like review infrastructure</h2>
          <p>
            The control plane decides what can be reviewed. The execution plane runs the modules.
            The output layer assembles the result into decision-grade artifacts.
          </p>
        </div>

        <StackDiagram rows={architectureRows} />

        <div className="architecture-notes">
          {architectureNotes.map((note) => (
            <article className="architecture-note" key={note.title}>
              <h3>{note.title}</h3>
              <p>{note.copy}</p>
            </article>
          ))}
        </div>
      </section>

      <section className="section">
        <div className="section__intro">
          <p className="eyebrow">Review modes</p>
          <h2>One architecture. Three review modes.</h2>
          <p>
            The system does not force a single validation workflow. It resolves the mode from the
            evidence available.
          </p>
        </div>

        <div className="mode-grid">
          {reviewModes.map((mode) => (
            <article className="mode-card" key={mode.title}>
              <p className="mode-card__trigger">{mode.trigger}</p>
              <h3>{mode.title}</h3>
              <p>{mode.copy}</p>
            </article>
          ))}
        </div>
      </section>

      <section className="section" id="outputs">
        <div className="section__intro">
          <p className="eyebrow">Outputs</p>
          <h2>The output is a review, not a transcript</h2>
          <p>The system produces work product a validation team can defend and a bank can use.</p>
        </div>

        <div className="output-grid">
          {outputCards.map((card) => (
            <article className="output-card" key={card.title}>
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
          <p className="eyebrow">Explore the system</p>
          <h2>See the operating model in full</h2>
          <p>
            A pitch surface for investors and design partners built around one idea: software that
            turns messy bank model packages into validation opinions.
          </p>
        </div>

        <div className="cta__actions">
          <a className="button button--primary" href="#operating-model">
            See the operating model
          </a>
          <a className="button button--secondary" href="#outputs">
            View output structure
          </a>
        </div>
      </section>
    </main>
  );
}
