<script setup>
import { computed } from "vue";
import { useRoute } from "vue-router";

import HiveMark from "@/components/HiveMark.vue";

const route = useRoute();
const isAuthScreen = computed(() => route.name === "login" || route.name === "signup");
</script>

<template>
  <div class="shell" :class="{ auth: isAuthScreen }">
    <header v-if="!isAuthScreen" class="top">
      <router-link to="/" class="brand">
        <HiveMark />
        SmartHive
      </router-link>
      <nav>
        <router-link to="/login">Login</router-link>
        <router-link to="/signup" class="cta">Get Started</router-link>
      </nav>
    </header>
    <router-view v-slot="{ Component }">
      <keep-alive>
        <component :is="Component" />
      </keep-alive>
    </router-view>
  </div>
</template>

<style scoped>
.shell.auth {
  min-height: 100vh;
}

.top {
  position: absolute;
  inset: 0 0 auto;
  z-index: 2;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1.1rem var(--space);
}

.brand {
  display: flex;
  align-items: center;
  gap: 0.45rem;
  color: #fff;
  font-weight: 800;
  font-size: 1.25rem;
}

nav {
  display: flex;
  align-items: center;
  gap: 1.1rem;
}

nav a {
  color: #fff;
  font-weight: 700;
}

nav a.cta {
  background: #fff;
  color: var(--oasis-teal);
  padding: 0.55rem 1rem;
  border-radius: 8px;
}

nav a.cta:hover {
  background: var(--oasis-mist);
  color: var(--oasis-teal);
}
</style>
