<template>
  <main>
    <section class="hero">
      <p class="eyebrow">Residences · Conservatories · Quiet farms</p>
      <h1>Intelligence,<br />held in reserve.</h1>
      <p class="lede">
        SmartHive is a climate and vision layer for rooms that should feel
        unhurried. Sensors speak in whispers. Images are read, not displayed
        as spectacle.
      </p>
      <div class="cta">
        <router-link class="fill" to="/signup">Begin</router-link>
        <router-link to="/login">I already have a key</router-link>
      </div>
    </section>

    <section class="strip">
      <article>
        <span>01</span>
        <h2>Climate</h2>
        <p>Temperature, humidity, soil, and air, composed as a single reading.</p>
      </article>
      <article>
        <span>02</span>
        <h2>Sight</h2>
        <p>Object and plant studies without a gallery of chrome and charts.</p>
      </article>
      <article>
        <span>03</span>
        <h2>Keys</h2>
        <p>A device token for hardware. A session for you. Nothing more on screen.</p>
      </article>
    </section>

    <footer>
      <p>SmartHive V2</p>
      <p>Designed to recede.</p>
    </footer>
  </main>
</template>

<style scoped>
.hero {
  padding: 7rem var(--space) 5rem;
  max-width: 52rem;
}

.eyebrow {
  letter-spacing: 0.2em;
  text-transform: uppercase;
  font-size: 0.72rem;
  color: var(--muted);
}

h1 {
  font-size: clamp(3.4rem, 8vw, 6.4rem);
  margin: 1.2rem 0 1.5rem;
}

.lede {
  max-width: 34rem;
  color: var(--muted);
  font-size: 1.05rem;
}

.cta {
  display: flex;
  gap: 1.75rem;
  align-items: center;
  margin-top: 2.5rem;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  font-size: 0.72rem;
}

.fill {
  background: var(--ink);
  color: var(--paper);
  padding: 0.9rem 1.3rem;
}

.strip {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  border-top: 1px solid var(--line);
}

article {
  padding: 2.5rem var(--space);
  border-right: 1px solid var(--line);
}

article:last-child {
  border-right: 0;
}

article span {
  color: var(--muted);
  font-size: 0.75rem;
}

article h2 {
  font-size: 2rem;
  margin: 1rem 0 0.75rem;
}

footer {
  display: flex;
  justify-content: space-between;
  padding: 1.4rem var(--space);
  border-top: 1px solid var(--line);
  color: var(--muted);
  font-size: 0.8rem;
}

@media (max-width: 840px) {
  .strip {
    grid-template-columns: 1fr;
  }

  article {
    border-right: 0;
    border-bottom: 1px solid var(--line);
  }
}
</style>
