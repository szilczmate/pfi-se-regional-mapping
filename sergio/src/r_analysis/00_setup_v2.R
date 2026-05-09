# Author: Sergio Flores - Viti Science - VS-2026-PFI-001
# 00_setup_v2.R — Publication-grade theme with proper typography.
#
# Loads IBM Plex Sans via showtext (no install needed), defines a refined Pfizer
# palette with desaturation for non-focal elements, and provides callout helpers.

suppressPackageStartupMessages({
  library(tidyverse)
  library(ggplot2)
  library(scales)
  library(ggrepel)
  library(patchwork)
  library(readxl)
  library(janitor)
  library(viridis)
  library(showtext)
  library(sysfonts)
  library(colorspace)
  library(ggtext)
})

# ==== Typography: IBM Plex Sans via Google Fonts ====
# Fallback to Calibri if Plex fetch fails (offline case)
font_loaded <- tryCatch({
  font_add_google("IBM Plex Sans", "plex")
  font_add_google("IBM Plex Sans Condensed", "plex_cond")
  font_add_google("IBM Plex Mono", "plex_mono")
  showtext_auto()
  showtext_opts(dpi = 320)
  TRUE
}, error = function(e) {
  message("Font load failed, falling back to Calibri: ", e$message)
  FALSE
})

BASE_FONT <- if (font_loaded) "plex" else "Calibri"
MONO_FONT <- if (font_loaded) "plex_mono" else "Consolas"

# ==== Pfizer palette (refined) ====
PF_PALETTE <- list(
  # Narrative-highlight (use sparingly)
  blue_primary = "#0093D0",
  navy         = "#003F7F",
  midnight     = "#00265E",
  red          = "#E4002B",
  gold         = "#FECC00",
  green        = "#2A9D8F",

  # Supporting tones (desaturated for non-focal)
  blue_soft    = "#6FB5DC",
  blue_pale    = "#CFE5F2",
  blue_wash    = "#E8F2F8",

  # Neutrals (for most non-narrative elements)
  charcoal     = "#1F2937",
  slate        = "#374151",
  grey         = "#6B7280",
  grey_light   = "#9CA3AF",
  grey_mist    = "#E5E7EB",
  off_white    = "#F9FAFB",
  white        = "#FFFFFF",

  # Text hierarchy
  text_primary   = "#1F2937",
  text_secondary = "#4B5563",
  text_muted     = "#6B7280"
)

# Backward-compatible aliases for existing scripts
PF_PALETTE$blue       <- PF_PALETTE$blue_primary
PF_PALETTE$light_blue <- PF_PALETTE$blue_pale
PF_PALETTE$orange     <- "#F4A261"
PF_PALETTE$purple     <- "#8B5CF6"
PF_PALETTE$off_white  <- "#F9FAFB"

# Sequential (for heatmaps, maps) — 7 steps, navy-anchored
PF_SEQ_BLUE <- c("#F8FAFC", "#E0ECF7", "#B6D4EA", "#7AAFD7", "#3C87BE",
                 "#155A9C", "#00265E")

# Diverging (for gap/change data)
PF_DIV <- c("#E4002B", "#EA5067", "#F5A2B0", "#F8F8F8",
            "#AFD5EA", "#4D96CC", "#003F7F")

# Categorical (for ≤6 categories)
PF_CATEGORICAL <- c(
  PF_PALETTE$navy,
  PF_PALETTE$red,
  PF_PALETTE$green,
  PF_PALETTE$gold,
  "#8B5CF6",   # purple
  PF_PALETTE$grey
)

# Healthcare-region colors (6 sjukvårdsregioner)
SVR_COLORS <- c(
  "Norra"             = PF_PALETTE$slate,
  "Mellansverige"     = PF_PALETTE$gold,
  "Stockholm-Gotland" = PF_PALETTE$blue_primary,
  "Sydöstra"          = PF_PALETTE$green,
  "Västra"            = "#8B5CF6",
  "Södra"             = PF_PALETTE$red
)

# ==== Refined publication theme ====
theme_pfizer <- function(base_size = 11, base_family = BASE_FONT) {
  theme_minimal(base_size = base_size, base_family = base_family) %+replace%
    theme(
      # Title hierarchy
      plot.title = element_text(
        face = "bold", size = rel(1.32), hjust = 0,
        color = PF_PALETTE$charcoal,
        margin = margin(b = 3, t = 2),
        family = base_family),
      plot.subtitle = element_text(
        size = rel(0.93), hjust = 0,
        color = PF_PALETTE$text_secondary,
        margin = margin(b = 14),
        lineheight = 1.25,
        family = base_family),
      plot.caption = element_text(
        size = rel(0.82), hjust = 0,        # bumped from 0.72 (chart audit 2026-04-25)
        color = PF_PALETTE$text_muted,
        margin = margin(t = 10),
        lineheight = 1.2,
        family = base_family),
      plot.caption.position = "plot",
      plot.title.position = "plot",

      # Axes — minimal, informative
      axis.title = element_text(size = rel(0.88), color = PF_PALETTE$text_secondary,
                                face = "plain", family = base_family),
      axis.title.x = element_text(margin = margin(t = 8)),
      axis.title.y = element_text(margin = margin(r = 8), angle = 90),
      axis.text = element_text(size = rel(0.82), color = PF_PALETTE$text_secondary,
                               family = base_family),
      axis.line.x = element_line(color = PF_PALETTE$grey_mist, linewidth = 0.3),
      axis.line.y = element_blank(),
      axis.ticks.x = element_line(color = PF_PALETTE$grey_mist, linewidth = 0.3),
      axis.ticks.y = element_blank(),
      axis.ticks.length = unit(0.15, "cm"),

      # Panel — very light gridlines, white background
      panel.grid.major.y = element_line(color = "#F3F4F6", linewidth = 0.3),
      panel.grid.major.x = element_blank(),
      panel.grid.minor = element_blank(),
      panel.background = element_rect(fill = "white", color = NA),
      plot.background = element_rect(fill = "white", color = NA),

      # Legend — top-left horizontal by default
      legend.title = element_text(size = rel(0.82), face = "bold",
                                  color = PF_PALETTE$text_primary,
                                  family = base_family),
      legend.text = element_text(size = rel(0.78), color = PF_PALETTE$text_secondary,
                                 family = base_family),
      legend.position = "top",
      legend.justification = "left",
      legend.background = element_blank(),
      legend.key = element_blank(),
      legend.margin = margin(b = 6),
      legend.box.spacing = unit(0.1, "cm"),

      # Facet strips
      strip.text = element_text(face = "bold", size = rel(0.88),
                                color = PF_PALETTE$navy,
                                family = base_family,
                                margin = margin(t = 4, b = 4)),
      strip.background = element_blank(),

      # Margins
      plot.margin = margin(t = 18, r = 22, b = 14, l = 18)
    )
}

# Map/choropleth theme (stripped-down version)
theme_pfizer_map <- function(base_family = BASE_FONT) {
  theme_void(base_family = base_family) %+replace%
    theme(
      plot.title = element_text(face = "bold", size = rel(1.5),
                                color = PF_PALETTE$charcoal, hjust = 0,
                                margin = margin(b = 3), family = base_family),
      plot.subtitle = element_text(size = rel(1.0), color = PF_PALETTE$text_secondary,
                                   hjust = 0, margin = margin(b = 14),
                                   lineheight = 1.25, family = base_family),
      plot.caption = element_text(size = rel(0.82), color = PF_PALETTE$text_muted,  # bumped from 0.72 (chart audit 2026-04-25)
                                  hjust = 0, margin = margin(t = 8),
                                  family = base_family),
      plot.title.position = "plot",
      plot.caption.position = "plot",
      legend.title = element_text(size = rel(0.82), face = "bold",
                                  color = PF_PALETTE$text_primary, family = base_family),
      legend.text = element_text(size = rel(0.78), color = PF_PALETTE$text_secondary,
                                 family = base_family),
      legend.position = "bottom",
      legend.justification = "left",
      plot.margin = margin(t = 14, r = 20, b = 14, l = 18),
      plot.background = element_rect(fill = "white", color = NA)
    )
}

# ==== Save helpers — publication quality PNG + SVG ====
FIG_DIR <- "C:/Users/sergi/OneDrive/Desktop/Viti Science/pfi-se-regional-mapping-main/working/data/master/figures_R"
dir.create(FIG_DIR, recursive = TRUE, showWarnings = FALSE)

save_fig <- function(plot, name, width = 10, height = 6, dpi = 320) {
  png_path <- file.path(FIG_DIR, paste0(name, ".png"))
  svg_path <- file.path(FIG_DIR, paste0(name, ".svg"))
  ggsave(png_path, plot = plot, width = width, height = height,
         dpi = dpi, bg = "white", device = "png")
  tryCatch(
    ggsave(svg_path, plot = plot, width = width, height = height, bg = "white",
           device = "svg"),
    error = function(e) message("  SVG save skipped: ", e$message)
  )
  message(sprintf("  Saved %s (%.1f × %.1f in)", name, width, height))
  invisible(png_path)
}

# ==== Region canonical + sjukvårdsregion ====
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

# ==== Data loader ====
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
  suppressWarnings({
    out <- list()
    rm <- read_excel(WORKBOOK, sheet = "Region master") %>% clean_names()
    rm$region <- normalise_region(rm$region)
    out$region_master <- rm %>% filter(region %in% REGION_ORDER)

    rx_raw <- read_excel(WORKBOOK, sheet = "Läkemedelsregistret Rx") %>% clean_names()
    out$rx_raw <- rx_raw

    rx24 <- read_excel(WORKBOOK, sheet = "Rx 2024 snapshot") %>% clean_names()
    rx24$region <- normalise_region(rx24$region)
    out$rx_2024 <- rx24 %>% filter(region %in% REGION_ORDER)

    eq <- read_excel(WORKBOOK, sheet = "Health equity overlay") %>% clean_names()
    eq$region <- normalise_region(eq$region)
    out$equity <- eq %>% filter(region %in% REGION_ORDER)

    mort <- read_excel(WORKBOOK, sheet = "Mortality indicators") %>% clean_names()
    mort$region <- normalise_region(mort$region)
    out$mortality <- mort %>% filter(region %in% REGION_ORDER)

    vacc <- read_excel(WORKBOOK, sheet = "Vaccine market share") %>% clean_names()
    vacc$region <- normalise_region(vacc$region)
    out$vaccines <- vacc %>% filter(region %in% REGION_ORDER)

    vacc_detail <- tryCatch(
      read_excel(WORKBOOK, sheet = "Vaccine sales detail") %>% clean_names(),
      error = function(e) NULL
    )
    if (!is.null(vacc_detail)) {
      vacc_detail$region <- normalise_region(vacc_detail$region)
      out$vaccines_detail <- vacc_detail %>% filter(region %in% REGION_ORDER)
    }

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
  })
  out
}

with_svr <- function(df) df %>% left_join(REGION_TO_SVR, by = "region")

# ==== Pfizer product catalogue ====
PFIZER_PRODUCTS <- tibble(
  atc = c("L01EF01","N07XX08","L01XK04","L01ED04","L01EH03","N02CD06","J05AE30"),
  brand = c("Ibrance","Vyndaqel","Talzenna","Lorbrena/Lorviqua","Tukysa","Vydura","Paxlovid"),
  indication_short = c("HR+/HER2- BC","ATTR-CM","BRCA-mut HER2- BC","ALK+ NSCLC",
                       "HER2+ BC + brain mets","Acute migraine","COVID-19"),
  therapy_area = c("Oncology","Rare disease","Oncology","Oncology","Oncology","Neurology","Infection"),
  # Approximate annual cost per patient (SEK, public/TLV benchmarks)
  annual_cost_sek = c(220000, 800000, 320000, 350000, 580000, 2500, 5400)
)

# ==== Annotation helper for callouts ====
annotate_callout <- function(plot, x, y, label, color = PF_PALETTE$navy,
                              size = 3.2, hjust = 0, vjust = 0.5,
                              box_padding = 0.4) {
  plot +
    annotate("label", x = x, y = y, label = label,
             color = color, fill = "white",
             family = BASE_FONT, fontface = "bold",
             size = size, hjust = hjust, vjust = vjust,
             label.padding = unit(box_padding, "lines"),
             label.size = 0.3, label.r = unit(0.15, "lines"))
}

# ==== Helper: dynamic text color for heatmap cells ====
# Returns "white" for dark fills, dark grey for light fills. Use as
#   geom_text(aes(color = stage(after_scale = ...))) — or compute outside the aes.
# Simple version: caller passes a numeric value + fill scale max; returns hex.
text_color_on_fill <- function(value, vmax, vmin = 0,
                                threshold = 0.55,
                                light_color = "#1F2937",   # dark charcoal for light fills
                                dark_color  = "white") {
  # Normalise value to 0..1 along the scale
  if (is.na(value)) return(light_color)
  norm <- (value - vmin) / pmax(vmax - vmin, 1e-9)
  ifelse(norm >= threshold, dark_color, light_color)
}

# Categorical version: caller passes a factor level + a named vector of fills,
# returns hex per element. Good for ordinal heatmaps with pre-set fills.
text_color_for_category <- function(category_value, fill_lookup) {
  # Compute luminance from fill_lookup hex; choose contrasting text color.
  luminance <- function(hex) {
    rgb_vals <- col2rgb(hex)[, 1] / 255
    # Relative luminance per WCAG (sRGB linearised approximation)
    sum(c(0.2126, 0.7152, 0.0722) * rgb_vals)
  }
  ifelse(luminance(fill_lookup[as.character(category_value)]) > 0.6, "#1F2937", "white")
}

message("[00_setup_v2] IBM Plex Sans loaded, theme_pfizer() v2 ready.")
message("[00_setup_v2] Helpers: theme_pfizer_map(), annotate_callout(), text_color_on_fill(), text_color_for_category().")
