# Author: Sergio Flores - Viti Science - VS-2026-PFI-001
# 04_cluster_regions.R — Cluster analysis: group the 21 regions by Pfizer profile
#
# Question: instead of my ad-hoc ★/★★/★★★ tiers, are there statistically-defined
# clusters of regions that share similar Pfizer-relevant characteristics?
#
# Method: k-means + hierarchical clustering on normalised features:
#   - Demography (pct_65, population_log)
#   - SES (foreign-born %, education %)
#   - Disease (cancer rate, premature mortality)
#   - Access (wait time, specialist density)
#   - Pfizer uptake (Ibrance, Vyndaqel, Vydura per 100k)
# Produces: dendrogram, cluster map, cluster-profile table.

source("00_setup_v2.R")
suppressPackageStartupMessages({
  library(cluster)
  library(factoextra)
  library(ggrepel)
})

DATA <- load_all_data()

rm <- DATA$region_master %>%
  mutate(population = as.numeric(population),
         pop_65 = as.numeric(pop_65),
         pct_65 = pop_65 / population * 100,
         log_pop = log10(population))

rx_2024 <- DATA$rx_long %>%
  filter(year == 2024) %>%
  left_join(rm %>% select(region, population), by = "region") %>%
  mutate(rate_100k = patients / population * 1e5)

rx_wide <- rx_2024 %>%
  select(region, atc, rate_100k) %>%
  pivot_wider(names_from = atc, values_from = rate_100k,
              names_prefix = "rx_") %>%
  replace(is.na(.), 0)

features <- rm %>%
  select(region, pct_65, log_pop,
         utrikes_fodda_pct = utrikes_fodda_percent_2024,
         eftergymn_pct = eftergymnasial_utbildning_25_64_percent_2024,
         premature_mort = fortida_dodsfall_25_64_100k_aldersstand,
         breast_ca_rate = breast_ca_rate_100k,
         median_wait_spec = median_wait_spec_days) %>%
  left_join(rx_wide, by = "region")

features_matrix <- features %>% select(-region)
rownames_fm <- features$region
X <- scale(as.matrix(features_matrix))
rownames(X) <- rownames_fm

# =========================================================
# Hierarchical clustering (Ward's method)
# =========================================================
d <- dist(X, method = "euclidean")
hc <- hclust(d, method = "ward.D2")

# Optimal number of clusters (silhouette method)
sil_scores <- sapply(2:8, function(k) {
  grp <- cutree(hc, k = k)
  sil <- silhouette(grp, d)
  mean(sil[, "sil_width"])
})
optimal_k <- which.max(sil_scores) + 1
cat(sprintf("Optimal k (silhouette): %d (score = %.3f)\n", optimal_k, max(sil_scores)))

clusters <- cutree(hc, k = optimal_k)
features$cluster <- factor(clusters)

# Name clusters based on their distinguishing profile
cluster_profiles <- features %>%
  group_by(cluster) %>%
  summarise(
    n_regions = n(),
    regions = paste(region, collapse = ", "),
    mean_pct_65 = mean(pct_65),
    mean_log_pop = mean(log_pop),
    mean_utrikes_fodda = mean(utrikes_fodda_pct),
    mean_eftergymn = mean(eftergymn_pct),
    mean_premature_mort = mean(premature_mort),
    mean_vyndaqel = mean(rx_N07XX08),
    mean_ibrance = mean(rx_L01EF01),
    .groups = "drop"
  )

# Assign cluster labels based on the profile
cluster_profiles <- cluster_profiles %>%
  mutate(cluster_label = case_when(
    mean_vyndaqel > 15 ~ "A. Northern — Skellefteå ATTR-CM cluster",
    mean_log_pop >= 6.2 ~ "B. Metropolitan — high-volume, research-intensive",
    mean_premature_mort >= 190 & mean_eftergymn <= 42 ~ "C. High-burden rural",
    mean_eftergymn >= 45 ~ "D. Affluent mid-size",
    TRUE ~ "E. Mid-range standard"
  ))

features <- features %>%
  left_join(cluster_profiles %>% select(cluster, cluster_label), by = "cluster")

write_csv(features, file.path(DATA_ROOT, "interim/analysis4_cluster_assignments.csv"))
write_csv(cluster_profiles, file.path(DATA_ROOT, "interim/analysis4_cluster_profiles.csv"))

# =========================================================
# Figure 4.1 — Dendrogram (publication quality)
# =========================================================
dendro_colors <- c(PF_PALETTE$red, PF_PALETTE$blue, PF_PALETTE$navy,
                   PF_PALETTE$green, PF_PALETTE$orange, PF_PALETTE$purple)[seq_len(optimal_k)]

p1 <- fviz_dend(hc, k = optimal_k,
                k_colors = dendro_colors,
                rect = TRUE, rect_fill = TRUE,
                rect_border = dendro_colors,
                lwd = 0.9,
                label_cols = "grey30",
                cex = 0.82,
                main = sprintf("Hierarchical clustering of Sweden's 21 regions (k = %d)", optimal_k),
                sub = "Ward's method on 14 normalised Pfizer-relevant features. Height = linkage distance.",
                horiz = FALSE) +
  labs(caption = "Features: demography, SES, disease burden, access, Pfizer Rx rates per 100k. Source: master_workbook_v13 + Läkemedelsregistret 2024.") +
  theme_pfizer() +
  theme(axis.text.x = element_text(size = 9, face = "bold", color = PF_PALETTE$navy),
        panel.grid = element_blank(),
        axis.line.y = element_line(color = PF_PALETTE$grey),
        axis.ticks.y = element_line(color = PF_PALETTE$grey))

save_fig(p1, "04_cluster_dendrogram", width = 13, height = 7)

# =========================================================
# Figure 4.2 — 2D PCA projection colored by cluster
# =========================================================
pca <- prcomp(X, center = FALSE, scale. = FALSE)
pca_df <- as_tibble(pca$x[, 1:2]) %>%
  rename(PC1 = 1, PC2 = 2) %>%
  mutate(region = rownames_fm,
         cluster = features$cluster,
         cluster_label = features$cluster_label)

var_exp <- round(100 * pca$sdev^2 / sum(pca$sdev^2))

p2 <- ggplot(pca_df, aes(x = PC1, y = PC2, color = cluster_label)) +
  stat_ellipse(aes(group = cluster_label, fill = cluster_label),
               geom = "polygon", alpha = 0.12, linewidth = 0.4, type = "norm") +
  geom_point(size = 4.5) +
  geom_text_repel(aes(label = region), size = 3.5,
                  color = PF_PALETTE$grey,
                  min.segment.length = 0.2,
                  max.overlaps = 21, force = 2) +
  scale_color_manual(values = setNames(dendro_colors, unique(features$cluster_label)),
                     name = "Cluster") +
  scale_fill_manual(values = setNames(dendro_colors, unique(features$cluster_label)),
                    guide = "none") +
  labs(
    title = "Region clusters — 2D principal-component projection",
    subtitle = sprintf("PC1 (%d%% variance) + PC2 (%d%% variance). Ellipses = cluster boundaries (normal). Colors match dendrogram.", var_exp[1], var_exp[2]),
    x = sprintf("Principal component 1 (%d%%)", var_exp[1]),
    y = sprintf("Principal component 2 (%d%%)", var_exp[2]),
    caption = "14-feature normalised region profile. Ward's hierarchical clustering with optimal k from silhouette."
  ) +
  theme_pfizer() +
  theme(legend.position = "top",
        legend.text = element_text(size = rel(0.85)),
        legend.key.size = unit(0.5, "cm"))

save_fig(p2, "04_cluster_pca_projection", width = 11, height = 8)

# =========================================================
# Cluster profile table (gt)
# =========================================================
library(gt)

profile_display <- cluster_profiles %>%
  select(cluster_label, n_regions, regions,
         mean_pct_65, mean_eftergymn, mean_premature_mort,
         mean_vyndaqel, mean_ibrance) %>%
  arrange(cluster_label) %>%
  mutate(across(starts_with("mean_"), ~ round(.x, 1)))

gt_tbl <- profile_display %>%
  gt() %>%
  tab_header(
    title = md("**Region clusters — profile summary**"),
    subtitle = "Mean values of key Pfizer-relevant characteristics per cluster"
  ) %>%
  cols_label(
    cluster_label = "Cluster",
    n_regions = "N",
    regions = "Regions",
    mean_pct_65 = "65+ %",
    mean_eftergymn = "Post-sec %",
    mean_premature_mort = "Prem mort /100k",
    mean_vyndaqel = "Vyndaqel /100k",
    mean_ibrance = "Ibrance /100k"
  ) %>%
  tab_source_note(md("Mean values across cluster members. Source: master_workbook_v13 + Läkemedelsregistret 2024.")) %>%
  tab_options(
    table.font.names = "Calibri",
    heading.title.font.size = 13,
    column_labels.background.color = PF_PALETTE$navy,
    column_labels.font.weight = "bold",
    table.font.size = 10
  ) %>%
  tab_style(style = cell_text(color = "white"),
            locations = cells_column_labels())

gtsave(gt_tbl, file.path(FIG_DIR, "04_cluster_profile_table.html"))

cat("\nCluster assignments:\n")
print(features %>% select(region, cluster, cluster_label))
cat("\nAnalysis 4 complete.\n")
