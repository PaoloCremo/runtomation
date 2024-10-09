import pandas as pd
import lalsimulation
import readsheet as rs

inj_num = 2
df_parameters = rs.read_sheet()
with open('original.ini', 'r')  as f:
    file = f.read()

def find_par(file : str, 
             par_name : str):
    
    par_names = ['injection-dict', 'prior-dict']
    if par_name not in par_names:
        raise ValueError(f'"par_name" should be on of {par_names}, not "{par_name}"')
    
    start_point = file.find(par_name)
    end_point = start_point + file[start_point:].find('}\n') + 1 
    paragraph = file[start_point:end_point]
    return paragraph

def exact_word(file, word):
    '''
    to do: if there are not correspondences!
    '''
    
    exact = False
    start = 0

    while not exact:
        start = start + file[start:].find(word)
        end = start + len(word)
        if end > len(file):
            raise ValueError('no correspondence found')
        elif file[start-1].isalpha() or file[end].isalpha():
            start = start + len(word)
        elif file[start:end] == word:
            exact = True
    
    return start, end

def find_next_number(file, start_index, decimal='.'):
    
    f = file[start_index:]
    cross = 0
    ind = 0
    while cross < 2:
        if cross == 0 and (f[ind].isnumeric() or f[ind] == '-'):
            start = ind
            cross += 1
        elif cross == 1 and not f[ind].isnumeric() and not f[ind] == decimal:
            end = ind
            cross += 1
        ind += 1

    return start_index + start, start_index + end

def add_new_value_inj(paragraph : str, 
                      parameter : str, 
                      value):
    
    start, end_name = exact_word(paragraph, parameter)
    start_val, end = find_next_number(paragraph, end_name)
    
    name = paragraph[start:end_name]
    all_par = paragraph[start:end]
    val = paragraph[start_val:end]
    
    all_par_new = all_par.replace(val, f' {value}')
    paragraph = paragraph.replace(all_par, all_par_new)
    
    return paragraph

def add_new_value_prior(paragraph : str, 
                        parameter : str, 
                        value_min, value_max, new_prior_type):
    
    parameter = parameter.replace('_', '-')
    
    if parameter in paragraph:
        start, end_name = exact_word(paragraph, parameter)
    
        end_type = end_name + paragraph[end_name:].find('(')
        smin, emin = find_next_number(paragraph, end_type + exact_word(paragraph[end_type:], 'minimum')[1])
        smax, emax = find_next_number(paragraph, end_type + exact_word(paragraph[end_type:], 'maximum')[1])
        end = end_name + paragraph[end_name:].find(')')
        
        name = paragraph[start:end_name]
        all_par = paragraph[start:end+1]
        
        val = paragraph[end_type+1:end] 
        minimum = paragraph[smin:emin]
        maximum = paragraph[smax:emax]
    
        prior_type = paragraph[end_name+1:end_type].replace(" ", "")
        
        new_par = paragraph.replace(prior_type, new_prior_type)
        new_val = val
        change = 0
        

        round_val = 3
        if not round(float(minimum), round_val) == round(float(value_min), round_val):
            new_val = val.replace(minimum, str(value_min))
            change += 1
        if not round(float(maximum), round_val) == round(float(value_max), round_val):
            new_val = new_val.replace(maximum, str(value_max))
            change += 1
        if change > 0:
            new_par = new_par.replace(val, new_val)
    
        return new_par
    
    else:
        return None


def update_injection(old_ini, df: pd.DataFrame, parameters, ici):

    par_inj = find_par(old_ini, 'injection-dict')
    
    for nr in range(3, 26):
        parameter = parameters.loc[nr]
        if parameter in par_inj:
            value = df.loc[nr][ici]
            par_inj = add_new_value_inj(par_inj, parameter, value)

    new_ini = old_ini.replace(find_par(old_ini, 'injection-dict'), par_inj)
    
    return new_ini

def update_priors(old_ini, df: pd.DataFrame, parameters, ici):

    par_pri = find_par(old_ini, 'prior-dict')
    
    for nr in range(3, 27):
        parameter = parameters.loc[nr]
        if parameter in par_pri and parameter != 'theta_jn':
            prior_type = df.loc[nr][ici + 1]
            minimum = df.loc[nr][ici + 2]
            maximum = df.loc[nr][ici + 3]
            par_pri = add_new_value_prior(par_pri, parameter, minimum, maximum, prior_type)

    new_ini = old_ini.replace(find_par(old_ini, 'prior-dict'), par_pri)
    
    return new_ini

def update_label_outdir(old_ini, injection_number):

    new_ini = old_ini.replace('label=gwmat0', f'label=gwmat{injection_number}')
    new_ini = new_ini.replace('outdir=/mnt/home/users/uib54_res/resh000287/lensing_runs/mlVSprec/gwmat0',
                              f'outdir=/mnt/home/users/uib54_res/resh000287/lensing_runs/mlVSprec/gwmat{injection_number}')
    
    return new_ini

def update_waveform_approximant(old_ini, df, ici, which):
    whichs = ["injection-waveform-approximant", "waveform-approximant"]
    if which not in whichs:
        raise ValueError(f'"which has to be one of {whichs}. Not {which}.')
    start, end_label = exact_word(old_ini, which)
    end = end_label + old_ini[end_label:].find("\n")
    all = old_ini[start:end]
    
    if which == "injection-waveform-approximant":
        wf_approx = df[ici][28]
    else:
        wf_approx = df[ici][28]

    new_ini = old_ini.replace(all, f"{which} = {wf_approx}")

    return new_ini

def create_ini(old_ini, 
               df_parameters : pd.DataFrame,
               injection_number):
    
    # initial column index
    ici = (injection_number - 1) * 4 + 1
    df = df_parameters[range(ici, ici+4)]
    params = df_parameters[0][3:-1]
    
    # update injection values
    new_ini = update_injection(old_ini, df, params, ici)
    new_ini = update_priors(new_ini, df, params, ici)
    
    # update waveform approximant
    for wf_approx in ["injection-waveform-approximant", "waveform-approximant"]:
        new_ini = update_waveform_approximant(new_ini, df_parameters, ici, wf_approx)
        
    # update label and location
    new_ini = update_label_outdir(new_ini, injection_number)

    return new_ini

def write_new_ini(new_ini, injection_number):
    with open(f'gwmat_{injection_number}.ini', 'w') as f:
        f.write(new_ini)


def get_l0par(injection_number, all=False):
    df = rs.read_sheet(SAMPLE_RANGE_NAME='Sheet1!B5:AA61')
    df.index = df[0]
    df = df.drop(0, axis=1)
    ici = (injection_number - 1) * 4 + 1
    
    
    thetajn, phijl, s1pol, s2pol, s12_deltaphi, spin1_a, spin2_a =  lalsimulation.SimInspiralTransformPrecessingWvf2PE(float(df[ici]['incl']), 
                                                                                                                       float(df[ici]['spin1x']), 
                                                                                                                       float(df[ici]['spin1y']), 
                                                                                                                       float(df[ici]['spin1z']), 
                                                                                                                       float(df[ici]['spin2x']), 
                                                                                                                       float(df[ici]['spin2y']), 
                                                                                                                       float(df[ici]['spin2z']),
                                                                                                                       float(df[ici]['mass_1']), 
                                                                                                                       float(df[ici]['mass_2']), 
                                                                                                                       float(df[ici]['reference_frequency']), 
                                                                                                                       float(df[ici]['phase']))
    
    out = {
    'theta_jn': thetajn,
    'phi_jl': phijl,
    'a_1': spin1_a,
    'a_2': spin2_a,
    'tilt_1': s1pol,
    'tilt_2': s2pol,
    'phi_12': s12_deltaphi
    }
    if all:
        return out
    else:
        return round(out['phi_jl'], 8)
