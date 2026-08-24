<script setup>
import { reactive, ref } from "vue";
import { useRouter } from "vue-router";

import AppButton from "@/components/AppButton.vue";
import AppField from "@/components/AppField.vue";
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
  <main class="wrap">
    <h1>Enter</h1>
    <p>A session lasts one hour. Your device key remains unchanged.</p>
    <form @submit.prevent="onSubmit">
      <AppField v-model="form.email" label="Email" type="email" autocomplete="email" />
      <AppField
        v-model="form.password"
        label="Password"
        type="password"
        autocomplete="current-password"
      />
      <p v-if="localError" class="err">{{ localError }}</p>
      <AppButton label="Continue" :busy="auth.pending" />
    </form>
    <router-link to="/signup">Need an account</router-link>
  </main>
</template>

<style scoped>
.wrap {
  max-width: 28rem;
  padding: 5rem var(--space) 6rem;
}

h1 {
  font-size: 4rem;
  margin-bottom: 0.6rem;
}

p,
a {
  color: var(--muted);
}

form {
  display: grid;
  gap: 1.4rem;
  margin: 2.5rem 0 1.5rem;
}

.err {
  color: var(--danger);
  font-size: 0.9rem;
}

a {
  font-size: 0.78rem;
  letter-spacing: 0.12em;
  text-transform: uppercase;
}
</style>
