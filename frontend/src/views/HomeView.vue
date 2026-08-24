<template>
  <main>
    <section class="hero brand-gradient">
      <h1>Welcome to SmartHive</h1>
      <p>Connect, control, and monitor your devices effortlessly.</p>
      <router-link to="/signup">Get Started</router-link>
    </section>

    <section class="features">
      <h2>Why Choose SmartHive?</h2>
      <div class="grid">
        <article>
          <h3>Real-Time Monitoring</h3>
          <p>Watch temperature, humidity, soil, and air quality as they change.</p>
        </article>
        <article>
          <h3>Secure Control</h3>
          <p>Sign in with a hashed password and keep a separate key for hardware.</p>
        </article>
        <article>
          <h3>Easy Integration</h3>
          <p>Send sensor pulses and camera stills with the same device token.</p>
        </article>
      </div>
    </section>

    <footer>
      <p>&copy; 2026 SmartHive. All rights reserved.</p>
    </footer>
  </main>
</template>

<style scoped>
.hero {
  min-height: 72vh;
  display: grid;
  place-content: center;
  text-align: center;
  color: #fff;
  padding: 7rem var(--space) 5rem;
}

h1 {
  font-size: clamp(2.6rem, 6vw, 4.2rem);
  font-weight: 800;
  margin-bottom: 0.85rem;
}

.hero p {
  font-size: 1.35rem;
  max-width: 36rem;
  margin: 0 auto 2rem;
}

.hero a {
  display: inline-block;
  justify-self: center;
  background: #fff;
  color: var(--oasis-teal);
  font-weight: 800;
  padding: 0.9rem 1.8rem;
  border-radius: 8px;
}

.hero a:hover {
  background: var(--oasis-mist);
}

.features {
  background: #fff;
  padding: 4rem var(--space);
  text-align: center;
}

h2 {
  font-size: 2.2rem;
  margin-bottom: 2rem;
}

.grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 1.5rem;
  max-width: 980px;
  margin: 0 auto;
}

article {
  background: var(--oasis-mist);
  border-radius: 12px;
  padding: 1.5rem 1.25rem;
  box-shadow: 0 4px 12px rgba(0, 109, 119, 0.08);
}

article:hover {
  transform: translateY(-6px);
  box-shadow: 0 10px 20px rgba(0, 0, 0, 0.12);
}

h3 {
  margin-bottom: 0.55rem;
}

article p {
  color: var(--muted);
}

footer {
  background: var(--oasis-teal);
  color: #fff;
  text-align: center;
  padding: 1.25rem;
}
</style>
