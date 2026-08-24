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
    <header>
      <h1>Profile</h1>
      <p>Account details for this session.</p>
    </header>
    <article>
      <dl>
        <div>
          <dt>Name</dt>
          <dd>{{ profile?.name || "—" }}</dd>
        </div>
        <div>
          <dt>Email</dt>
          <dd>{{ profile?.email || auth.email }}</dd>
        </div>
        <div>
          <dt>User ID</dt>
          <dd>{{ profile?.id || auth.uid }}</dd>
        </div>
      </dl>
      <p v-if="error" class="err">{{ error }}</p>
    </article>
  </section>
</template>

<style scoped>
header {
  margin-bottom: 1.2rem;
}

h1 {
  font-size: 1.8rem;
  font-weight: 800;
}

header p {
  color: var(--muted);
}

article {
  background: #fff;
  border-radius: var(--radius);
  padding: 0.4rem 1.3rem;
  box-shadow: var(--shadow);
  max-width: 36rem;
}

div {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
  padding: 0.95rem 0;
  border-bottom: 1px solid var(--line);
}

div:last-of-type {
  border-bottom: 0;
}

dt {
  color: var(--muted);
  font-weight: 700;
}

.err {
  color: var(--danger);
}
</style>
