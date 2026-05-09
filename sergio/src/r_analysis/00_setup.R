# Author: Sergio Flores - Viti Science - VS-2026-PFI-001
# 00_setup.R — DEPRECATED 2026-04-25
# ============================================================================
# This file is the v1 setup. Every active R script in this folder now sources
# 00_setup_v2.R instead. Kept on disk only for historical reference; do NOT
# source from new analyses.
#
# v2 differences:
#   - IBM Plex Sans loaded via showtext (vs base R fonts only)
#   - Expanded palette with text-hierarchy colors
#   - theme_pfizer_map() helper for choropleth maps
#   - text_color_on_fill() / text_color_for_category() helpers for heatmap labels
#   - annotate_callout() helper
#
# Migration: replace `source("00_setup.R")` with `source("00_setup_v2.R")`.
# ============================================================================
#
# Original v1 documentation below — for reference only:
# 00_setup.R — Shared theme, palette, data-load for Pfizer Regional Mapping
# Run once per session with: source("00_setup.R")
#
# Produces globals:
#   PF_PALETTE (named Pfizer brand colors)
#   theme_pfizer() ggplot2 theme function
#   DATA (list of loaded datasets from the master workbook + CSVs)
#   REGION_ORDER (21-region canonical order)
#   save_fig() helper to save PNG + SVG at publication quality

suppressPackageStartupMessages({
  library(tidyverse)
  library(ggplot2)
  library(scales)
  library(ggrepel)
  library(patchwork)
  library(readxl)
  library(janitor)
  library(viridis)
})

# =============================================================
# Pfizer brand palette (for academic/publication use)
# =============================================================
PF_PALETTE <- list(
  blue       = "#0093D0",   # primary
  navy       = "#003F7F",   # deep brand
  midnight   = "#00265E",   # darkest
  red        = "#E4002B",   # accent / negative trend
  gold       = "#FECC00",   # Swedish flag accent
  light_blue = "#B8DFE8",
  grey       = "#53565A",
  off_white  = "#F5F7FA",
  green      = "#2A9D8F",   # positive trend
  orange     = "#F4A261",   # mid/warning
  purple     = "#6A4C93"    # sixth category
)

# Ordinal palette (for ranked/ordinal visuals)
PF_ORDINAL <- c(PF_PALETTE$midnight, PF_PALETTE$navy, PF_PALETTE$blue,
                PF_PALETTE$light_blue, PF_PALETTE$grey)

# Healthcare-region colors (6 sjukvårdsregioner)
SVR_COLORS <- c(
  "Norra"             = PF_PALETTE$grey,
  "Mellansverige"     = PF_PALETTE$gold,
  "Stockholm-Gotland" = PF_PALETTE$blue,
  "Sydöstra"          = PF_PALETTE$green,
  "Västra"            = PF_PALETTE$purple,
  "Södra"             = PF_PALETTE$red
)

# =============================================================
# Publication theme (manuscript-quality)
# =============================================================
theme_pfizer <- function(base_size = 11, base_family = "") {
  theme_minimal(base_size = base_size, base_family = base_family) %+replace%
    theme(
      # Text hierarchy
      plot.title = element_text(face = "bold", size = rel(1.25),
                                hjust = 0, color = PF_PALETTE$midnight,
                                margin = margin(b = 4, t = 4)),
      plot.subtitle = element_text(size = rel(0.95), color = PF_PALETTE$grey,
                                   hjust = 0, margin = margin(b = 12)),
      plot.caption = element_text(size = rel(0.75), color = PF_PALETTE$grey,
                                  hjust = 0, margin = margin(t = 8),
                                  face = "italic"),
      plot.caption.position = "plot",
      plot.title.position = "plot",

      # Axes
      axis.title = element_text(size = rel(0.9), color = PF_PALETTE$navy,
                                face = "bold"),
      axis.title.x = element_text(margin = margin(t = 6)),
      axis.title.y = element_text(margin = margin(r = 6), angle = 90),
      axis.text = element_text(size = rel(0.85), color = PF_PALETTE$grey),
      axis.line = element_line(color = PF_PALETTE$grey, linewidth = 0.3),
      axis.ticks = element_line(color = PF_PALETTE$grey, linewidth = 0.3),

      # Panel
      panel.grid.major.y = element_line(color = "#E8ECEF", linewidth = 0.3),
      panel.grid.major.x = element_blank(),
      panel.grid.minor = element_blank(),
      panel.background = element_rect(fill = "white", color = NA),
      plot.background = element_rect(fill = "white", color = NA),

      # Legend
      legend.title = element_text(size = rel(0.85), face = "bold",
                                  color = PF_PALETTE$navy),
      legend.text = element_text(size = rel(0.8), color = PF_PALETTE$grey),
      legend.position = "top",
      legend.justification = "left",
      legend.background = element_blank(),
      legend.key = element_blank(),
      legend.margin = margin(b = 4),

      # Strip (facet labels)
      strip.text = element_text(face = "bold", size = rel(0.9),
                                color = PF_PALETTE$midnight),
      strip.background = element_rect(fill = PF_PALETTE$off_white,
                                       color = NA),

      # Spacing
      plot.margin = margin(t = 16, r = 20, b = 12, l = 16)
    )
}

# =============================================================
# Save helpers — publication quality PNG + SVG
# =============================================================
FIG_DIR <- "C:/Users/sergi/OneDrive/Desktop/Viti Science/pfi-se-regional-mapping-main/working/data/master/figures_R"
dir.create(FIG_DIR, recursive = TRUE, showWarnings = FALSE)

save_fig <- function(plot, name, width = 10, height = 6, dpi = 320) {
  png_path <- file.path(FIG_DIR, paste0(name, ".png"))
  svg_path <- file.path(FIG_DIR, paste0(name, ".svg"))
  ggsave(png_path, plot = plot, width = width, height = height,
         dpi = dpi, bg = "white")
  ggsave(svg_path, plot = plot, width = width, height = height, bg = "white")
  message(sprintf("  Saved %s (%.1f × %.1f in, %d dpi)", name, width, height, dpi))
  invisible(list(png = png_path, svg = svg_path))
}

# =============================================================
# Region canonical names + sjukvårdsregion mapping
# =============================================================
REGION_ORDER <- c(
  "Stockholm", "Uppsala", "Sörmland", "Östergötland", "Jönköping",
  "Kronoberg", "Kalmar", "Gotland", "Blekinge", "Skåne", "Halland",
  "Västra Götaland", "Värmland", "Örebro", "Västmanland", "Dalarna",
  "Gävleborg", "Västernorrland", "Jämtland Härjedalen", "Västerbotten",
  "Norrbotten"
)

REGION_TO_SVR <- tibble(
  region = REGION_ORDER,
  healthcare_region = c(
    "Stockholm-Gotland", "Mellansverige", "Mellansverige", "Sydöstra", "Sydöstra",
    "Södra", "Sydöstra", "Stockholm-Gotland", "Södra", "Södra", "Västra",
    "Västra", "Mellansverige", "Mellansverige", "Mellansverige", "Mellansverige",
    "Mellansverige", "Norra", "Norra", "Norra", "Norra"
  )
)

# Region code (SCB/Kolada 2-digit lan)
REGION_CODES <- tibble(
  region = REGION_ORDER,
  kolada_code = c(
    "0001","0003","0004","0005","0006","0007","0008","0009","0010","0012","0013",
    "0014","0017","0018","0019","0020","0021","0022","0023","0024","0025"
  ),
  lan_code = c(
    "01","03","04","05","06","07","08","09","10","12","13","14","17","18","19","20",
    "21","22","23","24","25"
  )
)

# =============================================================
# Data loader — pulls from the master workbook v13 + interim CSVs
# =============================================================
DATA_ROOT <- "C:/Users/sergi/OneDrive/Desktop/Viti Science/pfi-se-regional-mapping-main/working/data"
WORKBOOK <- file.path(DATA_ROOT, "master/master_workbook_v13.xlsx")

normalise_region <- function(s) {
  s <- trimws(s)
  s <- gsub("^Region ", "", s)
  s <- gsub(" län$", "", s)
  s <- gsub("Västra Götalandsregionen", "Västra Götaland", s)
  s <- gsub("Jönköpings", "Jönköping", s)
  s <- gsub("Örebro län", "Örebro", s)
  s
}

load_all_data <- function() {
  out <- list()

  # Region master — the 21×48 matrix
  rm <- read_excel(WORKBOOK, sheet = "Region master") %>%
    clean_names()
  rm$region <- normalise_region(rm$region)
  out$region_master <- rm %>% filter(region %in% REGION_ORDER)

  # Rx data (Läkemedelsregistret)
  rx <- read_excel(WORKBOOK, sheet = "Läkemedelsregistret Rx") %>%
    clean_names()
  out$rx_raw <- rx

  # Rx 2024 snapshot (per-capita)
  rx24 <- read_excel(WORKBOOK, sheet = "Rx 2024 snapshot") %>%
    clean_names()
  rx24$region <- normalise_region(rx24$region)
  out$rx_2024 <- rx24 %>% filter(region %in% REGION_ORDER)

  # Health equity overlay
  eq <- read_excel(WORKBOOK, sheet = "Health equity overlay") %>%
    clean_names()
  eq$region <- normalise_region(eq$region)
  out$equity <- eq %>% filter(region %in% REGION_ORDER)

  # Mortality indicators
  mort <- read_excel(WORKBOOK, sheet = "Mortality indicators") %>%
    clean_names()
  mort$region <- normalise_region(mort$region)
  out$mortality <- mort %>% filter(region %in% REGION_ORDER)

  # Interim CSVs — more granular
  out$rx_long <- read_csv(file.path(DATA_ROOT, "interim/lakemedelsregistret_patients_by_region_2021_2024.csv"),
                          show_col_types = FALSE) %>%
    pivot_longer(cols = -c(region_code, region),
                 names_to = "atc_year", values_to = "patients") %>%
    separate(atc_year, into = c("atc","year"), sep = "_") %>%
    mutate(year = as.integer(year),
           patients = as.integer(patients),
           region = normalise_region(region)) %>%
    filter(region %in% REGION_ORDER, !is.na(patients))

  out$education <- read_csv(file.path(DATA_ROOT, "interim/scb_education_by_region_2024.csv"),
                            show_col_types = FALSE) %>%
    mutate(region = normalise_region(region))
  out$foreign_born <- read_csv(file.path(DATA_ROOT, "interim/scb_inr_utr_fodda_by_region_2024.csv"),
                               show_col_types = FALSE) %>%
    mutate(region = normalise_region(region))
  out$kolada_mortality <- read_csv(file.path(DATA_ROOT, "interim/kolada_mortality_by_region.csv"),
                                   show_col_types = FALSE) %>%
    mutate(region = normalise_region(region))

  out
}

# Attach SVR to any tibble with a region col
with_svr <- function(df) {
  df %>% left_join(REGION_TO_SVR, by = "region")
}

# Pfizer product catalogue (for labeling)
PFIZER_PRODUCTS <- tibble(
  atc = c("L01EF01","N07XX08","L01XK04","L01ED04","L01EH03","N02CD06","J05AE30"),
  brand = c("Ibrance","Vyndaqel","Talzenna","Lorbrena/Lorviqua","Tukysa","Vydura","Paxlovid"),
  indication_short = c("HR+/HER2- BC","ATTR-CM","BRCA-mut HER2- BC","ALK+ NSCLC",
                       "HER2+ BC + brain mets","Acute migraine","COVID-19"),
  therapy_area = c("Oncology","Rare disease","Oncology","Oncology","Oncology","Neurology","Infection")
)

message("[00_setup] Theme, palette, loader ready. Call load_all_data() to load.")
