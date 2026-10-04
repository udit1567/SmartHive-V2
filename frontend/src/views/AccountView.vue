<script setup>
import { onMounted, reactive, ref } from "vue";

import AiProviderSettings from "@/components/AiProviderSettings.vue";
import AppButton from "@/components/AppButton.vue";
import AppField from "@/components/AppField.vue";
import { useAuthStore } from "@/stores/auth";

const auth = useAuthStore();
const form = reactive({
  firstName: "",
  lastName: "",
  address: "",
  telegramBotToken: "",
  telegramChatId: "",
});
const error = ref("");
const notice = ref("");
const busy = ref(false);

function applyProfile(profile) {
  form.firstName = profile?.firstName ?? "";
  form.lastName = profile?.lastName ?? "";
  form.address = profile?.address ?? "";
  form.telegramBotToken = profile?.telegramBotToken ?? "";
  form.telegramChatId = profile?.telegramChatId ?? "";
}

onMounted(async () => {
  try {
    applyProfile(await auth.loadProfile());
  } catch (err) {
    error.value = err.message;
  }
});

async function onSubmit() {
  error.value = "";
  notice.value = "";
  busy.value = true;
  try {
    const profile = await auth.updateProfile({ ...form });
    applyProfile(profile);
    notice.value = "Profile saved.";
  } catch (err) {
    error.value = err.message;
  } finally {
    busy.value = false;
  }
}
</script>

<template>
  <section>
    <header>
      <h1>Settings</h1>
      <p>Account details for this session.</p>
    </header>
    <div class="cards">
      <article>
        <dl>
          <div>
            <dt>Email</dt>
            <dd>{{ auth.email }}</dd>
          </div>
          <div>
            <dt>User ID</dt>
            <dd>{{ auth.uid }}</dd>
          </div>
        </dl>

        <form @submit.prevent="onSubmit">
          <div class="row">
            <AppField v-model="form.firstName" label="First name" autocomplete="given-name" />
            <AppField v-model="form.lastName" label="Last name" autocomplete="family-name" />
          </div>
          <AppField v-model="form.address" label="Address" autocomplete="street-address" />

          <div class="telegram">
            <h2>Telegram alerts</h2>
            <p>
              Create a bot with
              <a href="https://t.me/BotFather" target="_blank" rel="noopener">@BotFather</a>
              to get a bot token, then message your new bot once and open
              <code>https://api.telegram.org/bot&lt;token&gt;/getUpdates</code>
              to find your chat id.
            </p>
            <AppField v-model="form.telegramBotToken" label="Bot token" autocomplete="off" />
            <AppField v-model="form.telegramChatId" label="Chat id" autocomplete="off" />
          </div>

          <p v-if="error" class="err">{{ error }}</p>
          <p v-if="notice" class="ok">{{ notice }}</p>
          <AppButton label="Save profile" :busy="busy" />
        </form>
      </article>

      <AiProviderSettings />
    </div>
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

.cards {
  display: flex;
  flex-wrap: wrap;
  gap: 1.2rem;
  align-items: flex-start;
}

article {
  background: #fff;
  border-radius: var(--radius);
  padding: 0.4rem 1.3rem 1.3rem;
  box-shadow: var(--shadow);
  flex: 1 1 26rem;
  min-width: 0;
}

dl div {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
  padding: 0.95rem 0;
  border-bottom: 1px solid var(--line);
}

dt {
  color: var(--muted);
  font-weight: 700;
}

form {
  display: grid;
  grid-template-columns: minmax(0, 1fr);
  gap: 1rem;
  padding-top: 1.1rem;
}

.row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.9rem;
  min-width: 0;
}

.telegram {
  border-top: 1px solid var(--line);
  padding-top: 1rem;
  display: grid;
  grid-template-columns: minmax(0, 1fr);
  gap: 0.9rem;
}

.telegram h2 {
  font-size: 1.05rem;
}

.telegram p {
  color: var(--muted);
  font-size: 0.85rem;
}

.telegram code {
  background: var(--oasis-mist);
  border-radius: 4px;
  padding: 0.1rem 0.3rem;
  overflow-wrap: anywhere;
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

@media (max-width: 640px) {
  .row {
    grid-template-columns: 1fr;
  }
}
</style>
