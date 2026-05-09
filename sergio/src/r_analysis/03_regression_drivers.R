# Author: Sergio Flores - Viti Science - VS-2026-PFI-001
# 03_regression_drivers.R — What drives regional Pfizer uptake?

source("00_setup_v2.R")
suppressPackageStartupMessages({
  library(broom)
  library(gt)
  library(ggrepel)
})

DATA <- load_all_data()

rm <- DATA$region_master %>%
  mutate(population = as.numeric(population),
         pop_65 = as.numeric(pop_65),
         pct_65 = pop_65 / population * 100) %>%
  select(region, population, pct_65,
         specialist_lakare = specialist_lakare_number,
         hc_cost_per_inv = hc_cost_inv,
         median_wait_spec = median_wait_spec_days,
         utrikes_fodda_pct = utrikes_fodda_percent_2024,
         eftergymn_pct = eftergymnasial_utbildning_25_64_percent_2024,
         premature_mort = fortida_dodsfall_25_64_100k_aldersstand)

rx_2024 <- DATA$rx_long %>%
  filter(year == 2024) %>%
  left_join(rm %>% select(region, population), by = "region") %>%
  mutate(rate_100k = patients / population * 1e5)

products_to_fit <- c("L01EF01","N07XX08","L01EH03","N02CD06","J05AE30")

all_coefs <- list()
fit_list <- list()

for (atc_code in products_to_fit) {
  brand_name <- PFIZER_PRODUCTS$brand[PFIZER_PRODUCTS$atc == atc_code]
  cat(sprintf("\nFitting %s (%s)\n", brand_name, atc_code))

  model_df <- rx_2024 %>%
    filter(atc == atc_code) %>%
    left_join(rm %>% select(-population), by = "region") %>%
    mutate(log_rate = log(rate_100k + 1))

  predictors <- c("pct_65","utrikes_fodda_pct","eftergymn_pct",
                  "hc_cost_per_inv","median_wait_spec","premature_mort","specialist_lakare")
  model_df_std <- model_df
  for (p in predictors) {
    if (!is.null(model_df_std[[p]])) {
      model_df_std[[p]] <- scale(model_df[[p]])[,1]
    }
  }

  form <- switch(atc_code,
    "L01EF01" = log_rate ~ pct_65 + utrikes_fodda_pct + eftergymn_pct +
                hc_cost_per_inv + median_wait_spec + specialist_lakare,
    "N07XX08" = log_rate ~ pct_65 + utrikes_fodda_pct + eftergymn_pct +
                hc_cost_per_inv + specialist_lakare,
    "L01EH03" = log_rate ~ pct_65 + eftergymn_pct + hc_cost_per_inv +
                median_wait_spec + specialist_lakare,
    "N02CD06" = log_rate ~ pct_65 + utrikes_fodda_pct + eftergymn_pct +
                hc_cost_per_inv + specialist_lakare,
    "J05AE30" = log_rate ~ pct_65 + utrikes_fodda_pct + eftergymn_pct +
                hc_cost_per_inv + median_wait_spec + specialist_lakare
  )

  fit <- lm(form, data = model_df_std)
  fit_list[[atc_code]] <- fit

  coefs <- broom::tidy(fit, conf.int = TRUE) %>%
    filter(term != "(Intercept)") %>%
    mutate(brand = brand_name, atc = atc_code)
  all_coefs[[atc_code]] <- coefs
}

coef_df <- bind_rows(all_coefs) %>%
  mutate(sig = p.value < 0.05,
         brand = factor(brand, levels = PFIZER_PRODUCTS$brand[match(products_to_fit, PFIZER_PRODUCTS$atc)])) %>%
  mutate(term_label = recode(term,
    "pct_65"             = "% 65+ population",
    "utrikes_fodda_pct"  = "% foreign-born",
    "eftergymn_pct"      = "% post-secondary educ. 25-64",
    "hc_cost_per_inv"    = "HC cost per capita",
    "median_wait_spec"   = "Median specialist wait (days)",
    "premature_mort"     = "Premature mortality 25-64",
    "specialist_lakare"  = "Specialist physicians (#)"
  ))

write_csv(coef_df, file.path(DATA_ROOT, "interim/analysis3_regression_coefs.csv"))

r2_tbl <- tibble(
  atc = names(fit_list),
  brand = PFIZER_PRODUCTS$brand[match(names(fit_list), PFIZER_PRODUCTS$atc)],
  r2 = map_dbl(fit_list, ~ summary(.x)$r.squared),
  adj_r2 = map_dbl(fit_list, ~ summary(.x)$adj.r.squared),
  n = map_dbl(fit_list, ~ nobs(.x))
)
write_csv(r2_tbl, file.path(DATA_ROOT, "interim/analysis3_r2_summary.csv"))

# =========================================================
# Figure 3.1 — Coefficient forest plot
# =========================================================
p1 <- ggplot(coef_df, aes(x = estimate, y = term_label, color = sig)) +
  geom_errorbar(aes(xmin = conf.low, xmax = conf.high),
                 width = 0.25, linewidth = 0.7, orientation = "y") +
  geom_point(size = 3.5) +
  geom_vline(xintercept = 0, linetype = "dashed", color = PF_PALETTE$grey) +
  facet_wrap(~ brand, ncol = 3, scales = "free_x") +
  scale_color_manual(values = c("TRUE" = PF_PALETTE$red, "FALSE" = PF_PALETTE$grey),
                     labels = c("TRUE" = "p < 0.05", "FALSE" = "p ≥ 0.05"),
                     name = NULL) +
  labs(
    title = "What drives regional Pfizer uptake? Regression coefficients by product",
    subtitle = "Standardised predictors (z-score). Point = estimate, bars = 95% CI. Right of zero = positive association with uptake.",
    x = "Standardised coefficient (log-scale outcome)", y = NULL,
    caption = paste0("Outcome: log(patients per 100k + 1). Model: lm per product × 21 regions. ",
                     "R² ranges from ", sprintf("%.0f", min(r2_tbl$r2)*100), "% to ",
                     sprintf("%.0f", max(r2_tbl$r2)*100), "% by product.")
  ) +
  theme_pfizer() +
  theme(strip.text = element_text(size = rel(1.0)),
        panel.spacing.x = unit(1.0, "lines"))

save_fig(p1, "03_regression_coefficients", width = 13, height = 7)

# =========================================================
# Figure 3.2 — Vyndaqel genetic cluster beyond demographics
# =========================================================
vyndaqel_model_df <- rx_2024 %>%
  filter(atc == "N07XX08") %>%
  left_join(rm %>% select(-population), by = "region")

p2 <- ggplot(vyndaqel_model_df, aes(x = pct_65, y = rate_100k)) +
  geom_smooth(method = "lm", se = TRUE, fill = PF_PALETTE$light_blue,
              color = PF_PALETTE$navy, alpha = 0.3, linewidth = 1) +
  geom_point(aes(size = population, color = region %in% c("Norrbotten","Västerbotten"))) +
  geom_text_repel(aes(label = region), size = 3.2, color = PF_PALETTE$grey,
                  max.overlaps = 21, force = 1.5) +
  scale_color_manual(values = c("FALSE" = PF_PALETTE$blue, "TRUE" = PF_PALETTE$red),
                     labels = c("FALSE" = "Other regions", "TRUE" = "Skellefteå cluster"),
                     name = NULL) +
  scale_size_continuous(range = c(2, 10), name = "Population",
                        labels = scales::comma) +
  labs(
    title = "Vyndaqel — genetic cluster exceeds demographic explanation",
    subtitle = "While % 65+ explains some variation, Norrbotten and Västerbotten sit far above the regression line. The Skellefteå founder-variant cluster is visible in the raw data.",
    x = "% of regional population aged 65+",
    y = "Vyndaqel patients per 100 000 inhabitants (2024)",
    caption = "Source: Socialstyrelsen Prescribed Drug Register (N07XX08) + SCB BE0101. OLS line with 95% CI."
  ) +
  theme_pfizer() +
  theme(legend.position = "top",
        legend.box = "vertical")

save_fig(p2, "03_vyndaqel_beyond_demographics", width = 11, height = 7.5)

# =========================================================
# Simple gt regression table
# =========================================================
reg_table <- coef_df %>%
  select(brand, term_label, estimate, std.error, p.value, conf.low, conf.high) %>%
  mutate(estimate_fmt = sprintf("%+.2f (%.2f, %.2f)%s",
                                estimate, conf.low, conf.high,
                                ifelse(p.value < 0.05, " *", "")))

reg_wide <- reg_table %>%
  select(brand, term_label, estimate_fmt) %>%
  pivot_wider(names_from = brand, values_from = estimate_fmt)

gt_tbl <- reg_wide %>%
  gt(rowname_col = "term_label") %>%
  tab_header(
    title = md("**Regression of regional Pfizer uptake on demographics + access**"),
    subtitle = md("Standardised coefficients (95% CI). * = p < 0.05. Outcome = log(patients per 100k + 1)")
  ) %>%
  tab_stubhead(label = "Predictor") %>%
  tab_source_note(md("Source: Socialstyrelsen Prescribed Drug Register 2024 + SCB/Kolada regional covariates. N = 21 regions per model.")) %>%
  tab_options(
    table.font.names = "Calibri",
    heading.title.font.size = 13,
    column_labels.background.color = PF_PALETTE$navy,
    column_labels.font.weight = "bold",
    table.font.size = 9.5
  ) %>%
  tab_style(style = cell_text(color = "white"),
            locations = cells_column_labels())

gtsave(gt_tbl, file.path(FIG_DIR, "03_regression_table.html"))

cat("\nR² summary:\n")
print(r2_tbl)
cat("\nAnalysis 3 complete.\n")
