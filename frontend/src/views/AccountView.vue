<script setup>
import { onMounted, ref } from "vue";

import { useAuthStore } from "@/stores/auth";

const auth = useAuthStore();
const profile = ref(null);
const error = ref("");

onMounted(async () => {
  try {
    profile.value = await auth.loadProfile();
  } catch (err) {
    error.value = err.message;
  }
});
</script>

<template>
  <section>
    <p class="eyebrow">Account</p>
    <h1>{{ profile?.name || "—" }}</h1>
    <dl>
      <div>
        <dt>Email</dt>
        <dd>{{ profile?.email || auth.email }}</dd>
      </div>
      <div>
        <dt>Identifier</dt>
        <dd>{{ profile?.id || auth.uid }}</dd>
      </div>
    </dl>
    <p v-if="error" class="err">{{ error }}</p>
  </section>
</template>

<style scoped>
.eyebrow {
  letter-spacing: 0.18em;
  text-transform: uppercase;
  font-size: 0.7rem;
  color: var(--muted);
}

h1 {
  font-size: clamp(2.6rem, 5vw, 4.2rem);
  margin: 0.35rem 0 2rem;
}

dl {
  max-width: 28rem;
}

div {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
  border-top: 1px solid var(--line);
  padding: 0.85rem 0;
}

dt {
  color: var(--muted);
  letter-spacing: 0.12em;
  text-transform: uppercase;
  font-size: 0.7rem;
}

.err {
  color: var(--danger);
}
</style>
