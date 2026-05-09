# Author: Sergio Flores - Viti Science - VS-2026-PFI-001
# 05_opportunity_sizing.R — Market-opportunity sizing with uncertainty bands
#
# Question: if Pfizer "closes the gap" (e.g., if under-indexing regions moved to
# national median on Ibrance, Tukysa, etc.), how many additional patients per year?
# What is the plausible range?
#
# Method:
#   Observed patients per region × ATC (2024)
#   Scenario 1: all regions move to 25th-percentile region's rate (conservative ceiling — removes worst under-use)
#   Scenario 2: all regions move to national median rate
#   Scenario 3: all regions move to 75th-percentile region's rate (optimistic)
#   Bootstrap confidence intervals (n = 1000 samples).

source("00_setup_v2.R")
suppressPackageStartupMessages({
  library(gt)
})

DATA <- load_all_data()

rx_2024 <- DATA$rx_long %>%
  filter(year == 2024) %>%
  left_join(DATA$region_master %>%
              select(region, population) %>%
              mutate(population = as.numeric(population)),
            by = "region") %>%
  mutate(rate_100k = patients / population * 1e5)

# Per ATC: compute percentile benchmarks
atc_benchmarks <- rx_2024 %>%
  group_by(atc) %>%
  summarise(
    p25 = quantile(rate_100k, 0.25, na.rm = TRUE),
    p50 = median(rate_100k, na.rm = TRUE),
    p75 = quantile(rate_100k, 0.75, na.rm = TRUE),
    .groups = "drop"
  )

# Scenario patients = max(observed, benchmark × pop)
scenarios <- rx_2024 %>%
  left_join(atc_benchmarks, by = "atc") %>%
  left_join(PFIZER_PRODUCTS %>% select(atc, brand), by = "atc") %>%
  mutate(
    patients_at_p25 = pmax(patients, round(p25 * population / 1e5)),
    patients_at_p50 = pmax(patients, round(p50 * population / 1e5)),
    patients_at_p75 = pmax(patients, round(p75 * population / 1e5)),
    uplift_p25 = patients_at_p25 - patients,
    uplift_p50 = patients_at_p50 - patients,
    uplift_p75 = patients_at_p75 - patients
  )

national_uplift <- scenarios %>%
  group_by(brand, atc) %>%
  summarise(
    observed_2024 = sum(patients),
    at_p25 = sum(patients_at_p25),
    at_p50 = sum(patients_at_p50),
    at_p75 = sum(patients_at_p75),
    uplift_pct_p50 = (at_p50 - observed_2024)/observed_2024 * 100,
    uplift_pct_p75 = (at_p75 - observed_2024)/observed_2024 * 100,
    .groups = "drop"
  ) %>%
  arrange(desc(observed_2024))

# Bootstrap CI for median scenario uplift per product
set.seed(42)
boot_uplift <- scenarios %>%
  group_by(brand) %>%
  summarise(
    obs = sum(patients),
    mean_p50 = mean(replicate(1000, sum(pmax(sample(patients, replace = TRUE),
                                              round(p50 * population[1] / 1e5))))),
    lo_p50 = quantile(replicate(1000, sum(pmax(sample(patients, replace = TRUE),
                                                round(p50 * population[1] / 1e5)))), 0.025),
    hi_p50 = quantile(replicate(1000, sum(pmax(sample(patients, replace = TRUE),
                                                round(p50 * population[1] / 1e5)))), 0.975),
    .groups = "drop"
  )

write_csv(national_uplift, file.path(DATA_ROOT, "interim/analysis5_opportunity_uplift.csv"))

# =========================================================
# Figure 5.1 — Opportunity waterfall per product
# =========================================================
plot_data <- national_uplift %>%
  select(brand, observed_2024, at_p50, at_p75) %>%
  pivot_longer(cols = c(observed_2024, at_p50, at_p75),
               names_to = "scenario", values_to = "patients") %>%
  mutate(scenario = factor(scenario,
                            levels = c("observed_2024","at_p50","at_p75"),
                            labels = c("Observed 2024",
                                      "If all regions at median rate",
                                      "If all regions at 75th-pctile rate"))) %>%
  mutate(brand = fct_reorder(brand, patients, .fun = max, .desc = TRUE))

p1 <- ggplot(plot_data, aes(x = brand, y = patients, fill = scenario)) +
  geom_col(position = position_dodge(width = 0.75), width = 0.65) +
  geom_text(aes(label = scales::comma(patients)),
            position = position_dodge(width = 0.75),
            vjust = -0.35, size = 3, color = PF_PALETTE$grey) +
  scale_fill_manual(values = c("Observed 2024" = PF_PALETTE$navy,
                               "If all regions at median rate" = PF_PALETTE$blue,
                               "If all regions at 75th-pctile rate" = PF_PALETTE$green),
                    name = NULL) +
  scale_y_continuous(labels = scales::comma, expand = expansion(mult = c(0, 0.12))) +
  labs(
    title = "Market opportunity — patient uplift if under-indexing regions moved to benchmarks",
    subtitle = "Three scenarios per Pfizer oral product. 'Median' = half of regions already above this rate. '75th percentile' = top-quartile region.",
    x = NULL, y = "National patients per year",
    caption = "Source: Socialstyrelsen Prescribed Drug Register 2024. Opportunity = max(observed, benchmark × regional population). Regions already above benchmark are held at observed."
  ) +
  theme_pfizer() +
  theme(legend.position = "top",
        axis.text.x = element_text(angle = 0, face = "bold"))

save_fig(p1, "05_opportunity_waterfall", width = 12, height = 6.5)

# =========================================================
# Figure 5.2 — Regional uplift breakdown per product (top 10 opportunities)
# =========================================================
top_opportunities <- scenarios %>%
  filter(uplift_p50 > 0) %>%
  arrange(desc(uplift_p50)) %>%
  slice_head(n = 20) %>%
  mutate(label = sprintf("%s — %s", brand, region),
         label = fct_reorder(label, uplift_p50))

p2 <- ggplot(top_opportunities, aes(x = uplift_p50, y = label, fill = brand)) +
  geom_col(width = 0.7) +
  geom_text(aes(label = sprintf("+%d patients (obs %d → exp %d)",
                                 uplift_p50, patients, patients_at_p50),
                hjust = -0.05),
            size = 2.8, color = PF_PALETTE$grey) +
  scale_fill_manual(values = c(
    "Ibrance" = PF_PALETTE$blue,
    "Vyndaqel" = PF_PALETTE$red,
    "Tukysa" = PF_PALETTE$navy,
    "Vydura" = PF_PALETTE$purple,
    "Paxlovid" = PF_PALETTE$green,
    "Lorbrena/Lorviqua" = PF_PALETTE$orange,
    "Talzenna" = PF_PALETTE$midnight
  ), name = "Product") +
  scale_x_continuous(expand = expansion(mult = c(0, 0.35))) +
  labs(
    title = "Top 20 regional uplift opportunities (median-scenario)",
    subtitle = "Patient gain per region × product if that region moved to the national median rate per 100k.",
    x = "Patient uplift at national median rate", y = NULL,
    caption = "Source: Socialstyrelsen Prescribed Drug Register 2024. Assumes regions above national median hold at current rate."
  ) +
  theme_pfizer() +
  theme(legend.position = "top")

save_fig(p2, "05_top20_regional_uplift", width = 12, height = 9)

cat("\nNational-total uplift per product at median scenario:\n")
print(national_uplift)
cat("\nAnalysis 5 complete.\n")
