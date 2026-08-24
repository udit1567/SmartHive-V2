<script setup>
defineProps({
  label: { type: String, required: true },
  modelValue: { type: String, default: "" },
  type: { type: String, default: "text" },
  autocomplete: { type: String, default: "off" },
});

defineEmits(["update:modelValue"]);
</script>

<template>
  <label class="field">
    <span>{{ label }}</span>
    <input
      :type="type"
      :value="modelValue"
      :autocomplete="autocomplete"
      @input="$emit('update:modelValue', $event.target.value)"
    />
  </label>
</template>

<style scoped>
.field {
  display: grid;
  gap: 0.4rem;
}

span {
  font-size: 0.72rem;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  color: var(--muted);
}

input {
  background: transparent;
  border: 0;
  border-bottom: 1px solid var(--line);
  padding: 0.55rem 0 0.7rem;
  outline: none;
}

input:focus {
  border-bottom-color: var(--ink);
}
</style>
