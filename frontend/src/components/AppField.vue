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
  font-size: 0.8rem;
  font-weight: 700;
  color: var(--ink);
}

input {
  width: 100%;
  background: #fff;
  border: 1px solid var(--line);
  border-radius: 10px;
  padding: 0.75rem 0.85rem;
  outline: none;
}

input:focus {
  border-color: var(--brand);
  box-shadow: 0 0 0 3px rgba(0, 109, 119, 0.18);
}
</style>
