import pandas as pd
import lalsimulation
import readsheet as rs

inj_num = 2
df_parameters = rs.read_sheet()
with open('original.ini', 'r')  as f:
    file = f.read()

# new_file = '\n'.join(lines)
# print(new_file)

def find_feature(lines : list,
                 feature : str):
    features = ["injection-dict", "prior-dict", "trigger-time", "injection-waveform-approximant", "waveform-approximant",
                "numerical-relativity-file", "label", "outdir", "prior-dict"]
    line_number = -1
    if feature not in features:
        raise ValueError(f'"{feature}" not supported. "feature" has to be one of {features}.')
    else:
        for n,line in enumerate(lines):
            # print(f'INIZIO {n}\n{line}\nFINE\n')
            if feature in line and line[:len(feature)] == feature:
                line_number = n

    return line_number

def update_trigger_time(lines : list, df, ici : int):

    l = find_feature(lines, "trigger-time")
    trigger_time = float(df[ici][df[0] == "geocent_time"].values[0])
    new_line = f'trigger-time={trigger_time}'
    lines[l] = new_line
    
    return None

def update_wf_approx(lines : list, df, ici : int, which):
    whichs = ["injection-waveform-approximant", "waveform-approximant"]
    if which not in whichs:
        raise ValueError(f'"which has to be one of {whichs}. Not {which}.')
    
    l = find_feature(lines, which)
    wf_approximant = df[ici][df[0] == "waveform-approximant"].values[0]
    if which == "injection-waveform-approximant":
        wf_approximant = df[ici][df[0] == "waveform-approximant"].values[0]
        if not "NR_" in wf_approximant:
            lf = find_feature(lines, "numerical-relativity-file")
            lines.pop(lf)
    else:
        wf_approximant = df[ici+1][df[0] == "waveform-approximant"].values[0]

    new_line = f'{which}={wf_approximant}'
    lines[l] = new_line
    
    return None

def get_dict(lines : str):
    l = find_feature(lines=lines, feature="injection-dict")
    dict_str = lines[l]
    if ".," in dict_str:
        dict_str = dict_str.replace(".,", ".0,")
    start_dict = dict_str.find('{')
    only_dict = dict_str[start_dict:].replace("'", '"')
    injection_dict = json.loads(only_dict)
    
    return injection_dict


def update_injection(lines, df, ici):
    l = find_feature(lines, "injection-dict")
    dict = get_dict(lines)

    new_dict = {}
    for n in range(3,28):
        new_dict[df[0][n]] = float(df[ici][n])
    dict.update(new_dict)
    new_line = f'injection-dict={dict}'
    lines[l] = new_line
    

    return None

def update_label_outdir(lines, injection_number):

    l = find_feature(lines, "label")
    lines[l] = f"label=gwmat{injection_number}"
    l = find_feature(lines, "outdir")
    lines[l] = f"outdir=/mnt/home/users/uib54_res/resh000287/lensing_runs/mlVSprec/gwmat{injection_number}"
    
    return None

def get_priors(lines):
    l = find_feature(lines, "prior-dict")
    prior_dict = lines[l]
    only_dict = prior_dict[len("prior-dict={"):-1]

    return only_dict

def update_priors(lines, df):
    only_dict = get_priors(lines)
    # get parameters
    lines_dict = only_dict.split('), ')
    # '), '.join(lines_dict)
    lines_dict
    params = []
    for line in lines_dict:
        params.append(line.split(':')[0].replace('-', '_'))

    new_dict = []
    for ln, param in enumerate(params):
        df_line = df[df[0] == param]
        if 'latex_label' in lines_dict[ln]:
            lls = lines_dict[ln].split(',')
            for llsline in lls:
                if 'latex_label' in llsline:
                    latex_line = llsline
            new_dict.append(f"{param.replace('_', '-')}: {df_line[ici+1].values[0]}(minimum={df_line[ici+2].values[0]}, maximum={df_line[ici+3].values[0]}, name='{param}', {latex_line}, boundary=None)")
        else:
            new_dict.append(f"{param.replace('_', '-')}: {df_line[ici+1].values[0]}(minimum={df_line[ici+2].values[0]}, maximum={df_line[ici+3].values[0]}, name='{param}', boundary=None)")
            
    l = find_feature(lines, "prior-dict")
    lines[l] = f"prior-dict={{{', '.join(new_dict)} }}"

    return None

def create_new_ini(old_ini, 
                   df_parameters : pd.DataFrame,
                   injection_number):
    ici = (injection_number - 1) * 4 + 1
    lines = file.split('\n')
    
    update_trigger_time(lines=lines, df=df_parameters, ici=ici)
    for which in ["injection-waveform-approximant", "waveform-approximant"]:
        update_wf_approx(lines=lines, df=df_parameters, ici=ici, which=which)
    update_injection(lines=lines, df=df_parameters, ici=ici)
    update_label_outdir(lines=lines, injection_number=injection_number)
    update_priors(lines=lines, df=df_parameters)

    new_ini = '\n'.join(lines)

    return new_ini

def write_new_ini(injection_number):
    new_ini = create_new_ini(file, df_parameters, injection_number)
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
