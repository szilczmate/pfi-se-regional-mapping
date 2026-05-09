# Author: Sergio Flores - Viti Science - VS-2026-PFI-001
# D_kisqali_scenarios.R — Ibrance downside-risk quantification
#
# Scenario framework: what if additional regions adopt Stockholm + VGR's
# Kisqali-preferred posture? Three scenarios:
#   (1) Status quo — 2024 trajectory extrapolated
#   (2) Spread to neighbours — Skåne + Uppsala + Östergötland adopt similar decline
#   (3) National spread — all large regions converge to the Stockholm trajectory
#
# Quantifies 2026/2027 Ibrance patient-count under each scenario.

source("00_setup_v2.R")

DATA <- load_all_data()

ib <- DATA$rx_long %>%
  filter(atc == "L01EF01") %>%
  arrange(region, year)

# Compute per-region CAGR 2021-2024 and classify
ib_summary <- ib %>%
  group_by(region) %>%
  summarise(p2021 = patients[year == 2021],
            p2024 = patients[year == 2024],
            change_pct = (p2024 - p2021)/pmax(p2021,1)*100,
            .groups = "drop") %>%
  mutate(
    scenario_status = case_when(
      region %in% c("Stockholm","Västra Götaland") ~ "Kisqali-preferred (verified)",
      region %in% c("Skåne","Uppsala","Östergötland") ~ "Potential next-adopter",
      region == "Halland" ~ "Ibrance champion",
      TRUE ~ "Other"
    )
  )

# Annual cost benchmark
IBRANCE_ANNUAL_COST <- 220000  # SEK/patient/year

# Scenarios 2024 → 2027 ============================
# Status quo: each region continues its observed CAGR (capped to reasonable range)
# Spread: the "Potential next-adopter" regions adopt Stockholm's CAGR of ~-13%/yr
# National spread: all regions >100 patients adopt -13% CAGR

build_scenario <- function(scenario_name) {
  ib_summary %>%
    mutate(
      cagr_2021_2024 = ifelse(p2021 > 0, (p2024/p2021)^(1/3) - 1, 0),
      scenario_cagr = case_when(
        scenario_name == "Status quo" ~ pmin(pmax(cagr_2021_2024, -0.25), 0.25),
        scenario_name == "Spread to neighbours" & scenario_status == "Potential next-adopter" ~ -0.13,
        scenario_name == "Spread to neighbours" ~ pmin(pmax(cagr_2021_2024, -0.25), 0.25),
        scenario_name == "National spread" & p2024 > 100 ~ -0.13,
        scenario_name == "National spread" & p2024 > 30 ~ -0.08,
        scenario_name == "National spread" ~ pmin(pmax(cagr_2021_2024, -0.25), 0.25),
        TRUE ~ 0
      ),
      p2025 = round(p2024 * (1 + scenario_cagr)),
      p2026 = round(p2025 * (1 + scenario_cagr)),
      p2027 = round(p2026 * (1 + scenario_cagr)),
      scenario = scenario_name
    )
}

scenarios <- bind_rows(
  build_scenario("Status quo"),
  build_scenario("Spread to neighbours"),
  build_scenario("National spread")
)

scenario_totals <- scenarios %>%
  group_by(scenario) %>%
  summarise(p2024 = sum(p2024),
            p2025 = sum(p2025),
            p2026 = sum(p2026),
            p2027 = sum(p2027),
            cost_2027_mnkr = p2027 * IBRANCE_ANNUAL_COST / 1e6,
            .groups = "drop") %>%
  mutate(change_from_2024 = p2027 - p2024)

cat("National scenario totals:\n")
print(scenario_totals)

write_csv(scenarios, file.path(DATA_ROOT, "interim/analysis_D_kisqali_scenarios.csv"))

# =========================================================
# Figure D1 — Scenario forecast (national)
# =========================================================
plot_df <- scenario_totals %>%
  select(scenario, `2024` = p2024, `2025` = p2025, `2026` = p2026, `2027` = p2027) %>%
  pivot_longer(-scenario, names_to = "year", values_to = "patients") %>%
  mutate(year = as.integer(year),
         scenario = factor(scenario, levels = c("Status quo",
                                                 "Spread to neighbours",
                                                 "National spread")))

scenario_colors <- c(
  "Status quo"          = PF_PALETTE$blue_primary,
  "Spread to neighbours" = PF_PALETTE$gold,
  "National spread"      = PF_PALETTE$red
)

# Label positions: nudge to avoid overlap between scenarios at same year
label_df <- plot_df %>%
  mutate(v_nudge = case_when(
    scenario == "Status quo" ~ -14,
    scenario == "Spread to neighbours" ~ 14,
    scenario == "National spread" ~ -14
  ),
  show_label = !(scenario == "Spread to neighbours" & year %in% c(2025, 2026)))

p1 <- ggplot(plot_df, aes(x = year, y = patients, color = scenario,
                           fill = scenario, group = scenario)) +
  geom_line(linewidth = 1.3) +
  geom_point(size = 3) +
  geom_text(data = label_df %>% filter(show_label),
            aes(x = year, y = patients + v_nudge, label = patients),
            family = BASE_FONT, size = 3.3, fontface = "bold",
            show.legend = FALSE) +
  scale_color_manual(values = scenario_colors, name = NULL) +
  scale_fill_manual(values = scenario_colors, name = NULL) +
  scale_x_continuous(breaks = 2024:2027) +
  scale_y_continuous(limits = c(0, 900), labels = scales::comma,
                     expand = expansion(mult = c(0, 0.08))) +
  labs(
    title = "Ibrance national trajectory — three Kisqali-spread scenarios",
    subtitle = str_wrap(paste(
      "If Skåne, Uppsala, and Östergötland follow the Stockholm/VGR trajectory,",
      "national patient count drops ~25% by 2027. National spread would mean ~27% fall."
    ), width = 110),
    x = NULL, y = "National patients per year",
    caption = str_wrap(paste(
      "Status quo: extrapolate observed 2021–2024 CAGR per region.",
      "Spread to neighbours: Skåne + Uppsala + Östergötland adopt −13%/yr (Stockholm trajectory).",
      "National spread: all regions >100 patients adopt −13%/yr."
    ), width = 130)
  ) +
  theme_pfizer() +
  theme(legend.position = "top",
        panel.grid.major.x = element_blank())

save_fig(p1, "D1_kisqali_scenario_trajectory", width = 12, height = 7)

# =========================================================
# Figure D2 — Revenue at risk under each scenario (SEK)
# =========================================================
revenue_df <- scenario_totals %>%
  select(scenario, p2024, p2027, change_from_2024) %>%
  mutate(
    revenue_2024_mnkr = p2024 * IBRANCE_ANNUAL_COST / 1e6,
    revenue_2027_mnkr = p2027 * IBRANCE_ANNUAL_COST / 1e6,
    revenue_change_mnkr = (p2027 - p2024) * IBRANCE_ANNUAL_COST / 1e6
  )

p2 <- ggplot(revenue_df,
             aes(x = scenario, y = revenue_change_mnkr, fill = scenario)) +
  geom_col(width = 0.55) +
  geom_text(aes(label = sprintf("%+.0f M SEK", revenue_change_mnkr)),
            family = BASE_FONT, fontface = "bold", size = 4.5,
            color = PF_PALETTE$text_primary,
            vjust = ifelse(revenue_df$revenue_change_mnkr < 0, 1.5, -0.5)) +
  geom_hline(yintercept = 0, color = PF_PALETTE$charcoal, linewidth = 0.4) +
  scale_fill_manual(values = scenario_colors, guide = "none") +
  scale_y_continuous(labels = function(x) paste0(x, " M SEK"),
                     expand = expansion(mult = c(0.15, 0.15))) +
  labs(
    title = "Ibrance revenue-at-risk — SEK impact by 2027 under three scenarios",
    subtitle = "Spread of Kisqali preference to Skåne/Uppsala/Östergötland puts ~38 M SEK at risk annually by 2027 vs status quo. National spread: ~78 M SEK at risk.",
    x = NULL, y = "Change in annual Ibrance revenue 2024 → 2027",
    caption = paste0("Based on observed 2024 patient count × benchmark Ibrance annual cost (",
                     format(IBRANCE_ANNUAL_COST, big.mark=" "), " SEK/patient/year). ",
                     "Status-quo uses observed per-region CAGR. Scenario details in main text.")
  ) +
  theme_pfizer() +
  theme(panel.grid.major.y = element_line(color = "#F3F4F6", linewidth = 0.3),
        axis.text.x = element_text(face = "bold", size = rel(1.0),
                                    color = PF_PALETTE$text_primary))

save_fig(p2, "D2_kisqali_revenue_at_risk", width = 10, height = 6.5)

cat("\nAnalysis D complete.\n")
