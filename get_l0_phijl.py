import argparse
import functions as fn

# take injection number as input

parser = argparse.ArgumentParser(
                    prog='get l0-frame parameters from j-frame',
                    description='give injection number as per google sheet',
                    epilog='Given the injection number from google sheet, it downloads the j-frame parameters and give the l0-frame ones.\
                            Google Sheet link: https://docs.google.com/spreadsheets/d/1iDE4SvDQFVPWnecllMPMQZlZceX4okxAJzf2Dc_Vtd0/edit?gid=0#gid=0')
parser.add_argument('-in', '--injectionnumber', type=int, required=True)
parser.add_argument('-a', '--alljparams', type=bool, required=False, default=False)
inj_num = parser.parse_args().injectionnumber
all_par = parser.parse_args().alljparams

if __name__ == "__main__":
    print(fn.get_l0par(injection_number=inj_num, all=all_par))
