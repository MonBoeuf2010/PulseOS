// Map a briefing/opportunity category to one of the five chromatic accents from
// DESIGN.md. Used as a soft (tinted) badge — accents are surface fills, not buttons.
const ACCENTS = [
  { key: "purple", text: "text-accent-purple", soft: "bg-accent-purple/10", dot: "bg-accent-purple" },
  { key: "pink", text: "text-accent-pink", soft: "bg-accent-pink/10", dot: "bg-accent-pink" },
  { key: "blue", text: "text-accent-blue-deep", soft: "bg-accent-blue/10", dot: "bg-accent-blue" },
  { key: "orange", text: "text-accent-orange", soft: "bg-accent-orange/10", dot: "bg-accent-orange" },
  { key: "green", text: "text-signal-green", soft: "bg-accent-green/10", dot: "bg-accent-green" },
] as const;

export type CategoryAccent = (typeof ACCENTS)[number];

export function categoryAccent(category: string): CategoryAccent {
  let hash = 0;
  for (let i = 0; i < category.length; i++) hash = (hash * 31 + category.charCodeAt(i)) >>> 0;
  return ACCENTS[hash % ACCENTS.length];
}
