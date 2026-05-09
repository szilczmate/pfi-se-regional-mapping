# Author: Sergio Flores - Viti Science - VS-2026-PFI-001
# A_abrysvo_avvakta.R — The Abrysvo "avvakta" signal
#
# On 2023-10-05, NT-rådet issued an "avvakta" (hold / await) position on Abrysvo
# RSV vaccine — effectively a recommendation to regions NOT to start procuring
# pending updated evidence or a renegotiated price.
#
# Question: despite that national hold, which regions are actually buying Abrysvo?
# Those are the regions where LOCAL clinical leadership is overriding NATIONAL
# caution — the strongest political signal available in this dataset, and the
# most actionable identifier of Pfizer's natural early-partner regions.

source("00_setup_v2.R")

DATA <- load_all_data()

# Get Abrysvo share from vaccine-market-share sheet (already computed)
vacc <- DATA$vaccines %>%
  rename(
    rsv_total = rsv_total,
    abrysvo   = pfizer_abrysvo,
    rsv_share = share_percent_5
  ) %>%
  select(region, rsv_total, abrysvo, rsv_share) %>%
  left_join(DATA$region_master %>%
              select(region, population) %>%
              mutate(population = as.numeric(population)),
            by = "region") %>%
  mutate(abrysvo_spend_per_capita = abrysvo / population,
         abrysvo_active = abrysvo > 50000)  # threshold for "actively procuring"

national_abrysvo <- sum(vacc$abrysvo) / sum(vacc$rsv_total) * 100
cat(sprintf("National Abrysvo share (despite avvakta): %.1f%%\n", national_abrysvo))
cat(sprintf("Active regions (>50k SEK spend): %d of 21\n", sum(vacc$abrysvo_active)))

vacc <- vacc %>%
  mutate(
    signal_tier = case_when(
      rsv_share >= 75 ~ "Strong override (≥75% Pfizer share)",
      rsv_share >= 50 ~ "Moderate override (50–75%)",
      rsv_share >= 20 ~ "Cautious adoption (20–50%)",
      TRUE            ~ "Compliant with avvakta (<20%)"
    ),
    signal_tier = factor(signal_tier,
                         levels = c("Strong override (≥75% Pfizer share)",
                                    "Moderate override (50–75%)",
                                    "Cautious adoption (20–50%)",
                                    "Compliant with avvakta (<20%)"))
  ) %>%
  with_svr()

write_csv(vacc, file.path(DATA_ROOT, "interim/analysis_A_abrysvo_signal.csv"))

# =========================================================
# Figure A — Abrysvo avvakta signal ranked
# =========================================================
tier_colors <- c(
  "Strong override (≥75% Pfizer share)" = PF_PALETTE$red,
  "Moderate override (50–75%)"          = "#F4A261",
  "Cautious adoption (20–50%)"          = PF_PALETTE$blue_soft,
  "Compliant with avvakta (<20%)"       = PF_PALETTE$grey_light
)

plot_df <- vacc %>%
  arrange(desc(rsv_share)) %>%
  mutate(region = factor(region, levels = rev(region)))

p <- ggplot(plot_df, aes(x = rsv_share, y = region, fill = signal_tier)) +
  geom_col(width = 0.72) +
  # National avg line
  geom_vline(xintercept = national_abrysvo, linetype = "dashed",
             color = PF_PALETTE$charcoal, linewidth = 0.45) +
  # Value labels
  geom_text(aes(label = sprintf("%.0f%%", rsv_share), hjust = -0.25),
            family = BASE_FONT, size = 3.2, color = PF_PALETTE$text_primary,
            fontface = "bold") +
  annotate("text", x = national_abrysvo, y = 22,
           label = sprintf("National avg: %.1f%%", national_abrysvo),
           family = BASE_FONT, size = 3, color = PF_PALETTE$charcoal,
           vjust = -0.5, hjust = 0, fontface = "italic") +
  scale_fill_manual(values = tier_colors, name = NULL,
                    guide = guide_legend(nrow = 2, byrow = TRUE)) +
  scale_x_continuous(labels = function(x) paste0(x, "%"),
                     limits = c(0, 100),
                     expand = expansion(mult = c(0, 0.08))) +
  labs(
    title = "Abrysvo — the avvakta override signal",
    subtitle = "NT-rådet issued an 'avvakta' hold on Abrysvo on 2023-10-05. Regional procurement continuing despite the hold is the strongest political signal in the dataset — a marker of local clinical leadership overriding national caution.",
    x = "Pfizer Abrysvo share of RSV vaccine market (IQVIA 36-mo rolling)",
    y = NULL,
    caption = "Source: Pfizer IQVIA vaccines extract 2026-04-02 (ATC J07BX05). National RSV market includes Pfizer Abrysvo and GSK Arexvy."
  ) +
  theme_pfizer() +
  theme(legend.position = "top",
        panel.grid.major.y = element_blank())

save_fig(p, "A_abrysvo_avvakta_signal", width = 12, height = 8)

# =========================================================
# Figure A-2 — Strongest-override regions (callouts)
# =========================================================
top_override <- vacc %>%
  filter(rsv_share >= 60) %>%
  arrange(desc(rsv_share)) %>%
  slice_head(n = 8)

cat("\nTop override regions (Pfizer-share ≥60% despite avvakta):\n")
print(top_override %>% select(region, rsv_share, abrysvo_spend_per_capita, healthcare_region))

cat("\nAnalysis A complete.\n")
