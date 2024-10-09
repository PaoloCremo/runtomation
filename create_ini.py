import argparse
import functions as fn

# take injection number as input

parser = argparse.ArgumentParser(
                    prog='create ini file',
                    description='give injection number as per google sheet',
                    epilog='Given the injection number from google sheet, it compile the .ini file with proper values.\
                            Google Sheet link: https://docs.google.com/spreadsheets/d/1iDE4SvDQFVPWnecllMPMQZlZceX4okxAJzf2Dc_Vtd0/edit?gid=0#gid=0')
parser.add_argument('-in', '--injectionnumber', type=int, required=True)
inj_num = parser.parse_args().injectionnumber

if __name__ == "__main__":
    fn.write_new_ini(fn.create_ini(fn.file, fn.df_parameters, inj_num), inj_num)