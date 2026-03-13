"use client";

import { useState } from "react";

type Benefit = {
  title: string;
  copy: string;
  inverted?: boolean;
};

type Mode = {
  id: string;
  label: string;
  headline: string;
  summary: string;
  artifacts: string[];
  modules: string[];
  outputs: string[];
};

type Stage = {
  label: string;
  title: string;
  copy: string;
};

type ArchitectureCard = {
  title: string;
  copy: string;
};

const benefits: Benefit[] = [
  {
    title: "A constrained agent loop",
    copy:
      "The review engine works through fixed stages for discovery, resolution, execution, and reporting instead of relying on an open-ended chat flow.",
    inverted: true,
  },
  {
    title: "Skill-grounded planning",
    copy:
      "Each stage loads its own review instructions and module rules so the plan comes from the evidence package, not from a generic workflow template.",
  },
  {
    title: "Tool-backed execution",
    copy:
      "Runtime reruns, documentation cross-checks, data profiling, and comparison work happen through deterministic tools and isolated review steps.",
  },
  {
    title: "Deliverables with support behind them",
    copy:
      "The platform assembles the stakeholder memo together with a support pack of evidence maps, findings, coverage, provenance, and trace artifacts.",
  },
];

const modes: Mode[] = [
  {
    id: "full",
    label: "Full revalidation",
    headline: "A comprehensive package resolves into a full, execution-backed review.",
    summary:
      "When the package includes code, runtime assets, documentation, and baselines, the platform activates a near-complete revalidation path.",
    artifacts: ["Source code", "Runtime image", "Sample data", "Baseline metrics", "Methodology docs"],
    modules: [
      "Change review",
      "Runtime reproduction",
      "Baseline comparison",
      "Benchmark checks",
      "Documentation alignment",
    ],
    outputs: ["Revalidation memo", "Findings log", "Coverage summary", "Residual gap note"],
  },
  {
    id: "behavioral",
    label: "Behavioral review",
    headline: "An opaque package narrows into behavioral validation with clearly defined limits.",
    summary:
      "When the institution has a scorer or container but not internals, the platform shifts to replay, profiling, segmentation, and scoped findings.",
    artifacts: ["Scoring harness", "Container image", "Sample inputs", "Output schema", "Method note"],
    modules: [
      "Runtime replay",
      "Output profiling",
      "Segment analysis",
      "Limited documentation review",
      "Coverage boundary",
    ],
    outputs: ["Behavioral review memo", "Coverage limits", "Findings", "Missing evidence list"],
  },
  {
    id: "conceptual",
    label: "Conceptual review",
    headline: "A documentation-heavy package becomes a conceptual review with a clear path to deeper validation.",
    summary:
      "When the package is primarily documentary, the platform performs methodology review, consistency checks, data profiling, and reason-code assessment.",
    artifacts: ["Methodology docs", "Model card", "Prior memo", "Feature dictionary", "Reason-code mapping"],
    modules: [
      "Methodology review",
      "Document consistency checks",
      "Data profiling",
      "Reason-code assessment",
      "Gap report",
    ],
    outputs: ["Conceptual memo", "Findings", "Coverage statement", "Execution prerequisites"],
  },
];

const operatingStages: Stage[] = [
  {
    label: "Case intake",
    title: "The upload becomes a case, not just a folder",
    copy:
      "A bank or vendor package is materialized into a review workspace with input artifacts, outputs, and a structured case record.",
  },
  {
    label: "Discovery",
    title: "Codex scans the package into evidence",
    copy:
      "Artifacts are inventoried, typed, excerpted, and converted into a normalized evidence view with capability hints and gap signals.",
  },
  {
    label: "Resolution",
    title: "Skills and module rules determine the plan",
    copy:
      "The agent loads stage-specific skills and a module catalog, then marks what is executable, partial, or blocked before review work begins.",
  },
  {
    label: "Execution",
    title: "Tools run the work and the opinion is assembled",
    copy:
      "Deterministic review procedures, trace files, and support artifacts accumulate into coverage, findings, and a defensible validation deliverable.",
  },
];

const architectureCards: ArchitectureCard[] = [
  {
    title: "Case workspace",
    copy:
      "Every run has a persistent case record, a local workspace, and separate input and output boundaries. That gives the agent stable operating context from the first scan through the final memo.",
  },
  {
    title: "Skill registry",
    copy:
      "Discovery, playbook resolution, execution, and reporting each load explicit skill files. The agent is flexible because the stage behavior is encoded, not because the loop is unconstrained.",
  },
  {
    title: "Tool bridge",
    copy:
      "Execution routes through a Python bridge into deterministic review tools for reruns, comparisons, profiling, and document analysis. Optional sidecar analysis stays outside the core control loop.",
  },
  {
    title: "Support pack",
    copy:
      "The system writes the review plan, evidence map, findings register, coverage statement, artifact provenance, and trace alongside the stakeholder-facing opinion.",
  },
];

const assuranceCards = [
  {
    title: "Frontier capability with hard edges",
    copy:
      "The agent can interpret mixed packages, form a plan, and adapt the review path, but it does so inside explicit stages, skills, and tools.",
  },
  {
    title: "Previous deliverables stay in play",
    copy:
      "Prior outputs, baseline files, previous memos, and support artifacts can remain part of the case and inform what the next review cycle can support.",
  },
  {
    title: "The output is more than a memo",
    copy:
      "Banks get a review opinion, while model risk teams get the support record that explains how the system reached it and where coverage stopped.",
  },
];

const footerColumns = [
  {
    heading: "Platform",
    links: ["Operating model", "Architecture", "Outputs"],
  },
  {
    heading: "Review modes",
    links: ["Full revalidation", "Behavioral review", "Conceptual review"],
  },
  {
    heading: "Deployment",
    links: ["Cloud", "Private environment", "Bank controls"],
  },
  {
    heading: "Outputs",
    links: ["Validation memo", "Coverage summary", "Findings log"],
  },
];

const supportArtifacts = [
  "Review plan",
  "Evidence map",
  "Findings register",
  "Coverage statement",
  "Artifact provenance",
  "Codex trace",
];

function ProductCanvas() {
  return (
    <div className="product-canvas">
      <div className="product-canvas__toolbar">
        <span />
        <span />
        <span />
      </div>

      <div className="product-canvas__frame">
        <aside className="product-canvas__sidebar">
          <div className="product-canvas__sidebar-label">Package</div>
          <div className="product-canvas__item">code/</div>
          <div className="product-canvas__item">runtime/image.tar</div>
          <div className="product-canvas__item">methodology.pdf</div>
          <div className="product-canvas__item">sample.parquet</div>
          <div className="product-canvas__item">prior_memo.docx</div>
        </aside>

        <div className="product-canvas__graph">
          <div className="product-canvas__node product-canvas__node--large">Case record</div>
          <div className="product-canvas__node">Discovery skill</div>
          <div className="product-canvas__node">Playbook resolver</div>
          <div className="product-canvas__node">Execution skill</div>
          <div className="product-canvas__node">Evidence ledger</div>
          <div className="product-canvas__node">Support pack</div>
        </div>

        <aside className="product-canvas__inspector">
          <div className="product-canvas__sidebar-label">Opinion</div>
          <div className="product-canvas__stat">
            <span>Stages</span>
            <strong>04</strong>
          </div>
          <div className="product-canvas__stat">
            <span>Outputs</span>
            <strong>02</strong>
          </div>
          <div className="product-canvas__memo">
            Stakeholder memo
            <br />
            Support artifacts
            <br />
            Trace files
          </div>
        </aside>
      </div>
    </div>
  );
}

function ModeVisual({ mode }: { mode: Mode }) {
  return (
    <div className="mode-visual">
      <div className="mode-visual__column">
        <p>Package</p>
        {mode.artifacts.map((item) => (
          <div className="mode-visual__chip" key={item}>
            {item}
          </div>
        ))}
      </div>

      <div className="mode-visual__column">
        <p>Modules</p>
        {mode.modules.map((item) => (
          <div className="mode-visual__chip mode-visual__chip--active" key={item}>
            {item}
          </div>
        ))}
      </div>

      <div className="mode-visual__column mode-visual__column--output">
        <p>Outputs</p>
        {mode.outputs.map((item) => (
          <div className="mode-visual__chip mode-visual__chip--output" key={item}>
            {item}
          </div>
        ))}
      </div>
    </div>
  );
}

function ArchitectureMap() {
  return (
    <div className="agent-system">
      <div className="agent-system__board">
        <section className="agent-system__column">
          <p className="agent-system__label">Bank package</p>
          <h5>Upload whatever exists</h5>
          <div className="agent-system__stack">
            <div className="agent-system__chip">code</div>
            <div className="agent-system__chip">containers</div>
            <div className="agent-system__chip">docs</div>
            <div className="agent-system__chip">sample data</div>
            <div className="agent-system__chip">vendor artifacts</div>
            <div className="agent-system__chip">prior memos</div>
          </div>
        </section>

        <section className="agent-system__column agent-system__column--core">
          <p className="agent-system__label">Codex review engine</p>
          <h5>Scan, plan, execute, synthesize</h5>
          <div className="agent-system__sequence">
            <div className="agent-system__step">
              <strong>1. Create case</strong>
              <span>Workspace, input boundary, output boundary, case record</span>
            </div>
            <div className="agent-system__step">
              <strong>2. Discovery</strong>
              <span>Artifact inventory, evidence typing, capability hints, gap signals</span>
            </div>
            <div className="agent-system__step">
              <strong>3. Resolve</strong>
              <span>Module states, supported workflow, executable scope</span>
            </div>
            <div className="agent-system__step">
              <strong>4. Execute and report</strong>
              <span>Tool calls, findings, coverage, stakeholder memo, support pack</span>
            </div>
          </div>
        </section>

        <section className="agent-system__column">
          <p className="agent-system__label">Skills and tools</p>
          <h5>Ground the reasoning</h5>
          <div className="agent-system__stack">
            <div className="agent-system__mini">
              <strong>Stage skills</strong>
              <span>Discovery, playbook, execution, report</span>
            </div>
            <div className="agent-system__mini">
              <strong>Module catalog</strong>
              <span>Executable, partial, blocked review paths</span>
            </div>
            <div className="agent-system__mini">
              <strong>Bridge tools</strong>
              <span>Runtime, data, document, benchmark, comparison work</span>
            </div>
            <div className="agent-system__mini">
              <strong>Optional sidecar</strong>
              <span>Large-document analysis outside the core engine</span>
            </div>
          </div>
        </section>

        <section className="agent-system__column">
          <p className="agent-system__label">Deliverables</p>
          <h5>Issue the opinion with support behind it</h5>
          <div className="agent-system__stack">
            <div className="agent-system__chip agent-system__chip--output">Validation memo</div>
            <div className="agent-system__chip agent-system__chip--output">Findings register</div>
            <div className="agent-system__chip agent-system__chip--output">Coverage statement</div>
            <div className="agent-system__chip agent-system__chip--output">Evidence map</div>
            <div className="agent-system__chip agent-system__chip--output">Artifact provenance</div>
            <div className="agent-system__chip agent-system__chip--output">Trace files</div>
          </div>
        </section>
      </div>

      <div className="agent-system__support">
        <div className="agent-system__support-copy">
          <p className="agent-system__label">Support record</p>
          <h5>The agent keeps a working memory that survives the review</h5>
          <span>
            Case records, evidence ledgers, prior deliverables, planned procedures, tool outputs,
            and stage traces stay attached to the review so the system can justify both what it did
            and what it could not do.
          </span>
        </div>

        <div className="agent-system__support-chips">
          {supportArtifacts.map((item) => (
            <div className="agent-system__support-chip" key={item}>
              {item}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

export default function Home() {
  const [activeMode, setActiveMode] = useState<Mode>(modes[0]);

  return (
    <main className="site-shell">
      <div className="announcement-bar">
        <p>
          Read the latest platform thesis on turning fragmented model packages into review-grade
          validation output.
        </p>
        <a href="#architecture">See the architecture</a>
      </div>

      <header className="site-header">
        <a className="site-header__brand" href="#top">
          <span className="site-header__mark">AMV</span>
          <span>Agentic Model Validation</span>
        </a>

        <nav className="site-header__nav" aria-label="Primary">
          <a href="#platform">Platform</a>
          <a href="/demo">Demo</a>
          <a href="#architecture">Architecture</a>
        </nav>

        <a className="site-header__cta" href="#contact">
          Contact
        </a>
      </header>

      <section className="hero" id="top">
        <div className="hero__ornament hero__ornament--left" />
        <div className="hero__ornament hero__ornament--right" />

        <div className="hero__eyebrow">Built for model risk and validation teams</div>
        <h1>
          <span>From model package</span>
          <span>to validation opinion</span>
        </h1>
        <p className="hero__tagline">
          Bank artifacts go in. A staged review engine determines the defensible workflow, executes
          it, and returns the opinion with its support record.
        </p>
      </section>

      <section className="platform-intro" id="platform">
        <div className="platform-intro__copy">
          <p className="platform-intro__eyebrow">With</p>
          <h2>The Review Engine</h2>
          <p>
            This is not a workflow form wrapped around a language model. It is a case-driven
            system that scans a bank package, resolves what the evidence supports, executes the
            review work through constrained tools, and assembles both the memo and the support
            pack behind it.
          </p>
        </div>

        <div className="platform-intro__visual">
          <ProductCanvas />
          <p className="platform-intro__caption">Package to case to opinion</p>
        </div>
      </section>

      <section className="benefit-grid">
        {benefits.map((benefit) => (
          <article
            className={`benefit-card${benefit.inverted ? " benefit-card--inverted" : ""}`}
            key={benefit.title}
          >
            <div className="benefit-card__icon" />
            <h3>{benefit.title}</h3>
            <p>{benefit.copy}</p>
          </article>
        ))}
      </section>

      <section className="editorial-section">
        <div className="editorial-section__copy">
          <h4>An operating loop designed for messy bank packages</h4>
          <p>
            The system starts with real package conditions: mixed artifacts, incomplete evidence,
            prior deliverables, and uncertain runtime support. The review stays adaptive because
            the evidence stays explicit.
          </p>
        </div>

        <div className="editorial-section__diagram editorial-section__diagram--wide">
          <div className="rail-card">
            {operatingStages.map((stage) => (
              <div className="rail-card__group" key={stage.title}>
                <span>{stage.label}</span>
                <strong>{stage.title}</strong>
                <p>{stage.copy}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="tabbed-section">
        <h4>One engine. Different review paths.</h4>

        <div className="tabbed-section__controls" role="tablist" aria-label="Review modes">
          {modes.map((mode) => (
            <button
              key={mode.id}
              type="button"
              role="tab"
              aria-selected={mode.id === activeMode.id}
              className={`tabbed-section__tab${mode.id === activeMode.id ? " is-active" : ""}`}
              onClick={() => setActiveMode(mode)}
            >
              {mode.label}
            </button>
          ))}
        </div>

        <p className="tabbed-section__summary">{activeMode.summary}</p>

        <div className="tabbed-section__panel">
          <div className="tabbed-section__panel-copy">
            <h5>{activeMode.headline}</h5>
            <p>
              The planning layer changes because the package changes. That is the central product
              thesis in this repo and the reason the same engine can handle both rich and partial
              validation cases.
            </p>
          </div>

          <div className="tabbed-section__panel-visual">
            <ModeVisual mode={activeMode} />
            <p>Switch cases to see how artifacts, modules, and outputs reconfigure.</p>
          </div>
        </div>
      </section>

      <section className="section-heading" id="architecture">
        <h4>The frontier piece is not free-form generation. It is constrained review execution.</h4>
        <p>
          The architecture turns a mixed upload into a review by combining case state, stage
          skills, deterministic tools, prior deliverables, and a support record that survives the
          run. That is what makes the agent both adaptive and legible.
        </p>
      </section>

      <section className="architecture-diagram">
        <ArchitectureMap />
      </section>

      <section className="architecture-details">
        {architectureCards.map((card) => (
          <article className="architecture-detail" key={card.title}>
            <h5>{card.title}</h5>
            <p>{card.copy}</p>
          </article>
        ))}
      </section>

      <section className="section-heading" id="operating-model">
        <h4>Why this behaves like review infrastructure, not a chat session</h4>
        <p>
          The system can do frontier-style planning and adaptation, but the work is bounded by
          case state, stage rules, tool calls, and output obligations. That is the operating model.
        </p>
      </section>

      <section className="security-grid">
        {assuranceCards.map((card) => (
          <article className="security-card" key={card.title}>
            <div className="security-card__icon" />
            <h6>{card.title}</h6>
            <p>{card.copy}</p>
          </article>
        ))}
      </section>

      <section className="cta-banner" id="contact">
        <div className="cta-banner__spark" />
        <h2>Looking for validation infrastructure that can actually run the review?</h2>
        <a href="/demo">Explore the demo</a>
      </section>

      <footer className="site-footer">
        <div className="site-footer__brand">
          <span>AMV</span>
          <p>Agentic Model Validation</p>
        </div>

        <div className="site-footer__links">
          {footerColumns.map((column) => (
            <div key={column.heading}>
              <p>{column.heading}</p>
              {column.links.map((link) => (
                <span key={link}>{link}</span>
              ))}
            </div>
          ))}
        </div>

        <div className="site-footer__meta">
          <p>Designed for model risk, validation teams, and engineering groups operating in banks.</p>
          <p>© 2026 Agentic Model Validation</p>
        </div>
      </footer>
    </main>
  );
}
