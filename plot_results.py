#!/usr/bin/python3

import os 
import sys
path_home = os.path.expanduser('~')
import bilby
from bilby.core.prior import Uniform, Sine, PowerLaw
import numpy as np
import pandas as pd
import corner
import matplotlib.pyplot as plt

if True:
    from matplotlib.ticker import ScalarFormatter
    #To activate 
    # %config InlineBackend.figure_format = 'retina'
    sys.path.insert(1, '/Library/TeX/texbin')

# to use LaTex font
plt.rc('text', usetex=True)
plt.rc('font', family='serif')

#matplotlib configs
fontssz = 12
fontsz = 15
fontSz = 17
fontSZ = 20

CB_color_cycle = ['#377eb8', '#ff7f00', '#4daf4a',
                  '#e41a1c', '#984ea3', '#a65628', '#f781bf',
                  '#999999', '#dede00']
CB_color_cycle2 = ['#000000', '#E69F00', '#56B4E9',
                   '#009E73', '#F0E442', '#0072B2',
                   '#D55E00', '#CC79A7']
CB_cc = ['C'+str(i) for i in range(len(CB_color_cycle))]

c_main = CB_color_cycle2[5] 
cc_plus = CB_color_cycle2[3]
cc_minus = CB_color_cycle2[6]
c_inj = 'C2' 

defaults_kwargs = dict(bins=50, smooth=0.9, label_kwargs=dict(fontsize=fontSZ),
                       title_kwargs=dict(fontsize=fontssz), 
                       color=c_main,
                       truth_color='tab:orange', quantiles=[0.16, 0.84],
                       levels=(1 - np.exp(-0.5), 1 - np.exp(-2), 1 - np.exp(-9 / 2.)),
                       plot_density=False, plot_datapoints=True, fill_contours=True,
                       max_n_ticks=3, hist_kwargs=dict(density=True))

# import utils as tl

# define main folder
def get_file_path(folder : str, run : str):

    # runs = [0, 1, 'gwmat2/', 'gwmat3/', 'gwmat4/', 'gwmat5/', 'gwmat6/', 'gwmat7/', 'gwmat8/', 'gwmat9/']
    # run = runs[run_number]
    path_run = folder + run 
    if folder[:4] == '/mnt':
        path_run += '/result/'
    for ts in os.listdir(path_run):
         if 'hdf5' in ts or 'json' in ts and 'merge' in ts:
             file = ts

    file_path = path_run + file

    return file_path, path_run

def load_result(file_path):
    result = bilby.result.read_in_result(filename=file_path)
    return result

def get_injection(injection_number):
    
    import readsheet as rs
    df_parameters = rs.read_sheet()
    
    ici = injection_number * 4 + 1
    
    injection_par = {}
    for i in range(3,28):
        injection_par[df_parameters[0][i]] = df_parameters[ici][i]
        if df_parameters[0][i] == 'geocent_time':
            injection_par[df_parameters[0][i]] = 0.

    return injection_par
    

def plot_result(result, params, inj_par, run, save):
    
    # labels
    lbls = [result.priors[par].latex_label for par in params]
    for i in range(len(lbls)):
        if 'mathcal{M}' in lbls[i]:
            lbls[i] = lbls[i].replace('mathcal{M}', 'mathcal{M}_c')
        elif 'M_{lr}' in lbls[i]:
            lbls[i] = lbls[i].replace('M_{lr}', 'M_{L}')
    
    samples = result.posterior[params]
    corr_df = samples.corr()
    corr = corr_df.values

    #plot
    fig, axs = plt.subplots(len(params),len(params), figsize=(15,15)) # 6.4*7,4.8*7))
    
    corner.corner(data=samples.values,
                  labels=lbls, 
                  titles=lbls, 
                  show_titles=True,
                  fig=fig,
                  zorder=1,
                  **defaults_kwargs)
    
    if True:
        corner.overplot_lines(fig, inj_par, color=c_inj, zorder=2)
    
    for nr,axr in enumerate(axs):
        for nc,axc in enumerate(axr):
            if nr>nc:
                axc.fill_between([0.01, 0.1], y1=[0.01, 0.01], y2=[.99, .99], 
                                 transform=axc.transAxes, color='w', zorder=3)
                cor = (corr[nr][nc]+1)/2
                if cor >= 0.5:
                    cc = cc_plus 
                else:
                    cc = cc_minus 
                axc.fill_between([0., 0.1], y1=[0., 0.], y2=[abs(corr[nr][nc]), abs(corr[nr][nc])], 
                                 transform=axc.transAxes, color=cc, zorder=3)
                axc.text(0.017, 0.75, '%.2f'%(corr[nr][nc]), transform=axc.transAxes, rotation=90) # nr,nc
                axc.vlines(0.11, -1, 1, transform=axc.transAxes, color='k', alpha=0.25, zorder=3)
    
    
    
    if len(params) < 9:
        fig_name_complete = f'{result.outdir}{run[:-1]}_merged_corner.png' 
    else:
        fig_name_complete = f'{result.outdir}{run[:-1]}_merged_corner_complete.png'
    
    if save:
        print('saving...')
        plt.savefig(f'{fig_name_complete}', dpi=300, bbox_inches='tight', transparent=False)
        print(f'saved in\n{fig_name_complete}')
    else:
        print('NOT saved')
        plt.show()


def main(folder, run, save):
    file_path, path_run = get_file_path(folder=folder, run=run)
    result = load_result(file_path=file_path)
    result.outdir = path_run
    result.outdir = result.outdir.replace('local_', '')
    params = ['chirp_mass', 'mass_ratio', 'luminosity_distance', 'a_1', 'a_2', 'tilt_1', 'tilt_2', 'phi_12', 'phi_jl', 'Log_Mlz', 'yl']
    injection_number = int(run[5:].split('/')[0])
    injection_par = get_injection(injection_number=injection_number)
    inj_par = [float(injection_par[par]) for par in params]

    plot_result(result=result, params=params, inj_par=inj_par, run=run, save=save)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(
                        prog='pytohn3 plot_results.py',
                        description='Corner plot the result at "run" folder',
    )
                        # epilog='')
    parser.add_argument('-r', '--run', type=str, required=True, help='run name, i.e. name of the folder where the result is')
    parser.add_argument('-f', '--folder', type=str, required=True, help='folder where run is')
    parser.add_argument('-s', '--save', type=str, required=False, default='yes', choices=['yes', 'y', 'no', 'n'], help="save or just show the result plot")
    run = parser.parse_args().run + '/'
    folder = parser.parse_args().folder
    save_str = parser.parse_args().save
    if save_str == 'yes' or save_str == 'y':
        save = True
    elif save_str == 'no' or save_str == 'n':
        save = False
    else:
        raise ValueError(f'Save has to be "yes" or "no", not {save}')
    

    main(folder=folder, run=run, save=save)
