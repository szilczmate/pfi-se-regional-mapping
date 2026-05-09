# Author: Sergio Flores - Viti Science - VS-2026-PFI-001
# 06_sweden_maps.R — Sweden choropleth maps (the hero visualisations)
#
# Produces: maps showing
#   (a) Vyndaqel rate per 100k — the Skellefteå cluster
#   (b) Ibrance decline 2021→2024
#   (c) Health equity composite rank
#
# Audit 2026-04-25: deduplicated theme code (uses theme_pfizer_map() from setup_v2),
#                   fixed white-on-light label readability via text_color_on_fill(),
#                   resized maps to 8×11 (Sweden's tall-narrow geometry),
#                   switched centroids to st_point_on_surface for guaranteed-inside placement,
#                   added directional annotation to Health equity legend.

source("00_setup_v2.R")
suppressPackageStartupMessages({
  library(sf)
  library(ggrepel)
})

DATA <- load_all_data()

# =========================================================
# Sweden region shapefile
# =========================================================
geometry_ok <- FALSE
sweden <- NULL

tryCatch({
  gadm_url <- "https://geodata.ucdavis.edu/gadm/gadm4.1/json/gadm41_SWE_1.json.zip"
  tmp_zip <- tempfile(fileext = ".zip")
  utils::download.file(gadm_url, tmp_zip, mode = "wb", quiet = TRUE)
  tmp_dir <- tempfile()
  dir.create(tmp_dir)
  utils::unzip(tmp_zip, exdir = tmp_dir)
  json_file <- list.files(tmp_dir, pattern = "\\.json$", full.names = TRUE)[1]
  sweden <- sf::st_read(json_file, quiet = TRUE)
  geometry_ok <- TRUE
  message("Downloaded Sweden county boundaries from GADM")
}, error = function(e) {
  message("GADM download failed: ", e$message)
})

if (!geometry_ok) {
  stop("Cannot proceed without geometry. Check internet + GADM.")
}

cat("Sweden sf columns:\n")
print(names(sweden))
cat("\nSample NAME_1 values:\n")
print(unique(sweden$NAME_1)[1:5])

sweden_clean <- sweden %>%
  mutate(canonical = case_when(
    NAME_1 == "Jämtland" ~ "Jämtland Härjedalen",
    NAME_1 == "Södermanland" ~ "Sörmland",
    NAME_1 == "Orebro" ~ "Örebro",
    NAME_1 == "VästraGötaland" ~ "Västra Götaland",
    TRUE ~ NAME_1
  )) %>%
  filter(canonical %in% REGION_ORDER)

cat("\nRegion match after cleaning:\n")
cat(sprintf("  matched: %d / 21\n", sum(sweden_clean$canonical %in% REGION_ORDER)))

# Use point_on_surface for guaranteed-inside label placement (audit fix R4)
label_geom <- function(sf_obj) sf::st_point_on_surface(sf::st_make_valid(sf_obj))

# =========================================================
# Figure 6.1 — Vyndaqel rate per 100k map
# =========================================================
rx_2024 <- DATA$rx_long %>% filter(year == 2024)
vyn <- rx_2024 %>%
  filter(atc == "N07XX08") %>%
  left_join(DATA$region_master %>% select(region, population) %>%
              mutate(population = as.numeric(population)),
            by = "region") %>%
  mutate(rate_100k = patients / population * 1e5)

map_data <- sweden_clean %>%
  left_join(vyn %>% select(canonical = region, rate_100k, patients),
            by = "canonical") %>%
  # text color: dark on low fills (< 8/100k), white on high fills
  mutate(label_text_color = ifelse(is.na(rate_100k) | rate_100k < 8,
                                    PF_PALETTE$charcoal, "white"))

p1 <- ggplot(map_data) +
  geom_sf(aes(fill = rate_100k), color = "white", linewidth = 0.3) +
  geom_sf_text(aes(label = ifelse(is.na(rate_100k), "—", sprintf("%.1f", rate_100k)),
                    color = I(label_text_color)),
               size = 3.0, fontface = "bold",
               family = BASE_FONT,
               fun.geometry = label_geom) +
  scale_fill_gradientn(
    colors = c("#F5F7FA", "#B8DFE8", "#0093D0", "#003F7F", "#E4002B"),
    values = scales::rescale(c(0, 5, 10, 20, 31)),
    name = "Patients / 100k",
    na.value = "#F5F7FA",
    guide = guide_colorbar(barwidth = 14, barheight = 0.5,
                           title.position = "top", title.hjust = 0)
  ) +
  labs(
    title = "Vyndaqel (tafamidis) — regional prescribing rate 2024",
    subtitle = "Hereditary ATTR-CM Skellefteå founder cluster is geographically visible. Norrbotten (31.0/100k) and Västerbotten (23.8/100k) combine for 31% of Sweden's patients in 2.8% of population.",
    caption = "Source: Socialstyrelsen Prescribed Drug Register (ATC N07XX08) 2024 + SCB BE0101 population. Labels = patients per 100 000 inhabitants."
  ) +
  theme_pfizer_map()

save_fig(p1, "06_map_vyndaqel", width = 8, height = 11)

# =========================================================
# Figure 6.2 — Ibrance decline map (2021 → 2024 % change)
# =========================================================
ib <- DATA$rx_long %>%
  filter(atc == "L01EF01") %>%
  group_by(region) %>%
  summarise(
    p2021 = patients[year == 2021],
    p2024 = patients[year == 2024],
    change_pct = (p2024 - p2021) / pmax(p2021, 1) * 100,
    .groups = "drop"
  )

map_ib <- sweden_clean %>%
  left_join(ib %>% select(canonical = region, change_pct, p2024), by = "canonical") %>%
  mutate(label_text_color = ifelse(is.na(change_pct) | abs(change_pct) < 25,
                                    PF_PALETTE$charcoal, "white"))

p2 <- ggplot(map_ib) +
  geom_sf(aes(fill = change_pct), color = "white", linewidth = 0.3) +
  geom_sf_text(aes(label = ifelse(is.na(change_pct), "—",
                                    sprintf("%+d%%", round(change_pct))),
                    color = I(label_text_color)),
               size = 3.0, fontface = "bold",
               family = BASE_FONT,
               fun.geometry = label_geom) +
  scale_fill_gradient2(
    low = PF_PALETTE$red, mid = "#F5F7FA", high = PF_PALETTE$green,
    midpoint = 0, limits = c(-100, 50),
    oob = scales::squish,
    name = "Change 2021 → 2024",
    labels = function(x) sprintf("%+d%%", x),
    na.value = "#F5F7FA",
    guide = guide_colorbar(barwidth = 14, barheight = 0.5,
                           title.position = "top", title.hjust = 0)
  ) +
  labs(
    title = "Ibrance (palbociclib) — regional change 2021 → 2024",
    subtitle = "Cost-driven Kisqali substitution in Stockholm (−33%) and VGR (−36%) is geographically the two largest regional markets. Halland and Skåne hold Ibrance positioning.",
    caption = "Source: Socialstyrelsen Prescribed Drug Register (ATC L01EF01) 2021 and 2024."
  ) +
  theme_pfizer_map()

save_fig(p2, "06_map_ibrance_change", width = 8, height = 11)

# =========================================================
# Figure 6.3 — Health equity composite rank map
# =========================================================
eq <- DATA$equity %>%
  rename(canonical = region,
         ses_rank = ses_composite_rank_1_highest_need) %>%
  mutate(ses_rank = as.numeric(ses_rank))

map_eq <- sweden_clean %>%
  left_join(eq %>% select(canonical, ses_rank), by = "canonical") %>%
  # rank 1-7 are red-ish (high need = dark fill, white text); rank 15-21 are pale (light fill, dark text)
  mutate(label_text_color = ifelse(is.na(ses_rank) | ses_rank > 10,
                                    PF_PALETTE$charcoal, "white"))

p3 <- ggplot(map_eq) +
  geom_sf(aes(fill = ses_rank), color = "white", linewidth = 0.3) +
  geom_sf_text(aes(label = ifelse(is.na(ses_rank), "—", as.integer(ses_rank)),
                    color = I(label_text_color)),
               size = 3.2, fontface = "bold",
               family = BASE_FONT,
               fun.geometry = label_geom) +
  scale_fill_gradient(
    low = PF_PALETTE$red, high = "#F5F7FA",
    name = "Need rank  ←  highest (1) to lowest (21)",
    na.value = "#F5F7FA",
    breaks = c(1, 5, 10, 15, 21),
    guide = guide_colorbar(barwidth = 14, barheight = 0.5,
                           title.position = "top", title.hjust = 0,
                           reverse = FALSE)
  ) +
  labs(
    title = "Health equity composite rank — where unmet need is highest",
    subtitle = "Rank 1 = highest need (Sörmland, then Norrbotten, Gävleborg, Västmanland, Örebro). Composite of foreign-born %, post-secondary education %, premature mortality 25-64, healthcare-amenable mortality.",
    caption = "Source: SCB UF0506 + BE0101 + Kolada N79190, N72461. 2024."
  ) +
  theme_pfizer_map()

save_fig(p3, "06_map_health_equity", width = 8, height = 11)

cat("\nAnalysis 6 (maps) complete.\n")
