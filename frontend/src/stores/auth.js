import { defineStore } from "pinia";
import { computed, ref } from "vue";

import { request } from "@/api/client";

const STORAGE_KEY = "smarthive.session";

function readSession() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    return raw ? JSON.parse(raw) : null;
  } catch {
    return null;
  }
}

export const useAuthStore = defineStore("auth", () => {
  const session = ref(readSession());
  const error = ref("");
  const pending = ref(false);

  const isAuthenticated = computed(() => Boolean(session.value?.access_token));
  const token = computed(() => session.value?.access_token ?? "");
  const deviceToken = computed(() => session.value?.auth_token ?? "");
  const email = computed(() => session.value?.email ?? "");
  const uid = computed(() => session.value?.uid ?? null);

  function persist(next) {
    session.value = next;
    if (next) {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(next));
    } else {
      localStorage.removeItem(STORAGE_KEY);
    }
  }

  async function login(credentials) {
    pending.value = true;
    error.value = "";
    try {
      const data = await request("/login", {
        method: "POST",
        json: credentials,
      });
      persist({
        access_token: data.access_token,
        auth_token: data.auth_token,
        email: data.email,
        uid: data.uid,
      });
    } catch (err) {
      error.value = err.message;
      throw err;
    } finally {
      pending.value = false;
    }
  }

  async function signup(payload) {
    pending.value = true;
    error.value = "";
    try {
      return await request("/signup", { method: "POST", json: payload });
    } catch (err) {
      error.value = err.message;
      throw err;
    } finally {
      pending.value = false;
    }
  }

  async function logout() {
    try {
      if (token.value) {
        await request("/logout", { method: "POST", token: token.value });
      }
    } catch {
      // Session is cleared locally regardless of network outcome.
    }
    persist(null);
  }

  async function loadProfile() {
    if (!email.value || !token.value) {
      return null;
    }
    return request(`/profile/${encodeURIComponent(email.value)}`, {
      token: token.value,
    });
  }

  return {
    session,
    error,
    pending,
    isAuthenticated,
    token,
    deviceToken,
    email,
    uid,
    login,
    signup,
    logout,
    loadProfile,
  };
});
