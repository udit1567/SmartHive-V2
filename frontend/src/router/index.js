import { createRouter, createWebHashHistory } from "vue-router";

import AppLayout from "@/layouts/AppLayout.vue";
import MarketingLayout from "@/layouts/MarketingLayout.vue";
import { useAuthStore } from "@/stores/auth";
import AccountView from "@/views/AccountView.vue";
import DashboardEditView from "@/views/DashboardEditView.vue";
import DeviceView from "@/views/DeviceView.vue";
import HomeView from "@/views/HomeView.vue";
import LoginView from "@/views/LoginView.vue";
import OverviewView from "@/views/OverviewView.vue";
import PlantsView from "@/views/PlantsView.vue";
import SightView from "@/views/SightView.vue";
import SignupView from "@/views/SignupView.vue";

const router = createRouter({
  history: createWebHashHistory(),
  routes: [
    {
      path: "/",
      component: MarketingLayout,
      children: [
        { path: "", name: "home", component: HomeView },
        { path: "login", name: "login", component: LoginView },
        { path: "signup", name: "signup", component: SignupView },
      ],
    },
    {
      path: "/app",
      component: AppLayout,
      meta: { requiresAuth: true },
      children: [
        { path: "", name: "overview", component: OverviewView },
        { path: "edit", name: "edit", component: DashboardEditView },
        { path: "plants", name: "plants", component: PlantsView },
        { path: "sight", name: "sight", component: SightView },
        { path: "device", name: "device", component: DeviceView },
        { path: "account", name: "account", component: AccountView },
      ],
    },
    { path: "/:pathMatch(.*)*", redirect: "/" },
  ],
  scrollBehavior(to, from, savedPosition) {
    if (to.path.startsWith("/app") && from.path.startsWith("/app")) {
      return false;
    }
    return savedPosition || { top: 0 };
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
