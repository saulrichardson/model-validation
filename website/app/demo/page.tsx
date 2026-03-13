export default function DemoPage() {
  return (
    <main className="site-shell demo-page">
      <header className="site-header">
        <a className="site-header__brand" href="/">
          <span className="site-header__mark">AMV</span>
          <span>Agentic Model Validation</span>
        </a>

        <nav className="site-header__nav" aria-label="Primary">
          <a href="/">Platform</a>
          <a href="/demo">Demo</a>
        </nav>

        <a className="site-header__cta" href="/#contact">
          Contact
        </a>
      </header>

      <section className="demo-hero">
        <p className="hero__eyebrow">Demo environment</p>
        <h1>
          <span>Interactive platform</span>
          <span>demo scaffold</span>
        </h1>
        <p className="demo-hero__copy">
          This page is reserved for the live product walkthrough. For now, it is structured to
          support an embedded demo, guided package examples, and review outputs in one place.
        </p>
      </section>

      <section className="demo-status-grid">
        <article className="demo-status-card demo-status-card--inverted">
          <p>Current status</p>
          <h2>Scaffolded and ready for demo content</h2>
          <span>
            The route exists, the layout is in place, and the page is ready for the live demo
            surface when you want to wire it in.
          </span>
        </article>

        <article className="demo-status-card">
          <p>Planned section</p>
          <h2>Guided walkthrough</h2>
          <span>Space for a narrated flow through package intake, review resolution, and output.</span>
        </article>

        <article className="demo-status-card">
          <p>Planned section</p>
          <h2>Example packages</h2>
          <span>Space for switching between full revalidation, behavioral review, and conceptual review.</span>
        </article>
      </section>

      <section className="demo-stage">
        <div className="demo-stage__copy">
          <h3>Reserved for the live platform experience</h3>
          <p>
            This area can hold an embedded product demo, a recorded walkthrough, or a staged
            click-through environment. The framing is already set up to keep the demo centered and
            easy to present.
          </p>
        </div>

        <div className="demo-stage__canvas">
          <div className="demo-stage__window">
            <div className="demo-stage__toolbar">
              <span />
              <span />
              <span />
            </div>

            <div className="demo-stage__placeholder">
              <div className="demo-stage__placeholder-label">Demo surface</div>
              <div className="demo-stage__placeholder-box">Embed live product demo here</div>
            </div>
          </div>
        </div>
      </section>

      <section className="demo-checklist">
        <article className="demo-checklist__card">
          <p>Walkthrough</p>
          <h3>Hero path</h3>
          <span>Show a mixed package arriving, the evidence view being built, and the review path being resolved.</span>
        </article>

        <article className="demo-checklist__card">
          <p>Artifacts</p>
          <h3>Package examples</h3>
          <span>Prepare one complete package, one opaque runtime package, and one documentation-heavy package.</span>
        </article>

        <article className="demo-checklist__card">
          <p>Outputs</p>
          <h3>Work product</h3>
          <span>Surface memo fragments, findings, coverage summaries, and missing evidence requests.</span>
        </article>

        <article className="demo-checklist__card">
          <p>Presentation</p>
          <h3>Investor or buyer mode</h3>
          <span>Use the same page for a concise investor walkthrough or a deeper product presentation.</span>
        </article>
      </section>
    </main>
  );
}
