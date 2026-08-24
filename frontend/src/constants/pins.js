export const PINS = ["D1", "D2", "D3", "D4", "D5", "D6", "D7", "D8"];

export const WIDGET_TYPES = [
  {
    type: "value",
    label: "Labeled value",
    hint: "Latest reading from one pin",
  },
  {
    type: "gauge",
    label: "Gauge",
    hint: "Level between min and max",
  },
  {
    type: "chart",
    label: "Superchart",
    hint: "History for one pin",
  },
];

export const WIDGET_COLORS = [
  { id: "teal", label: "Teal", value: "#006d77" },
  { id: "water", label: "Water", value: "#83c5be" },
  { id: "clay", label: "Clay", value: "#e29578" },
  { id: "ink", label: "Ink", value: "#1a3c40" },
];
