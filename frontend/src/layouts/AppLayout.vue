<script setup>
import { onMounted, onUnmounted } from "vue";
import { RouterLink, RouterView, useRouter } from "vue-router";

import HiveMark from "@/components/HiveMark.vue";
import { useAuthStore } from "@/stores/auth";
import { useDashboardStore } from "@/stores/dashboard";
import { useSensorStore } from "@/stores/sensors";

const auth = useAuthStore();
const dashboard = useDashboardStore();
const sensors = useSensorStore();
const router = useRouter();

const links = [
  { to: { name: "overview" }, label: "Dashboard" },
  { to: { name: "edit" }, label: "Edit" },
  { to: { name: "plants" }, label: "Plant Health" },
  { to: { name: "sight" }, label: "Object Detection" },
  { to: { name: "device" }, label: "Add Device" },
  { to: { name: "account" }, label: "Profile" },
];

async function signOut() {
  await auth.logout();
  router.push({ name: "home" });
}

onMounted(() => {
  dashboard.load();
  sensors.startPolling();
});

onUnmounted(() => {
  sensors.stopPolling();
});
</script>

<template>
  <div class="app">
    <header class="bar brand-gradient">
      <router-link to="/" class="brand">
        <HiveMark />
        SmartHive
      </router-link>
      <p>{{ auth.email }}</p>
    </header>
    <div class="body">
      <aside>
        <nav>
          <router-link v-for="link in links" :key="link.label" :to="link.to">
            {{ link.label }}
          </router-link>
        </nav>
        <button type="button" @click="signOut">Logout</button>
      </aside>
      <main>
        <router-view v-slot="{ Component }">
          <keep-alive>
            <component :is="Component" />
          </keep-alive>
        </router-view>
      </main>
    </div>
  </div>
</template>

<style scoped>
.app {
  min-height: 100vh;
}

.bar {
  height: 64px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 var(--space);
  color: #fff;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.12);
}

.brand {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-weight: 800;
  font-size: 1.2rem;
}

.bar p {
  font-size: 0.9rem;
  opacity: 0.92;
}

.body {
  display: grid;
  grid-template-columns: 240px 1fr;
  min-height: calc(100vh - 64px);
}

aside {
  background: #fff;
  border-right: 1px solid var(--line);
  padding: 1.25rem 0.9rem 1.5rem;
  display: flex;
  flex-direction: column;
}

nav {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}

nav a {
  padding: 0.75rem 0.9rem;
  border-radius: 10px;
  color: var(--muted);
  font-weight: 700;
}

nav a.router-link-active {
  background: #e7f4f4;
  color: var(--brand);
}

button {
  margin-top: auto;
  background: none;
  border: 0;
  text-align: left;
  padding: 0.75rem 0.9rem;
  color: var(--muted);
  font-weight: 700;
}

main {
  padding: 1.5rem var(--space) 3rem;
}

@media (max-width: 840px) {
  .body {
    grid-template-columns: 1fr;
  }

  aside {
    border-right: 0;
    border-bottom: 1px solid var(--line);
    flex-direction: row;
    align-items: center;
    gap: 0.5rem;
  }

  nav {
    flex-direction: row;
    flex-wrap: wrap;
  }

  button {
    margin-top: 0;
    margin-left: auto;
  }
}
</style>
