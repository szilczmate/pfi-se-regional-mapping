# Author: Sergio Flores - Viti Science - VS-2026-PFI-001
# B_budget_impact.R — Regional budget impact in SEK per Pfizer product
#
# Translates patient counts into financial impact per region.
# Budget is the language regions actually use to make decisions.

source("00_setup_v2.R")

DATA <- load_all_data()

rx <- DATA$rx_long %>%
  filter(year == 2024) %>%
  left_join(DATA$region_master %>%
              select(region, population, hc_cost_per_capita = hc_cost_inv) %>%
              mutate(population = as.numeric(population),
                     hc_cost_per_capita = as.numeric(hc_cost_per_capita)),
            by = "region") %>%
  left_join(PFIZER_PRODUCTS %>% select(atc, brand, annual_cost_sek),
            by = "atc") %>%
  mutate(
    annual_cost_mnkr = patients * annual_cost_sek / 1e6,
    cost_per_capita = patients * annual_cost_sek / population,
    pct_of_hc_budget = (cost_per_capita / hc_cost_per_capita) * 100
  )

# Per-product national total
national_cost <- rx %>%
  group_by(brand) %>%
  summarise(total_patients = sum(patients),
            total_cost_mnkr = sum(annual_cost_mnkr),
            .groups = "drop") %>%
  arrange(desc(total_cost_mnkr))

cat("National Pfizer oral-Rx cost by product (2024):\n")
print(national_cost)
write_csv(rx, file.path(DATA_ROOT, "interim/analysis_B_budget_impact.csv"))

# =========================================================
# Figure B1 — Budget impact per product × region (SEK mnkr)
# =========================================================
heatmap_data <- rx %>%
  mutate(region = factor(region, levels = rev(REGION_ORDER)),
         brand = factor(brand, levels = PFIZER_PRODUCTS$brand))

# Audit fix R15: dynamic text color so labels readable on any fill
# Cells below 33% of max get dark text; above get white
fill_max <- max(heatmap_data$annual_cost_mnkr, na.rm = TRUE)
heatmap_data <- heatmap_data %>%
  mutate(label_color = ifelse(annual_cost_mnkr / fill_max < 0.33,
                              PF_PALETTE$charcoal, "white"))

p1 <- ggplot(heatmap_data, aes(x = brand, y = region,
                                fill = annual_cost_mnkr)) +
  geom_tile(color = "white", linewidth = 0.4) +
  geom_text(aes(label = ifelse(annual_cost_mnkr >= 1,
                                sprintf("%.0f", annual_cost_mnkr),
                                ifelse(annual_cost_mnkr >= 0.1,
                                       sprintf("%.1f", annual_cost_mnkr),
                                       "")),
                 color = I(label_color)),
            family = BASE_FONT, size = 2.9, fontface = "bold") +
  scale_fill_gradientn(colors = PF_SEQ_BLUE,
                       name = "Annual cost (M SEK)",
                       labels = function(x) paste0(x, " M"),
                       guide = guide_colorbar(barwidth = 14, barheight = 0.45,
                                              title.position = "top",
                                              title.hjust = 0)) +
  scale_x_discrete(position = "top") +
  labs(
    title = "Regional budget impact of Pfizer oral-Rx products (2024)",
    subtitle = "Estimated annual cost per region × product in millions SEK. Based on observed patient counts × TLV/benchmark annual price. Text shown where cost ≥0.1 M SEK.",
    x = NULL, y = NULL,
    caption = "Source: Socialstyrelsen Prescribed Drug Register 2024 + TLV/published annual-cost benchmarks per product. Conservative price estimates: Ibrance ~220k, Vyndaqel ~800k, Talzenna ~320k, Lorbrena ~350k, Tukysa ~580k, Vydura ~2,5k, Paxlovid ~5,4k SEK/patient/year."
  ) +
  theme_pfizer() +
  theme(panel.grid = element_blank(),
        axis.ticks = element_blank(),
        axis.line = element_blank(),
        axis.text.x.top = element_text(face = "bold"),
        legend.position = "bottom")

save_fig(p1, "B1_budget_impact_heatmap", width = 11, height = 8)

# =========================================================
# Figure B2 — Per-capita cost by region (bar)
# =========================================================
per_capita_total <- rx %>%
  group_by(region) %>%
  summarise(total_cost_per_capita = sum(cost_per_capita, na.rm = TRUE),
            .groups = "drop") %>%
  arrange(desc(total_cost_per_capita)) %>%
  mutate(region = factor(region, levels = rev(region))) %>%
  with_svr()

p2 <- ggplot(per_capita_total, aes(x = total_cost_per_capita, y = region,
                                    fill = healthcare_region)) +
  geom_col(width = 0.72) +
  geom_text(aes(label = sprintf("%.0f", total_cost_per_capita), hjust = -0.2),
            family = BASE_FONT, size = 3.2, color = PF_PALETTE$text_primary,
            fontface = "bold") +
  scale_fill_manual(values = SVR_COLORS, name = "Healthcare region") +
  scale_x_continuous(labels = function(x) paste0(x, " SEK"),
                     expand = expansion(mult = c(0, 0.08))) +
  labs(
    title = "Pfizer oral-Rx cost per capita by region",
    subtitle = "Total annual cost of Pfizer oral prescription products (7 ATCs) per resident. Reflects both disease-burden variation and regional prescribing preference.",
    x = "SEK per resident per year",
    y = NULL,
    caption = "Source: Socialstyrelsen Prescribed Drug Register 2024 + benchmark prices. Divided by SCB BE0101 population."
  ) +
  theme_pfizer() +
  theme(panel.grid.major.y = element_blank())

save_fig(p2, "B2_pfizer_cost_per_capita", width = 11, height = 8)

# =========================================================
# Figure B3 — Pfizer cost as % of healthcare budget
# =========================================================
budget_share <- rx %>%
  group_by(region) %>%
  summarise(cost_per_capita = sum(cost_per_capita, na.rm = TRUE),
            hc_cost_per_capita = first(hc_cost_per_capita),
            .groups = "drop") %>%
  mutate(share_pct = cost_per_capita / hc_cost_per_capita * 100) %>%
  arrange(desc(share_pct)) %>%
  mutate(region = factor(region, levels = rev(region))) %>%
  with_svr()

p3 <- ggplot(budget_share, aes(x = share_pct, y = region,
                                fill = healthcare_region)) +
  geom_col(width = 0.72) +
  geom_text(aes(label = sprintf("%.3f%%", share_pct), hjust = -0.15),
            family = BASE_FONT, size = 3.0, color = PF_PALETTE$text_primary) +
  scale_fill_manual(values = SVR_COLORS, name = "Healthcare region") +
  scale_x_continuous(labels = function(x) paste0(x, "%"),
                     expand = expansion(mult = c(0, 0.15))) +
  labs(
    title = "Pfizer oral-Rx spend as share of regional healthcare budget",
    subtitle = "Pfizer's 7 oral products account for 0.03–0.15% of total per-capita healthcare spending. Northern regions over-index driven by Vyndaqel's Skellefteå cluster economics.",
    x = "Pfizer oral-Rx / total HC cost per capita",
    y = NULL,
    caption = "Source: Socialstyrelsen Prescribed Drug Register 2024 + Kolada N70061 total HC cost per capita. Benchmark annual-cost estimates per product."
  ) +
  theme_pfizer() +
  theme(panel.grid.major.y = element_blank())

save_fig(p3, "B3_pfizer_share_of_hc_budget", width = 11, height = 8)

cat("\nAnalysis B complete.\n")
