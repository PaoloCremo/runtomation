# runtomation

Scripts to create .ini file for bayesian parameter estimation of gravitational waves signals from google sheet table.

## Composition

- `bbh_parameters.pdf`   
    summary PDF with information about equations used in the scripts
- `create_ini.py`  
    script to run to create the ini file
- `functions.py`  
    main file with relevant functions
- `get_l0_phijl.py`  
    get ```phi_jl``` from jframe parameters
- `original.ini`  
    ini template file to take as reference
- `plot_result.py`  
    script to plot the result from result file from bayesian analysis
- `readsheet.py`  
    script to read the googlesheet file

## Usage

To get the ini file, run
```bash
python3 create_ini.py -in n
```
with ```n``` the number of the injection you want to study.  

To get the ```phi_jl``` parameter, run:
```bash
python3 get_l0_phijl.py -in n -a True/False
```
with ```n``` the number of the injection you are studying and ```a``` whether you want all the parameters as output, or only ```phi_jl```.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE.md) file for details.


## Contact

Paolo Cremonese | [@PaoloCremo](https://github.com/PaoloCremo)