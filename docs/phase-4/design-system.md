# Phase 4 — PulseOS Design System

> Bar: Apple (clarity, restraint), Linear (speed, density, keyboard-first), Stripe (precision, trust), Arc (delight, spatial nav), Notion (flexible structure). **Dark-mode default, light supported. Mobile-first, desktop-optimized. WCAG 2.2 AA.** These tokens are implemented in `frontend/styles` and `tailwind.config.ts`.

## 1. Design language

**Personality:** Calm precision. The product is a Bloomberg terminal that went to design school. It is information-dense but never noisy; fast but never frantic. It earns attention by being *right and brief*.

Principles:
1. **Signal over chrome.** Content is the UI; chrome recedes. Borders are hairlines, shadows are whispers.
2. **Confidence is visible.** Every recommendation shows its confidence and evidence — design treats uncertainty as a first-class visual property (confidence meters, dissent chips), never hidden.
3. **One primary action per view.** The "highest-value action right now" is always the visual hero.
4. **Keyboard is a first-class citizen.** ⌘K command palette, j/k navigation, everything reachable without a mouse (Linear standard).
5. **Motion is meaning.** Animation communicates state change and spatial relationship; never decorative. ≤200ms, hardware-accelerated transforms/opacity only.
6. **Density is earned.** Default to comfortable density; offer a compact mode for power users.

## 2. Color system

Semantic tokens (not raw hex in components). Dark is canonical; light is derived. OKLCH for perceptual uniformity.

### Dark (default)
| Token | Value (approx) | Use |
|---|---|---|
| `--bg-base` | `#0A0B0D` | app background |
| `--bg-surface` | `#121316` | cards, panels |
| `--bg-elevated` | `#1A1C20` | popovers, modals |
| `--bg-inset` | `#0E0F12` | wells, code |
| `--border-subtle` | `#23262B` | hairlines |
| `--border-strong` | `#33373E` | focus dividers |
| `--text-primary` | `#F2F3F5` | body |
| `--text-secondary` | `#A6ABB3` | meta |
| `--text-tertiary` | `#6B7178` | hints |
| `--accent` | `#5B8DEF` (PulseOS blue) | primary actions, links |
| `--accent-hover` | `#6F9CF2` | |
| `--success` | `#3FB97A` | positive EV, gains |
| `--warning` | `#E0A23C` | risks, attention |
| `--danger` | `#E0544E` | destructive, losses |
| `--info` | `#4FB6C9` | neutral signal |

### Semantic intelligence colors
- **Confidence scale** (gradient): low `#E0544E` → mid `#E0A23C` → high `#3FB97A`, used in confidence meters.
- **Verification levels:** low/med/high map to warning/info/success.
- **Money:** gains success-green, losses danger-red, neutral text-secondary. Never rely on color alone (WCAG) — pair with icon/label/sign.

### Light mode
Inverted luminance with the same hues; maintain ≥4.5:1 text contrast, ≥3:1 UI. Accent darkens slightly for contrast on white.

**Contrast:** all text/icon tokens verified ≥ AA (4.5:1 normal, 3:1 large/UI). Never encode meaning in hue alone.

## 3. Typography

- **Sans:** Inter (or SF Pro on Apple platforms) — UI, body.
- **Mono:** JetBrains Mono / SF Mono — numbers, data, code, ticker-like figures (tabular nums on by default for all metrics).
- **Scale (modular, 1.2 ratio), rem-based for accessibility/zoom:**

| Token | Size / line-height | Use |
|---|---|---|
| `display` | 40/44, -0.02em | hero numbers, landing |
| `h1` | 28/34 | page titles |
| `h2` | 22/28 | section |
| `h3` | 18/24 | card titles |
| `body` | 15/22 | default |
| `body-sm` | 13/18 | meta |
| `caption` | 12/16 | labels, timestamps |
| `mono-data` | 14/20 tabular | metrics, EV, confidence |

Weights: 400 body, 500 emphasis, 600 headings. Never 700+ (too loud for the brand). Letter-spacing tightens slightly at large sizes.

## 4. Spacing & layout

- **4px base grid.** Spacing tokens: `0,1(4),2(8),3(12),4(16),5(20),6(24),8(32),10(40),12(48),16(64)`.
- **Radius:** `sm 6`, `md 10`, `lg 14`, `xl 20`, `full`. Cards `lg`, buttons `md`, pills `full`.
- **Elevation:** 4 levels via subtle shadow + 1px border (dark mode leans on borders, not shadows).
- **Grid:** 12-col desktop (max content 1200–1440), 4-col mobile. Gutters 16/24.
- **Density modes:** Comfortable (default) and Compact (−25% vertical padding) — user toggle, persisted.

## 5. Component library (shadcn/ui base, extended)

Foundational (shadcn): Button, Input, Select, Checkbox, Radio, Switch, Tabs, Dialog, Sheet, Popover, Tooltip, Dropdown, Toast, Skeleton, Badge, Avatar, ScrollArea, Command (⌘K).

**PulseOS-specific (the brand-defining ones):**
| Component | Purpose | Key behavior |
|---|---|---|
| `BriefingCard` | one ranked action | title, rationale, confidence meter, EV, cost-of-inaction, evidence expander, 1-tap feedback |
| `ConfidenceMeter` | calibrated confidence | segmented bar + %; color from confidence scale; tooltip = calibration note |
| `EvidenceList` | linked sources | source, reliability dot, snippet, external-link; collapsible |
| `DissentChips` | council disagreement | chip per dissenting agent; click → trace |
| `CouncilReportPanel` | full council output | exec summary → consensus → dissent → agent traces → evidence (progressive disclosure) |
| `OpportunityCard` | EV-ranked opportunity | score ring, EV range, risk, recommended action, regulated badge |
| `StreamItem` | followed-entity update | source avatar, kind, timestamp, summary |
| `VerificationBadge` | community report trust | level + score + components on hover |
| `MetricStat` | analytics figure | big tabular number, delta, sparkline |
| `CommandPalette` | ⌘K | search + actions + nav, fuzzy, keyboard-driven |
| `ReputationBadge` | contributor standing | score + tier ring |

States are designed for **every** component: default, hover, focus-visible (2px accent ring, always visible for keyboard), active, disabled, loading (skeleton), error, empty.

## 6. Navigation architecture

**Desktop:** persistent **left sidebar** (collapsible) + **top bar** (search/⌘K, tenant switcher, notifications, profile). Sidebar sections: Dashboard, Opportunities, Communities, Following, Companies, Meetings (B/E), Analytics, Settings. Admin/Enterprise get extra sections by role.

**Mobile:** bottom **tab bar** (Home/Briefing, Opportunities, Search, Communities, Profile) + contextual top bar. Sheets replace side panels. Thumb-reachable primary actions.

**Spatial model (Arc-inspired):** the briefing is "home base"; drilling into an item slides in a detail panel (desktop) / pushes a screen (mobile); council/evidence are progressive overlays, not page reloads. Back is always non-destructive.

Global: ⌘K command palette is the universal entry point (search + navigate + act).

## 7. Accessibility (WCAG 2.2 AA — enforced, not retrofitted)
- All interactive elements keyboard-reachable; visible focus (2px ring, ≥3:1); logical tab order; skip-links.
- Screen-reader: semantic HTML, ARIA only where needed, live regions for async updates (briefing ready, council done), labeled icons.
- Contrast verified for every token; never color-only meaning; respects `prefers-reduced-motion` (disables non-essential animation), `prefers-color-scheme`, and 200% zoom/reflow.
- Targets ≥24×24px (2.2 target size); forms with explicit labels + error text tied via `aria-describedby`.
- Tested with axe + manual SR (VoiceOver/NVDA) in CI and release QA.

## 8. Motion
- Library: Framer Motion. Allowed: `transform`, `opacity` (GPU). Durations: micro 120ms, standard 180ms, panel 220ms; easing `cubic-bezier(0.2,0,0,1)` (decelerate).
- Patterns: list items stagger-in (≤30ms step), panels slide+fade, numbers count-up on first reveal, skeleton→content cross-fade. **No** parallax, bounce, or attention-grabbing loops. All disabled under reduced-motion.

## 9. State design (cross-cutting)
- **Empty:** purposeful, not blank — explain what will appear + a primary action (e.g., briefing empty → "Tell us a goal to start"). Never a dead end.
- **Loading:** skeletons matching final layout (no spinners for content); optimistic UI for feedback/dismiss; streamed council results render progressively.
- **Error:** human copy + cause + recovery action + trace id (support); never raw stack/JSON. Degraded-AI banner when the council is down (app stays useful with cached intelligence).
- **Quiet day:** "Nothing urgent today" is a *designed, positive* state (avoids the empty-briefing churn risk from Phase 1) — shows evergreen optimizations instead.

## 10. Tokens → code
Tokens exported as CSS variables + Tailwind theme extension (`tailwind.config.ts`), consumed by shadcn components. Single source of truth in `frontend/styles/tokens.css`; designers and engineers share it. Storybook hosts the component catalog with all states + a11y addon.
