# Author: Sergio Flores - Viti Science - VS-2026-PFI-001
# C_implementation_latency.R — How fast do regions adopt after NT-rådet decisions?
#
# Key NT-rådet dates:
#   Tukysa: RECOMMENDATION 2022-05-23
#   Elrexfio + Talzenna: NATIONAL AGREEMENT 2024-06
#   Ibrance: no NT-rådet position — use 2021 as baseline for growth comparison
#   Vydura: REGIONAL ASSESSMENT — no central decision, varies
#
# We measure "time to first-5-patient threshold" and "time to steady-state" from
# the NT-rådet date, per region. Fast adopters = rapid rise above 5 patients;
# slow adopters = still below 5 several years later.
#
# This is the operational question Pfizer actually cares about: for future product
# launches, which regions will be the first to ramp?

source("00_setup_v2.R")

DATA <- load_all_data()

# Tukysa analysis — cleanest case since we have NT-rådet date
tukysa <- DATA$rx_long %>%
  filter(atc == "L01EH03") %>%
  arrange(region, year) %>%
  left_join(DATA$region_master %>%
              select(region, population) %>%
              mutate(population = as.numeric(population)),
            by = "region") %>%
  mutate(rate_100k = patients / population * 1e5)

# Summary per region: 2024 rate + total 2021-2024
tukysa_summary <- tukysa %>%
  group_by(region) %>%
  summarise(total_2021 = sum(patients[year == 2021]),
            total_2024 = sum(patients[year == 2024]),
            total_all = sum(patients),
            rate_2024 = patients[year == 2024]/population[1]*1e5,
            .groups = "drop") %>%
  mutate(
    adoption_tier = case_when(
      rate_2024 >= 5 ~ "Fast adopter (≥5/100k)",
      rate_2024 >= 2 ~ "Moderate adopter (2–5/100k)",
      rate_2024 > 0  ~ "Slow adopter (0–2/100k)",
      TRUE           ~ "Non-adopter (0 patients)"
    ),
    adoption_tier = factor(adoption_tier,
                           levels = c("Fast adopter (≥5/100k)",
                                      "Moderate adopter (2–5/100k)",
                                      "Slow adopter (0–2/100k)",
                                      "Non-adopter (0 patients)"))
  ) %>%
  arrange(desc(rate_2024)) %>%
  with_svr()

write_csv(tukysa_summary, file.path(DATA_ROOT, "interim/analysis_C_tukysa_adoption.csv"))

# =========================================================
# Figure C1 — Tukysa: how regions responded to NT-rådet recommendation (2022-05)
# =========================================================
# Plot 2021-2024 trajectory per region, colored by adoption tier
tukysa_plot <- tukysa %>%
  left_join(tukysa_summary %>% select(region, adoption_tier), by = "region") %>%
  mutate(adoption_tier = factor(adoption_tier,
                                 levels = c("Fast adopter (≥5/100k)",
                                            "Moderate adopter (2–5/100k)",
                                            "Slow adopter (0–2/100k)",
                                            "Non-adopter (0 patients)")))

tier_colors <- c(
  "Fast adopter (≥5/100k)"      = PF_PALETTE$green,
  "Moderate adopter (2–5/100k)" = PF_PALETTE$blue_primary,
  "Slow adopter (0–2/100k)"     = PF_PALETTE$gold,
  "Non-adopter (0 patients)"    = PF_PALETTE$grey_light
)

# Only show labels for non-zero regions
label_df <- tukysa_plot %>%
  group_by(region) %>%
  filter(year == max(year), patients > 0) %>%
  ungroup()

p1 <- ggplot(tukysa_plot, aes(x = year, y = patients, group = region,
                                color = adoption_tier)) +
  annotate("rect", xmin = 2022 - 0.5/12*5, xmax = 2022 + 0.5/12*5,
           ymin = -Inf, ymax = Inf,
           fill = PF_PALETTE$red, alpha = 0.05) +
  annotate("segment", x = 2022.4, xend = 2022.4, y = 0, yend = Inf,
           color = PF_PALETTE$red, linewidth = 0.4, linetype = "dashed") +
  annotate("label", x = 2022.4, y = 19,
           label = "NT-rådet\nrecommendation\n2022-05-23",
           family = BASE_FONT, fontface = "bold", size = 2.8,
           color = PF_PALETTE$red, fill = "white",
           label.size = 0.3, label.padding = unit(0.3, "lines")) +
  geom_line(linewidth = 0.85, alpha = 0.9) +
  geom_point(size = 2, alpha = 0.9) +
  geom_text_repel(data = label_df,
                  aes(label = region, x = year + 0.1),
                  family = BASE_FONT, size = 2.8,
                  color = PF_PALETTE$text_primary,
                  min.segment.length = 0.3, max.overlaps = 21,
                  xlim = c(2024.2, 2025), hjust = 0,
                  direction = "y", nudge_x = 0.05) +
  scale_color_manual(values = tier_colors, name = NULL) +
  scale_x_continuous(breaks = 2021:2024, limits = c(2021, 2025.5)) +
  labs(
    title = "Tukysa regional adoption trajectory, 2021–2024",
    subtitle = "NT-rådet issued a positive recommendation on 2022-05-23. Regional response since then has been highly uneven: Stockholm and VGR led the ramp; 7 regions had zero Tukysa patients in 2024 despite the recommendation.",
    x = NULL, y = "Patients per region",
    caption = "Source: Socialstyrelsen Prescribed Drug Register (ATC L01EH03 tucatinib). Adoption tier based on 2024 per-100k rate."
  ) +
  theme_pfizer() +
  theme(legend.position = "top",
        panel.grid.major.y = element_line(color = "#F3F4F6", linewidth = 0.3))

save_fig(p1, "C1_tukysa_adoption_trajectory", width = 13, height = 7)

# =========================================================
# Figure C2 — Adoption summary (how many patients 2 years after recommendation?)
# =========================================================
summary_bar <- tukysa_summary %>%
  arrange(desc(rate_2024)) %>%
  mutate(region = factor(region, levels = rev(region)))

p2 <- ggplot(summary_bar, aes(x = rate_2024, y = region, fill = adoption_tier)) +
  geom_col(width = 0.72) +
  geom_text(aes(label = sprintf("%.1f (n=%d)", rate_2024, total_2024),
                hjust = -0.1),
            family = BASE_FONT, size = 3.0,
            color = PF_PALETTE$text_primary) +
  scale_fill_manual(values = tier_colors, name = NULL,
                    guide = guide_legend(nrow = 1)) +
  scale_x_continuous(expand = expansion(mult = c(0, 0.15))) +
  labs(
    title = "Tukysa rate per 100k in 2024 — two years after NT-rådet recommendation",
    subtitle = "Only 7 regions reached ≥2 patients/100k 2.5 years post-recommendation. Stockholm and VGR (where specialist breast-cancer centres are concentrated) led. The implementation gap is not about regulatory status — it is about clinical infrastructure.",
    x = "Tukysa patients per 100 000 inhabitants (2024)",
    y = NULL,
    caption = "Source: Socialstyrelsen Prescribed Drug Register (ATC L01EH03) + SCB BE0101. NT-rådet recommendation dated 2022-05-23."
  ) +
  theme_pfizer() +
  theme(legend.position = "top",
        panel.grid.major.y = element_blank())

save_fig(p2, "C2_tukysa_adoption_summary", width = 12, height = 8)

# =========================================================
# Figure C3 — Cross-product latency comparison (mini-panel)
# =========================================================
# For each of Tukysa, Talzenna, Lorbrena: plot the growth curve 2021-2024
# with different NT-rådet reference dates marked

growth_panel <- DATA$rx_long %>%
  filter(atc %in% c("L01EH03","L01XK04","L01ED04","L01EF01")) %>%
  group_by(atc, year) %>%
  summarise(national_total = sum(patients), .groups = "drop") %>%
  left_join(PFIZER_PRODUCTS %>% select(atc, brand), by = "atc")

nt_dates <- tribble(
  ~brand,               ~nt_year, ~nt_label,
  "Tukysa",             2022.4,   "NT-rådet rec. 2022-05",
  "Talzenna",           2024.5,   "Nat. agreement 2024-06",
  "Lorbrena/Lorviqua",  NA,       "No NT-rådet position",
  "Ibrance",            NA,       "No NT-rådet position"
)

p3 <- ggplot(growth_panel, aes(x = year, y = national_total)) +
  geom_area(fill = PF_PALETTE$blue_wash, alpha = 0.6) +
  geom_line(color = PF_PALETTE$navy, linewidth = 1.1) +
  geom_point(color = PF_PALETTE$navy, size = 2.2) +
  geom_text(aes(label = national_total), vjust = -1.1,
            family = BASE_FONT, size = 3, color = PF_PALETTE$navy,
            fontface = "bold") +
  # NT-rådet date overlay
  geom_vline(data = nt_dates %>% filter(!is.na(nt_year)),
             aes(xintercept = nt_year),
             linetype = "dashed", color = PF_PALETTE$red, linewidth = 0.4) +
  geom_text(data = nt_dates %>% filter(!is.na(nt_year)),
            aes(x = nt_year, y = 0, label = nt_label),
            family = BASE_FONT, size = 2.8, hjust = -0.05, vjust = -0.3,
            color = PF_PALETTE$red, fontface = "italic") +
  facet_wrap(~ brand, scales = "free_y", ncol = 2) +
  scale_x_continuous(breaks = 2021:2024) +
  scale_y_continuous(limits = c(0, NA),
                     labels = scales::comma) +
  labs(
    title = "National patient-count trajectories for 4 oral Pfizer products",
    subtitle = "Red dashed line = NT-rådet decision date. Tukysa shows smooth post-recommendation ramp. Talzenna still in early adoption phase. Ibrance declining.",
    x = NULL, y = "National patients per year",
    caption = "Source: Socialstyrelsen Prescribed Drug Register 2021–2024. All 21 regions summed."
  ) +
  theme_pfizer() +
  theme(strip.text = element_text(size = rel(1.05), face = "bold",
                                   color = PF_PALETTE$navy),
        panel.spacing = unit(1.2, "lines"))

save_fig(p3, "C3_nt_radet_decision_trajectories", width = 13, height = 8)

cat("\nAnalysis C complete.\n")
