# Author: Sergio Flores - Viti Science - VS-2026-PFI-001
# 02_ibrance_forecast.R — Time-series decomposition + short-horizon forecast for Ibrance

source("00_setup_v2.R")
suppressPackageStartupMessages({
  library(forecast)
  library(broom)
  library(gt)
  library(ggrepel)
})

DATA <- load_all_data()

ib <- DATA$rx_long %>%
  filter(atc == "L01EF01") %>%
  arrange(region, year)

# CAGR per region
cagr <- ib %>%
  group_by(region) %>%
  summarise(patients_2021 = patients[year == 2021],
            patients_2024 = patients[year == 2024],
            change_abs = patients_2024 - patients_2021,
            change_pct = (patients_2024 - patients_2021) / patients_2021 * 100,
            cagr = if (patients_2021 > 0) (patients_2024/patients_2021)^(1/3) - 1 else NA_real_,
            .groups = "drop") %>%
  mutate(cagr_pct = cagr * 100) %>%
  with_svr() %>%
  arrange(desc(patients_2021))

write_csv(cagr, file.path(DATA_ROOT, "interim/analysis2_ibrance_cagr.csv"))

# =========================================================
# Figure 2.1 — CAGR ranked
# =========================================================
cagr_plot <- cagr %>%
  filter(patients_2021 >= 10) %>%
  mutate(region = fct_reorder(region, change_pct),
         highlight = case_when(
           region %in% c("Stockholm","Västra Götaland") ~ "Kisqali substitution",
           change_pct >= 10 ~ "Growth",
           change_pct <= -20 & !region %in% c("Stockholm","Västra Götaland") ~ "Decline",
           TRUE ~ "Stable"
         ))

hl_colors <- c("Kisqali substitution" = PF_PALETTE$red,
               "Decline" = PF_PALETTE$orange,
               "Stable" = PF_PALETTE$grey,
               "Growth" = PF_PALETTE$green)

p1 <- ggplot(cagr_plot, aes(x = change_pct, y = region, fill = highlight)) +
  geom_col(width = 0.7) +
  geom_text(aes(label = sprintf("%+d%% (n %d→%d)", round(change_pct),
                                 patients_2021, patients_2024),
                hjust = ifelse(change_pct > 0, -0.05, 1.05)),
            size = 3, color = PF_PALETTE$grey) +
  geom_vline(xintercept = 0, color = PF_PALETTE$grey, linewidth = 0.3) +
  scale_fill_manual(values = hl_colors, name = NULL) +
  scale_x_continuous(labels = function(x) paste0(x, "%"),
                     expand = expansion(mult = c(0.25, 0.25))) +
  labs(
    title = "Ibrance patient-count change 2021 → 2024 by region",
    subtitle = "Stockholm −33% and VGR −36% drive the cost-driven switch to Kisqali. Halland and Skåne hold Ibrance positioning.",
    x = "Change 2021 → 2024 (%)", y = NULL,
    caption = "Source: Socialstyrelsen Prescribed Drug Register (ATC L01EF01) 2021–2024. Only regions with ≥10 patients in 2021."
  ) +
  theme_pfizer()

save_fig(p1, "02_ibrance_cagr_ranked", width = 11, height = 8)

# =========================================================
# Figure 2.2 — Small multiples with forecast
# =========================================================
forecast_data <- list()
for (r in cagr$region) {
  region_ts <- ib %>% filter(region == r) %>% arrange(year)
  if (region_ts$patients[region_ts$year == 2021] < 40 || nrow(region_ts) < 4) next

  ts_obj <- ts(region_ts$patients, start = 2021, frequency = 1)
  fit <- tryCatch(ets(ts_obj, model = "ANN", damped = NULL), error = function(e) NULL)
  if (is.null(fit)) next

  fc <- forecast(fit, h = 2, level = 80)
  forecast_data[[r]] <- tibble(
    region = r,
    year = c(2021:2024, 2025, 2026),
    patients = c(region_ts$patients, as.numeric(fc$mean)),
    lower80 = c(rep(NA_real_, 4), as.numeric(fc$lower)),
    upper80 = c(rep(NA_real_, 4), as.numeric(fc$upper)),
    is_forecast = c(rep(FALSE, 4), TRUE, TRUE)
  )
}

if (length(forecast_data) > 0) {
  fcast_df <- bind_rows(forecast_data) %>%
    mutate(region = factor(region, levels = cagr$region[cagr$patients_2021 >= 40])) %>%
    mutate(is_kisqali = region %in% c("Stockholm","Västra Götaland"))

  p2 <- ggplot(fcast_df, aes(x = year, y = patients)) +
    geom_ribbon(aes(ymin = pmax(lower80, 0), ymax = upper80),
                fill = PF_PALETTE$light_blue, alpha = 0.5, data = ~filter(.x, is_forecast)) +
    geom_line(data = ~filter(.x, !is_forecast),
              aes(color = is_kisqali), linewidth = 1.1) +
    geom_line(data = ~filter(.x, is_forecast | year == 2024),
              aes(color = is_kisqali), linewidth = 1.1, linetype = "dashed") +
    geom_point(data = ~filter(.x, !is_forecast),
               aes(color = is_kisqali), size = 2) +
    scale_color_manual(values = c("FALSE" = PF_PALETTE$blue, "TRUE" = PF_PALETTE$red),
                       labels = c("FALSE" = "Other regions", "TRUE" = "Kisqali substitution"),
                       name = NULL) +
    scale_x_continuous(breaks = c(2021, 2023, 2025)) +
    scale_y_continuous(limits = c(0, NA)) +
    facet_wrap(~ region, ncol = 4, scales = "free_y") +
    labs(
      title = "Ibrance forecast 2025 and 2026 — ETS with 80% prediction interval",
      subtitle = "History 2021–2024 solid line; forecast dashed. Shaded band = 80% prediction interval.",
      x = NULL, y = "Number of patients",
      caption = paste0("Source: Socialstyrelsen Prescribed Drug Register (ATC L01EF01). ",
                       "ETS(ANN) model fitted per region for regions with ≥40 patients in 2021. ",
                       "Forecast 2025–2026, 80% interval.")
    ) +
    theme_pfizer() +
    theme(legend.position = "top",
          panel.spacing = unit(1.3, "lines"))

  save_fig(p2, "02_ibrance_forecast_small_multiples", width = 13, height = 8)

  fcast_summary <- fcast_df %>%
    filter(is_forecast) %>%
    select(region, year, patients, lower80, upper80) %>%
    pivot_wider(names_from = year,
                values_from = c(patients, lower80, upper80),
                names_sep = "_") %>%
    left_join(cagr %>% select(region, patients_2024), by = "region") %>%
    mutate(pct_change_2024_2026 = (patients_2026 - patients_2024) / patients_2024 * 100) %>%
    arrange(desc(patients_2024))

  write_csv(fcast_summary, file.path(DATA_ROOT, "interim/analysis2_ibrance_forecast.csv"))
}

# =========================================================
# Figure 2.3 — National trend
# =========================================================
national_trend <- ib %>%
  group_by(year) %>%
  summarise(total = sum(patients, na.rm = TRUE), .groups = "drop")

p3 <- ggplot(national_trend, aes(x = year, y = total)) +
  geom_area(fill = PF_PALETTE$light_blue, alpha = 0.7) +
  geom_line(color = PF_PALETTE$navy, linewidth = 1.4) +
  geom_point(color = PF_PALETTE$navy, size = 3.5) +
  geom_text(aes(label = total), vjust = -1.3, size = 4,
            color = PF_PALETTE$navy, fontface = "bold") +
  scale_x_continuous(breaks = 2021:2024) +
  scale_y_continuous(limits = c(0, 1200), labels = scales::comma) +
  labs(
    title = "Ibrance national total — 27% decline 2021–2024",
    subtitle = "Stockholm (−33%) and Västra Götaland (−36%) account for essentially the entire national decline.",
    x = NULL, y = "Number of patients",
    caption = "Source: Socialstyrelsen Prescribed Drug Register (ATC L01EF01 palbociclib). All 21 regions summed."
  ) +
  theme_pfizer() +
  theme(panel.grid.major.x = element_blank())

save_fig(p3, "02_ibrance_national_trend", width = 10, height = 5.5)

cat("\nAnalysis 2 complete.\n")
