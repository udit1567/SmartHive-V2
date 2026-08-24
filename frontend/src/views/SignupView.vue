<script setup>
import { reactive, ref } from "vue";
import { useRouter } from "vue-router";

import AppButton from "@/components/AppButton.vue";
import AppField from "@/components/AppField.vue";
import HiveMark from "@/components/HiveMark.vue";
import { useAuthStore } from "@/stores/auth";

const auth = useAuthStore();
const router = useRouter();
const form = reactive({
  username: "",
  email: "",
  firstName: "",
  lastName: "",
  password: "",
  address: "",
  source: "web",
});
const localError = ref("");
const notice = ref("");

async function onSubmit() {
  localError.value = "";
  notice.value = "";
  try {
    const result = await auth.signup(form);
    notice.value = result.message || "Signup successful.";
    setTimeout(() => router.push({ name: "login" }), 900);
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
        <h1>Create Account</h1>
        <p>Join SmartHive today.</p>
      </header>
      <form @submit.prevent="onSubmit">
        <div class="row">
          <AppField v-model="form.firstName" label="First name" autocomplete="given-name" />
          <AppField v-model="form.lastName" label="Last name" autocomplete="family-name" />
        </div>
        <AppField v-model="form.username" label="Username" autocomplete="username" />
        <AppField v-model="form.email" label="Email" type="email" autocomplete="email" />
        <AppField
          v-model="form.password"
          label="Password"
          type="password"
          autocomplete="new-password"
        />
        <AppField v-model="form.address" label="Address" autocomplete="street-address" />
        <AppField v-model="form.source" label="How did you hear about us?" />
        <p v-if="localError" class="err">{{ localError }}</p>
        <p v-if="notice" class="ok">{{ notice }}</p>
        <AppButton label="Sign Up" :busy="auth.pending" />
      </form>
      <p class="alt">
        Already have an account?
        <router-link to="/login">Login</router-link>
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
  width: min(100%, 520px);
  background: #fff;
  border-radius: 1rem;
  overflow: hidden;
  box-shadow: var(--shadow);
}

header {
  color: #fff;
  text-align: center;
  padding: 1.8rem 1.5rem 1.4rem;
}

header :deep(.mark) {
  margin: 0 auto 0.7rem;
  width: 2rem;
  height: 2rem;
}

h1 {
  font-size: 1.75rem;
  font-weight: 800;
}

form {
  display: grid;
  gap: 1rem;
  padding: 1.5rem 1.5rem 0.3rem;
}

.row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.9rem;
}

.err,
.ok {
  border-radius: 8px;
  padding: 0.7rem 0.8rem;
}

.err {
  color: var(--danger);
  background: #fef2f2;
}

.ok {
  color: var(--ok);
  background: #e7f4f4;
}

.alt {
  text-align: center;
  padding: 0 1.5rem 1.5rem;
  color: var(--muted);
}

a {
  color: var(--oasis-teal);
  font-weight: 700;
}

@media (max-width: 640px) {
  .row {
    grid-template-columns: 1fr;
  }
}
</style>
