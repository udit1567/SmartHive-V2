<script setup>
import { reactive, ref } from "vue";
import { useRouter } from "vue-router";

import AppButton from "@/components/AppButton.vue";
import AppField from "@/components/AppField.vue";
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
  source: "atelier",
});
const localError = ref("");
const notice = ref("");

async function onSubmit() {
  localError.value = "";
  notice.value = "";
  try {
    const result = await auth.signup(form);
    notice.value = result.message || "Account created.";
    setTimeout(() => router.push({ name: "login" }), 900);
  } catch (err) {
    localError.value = err.message;
  }
}
</script>

<template>
  <main class="wrap">
    <h1>Open</h1>
    <p>Names are stored as you write them. Passwords are hashed immediately.</p>
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
      <AppField v-model="form.source" label="How you arrived" />
      <p v-if="localError" class="err">{{ localError }}</p>
      <p v-if="notice" class="ok">{{ notice }}</p>
      <AppButton label="Create account" :busy="auth.pending" />
    </form>
  </main>
</template>

<style scoped>
.wrap {
  max-width: 34rem;
  padding: 4.5rem var(--space) 6rem;
}

h1 {
  font-size: 4rem;
}

p {
  color: var(--muted);
  margin-top: 0.4rem;
}

form {
  display: grid;
  gap: 1.3rem;
  margin-top: 2.4rem;
}

.row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.2rem;
}

.err {
  color: var(--danger);
}

.ok {
  color: var(--ok);
}

@media (max-width: 640px) {
  .row {
    grid-template-columns: 1fr;
  }
}
</style>
