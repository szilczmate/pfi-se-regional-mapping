# Author: Sergio Flores - Viti Science - VS-2026-PFI-001
# 01_penetration_gap.R — Demographic-adjusted penetration gap per Pfizer product × region
#
# Question: given each region's eligible-population denominator, how does observed
# Rx use compare to expected? Negative gap = under-treating; positive gap = over-indexing.

source("00_setup_v2.R")
suppressPackageStartupMessages({
  library(gt)
  library(ggrepel)
})

DATA <- load_all_data()

rx <- DATA$rx_long %>%
  left_join(DATA$region_master %>%
              select(region, population) %>%
              mutate(population = as.numeric(population)),
            by = "region") %>%
  mutate(patients_per_100k = patients / population * 1e5)

rx_2024 <- rx %>% filter(year == 2024)

nat_rate <- rx_2024 %>%
  group_by(atc) %>%
  summarise(total_patients = sum(patients, na.rm = TRUE),
            total_pop = sum(population, na.rm = TRUE),
            national_per_100k = total_patients / total_pop * 1e5,
            .groups = "drop") %>%
  left_join(PFIZER_PRODUCTS, by = "atc")

gap <- rx_2024 %>%
  left_join(nat_rate %>% select(atc, national_per_100k), by = "atc") %>%
  mutate(expected_patients = round(national_per_100k * population / 1e5),
         gap = patients - expected_patients,
         gap_pct = (patients - expected_patients) / pmax(expected_patients, 1) * 100,
         gap_category = case_when(
           gap_pct <= -50 ~ "Severe under-use (≤−50%)",
           gap_pct <= -20 ~ "Moderate under-use (−50 to −20%)",
           gap_pct >= 50  ~ "Severe over-use (≥+50%)",
           gap_pct >= 20  ~ "Moderate over-use (+20 to +50%)",
           TRUE           ~ "Near expected (±20%)"
         )) %>%
  left_join(PFIZER_PRODUCTS %>% select(atc, brand, indication_short), by = "atc") %>%
  with_svr()

write_csv(gap, file.path(DATA_ROOT, "interim/analysis1_penetration_gap.csv"))

# ========================================================
# Figure 1.1 — Penetration gap heatmap
# ========================================================
gap_category_levels <- c(
  "Severe under-use (≤−50%)",
  "Moderate under-use (−50 to −20%)",
  "Near expected (±20%)",
  "Moderate over-use (+20 to +50%)",
  "Severe over-use (≥+50%)"
)

heatmap_data <- gap %>%
  mutate(gap_category = factor(gap_category, levels = gap_category_levels),
         region = factor(region, levels = rev(REGION_ORDER)),
         brand = factor(brand, levels = PFIZER_PRODUCTS$brand))

cat_colors <- c(
  "Severe under-use (≤−50%)"           = PF_PALETTE$red,
  "Moderate under-use (−50 to −20%)"    = PF_PALETTE$orange,
  "Near expected (±20%)"                = "#D3D3D3",
  "Moderate over-use (+20 to +50%)"     = PF_PALETTE$light_blue,
  "Severe over-use (≥+50%)"             = PF_PALETTE$navy
)

# Audit fix R10: dynamic text color so labels are readable on any fill
# Light grey "Near expected" cells now get dark text; saturated cells get white
heatmap_data <- heatmap_data %>%
  mutate(label_color = ifelse(gap_category == "Near expected (±20%)",
                              PF_PALETTE$charcoal, "white"))

p1 <- ggplot(heatmap_data, aes(x = brand, y = region, fill = gap_category)) +
  geom_tile(color = "white", linewidth = 0.4) +
  geom_text(aes(label = ifelse(abs(gap_pct) >= 30,
                                 sprintf("%+d%%", round(gap_pct)),
                                 ""),
                 color = I(label_color)),
            family = BASE_FONT, size = 3, fontface = "bold") +
  scale_fill_manual(values = cat_colors, drop = FALSE,
                    name = NULL, guide = guide_legend(nrow = 2, byrow = TRUE)) +
  scale_x_discrete(position = "top") +
  labs(
    title = "Regional penetration gap — Pfizer products 2024",
    subtitle = "Gap = observed patients − demographically expected (national per-capita rate × regional population)",
    x = NULL, y = NULL,
    caption = "Source: Socialstyrelsen Prescribed Drug Register 2024 + SCB BE0101 population 2024.\nText shown for deviations ≥ 30%."
  ) +
  theme_pfizer() +
  theme(
    panel.grid = element_blank(),
    axis.ticks = element_blank(),
    axis.line = element_blank(),
    axis.text.x.top = element_text(angle = 0, hjust = 0.5, face = "bold"),
    legend.position = "bottom"
  )

save_fig(p1, "01_penetration_gap_heatmap", width = 11, height = 8)

# ========================================================
# Figure 1.2 — Top 20 penetration signals
# ========================================================
top_signals <- gap %>%
  filter(expected_patients >= 5) %>%
  mutate(signal_label = sprintf("%s — %s", brand, region)) %>%
  arrange(desc(abs(gap_pct))) %>%
  slice_head(n = 20) %>%
  mutate(signal_label = factor(signal_label, levels = rev(signal_label)),
         direction = ifelse(gap_pct > 0, "Over-use", "Under-use"))

p2 <- ggplot(top_signals, aes(x = gap_pct, y = signal_label, fill = direction)) +
  geom_col(width = 0.7) +
  geom_text(aes(label = sprintf("obs %d · exp %d", patients, expected_patients),
                hjust = ifelse(gap_pct > 0, -0.05, 1.05)),
            size = 2.8, color = PF_PALETTE$grey) +
  geom_vline(xintercept = 0, color = PF_PALETTE$grey, linewidth = 0.3) +
  scale_fill_manual(values = c("Over-use" = PF_PALETTE$navy,
                               "Under-use" = PF_PALETTE$red),
                    name = NULL) +
  scale_x_continuous(labels = function(x) paste0(x, "%"),
                     expand = expansion(mult = c(0.15, 0.15))) +
  labs(
    title = "Top 20 penetration signals — largest deviations from demographic expectation",
    subtitle = "Positive = region over-indexes vs expected; negative = under-uses. Excludes combinations with <5 expected patients.",
    x = "Deviation from expected (%)", y = NULL,
    caption = "Source: Socialstyrelsen Prescribed Drug Register + SCB 2024. Expected = national per 100k × regional population."
  ) +
  theme_pfizer()

save_fig(p2, "01_penetration_gap_top20", width = 11, height = 9)

# ========================================================
# gt summary table (just HTML — skip PNG export to avoid webshot complexity)
# ========================================================
summary_tbl <- gap %>%
  group_by(brand, indication_short) %>%
  summarise(
    national_obs = sum(patients),
    national_expected = sum(expected_patients),
    n_regions_under = sum(gap_pct <= -20, na.rm = TRUE),
    n_regions_over = sum(gap_pct >= 20, na.rm = TRUE),
    spread_max_over = max(gap_pct, na.rm = TRUE),
    spread_max_under = min(gap_pct, na.rm = TRUE),
    .groups = "drop"
  ) %>%
  arrange(desc(national_obs))

gt_tbl <- summary_tbl %>%
  gt() %>%
  tab_header(
    title = md("**Pfizer products — penetration gap summary 2024**"),
    subtitle = "Based on Socialstyrelsen Prescribed Drug Register per region × ATC"
  ) %>%
  cols_label(
    brand = "Product",
    indication_short = "Indication",
    national_obs = "Total patients",
    national_expected = "Expected",
    n_regions_under = "Regions −20%",
    n_regions_over = "Regions +20%",
    spread_max_over = "Max over-index",
    spread_max_under = "Max under-index"
  ) %>%
  fmt_number(columns = c(national_obs, national_expected),
             decimals = 0, sep_mark = " ") %>%
  fmt_number(columns = c(spread_max_over, spread_max_under),
             decimals = 0, pattern = "{x}%") %>%
  tab_source_note("Source: Socialstyrelsen Prescribed Drug Register + SCB BE0101. Extracted 2026-04-24.") %>%
  tab_options(
    table.font.names = "Calibri",
    heading.title.font.size = 14,
    column_labels.background.color = PF_PALETTE$navy,
    column_labels.font.weight = "bold",
    table.font.size = 10
  ) %>%
  tab_style(style = cell_text(color = "white"),
            locations = cells_column_labels())

gtsave(gt_tbl, file.path(FIG_DIR, "01_penetration_gap_summary_table.html"))

cat("\nTop penetration signals:\n")
top_signals %>% head(10) %>% select(brand, region, patients, expected_patients, gap_pct) %>% print()
cat("\nAnalysis 1 complete.\n")
