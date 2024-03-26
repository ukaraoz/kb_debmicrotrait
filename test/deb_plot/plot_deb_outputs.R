#!/usr/bin/env Rscript

# 
suppressPackageStartupMessages(library(argparser))
suppressMessages(library(dplyr))
suppressMessages(library(readr))
suppressMessages(library(ggplot2))
suppressMessages(library(ggpubr))
#suppressMessages(library(here))
#source(here::here("microtrait_kbaseutils.R"))
# create parser object

parser <- arg_parser(description = "Simple script that generates plots for DEB inputs and simulations.", 
                     name = "plot_deb_outputs.R",
                     hide.opts = TRUE)
parser <- add_argument(parser, "data_folder", type = "character", help = "input directory with the files")
parser <- add_argument(parser, "figures_folder", type = "character", help = "input directory with the files")
parser <- add_argument(parser, "--verbose", flag = T, short = "v", help = "be verbose")
args <- parse_args(parser)


read_data = function(data_folder, type) {
    if(type == "thermodynamic") {
        file = file.path(data_folder, "substrate_thermodynamic_traits.csv")
        data <- tryCatch(
            {
                data = readr::read_delim(file, delim = ",") 
                data
            },
            error = function(e) {
                print(e, " doesn't exist.") 
                return(FALSE)
            }
        )
    }
   if(type == "kinetic") {
        file = file.path(data_folder, "substrate_kinetic_traits.csv")
        data <- tryCatch(
            {
                data = readr::read_delim(file, delim = ",") 
                data
            },
            error = function(e) {
                print(e, " doesn't exist.") 
                return(FALSE)
            }
        )
   }
    if(type == "phenotype") {
        file = file.path(data_folder, "phenotypic_traits.csv")
        data <- tryCatch(
            {
                data = readr::read_delim(file, delim = ",") 
                data
            },
            error = function(e) {
                print(e, " doesn't exist.") 
                return(FALSE)
            }
        )
    }
    if(type == "mixed") {
        file = file.path(data_folder, "mixed_medium.csv")
        data <- tryCatch(
            {
                data = readr::read_delim(file, delim = ",") 
                data
            },
            error = function(e) {
                print(e, " doesn't exist.") 
                return(FALSE)
            }
        )
    }
    data
}

plot = function(data_folder, out_folder, type) {
    if(type == "thermodynamic") {
        data = read_data(data_folder, type)
        p = data %>%
            ggplot2::ggplot(aes(x = reorder(ontology, -delGcox, FUN = median), y = delGcox, fill=ontology)) +
            geom_boxplot(alpha=0.3) +
            geom_jitter(position=position_jitter(0.2)) +
            scale_x_discrete(guide = guide_axis(angle = 30)) +
            scale_fill_brewer(palette="BuPu") +
            theme(legend.position="none", axis.text.x = element_text(size = 12), axis.text.y = element_text(size = 12), axis.title.y = element_text(size = 12)) +
            xlab("") +
            scale_y_continuous(name = c(expression("Available Gibbs free energy dG" [cox]* ""* "(kJ/mol)")))
        
        pdf_outfile = file.path(out_folder, paste0(type, ".pdf"))
        suppressMessages(ggsave(p, device = "pdf", width = 8, height = 8, file = pdf_outfile))
        png_outfile = file.path(out_folder, paste0(type, ".png"))
        suppressMessages(ggsave(p, device = "png", width = 8, height = 8, file = png_outfile))
    }
    if(type == "kinetic") {
        data = read_data(data_folder, type)
        p = data %>%
            ggplot2::ggplot(aes(x = reorder(ontology, -Vmax, FUN = median), y = Vmax, fill=ontology)) +
            geom_jitter(position=position_jitter(0.15), size=0.01) +
            geom_boxplot(alpha=0.3, outlier.shape = NA) +
            scale_y_continuous(trans='log10', name = c(expression("Maximum specific uptake rate V" [max]* ""* "(mM)"))) +
            scale_x_discrete(guide = guide_axis(angle = 30)) +
            scale_fill_brewer(palette="BuPu") +
            theme(legend.position="none", axis.text.x = element_text(size = 12), axis.text.y = element_text(size = 12), axis.title.y = element_text(size = 12)) +
            xlab("")
        
            pdf_outfile = file.path(out_folder, paste0(type, "_Vmax.pdf"))
            suppressMessages(ggsave(p, device = "pdf", width = 8, height = 8, file = pdf_outfile))
            png_outfile = file.path(out_folder, paste0(type, "_Vmax.png"))
            suppressMessages(ggsave(p, device = "png", width = 8, height = 8, file = png_outfile))
            
            p = data %>%
                ggplot2::ggplot(aes(x = reorder(ontology, -KD, FUN = median), y = KD, fill=ontology)) +
                geom_jitter(position=position_jitter(0.15), size=0.01) +
                geom_boxplot(alpha=0.3, outlier.shape = NA) +
                scale_y_continuous(trans='log10', name = c(expression("Half saturation constant K" [0]* ""* "(mM)"))) +
                scale_x_discrete(guide = guide_axis(angle = 30)) +
                scale_fill_brewer(palette="BuPu") +
                theme(legend.position="none", axis.text.x = element_text(size = 12), axis.text.y = element_text(size = 12), axis.title.y = element_text(size = 12)) +
                xlab("")
            
            pdf_outfile = file.path(out_folder, paste0(type, "_KD.pdf"))
            suppressMessages(ggsave(p, device = "pdf", width = 8, height = 8, file = pdf_outfile))
            png_outfile = file.path(out_folder, paste0(type, "_KD.png"))
            suppressMessages(ggsave(p, device = "png", width = 8, height = 8, file = png_outfile))
    }
    if(type == "phenotype") {
        data = read_data(data_folder, type)
        p <- ggplot(data, aes(x = CUE)) +
            geom_histogram(alpha=0.3, bins=39) + 
            xlab("Carbon use efficiency (-)") +
            ylab("Frequency")
        
        pdf_outfile = file.path(out_folder, paste0(type, "_CUE.pdf"))
        suppressMessages(ggsave(p, device = "pdf", width = 8, height = 8, file = pdf_outfile))
        png_outfile = file.path(out_folder, paste0(type, "_CUE.png"))
        suppressMessages(ggsave(p, device = "png", width = 8, height = 8, file = png_outfile))
        
        p <- ggplot(data, aes(x = rgrowth)) +
            geom_histogram(alpha=0.3, bins=39) + 
            scale_x_continuous(trans="log10") +
            xlab("Growth rate (1/h)") +
            ylab("Frequency")
        
        pdf_outfile = file.path(out_folder, paste0(type, "_rgrowth.pdf"))
        suppressMessages(ggsave(p, device = "pdf", width = 8, height = 8, file = pdf_outfile))
        png_outfile = file.path(out_folder, paste0(type, "_rgrowth.png"))
        suppressMessages(ggsave(p, device = "png", width = 8, height = 8, file = png_outfile))
    }
    if(type == "mixed") {
        data = read_data(data_folder, type)
        
        p = data %>%
            ggplot2::ggplot(aes(x = reorder(ontology, -percent_uptake, FUN = median), y = percent_uptake)) +
            geom_boxplot() +
            geom_jitter(position=position_jitter(0.2), size=0.4) +
            scale_x_discrete(guide = guide_axis(angle = 30)) +
            theme(legend.position="none", axis.text.x = element_text(size = 12), axis.text.y = element_text(size = 12), axis.title.y = element_text(size = 12)) +
            xlab("") +
            ylab(("Uptake of substrate from the medium (%)"))
        
        pdf_outfile = file.path(out_folder, paste0(type, "_uptake.pdf"))
        suppressMessages(ggsave(p, device = "pdf", width = 8, height = 8, file = pdf_outfile))
        png_outfile = file.path(out_folder, paste0(type, "_uptake.png"))
        suppressMessages(ggsave(p, device = "png", width = 8, height = 8, file = png_outfile))
        
        p <- ggplot(data, aes(x = levins_index)) +
            geom_density() + 
            xlab("Levins index (-)") +
            ylab("Frequency")
        
        pdf_outfile = file.path(out_folder, paste0(type, "_levins.pdf"))
        suppressMessages(ggsave(p, device = "pdf", width = 8, height = 8, file = pdf_outfile))
        png_outfile = file.path(out_folder, paste0(type, "_levins.png"))
        suppressMessages(ggsave(p, device = "png", width = 8, height = 8, file = png_outfile))
    }
}

plot(data_folder, figures_folder, type = "thermodynamic")
plot(data_folder, figures_folder, type = "kinetic")
plot(data_folder, figures_folder, type = "phenotype")
plot(data_folder, figures_folder, type = "mixed")


