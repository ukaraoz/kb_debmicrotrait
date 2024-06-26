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
parser <- add_argument(parser, "figure_folder", type = "character", help = "input directory with the files")
parser <- add_argument(parser, "--verbose", flag = T, short = "v", help = "be verbose")
args <- parse_args(parser)


read_data = function(data_folder, type) {
   if(type == "kinetic") {
        file = file.path(data_folder, "substrate_kinetic_traits.csv")
        data <- tryCatch(
            {
                data = readr::read_delim(file, delim = ",") %>%
                    tidyr::pivot_longer(!c(guildid, Ontology), names_to = "type", values_to = "value") %>%
                    # assumes all levels always exist
                    dplyr::mutate(Ontology = factor(Ontology, 
                                                    levels = c("Amino acids", "Organic acids", "Nucleotides", "Sugars", "Auxins", "Fatty acids"),
                                                    ordered = T))  
                data
            },
            error = function(e) {
                print(e, " doesn't exist.") 
                return(FALSE)
            }
        )
    }
    if(type == "thermodynamic") {
        file = file.path(data_folder, "substrate_thermodynamic_traits.csv")
        data <- tryCatch(
            {
                data = readr::read_delim(file, delim = ",") %>%
                    tidyr::pivot_longer(!c(guildid, Ontology), names_to = "type", values_to = "value") %>%
                    # assumes all levels always exist
                    dplyr::mutate(Ontology = factor(Ontology, 
                                                    levels = c("Amino acids", "Organic acids", "Nucleotides", "Sugars", "Auxins", "Fatty acids"),
                                                    ordered = T))  
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

plot = function(data_folder, figure_folder, type) {
    if(type == "kinetic") {
        variables = c("Vmax", "KD")
        labels = c(expression('Maximum specific uptake rate V'[max]), expression('Half saturation constant K'[0]))
        data = read_data(data_folder, type)
        for(i in 1:length(variables)) {
            p = data %>%
                dplyr::filter(type == variables[i]) %>%
                ggpubr::ggboxplot(x = "Ontology", y = "value",
                                  color = "black", fill = "white", size = 0.5, 
                                  #add.params = list(color = "black", size= 1.5),
                                  #add = "jitter", 
                                  ylab = "") + 
                # ggboxplot doesn't work with expression in the labels
                labs(y = labels[i], x = "") + 
                scale_y_continuous(trans='log10') +
                annotation_logticks(sides = "l") +
                scale_y_log10(breaks = scales::trans_breaks("log10", function(x) 10^x),
                              labels = scales::trans_format("log10", math_format(10^.x)))
            p = p + stat_compare_means(label = "p.sign", method = "wilcox.test", 
                                       label.y = 0.1,
                                        method.args = list(alternative = "two.sided"), 
                                        comparisons = comparisons, 
                                        symnum.args = list(cutpoints = c(0, 0.001, 0.01, 0.05, Inf), symbols = c("***", "**", "*", "NS")),
                                        show.legend = F, bracket.size=0.2, tip.length=0.01, vjust=1, step.increase=0.015)
            suppressMessages(ggsave(p, width = 8, height = 8, file = pdf_outfile))


        }

    }
}

classes = c("Amino acids", "Organic acids", "Nucleotides", "Sugars", "Auxins", "Fatty acids")
pairs = t(combn(classes, 2))
comparisons = list()
for(i in 1:nrow(pairs)) { comparisons[[i]] = pairs[i,]}
p = data %>%
    dplyr::filter(type == "Vmax") %>%
    ggpubr::ggboxplot(x = "Ontology", y = "value",
                      color = "black", fill = "white", size = 0.5, 
                      #add.params = list(color = "black", size= 1.5),
                      #add = "jitter", 
                      ylab = "") + 
    # ggboxplot doesn't work with expression in the labels
    labs(y=expression('Maximum specific uptake rate V'[max])) + 
    scale_y_continuous(trans='log10') +
    annotation_logticks(sides = "l") +
    scale_y_log10(breaks = scales::trans_breaks("log10", function(x) 10^x),
                  labels = scales::trans_format("log10", math_format(10^.x)))
 p = p + stat_compare_means(label = "p.sign", method = "wilcox.test", 
                            label.y = 0.1,
                             method.args = list(alternative = "two.sided"), 
                             comparisons = comparisons, 
                             symnum.args = list(cutpoints = c(0, 0.001, 0.01, 0.05, Inf), symbols = c("***", "**", "*", "NS")),
                             show.legend = F, bracket.size=0.2, tip.length=0.01, vjust=1, step.increase=0.015)

