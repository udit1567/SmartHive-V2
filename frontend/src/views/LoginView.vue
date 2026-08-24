<script setup>
import { reactive, ref } from "vue";
import { useRouter } from "vue-router";

import AppButton from "@/components/AppButton.vue";
import AppField from "@/components/AppField.vue";
import HiveMark from "@/components/HiveMark.vue";
import { useAuthStore } from "@/stores/auth";

const auth = useAuthStore();
const router = useRouter();
const form = reactive({ email: "", password: "" });
const localError = ref("");

async function onSubmit() {
  localError.value = "";
  try {
    await auth.login(form);
    router.push({ name: "overview" });
  } catch (err) {
    localError.value = err.message;
  }
}
</script>

<template>
  <main class="page">
    <div class="card">
      <header class="brand-gradient">
        <HiveMark />
        <h1>SmartHive</h1>
        <p>Welcome back. Please login to continue.</p>
      </header>
      <form @submit.prevent="onSubmit">
        <AppField v-model="form.email" label="Email" type="email" autocomplete="email" />
        <AppField
          v-model="form.password"
          label="Password"
          type="password"
          autocomplete="current-password"
        />
        <p v-if="localError" class="err">{{ localError }}</p>
        <AppButton label="Login" :busy="auth.pending" />
      </form>
      <p class="alt">
        Don't have an account?
        <router-link to="/signup">Sign up</router-link>
      </p>
    </div>
  </main>
</template>

<style scoped>
.page {
  min-height: 100vh;
  display: grid;
  place-items: center;
  padding: 1.5rem;
  background: linear-gradient(135deg, var(--oasis-mist), var(--oasis-sand));
}

.card {
  width: min(100%, 420px);
  background: #fff;
  border-radius: 1rem;
  overflow: hidden;
  box-shadow: var(--shadow);
}

header {
  color: #fff;
  text-align: center;
  padding: 2rem 1.5rem 1.6rem;
}

header :deep(.mark) {
  margin: 0 auto 0.7rem;
  width: 2rem;
  height: 2rem;
}

h1 {
  font-size: 1.85rem;
  font-weight: 800;
}

header p {
  opacity: 0.95;
  margin-top: 0.3rem;
}

form {
  display: grid;
  gap: 1.1rem;
  padding: 1.6rem 1.5rem 0.4rem;
}

.err {
  color: var(--danger);
  background: #fef2f2;
  border-radius: 8px;
  padding: 0.7rem 0.8rem;
  font-size: 0.9rem;
}

.alt {
  text-align: center;
  padding: 0 1.5rem 1.6rem;
  color: var(--muted);
}

a {
  color: var(--oasis-teal);
  font-weight: 700;
}
</style>
