# Author: Sergio Flores - Viti Science - VS-2026-PFI-001
# 08_priority_matrix.R — Strategic priority matrix integrating all analyses
#
# Positions each of the 21 regions on two dimensions:
#   X axis: Current Pfizer footprint (composite of Rx volumes + vaccine share)
#   Y axis: Strategic leverage opportunity (composite of cluster, stakeholder, equity rank)
# Bubble size = population
# Color = regional cluster (from Analysis 4)
#
# Output: the single most strategic decision-support visualization — "where should
# Pfizer Access focus per unit of effort".

source("00_setup_v2.R")
suppressPackageStartupMessages({
  library(ggrepel)
  library(readxl)
})

DATA <- load_all_data()

# Read cluster assignments from Analysis 4
clusters <- read_csv(file.path(DATA_ROOT, "interim/analysis4_cluster_assignments.csv"),
                     show_col_types = FALSE)

# Read penetration gap
penetration <- read_csv(file.path(DATA_ROOT, "interim/analysis1_penetration_gap.csv"),
                        show_col_types = FALSE)

# Read equity rank
eq <- DATA$equity %>%
  rename(ses_rank = ses_composite_rank_1_highest_need) %>%
  mutate(ses_rank = as.numeric(ses_rank))

# =========================================================
# Build composite axes
# =========================================================

# X: Pfizer Rx footprint per capita (sum all Pfizer oral products / capita)
rm <- DATA$region_master %>%
  select(region, population) %>%
  mutate(population = as.numeric(population))

pfizer_footprint <- DATA$rx_long %>%
  filter(year == 2024) %>%
  left_join(rm, by = "region") %>%
  mutate(rate_100k = patients / population * 1e5) %>%
  group_by(region) %>%
  summarise(total_pfizer_rate_100k = sum(rate_100k, na.rm = TRUE), .groups = "drop")

# Y: strategic leverage opportunity
# Built from:
#   - How many Pfizer products are strongly under-indexing in this region (≤-20%)
#   - Health equity need (lower rank = higher need = higher leverage)
#   - Cornerstone stakeholder bonus

cornerstone_regions <- tibble(
  region = c("Jönköping","Västerbotten","Norrbotten","Uppsala"),
  cornerstone = TRUE
)

leverage <- penetration %>%
  group_by(region) %>%
  summarise(n_under = sum(gap_pct <= -20, na.rm = TRUE),
            n_over = sum(gap_pct >= 20, na.rm = TRUE),
            .groups = "drop") %>%
  left_join(eq %>% select(region, ses_rank), by = "region") %>%
  left_join(cornerstone_regions, by = "region") %>%
  mutate(cornerstone = ifelse(is.na(cornerstone), FALSE, cornerstone),
         # Leverage score: more under-indexing products (opportunity to unlock) +
         # worse equity rank (higher need) + cornerstone status
         leverage_score = n_under * 2 + (22 - ses_rank) + ifelse(cornerstone, 8, 0))

matrix_df <- pfizer_footprint %>%
  left_join(leverage, by = "region") %>%
  left_join(rm, by = "region") %>%
  left_join(clusters %>% select(region, cluster_label), by = "region") %>%
  with_svr()

write_csv(matrix_df, file.path(DATA_ROOT, "interim/analysis8_priority_matrix.csv"))

# Split at medians for quadrant labels
x_med <- median(matrix_df$total_pfizer_rate_100k)
y_med <- median(matrix_df$leverage_score)

# Quadrant labels
matrix_df <- matrix_df %>%
  mutate(quadrant = case_when(
    total_pfizer_rate_100k >= x_med & leverage_score >= y_med ~ "Flagship — strong footprint, high leverage",
    total_pfizer_rate_100k <  x_med & leverage_score >= y_med ~ "Opportunity — low footprint, high leverage",
    total_pfizer_rate_100k >= x_med & leverage_score <  y_med ~ "Maintain — strong footprint, low leverage",
    TRUE ~ "Efficient — low footprint, low leverage"
  ))

# =========================================================
# Figure 8.1 — Priority matrix (2×2 quadrant)
# =========================================================
cluster_colors <- c(
  "A. Northern — Skellefteå ATTR-CM cluster" = PF_PALETTE$red,
  "B. Metropolitan — high-volume, research-intensive" = PF_PALETTE$navy,
  "C. High-burden rural" = PF_PALETTE$orange,
  "D. Affluent mid-size" = PF_PALETTE$green,
  "E. Mid-range standard" = PF_PALETTE$grey
)

p1 <- ggplot(matrix_df, aes(x = total_pfizer_rate_100k, y = leverage_score)) +
  # Quadrant backgrounds
  annotate("rect", xmin = -Inf, xmax = x_med, ymin = y_med, ymax = Inf,
           fill = "#FFF5F0", alpha = 0.5) +
  annotate("rect", xmin = x_med, xmax = Inf, ymin = y_med, ymax = Inf,
           fill = "#F0F5FF", alpha = 0.5) +
  annotate("rect", xmin = -Inf, xmax = x_med, ymin = -Inf, ymax = y_med,
           fill = "#FAFAFA", alpha = 0.5) +
  annotate("rect", xmin = x_med, xmax = Inf, ymin = -Inf, ymax = y_med,
           fill = "#F5F5F0", alpha = 0.5) +
  # Median lines
  geom_vline(xintercept = x_med, linetype = "dashed",
             color = PF_PALETTE$grey, linewidth = 0.4) +
  geom_hline(yintercept = y_med, linetype = "dashed",
             color = PF_PALETTE$grey, linewidth = 0.4) +
  # Points
  geom_point(aes(size = population, fill = cluster_label, color = cluster_label),
             shape = 21, alpha = 0.75, stroke = 0.8) +
  geom_text_repel(aes(label = region), size = 3.3, color = PF_PALETTE$grey,
                  max.overlaps = 25, force = 1.5, min.segment.length = 0.3,
                  box.padding = 0.3) +
  # Quadrant labels (in corners)
  annotate("text", x = min(matrix_df$total_pfizer_rate_100k),
           y = max(matrix_df$leverage_score),
           label = "OPPORTUNITY\nlow footprint, high leverage",
           hjust = 0, vjust = 1, size = 3, fontface = "bold",
           color = PF_PALETTE$red) +
  annotate("text", x = max(matrix_df$total_pfizer_rate_100k),
           y = max(matrix_df$leverage_score),
           label = "FLAGSHIP\nstrong footprint, high leverage",
           hjust = 1, vjust = 1, size = 3, fontface = "bold",
           color = PF_PALETTE$navy) +
  annotate("text", x = min(matrix_df$total_pfizer_rate_100k),
           y = min(matrix_df$leverage_score),
           label = "EFFICIENT\nlow footprint, low leverage",
           hjust = 0, vjust = 0, size = 3, fontface = "bold",
           color = PF_PALETTE$grey) +
  annotate("text", x = max(matrix_df$total_pfizer_rate_100k),
           y = min(matrix_df$leverage_score),
           label = "MAINTAIN\nstrong footprint, low leverage",
           hjust = 1, vjust = 0, size = 3, fontface = "bold",
           color = PF_PALETTE$green) +

  scale_size_continuous(range = c(3, 14), name = "Population",
                        labels = scales::comma,
                        guide = guide_legend(override.aes = list(fill = PF_PALETTE$grey))) +
  scale_color_manual(values = cluster_colors, name = "Regional cluster",
                     guide = guide_legend(override.aes = list(size = 4, alpha = 1))) +
  scale_fill_manual(values = cluster_colors, guide = "none") +
  labs(
    title = "Pfizer Sweden — regional priority matrix",
    subtitle = "X: current Pfizer oral-Rx footprint per 100k (2024). Y: strategic leverage (under-use × equity need × cornerstone status). Size: population.",
    x = "Pfizer oral-Rx footprint (sum of rates per 100k, 2024)",
    y = "Strategic leverage score (higher = greater latent opportunity)",
    caption = paste0("Source: Socialstyrelsen Prescribed Drug Register 2024 + SES composite + cornerstone analysis. ",
                     "Cornerstone regions (Jönköping, Uppsala, Västerbotten, Norrbotten) receive +8 leverage bonus.")
  ) +
  theme_pfizer() +
  theme(legend.position = "top",
        legend.box = "vertical",
        legend.spacing.y = unit(0.2, "cm"),
        legend.text = element_text(size = rel(0.78)))

save_fig(p1, "08_priority_matrix", width = 13, height = 9)

# =========================================================
# Summary table: regions ranked by leverage
# =========================================================
summary_tbl <- matrix_df %>%
  arrange(desc(leverage_score)) %>%
  select(region, quadrant, leverage_score, total_pfizer_rate_100k,
         n_under, ses_rank, cornerstone)

cat("\nRegions ranked by strategic leverage:\n")
print(summary_tbl, n = 25)

cat("\nAnalysis 8 (priority matrix) complete.\n")
