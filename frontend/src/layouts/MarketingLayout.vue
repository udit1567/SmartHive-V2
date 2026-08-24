<template>
  <div class="shell">
    <header class="top">
      <router-link to="/" class="mark">SmartHive</router-link>
      <nav>
        <router-link to="/login">Enter</router-link>
        <router-link to="/signup" class="ghost">Open an account</router-link>
      </nav>
    </header>
    <router-view />
  </div>
</template>

<style scoped>
.shell {
  min-height: 100vh;
}

.top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1.5rem var(--space);
  border-bottom: 1px solid var(--line);
}

.mark {
  font-family: var(--serif);
  font-size: 1.35rem;
  letter-spacing: -0.03em;
}

nav {
  display: flex;
  align-items: center;
  gap: 1.75rem;
  font-size: 0.82rem;
  letter-spacing: 0.12em;
  text-transform: uppercase;
}

.ghost {
  border: 1px solid var(--ink);
  padding: 0.55rem 0.95rem;
}
</style>
