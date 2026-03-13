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

const benefits: Benefit[] = [
  {
    title: "Resolve the review path from the package",
    copy:
      "The engine maps code, containers, documents, data, and vendor artifacts into a usable evidence view.",
    inverted: true,
  },
  {
    title: "Execute real validation modules",
    copy:
      "Runtime checks, conceptual review, baseline comparison, and reason-code assessment run in one system.",
  },
  {
    title: "Set the coverage boundary explicitly",
    copy:
      "The platform states what the evidence supports, where the review remains partial, and what is still blocked.",
  },
  {
    title: "Produce decision-grade work product",
    copy: "Validation memos, findings, coverage summaries, and gap reports are generated as outputs.",
  },
];

const modes: Mode[] = [
  {
    id: "full",
    label: "Full revalidation",
    headline: "A comprehensive package resolves into full execution-backed review.",
    summary:
      "When the package includes code, runtime assets, documentation, and baselines, the engine activates a near-complete revalidation path.",
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
    headline: "An opaque package narrows into behavioral validation with explicit limits.",
    summary:
      "When the bank has a scorer or container but not internals, the engine switches to replay, profiling, segmentation, and scoped findings.",
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
    headline: "A documentation-heavy package becomes a conceptual review plus gap report.",
    summary:
      "When the package is primarily documentary, the engine performs methodology review, consistency checks, data profiling, and reason-code assessment.",
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

const operatingCards = [
  {
    label: "Package intake",
    title: "Accept messy model packages as-is",
    copy:
      "Mixed bank and vendor artifacts are ingested without forcing the team to normalize everything up front.",
  },
  {
    label: "Evidence mapping",
    title: "Build the evidence view",
    copy:
      "Assets are typed, linked to model scope, and checked for whether they support runtime, conceptual, or comparative review.",
  },
  {
    label: "Review resolution",
    title: "Select the applicable path",
    copy:
      "The control layer determines which modules can actually be defended from the package provided.",
  },
];

const architectureMarkers = [
  {
    title: "Application layer",
    copy: "Interfaces for bank teams, model risk, and engineers to submit packages and review outputs.",
  },
  {
    title: "Control plane",
    copy: "Artifact intake, evidence graphing, workflow resolution, and coverage accounting.",
  },
  {
    title: "Execution plane",
    copy: "Isolated services that run runtime, data, document, benchmark, and reason-code review modules.",
  },
];

const securityCards = [
  {
    title: "Isolated execution",
    copy:
      "Runtime review and model reproduction run in controlled environments instead of mixing bank artifacts into a generic orchestration stack.",
  },
  {
    title: "Deployment flexibility",
    copy:
      "The architecture can be deployed to fit enterprise control boundaries while preserving a single review model.",
  },
  {
    title: "Evidence traceability",
    copy:
      "Findings, coverage, and output documents remain tied to artifacts and review modules rather than free-form operator notes.",
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
          <div className="product-canvas__node product-canvas__node--large">Evidence graph</div>
          <div className="product-canvas__node">Workflow resolver</div>
          <div className="product-canvas__node">Coverage ledger</div>
          <div className="product-canvas__node">Runtime review</div>
          <div className="product-canvas__node">Doc analysis</div>
          <div className="product-canvas__node">Benchmark checks</div>
        </div>

        <aside className="product-canvas__inspector">
          <div className="product-canvas__sidebar-label">Opinion</div>
          <div className="product-canvas__stat">
            <span>Coverage</span>
            <strong>74%</strong>
          </div>
          <div className="product-canvas__stat">
            <span>Findings</span>
            <strong>05</strong>
          </div>
          <div className="product-canvas__memo">
            Validation memo
            <br />
            Coverage summary
            <br />
            Gap report
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

export default function Home() {
  const [activeMode, setActiveMode] = useState<Mode>(modes[0]);

  return (
    <main className="site-shell">
      <div className="announcement-bar">
        <p>
          Read the operating thesis for turning messy model packages into decision-grade
          validation work.
        </p>
        <a href="#operating-model">Learn more</a>
      </div>

      <header className="site-header">
        <a className="site-header__brand" href="#top">
          <span className="site-header__mark">AMV</span>
          <span>Agentic Model Validation</span>
        </a>

        <nav className="site-header__nav" aria-label="Primary">
          <a href="#platform">Platform</a>
          <a href="#operating-model">Operating Model</a>
          <a href="#architecture">Architecture</a>
        </nav>

        <a className="site-header__cta" href="#contact">
          Contact
        </a>
      </header>

      <section className="hero" id="top">
        <div className="hero__ornament hero__ornament--left" />
        <div className="hero__ornament hero__ornament--right" />

        <div className="hero__eyebrow">Messy inputs. Defensible outputs.</div>
        <h1>
          <span>From model package</span>
          <span>to validation opinion</span>
        </h1>
        <p className="hero__tagline">Elegant operating model. Mission-critical review output.</p>
      </section>

      <section className="platform-intro" id="platform">
        <div className="platform-intro__copy">
          <p className="platform-intro__eyebrow">With</p>
          <h2>The Review Engine</h2>
          <p>
            A validation platform designed to bridge the gap between messy real-world model
            packages and secure, review-grade output. It does not ask the bank to clean the
            package first. It discovers what is there, resolves the applicable review path, and
            executes the work.
          </p>
        </div>

        <div className="platform-intro__visual">
          <ProductCanvas />
          <p className="platform-intro__caption">The review workspace</p>
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
          <h4>Purpose-built interfaces for enterprise-grade review work</h4>
          <p>
            Whether the package comes from model risk, a bank engineering team, or a vendor,
            the system abstracts away package chaos without flattening the review itself. The
            workflow remains dynamic because the evidence remains dynamic.
          </p>
        </div>

        <div className="editorial-section__diagram editorial-section__diagram--wide">
          <div className="rail-card">
            <div className="rail-card__group">
              <span>Package boundary</span>
              <strong>Upload and classify</strong>
            </div>
            <div className="rail-card__group">
              <span>Control layer</span>
              <strong>Map evidence and resolve review path</strong>
            </div>
            <div className="rail-card__group">
              <span>Execution layer</span>
              <strong>Run runtime, data, and document modules</strong>
            </div>
            <div className="rail-card__group">
              <span>Output</span>
              <strong>Issue memo, findings, and coverage</strong>
            </div>
          </div>
        </div>
      </section>

      <section className="tabbed-section">
        <h4>Explore different review paths resolved by the engine</h4>

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
              The same architecture produces a different review path because the evidence package
              changes. That is the core operating model.
            </p>
          </div>

          <div className="tabbed-section__panel-visual">
            <ModeVisual mode={activeMode} />
            <p>Switch review modes to see the path change with the evidence.</p>
          </div>
        </div>
      </section>

      <section className="section-heading" id="operating-model">
        <h4>The operating model designed for banks with real package complexity</h4>
        <p>
          No matter where the artifacts originate, the system is built to preserve provenance,
          resolve the review mode, and produce structured outputs that can be defended.
        </p>
      </section>

      <section className="operating-model">
        {operatingCards.map((card) => (
          <article className="operating-card" key={card.title}>
            <p>{card.label}</p>
            <h5>{card.title}</h5>
            <span>{card.copy}</span>
          </article>
        ))}
      </section>

      <section className="section-heading" id="architecture">
        <h4>Architecture built for review infrastructure, not just orchestration</h4>
        <p>
          The control plane decides what can be reviewed. The execution plane runs the modules.
          The output layer turns the result into formal work product.
        </p>
      </section>

      <section className="architecture-stage">
        <div className="architecture-stage__figure">
          <div className="architecture-stage__base">
            <div className="architecture-stage__layer architecture-stage__layer--top">
              Application layer
            </div>
            <div className="architecture-stage__layer architecture-stage__layer--mid">
              Control plane
            </div>
            <div className="architecture-stage__layer architecture-stage__layer--mid">
              Execution plane
            </div>
            <div className="architecture-stage__layer architecture-stage__layer--bottom">
              Output layer
            </div>
          </div>
        </div>

        <div className="architecture-stage__markers">
          {architectureMarkers.map((marker) => (
            <article className="architecture-marker" key={marker.title}>
              <div className="architecture-marker__dot" />
              <div>
                <h5>{marker.title}</h5>
                <p>{marker.copy}</p>
              </div>
            </article>
          ))}
        </div>
      </section>

      <section className="section-heading">
        <h4>Bank-grade control boundaries and traceable execution</h4>
        <p>
          The platform is designed so that adoption does not require giving up control over how
          artifacts are handled, how execution occurs, or how outputs are traced back to evidence.
        </p>
      </section>

      <section className="security-grid">
        {securityCards.map((card) => (
          <article className="security-card" key={card.title}>
            <div className="security-card__icon" />
            <h6>{card.title}</h6>
            <p>{card.copy}</p>
          </article>
        ))}
      </section>

      <section className="cta-banner" id="contact">
        <div className="cta-banner__spark" />
        <h2>Looking for a validation platform built to do the review itself?</h2>
        <a href="#top">See the platform approach</a>
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
          <p>Designed for model risk, validation teams, and bank engineering groups.</p>
          <p>© 2026 Agentic Model Validation</p>
        </div>
      </footer>
    </main>
  );
}
