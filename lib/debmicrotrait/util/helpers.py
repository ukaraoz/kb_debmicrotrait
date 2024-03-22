import os
import matplotlib.pyplot as pyplot
from matplotlib import gridspec
import seaborn as sns
import pandas as pd
import scikit_posthocs as sp

def html_add_batch_summary(params, api_results, html_output_dir):

    html_file = 'test' + '.html'
    output_html_file_path = os.path.join(html_output_dir, html_file)

    img_dpi = 300
    img_units = "in"
    img_pix_width = 1200
    img_in_width = round(float(img_pix_width) / float(img_dpi), 1)
    img_html_width = img_pix_width // 2

    # Make HTML
    intree_name = 'intreename'

    html_report_lines = []
    html_report_lines.append('<html>')
    html_report_lines.append('<head>')
    html_report_lines.append('<title>KBase Tree: {0}</title>'.format(intree_name))
    html_report_lines.append('<style>')
    html_report_lines.append('.tab {')
    html_report_lines.append('  display: none;')
    html_report_lines.append('}')
    html_report_lines.append('.active {')
    html_report_lines.append('  display: block;')
    html_report_lines.append('}')
    html_report_lines.append('.tab-button {')  # Added class for tab buttons
    html_report_lines.append('  background-color: white;')  # Set background color to white
    html_report_lines.append('  padding: 10px 20px;')  # Adjust padding to increase button size
    html_report_lines.append('  font-size: 16px;')  # Adjust font size
    html_report_lines.append('  border: 1px solid #ccc;')  # Add border for button
    html_report_lines.append('  border-radius: 5px;')  # Add border radius for button
    html_report_lines.append('  cursor: pointer;')
    html_report_lines.append('}')
    html_report_lines.append('</style>')
    html_report_lines.append('</head>')
    html_report_lines.append('<body>')

    # Tab navigation
    html_report_lines.append('<div>')
    html_report_lines.append('<button class="tab-button" onclick="showTab(0)">Substrate Thermodynamic Traits</button>')  # Added class for tab buttons
    html_report_lines.append('<button class="tab-button" onclick="showTab(1)">Substrate Kinetic Traits</button>')  # Added class for tab buttons
    html_report_lines.append('<button class="tab-button" onclick="showTab(2)">Phenotypic Traits</button>')  # Added class for tab buttons
    html_report_lines.append('<button class="tab-button" onclick="showTab(3)">Table</button>') 
    html_report_lines.append('</div>')

    # Tab content
    html_report_lines.append('<div id="tabContent">')
    html_report_lines.append('<div class="tab active">')
    html_report_lines.append('<div><h2>Image 1</h2></div>')  # Header for Image 1
    html_report_lines.append('<img width="{0}" src="{1}">'.format(img_html_width, api_results["png"][0]))
    html_report_lines.append('</div>')
    html_report_lines.append('<div class="tab">')
    html_report_lines.append('<div><h2>Image 2</h2></div>')  # Header for Image 1
    html_report_lines.append('<img width="{0}" src="{1}">'.format(img_html_width, api_results["png"][1]))
    html_report_lines.append('</div>')
    html_report_lines.append('<div class="tab">')
    html_report_lines.append('<div><h2>Background</h2></div>') 
    html_report_lines.append('<div style="width: 100%; height: 100vh; background-color: black;"></div>')
    html_report_lines.append('</div>')
    html_report_lines.append('<div class="tab">')
    html_report_lines.append('<div><h2>Table</h2></div>')  # Header for the table tab

    # Table content
    html_report_lines.append('<table border="1">')  # Basic table with borders
    # Table header row
    html_report_lines.append('<tr>')
    for header in api_results["header"]:
        html_report_lines.append('<th>{}</th>'.format(header))
    html_report_lines.append('</tr>')
    # Data rows
    for row in api_results["data"]:
        html_report_lines.append('<tr>')
        for cell in row:
            html_report_lines.append('<td>{}</td>'.format(cell))
        html_report_lines.append('</tr>')
    html_report_lines.append('</table>')
    html_report_lines.append('</div>')
    html_report_lines.append('</div>')
 

    # JavaScript for tab switching
    html_report_lines.append('<script>')
    html_report_lines.append('function showTab(index) {')
    html_report_lines.append('  var tabs = document.getElementsByClassName("tab");')
    html_report_lines.append('  for (var i = 0; i < tabs.length; i++) {')
    html_report_lines.append('    tabs[i].classList.remove("active");')
    html_report_lines.append('  }')
    html_report_lines.append('  tabs[index].classList.add("active");')
    html_report_lines.append('}')
    html_report_lines.append('</script>')

    html_report_lines.append('</body>')
    html_report_lines.append('</html>')

    html_report_str = "\n".join(html_report_lines)


     # Write HTML to file
    with open(output_html_file_path, 'w') as html_handle:
        html_handle.write(html_report_str)


    return {'path': output_html_file_path,
            'name': os.path.basename(output_html_file_path),
            'description': 'HTML report for batch mode simulations'}

def plot_substrate_thermodynamic_traits(params, data_path, html_output_dir):
        df_thermo = pd.read_csv(data_path)
        #
        img_dpi = 300
        img_units = "in"
        img_pix_width = 1200
        img_in_width = round(float(img_pix_width) / float(img_dpi), 1)
        img_html_width = img_pix_width // 2
        # Get unique ontologies from the dataframe
        unique_ontologies = df_thermo['ontology'].unique()
        num_colors = len(unique_ontologies)
        # Choose a qualitative color palette with the desired number of colors
        palette = sns.color_palette("colorblind", n_colors=num_colors)
        # Set the figure size before creating subplots
        fig = pyplot.figure(figsize=(img_in_width*1.618, img_in_width))

        # Create subplots
        ax = fig.subplots(nrows=1, ncols=1)

        # Plot the seaborn histplot on the specified axis with the chosen color palette
        sns.histplot(data=df_thermo, x="delGcox", hue="ontology", multiple="stack", bins=30,
                    palette=palette,
                    ax=ax)

        ax.set_xlabel(r'Estimated available Gibbs free energy $\Delta G_{\mathrm{cox}}$ (kJ/mol)')

        # Add a legend with labels and set font size
        legend = ax.legend(unique_ontologies, title="Chemical Class", fontsize=10)
        # Set the title font size
        legend.get_title().set_fontsize('10')
   
        png_file = 'substrate_thermodynamic_traits_plot.png'
        output_png_file_path = os.path.join(html_output_dir, png_file)
        fig.savefig(output_png_file_path, dpi=200)

        pyplot.close(fig)

        return {'path': output_png_file_path,
                'name': png_file,
                'description': 'Plots for Substrate Thermodynamic Traits'}


def plot_substrate_kinetic_traits(params, data_path, html_output_dir):
        df_kinetics = pd.read_csv(data_path)
        df_kinetics = df_kinetics[df_kinetics.Vmax > 1e-8]
       #
        img_dpi = 300
        img_units = "in"
        img_pix_width = 1200
        img_in_width = round(float(img_pix_width) / float(img_dpi), 1)
        img_html_width = img_pix_width // 2
        #
        post_hoc_vmax = sp.posthoc_conover(df_kinetics, val_col='Vmax', group_col='Ontology', \
                              p_adjust = 'holm')
        post_hoc_kd = sp.posthoc_conover(df_kinetics, val_col='KD', group_col='Ontology', \
                              p_adjust = 'holm')
        # Get unique ontologies from the dataframe
        unique_ontologies = df_kinetics['Ontology'].unique()
        num_colors = len(unique_ontologies)

        # Choose a qualitative color palette with the desired number of colors
        palette = sns.color_palette("colorblind", n_colors=num_colors)

        # Set the figure size before creating subplots
        fig = pyplot.figure(figsize=(img_in_width*1.618, img_in_width*1.1*2))
        gs  = gridspec.GridSpec(2, 2, width_ratios=[3, 1])

        # Create subplots
        ax0 = pyplot.subplot(gs[0])

        sns.boxplot(x='Ontology', y='Vmax', data=df_kinetics, showfliers=False, width=0.5, ax=ax0)
        ax0.set_yscale("log")
        ax0.set_xticklabels(ax0.get_xticklabels(),rotation=30)
        ax0.set_xlabel("")
        ax0.set_ylabel(r"Maximum specific uptake rate $V_{\mathrm{max}}$ (1/h)")

        ax1 = pyplot.subplot(gs[1])

        heatmap_args = {'cmap': ['1', '#fb6a4a',  '#08306b',  '#4292c6', '#c6dbef'], 
                        'linewidths': 0.25, 
                        'linecolor': '0.5', 
                        'clip_on': False, 
                        'square': True, 
                        'cbar_ax_bbox': [1, 0.42, 0.04, 0.3],
                    }

        #sp.sign_plot(post_hoc_vmax, labels=False)

        #ax1.set_title('Significance plot', fontsize=10)
        #ax1.set_yticklabels(ax0.get_xticklabels(), rotation=0, fontsize=10)
        #ax1.set_xticklabels(ax0.get_xticklabels(), rotation=90, fontsize=10)

        # Create subplots
        ax2 = pyplot.subplot(gs[2])

        sns.boxplot(x='Ontology', y='KD', data=df_kinetics, showfliers=False, width=0.5, ax=ax2)
        ax2.set_yscale("log")
        #ax2.set_xticklabels(ax2.get_xticklabels(),rotation=30)
        #ax2.set_xlabel("")
        #ax2.set_ylabel(r"Half-saturation constant $K_{\mathrm{0}}$ (mM)")

        ax3 = pyplot.subplot(gs[3])

        heatmap_args = {'cmap': ['1', '#fb6a4a',  '#08306b',  '#4292c6', '#c6dbef'], 
                        'linewidths': 0.25, 
                        'linecolor': '0.5', 
                        'clip_on': False, 
                        'square': True, 
                        'cbar_ax_bbox': [1, 0.42, 0.04, 0.3],
                    }

        #sp.sign_plot(post_hoc_kd, labels=False)

        #ax3.set_title('Significance plot', fontsize=10)
        #ax3.set_yticklabels(ax3.get_xticklabels(), rotation=0, fontsize=10)
        #ax3.set_xticklabels(ax3.get_xticklabels(), rotation=90, fontsize=10)
        pyplot.tight_layout()
        
        png_file = 'substrate_kinetic_traits_plot.png'
        output_png_file_path = os.path.join(html_output_dir, png_file)
        fig.savefig(output_png_file_path, dpi=200)

        pyplot.close(fig)

        return {'path': output_png_file_path,
                'name': png_file,
                'description': 'Plots for Substrate Kinetic Traits'}