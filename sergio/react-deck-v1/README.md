# Pfizer Sweden Regional Landscape Mapping — deck

React + TypeScript single-file presentation. Each slide is its own component file in `src/slides/`, so editing a slide means opening one file and saving.

## Quick start

```bash
npm install
npm run dev      # localhost:5173, hot-reload
npm run build    # writes a single self-contained dist/index.html
```

The build output is one HTML file with CSS, JS and fonts inlined. Open it in any browser, no server needed. Use it for presenting, sharing or printing to PDF.

## Editing a slide

Each slide is a single `.tsx` file under `src/slides/`. Open the file, change the JSX (HTML-like syntax with `className` instead of `class`), save. `npm run dev` picks it up.

## Adding a slide

1. Create `src/slides/MySlide.tsx` using any existing slide as a template.
2. Import it in `src/slides/index.ts` and add it to the `ALL_SLIDES` array at the position you want.
3. Add a title to `SLIDE_TITLES` so it shows up in the table-of-contents overlay.

## Project structure

```
src/
├── App.tsx                 main shell, keyboard navigation, scale-to-fit
├── main.tsx                React entry point
├── styles/
│   └── presentation.css    design tokens and layout
├── lib/
│   └── format.ts           number formatters (Swedish locale)
├── types/
│   └── index.ts            shared TypeScript types
├── components/
│   ├── Slide.tsx           slide shell (topbar, conf-strip, body, foot)
│   ├── SectionDivider.tsx  full-bleed section break
│   ├── Navigation.tsx      bottom nav bar and ToC overlay
│   ├── KPI.tsx             KPI grid and KPI cell
│   ├── Sparkline.tsx       inline mini-line chart for table cells
│   ├── LineChart.tsx       multi-series SVG line chart
│   ├── ConfidencePill.tsx  small status pill
│   └── Icon.tsx            inline SVG icon set
├── data/                   all data lives here as JSON imports
└── slides/                 one .tsx file per slide
```

## Data

All data is in `src/data/*.json`, imported directly by the slide components. The JSON files are generated from the project master workbook and the per-region source set.

| File | Source | Contents |
|------|--------|----------|
| `data.json` | Master workbook | Region master: population, budget, KPIs, Pfizer footprint per region |
| `stakeholders.json` | Stakeholder workbook | 21 regions × 7 roles |
| `named.json` | Stakeholder workbook | Named individuals on national bodies (NT-rådet, NSG) |
| `stakeholderpriorities.json` | Per-region source set | Per-role priorities |
| `nt_radet.json` | TLV / samverkanlakemedel.se | NT-rådet status per Pfizer product |
| `pts_latest.json` | AVA + Socialstyrelsen | Latest patient counts (AVA where available, Socialstyrelsen otherwise) |
| `brick.json` | IQVIA Sell-In | 78-brick CDK4/6 priority data |
| `attr.json` | AVA Vyndaqel | ATTR concentration per sjukvårdsregion |
| `pfizer_monthly.json` | IQVIA Sell-In | Monthly Pfizer-product trajectories |
| `vaccine_monthly.json` | IQVIA Vaccines | Monthly trajectories for RSV, pneumococcal, TBE |

## Visual style

- 1280×720 fixed slide, auto-scaled to viewport
- Inter Variable font (inlined via `@fontsource-variable/inter`)
- Four colour-coded tracks (A blue, B amber, C green, D grey) used consistently across all slides
- Status pills: VERIFIED green, OBSERVED cyan, INFERRED amber, OPEN red

## Keyboard shortcuts

| Key | Action |
|-----|--------|
| `→` · `Space` · `PageDown` | Next slide |
| `←` · `PageUp` | Previous slide |
| `Home` | First slide |
| `End` | Last slide |
| ToC button | Overlay grid for jumping to any slide |

## Build output

`npm run build` produces a single `dist/index.html` (~670 KB, gzipped ~330 KB). No external dependencies at runtime. Suitable for emailing, hosting on any static service, or printing to PDF via the browser.
