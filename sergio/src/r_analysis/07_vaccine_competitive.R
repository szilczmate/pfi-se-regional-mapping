# Author: Sergio Flores - Viti Science - VS-2026-PFI-001
# 07_vaccine_competitive.R — Pfizer's competitive vaccine share per region + ATC class
#
# Source data: Pfizer IQVIA extract delivered 2026-04-02, integrated into
# master_workbook_v13 "Vaccine market share" sheet.
# Classes:
#   J07BX05 — RSV (Abrysvo vs Arexvy/GSK)
#   J07AL02 — Pneumococcal conjugate (Prevenar 20 vs Vaxneuvance/Capvaxive/MSD)
#   J07BA01 — TBE (FSME-IMMUN vs Encepur/Bavarian Nordic)

source("00_setup_v2.R")
suppressPackageStartupMessages({
  library(readxl)
  library(ggrepel)
})

DATA <- load_all_data()

vacc <- read_excel(WORKBOOK, sheet = "Vaccine market share") %>%
  clean_names() %>%
  mutate(region = normalise_region(region)) %>%
  filter(region %in% REGION_ORDER) %>%
  rename(
    rsv_total = rsv_total,
    abrysvo = pfizer_abrysvo,
    rsv_share = share_percent_5,
    pneu_total = pneu_total,
    prevenar = pfizer_prevenar,
    pneu_share = share_percent_8,
    tbe_total = tbe_total,
    fsme = pfizer_fsme,
    tbe_share = share_percent_11
  )

# Long format for plotting
vacc_long <- vacc %>%
  select(region,
         RSV = rsv_share,
         Pneumococcal = pneu_share,
         TBE = tbe_share) %>%
  pivot_longer(-region, names_to = "class", values_to = "share_pct") %>%
  with_svr()

# National weighted share
national <- vacc %>%
  summarise(
    RSV = sum(abrysvo) / sum(rsv_total) * 100,
    Pneumococcal = sum(prevenar) / sum(pneu_total) * 100,
    TBE = sum(fsme) / sum(tbe_total) * 100
  ) %>%
  pivot_longer(everything(), names_to = "class", values_to = "national_share_pct")

cat("Pfizer national weighted shares:\n")
print(national)

# =========================================================
# Figure 7.1 — Pfizer vaccine share by class × region
# =========================================================
heatmap_data <- vacc_long %>%
  mutate(class = factor(class, levels = c("Pneumococcal","RSV","TBE")),
         region = factor(region, levels = rev(REGION_ORDER)))

p1 <- ggplot(heatmap_data, aes(x = class, y = region, fill = share_pct)) +
  geom_tile(color = "white", linewidth = 0.4) +
  geom_text(aes(label = sprintf("%.0f%%", share_pct)),
            color = ifelse(heatmap_data$share_pct > 55, "white", "#333333"),
            size = 3.2, fontface = "bold") +
  scale_fill_gradientn(
    colors = c("#FAFAFA", "#E8F1F8", PF_PALETTE$light_blue, PF_PALETTE$blue, PF_PALETTE$navy),
    limits = c(0, 100), name = "Pfizer share (%)",
    guide = guide_colorbar(barwidth = 13, barheight = 0.5,
                           title.position = "top", title.hjust = 0)
  ) +
  scale_x_discrete(position = "top") +
  labs(
    title = "Pfizer's competitive share in the Swedish vaccine market",
    subtitle = "Rolling 36-month IQVIA data per ATC class × region. Pneumococcal = Prevenar 20 vs Merck Vaxneuvance/Capvaxive; RSV = Abrysvo vs GSK Arexvy; TBE = FSME-IMMUN vs Bavarian Nordic Encepur.",
    x = NULL, y = NULL,
    caption = "Source: Pfizer IQVIA extract delivered 2026-04-02. All vaccines in each ATC class, sum of sell-in value."
  ) +
  theme_pfizer() +
  theme(
    panel.grid = element_blank(),
    axis.ticks = element_blank(),
    axis.line = element_blank(),
    axis.text.x.top = element_text(face = "bold"),
    legend.position = "bottom"
  )

save_fig(p1, "07_vaccine_share_heatmap", width = 9, height = 9)

# =========================================================
# Figure 7.2 — Top vs bottom regions per class
# =========================================================
p2_data <- vacc_long %>%
  group_by(class) %>%
  mutate(rank = rank(-share_pct, ties.method = "min")) %>%
  ungroup() %>%
  filter(rank <= 5 | rank >= 17) %>%
  mutate(tier = ifelse(rank <= 5, "Top 5", "Bottom 5"),
         class = factor(class, levels = c("Pneumococcal","RSV","TBE")))

p2 <- ggplot(p2_data, aes(x = share_pct, y = reorder(region, share_pct), fill = tier)) +
  geom_col(width = 0.7) +
  geom_text(aes(label = sprintf("%.0f%%", share_pct), hjust = -0.1),
            size = 3, color = PF_PALETTE$grey) +
  facet_wrap(~ class, scales = "free_y") +
  scale_fill_manual(values = c("Top 5" = PF_PALETTE$navy, "Bottom 5" = PF_PALETTE$red),
                    name = NULL) +
  scale_x_continuous(labels = function(x) paste0(x, "%"),
                     limits = c(0, 115),
                     expand = c(0, 0)) +
  labs(
    title = "Top 5 and bottom 5 regions per Pfizer vaccine class",
    subtitle = "Largest regional spread is in TBE (broad geographic variation) and Pneumococcal (procurement-driven differences).",
    x = "Pfizer regional share (%)", y = NULL,
    caption = "Source: Pfizer IQVIA extract 2026-04-02. Rolling 36-month cumulative sell-in."
  ) +
  theme_pfizer() +
  theme(strip.text = element_text(size = rel(1.0)))

save_fig(p2, "07_vaccine_top_bottom", width = 13, height = 7)

cat("\nAnalysis 7 complete.\n")
