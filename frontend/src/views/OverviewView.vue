<script setup>
import { useLivePins } from "@/composables/useLivePins";
import WidgetCard from "@/components/WidgetCard.vue";

const { dashboard, historyByPin, reading } = useLivePins();
</script>

<template>
  <section>
    <header>
      <div>
        <h1>Dashboard</h1>
        <p>Live readings from the widgets you already set up.</p>
      </div>
      <router-link class="edit" :to="{ name: 'edit' }">Edit</router-link>
    </header>

    <div v-if="dashboard.widgets.length" class="grid">
      <WidgetCard
        v-for="widget in dashboard.widgets"
        :key="widget.id"
        :widget="widget"
        :value="reading(widget.pin)"
        :history="historyByPin[widget.pin] || []"
      />
    </div>

    <div v-else class="empty">
      <p>No widgets yet. Open Edit to drag cards onto the board and bind them to D1–D8.</p>
      <router-link :to="{ name: 'edit' }">Edit dashboard</router-link>
    </div>
  </section>
</template>

<style scoped>
header {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  gap: 1rem;
  margin-bottom: 1.2rem;
}

h1 {
  font-size: 1.9rem;
  font-weight: 800;
}

header p {
  color: var(--muted);
  margin-top: 0.3rem;
}

.edit {
  background: var(--oasis-teal);
  color: #fff;
  font-weight: 800;
  padding: 0.65rem 1rem;
  border-radius: 8px;
}

.grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  gap: 1rem;
}

.empty {
  background: #fff;
  border-radius: var(--radius);
  box-shadow: var(--shadow);
  padding: 3.5rem 1.5rem;
  text-align: center;
  color: var(--muted);
}

.empty a {
  display: inline-block;
  margin-top: 1rem;
  color: var(--oasis-teal);
  font-weight: 800;
}
</style>
