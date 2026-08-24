import { createRouter, createWebHistory } from "vue-router";

import { useAuthStore } from "@/stores/auth";

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: "/",
      component: () => import("@/layouts/MarketingLayout.vue"),
      children: [
        {
          path: "",
          name: "home",
          component: () => import("@/views/HomeView.vue"),
        },
        {
          path: "login",
          name: "login",
          component: () => import("@/views/LoginView.vue"),
        },
        {
          path: "signup",
          name: "signup",
          component: () => import("@/views/SignupView.vue"),
        },
      ],
    },
    {
      path: "/app",
      component: () => import("@/layouts/AppLayout.vue"),
      meta: { requiresAuth: true },
      children: [
        {
          path: "",
          name: "overview",
          component: () => import("@/views/OverviewView.vue"),
        },
        {
          path: "plants",
          name: "plants",
          component: () => import("@/views/PlantsView.vue"),
        },
        {
          path: "sight",
          name: "sight",
          component: () => import("@/views/SightView.vue"),
        },
        {
          path: "device",
          name: "device",
          component: () => import("@/views/DeviceView.vue"),
        },
        {
          path: "account",
          name: "account",
          component: () => import("@/views/AccountView.vue"),
        },
      ],
    },
    { path: "/:pathMatch(.*)*", redirect: "/" },
  ],
  scrollBehavior() {
    return { top: 0 };
  },
});

router.beforeEach((to) => {
  const auth = useAuthStore();
  if (to.meta.requiresAuth && !auth.isAuthenticated) {
    return { name: "login" };
  }
  if ((to.name === "login" || to.name === "signup") && auth.isAuthenticated) {
    return { name: "overview" };
  }
  return true;
});

export default router;
