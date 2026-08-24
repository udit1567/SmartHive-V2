<script setup>
import { RouterLink, RouterView, useRouter } from "vue-router";

import { useAuthStore } from "@/stores/auth";

const auth = useAuthStore();
const router = useRouter();

const links = [
  { to: { name: "overview" }, label: "Overview" },
  { to: { name: "plants" }, label: "Plants" },
  { to: { name: "sight" }, label: "Sight" },
  { to: { name: "device" }, label: "Device" },
  { to: { name: "account" }, label: "Account" },
];

async function signOut() {
  await auth.logout();
  router.push({ name: "home" });
}
</script>

<template>
  <div class="app">
    <aside>
      <router-link to="/" class="mark">SmartHive</router-link>
      <nav>
        <router-link
          v-for="link in links"
          :key="link.label"
          :to="link.to"
        >
          {{ link.label }}
        </router-link>
      </nav>
      <button type="button" class="leave" @click="signOut">Sign out</button>
    </aside>
    <main>
      <router-view />
    </main>
  </div>
</template>

<style scoped>
.app {
  min-height: 100vh;
  display: grid;
  grid-template-columns: 220px 1fr;
}

aside {
  border-right: 1px solid var(--line);
  padding: 1.75rem 1.4rem 2rem;
  display: flex;
  flex-direction: column;
  gap: 2.5rem;
}

.mark {
  font-family: var(--serif);
  font-size: 1.4rem;
}

nav {
  display: flex;
  flex-direction: column;
  gap: 0.85rem;
  font-size: 0.92rem;
}

nav a {
  color: var(--muted);
}

nav a.router-link-active {
  color: var(--ink);
}

.leave {
  margin-top: auto;
  background: none;
  border: 0;
  padding: 0;
  text-align: left;
  color: var(--muted);
  letter-spacing: 0.08em;
  text-transform: uppercase;
  font-size: 0.72rem;
}

main {
  padding: 2.5rem var(--space) 4rem;
}

@media (max-width: 840px) {
  .app {
    grid-template-columns: 1fr;
  }

  aside {
    border-right: 0;
    border-bottom: 1px solid var(--line);
    flex-direction: row;
    align-items: center;
    gap: 1.2rem;
    padding: 1rem var(--space);
  }

  nav {
    flex-direction: row;
    flex-wrap: wrap;
    gap: 1rem;
  }

  .leave {
    margin-top: 0;
    margin-left: auto;
  }
}
</style>
