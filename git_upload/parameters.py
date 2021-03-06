#parameters.py
"""
###############################
### FIREFLY PARAMETERS FILE ### 
###############################

### Edit this file to set up firefly's options, 
### choose your input files, output files, and models. 


# Edit the following lines to your requirements.
# Commented out lines (#) mean that the default parameters are used (see README).

"""

# DATA PARAMETERS, TYPE
# =====================

# Allowed data types for 'data_type': sdss_dr7, sdss_boss, pmanga, mock_ssp, mock_csp, m67, ngc, custom
# test_sdss, test_mock, test_manga,matt,moresco_boss
data_type = 'sdss_dr7'
milky_way_reddening     = True
data_format             = 'fits'
#observation_type = 'ifu'
#radial_or_rss='radial'

#redshift    = 0.0
#vdisp       = 90.0

# FITTING PARAMETERS
# ==================

# HPF mode: on (default): run models and data through hpf filter to determine dust, then refit
#			off: assume model attenuation curve and fit full spectrum for each of these
#			hpf_only	: run models and data through hpf filter and use these results directly 
hpf_mode 	= 'on'
models = 'm11' # m11/bc03 / m09
restrict_ages = 'default' # default,strict,off\

downgrade_models = True

# Detailed dust stuff!
dust_law = 'calzetti'
max_ebv = 1.0
num_dust_vals = 100
dust_smoothing_length = 200

# Plotting options
plot_diagnostics=False
plot_fits = False
plot_eps = False # plotting during the fitting routine (useful diagnostic)


# Specific fitting options
max_iterations = 10
fit_per_iteration_cap = 1000
# Sampling size when calculating the maximum pdf (100=recommended)
pdf_sampling = 300

# Default is air, unless manga is used
data_wave_medium = 'vacuum'

#min_wavelength = 0
#max_wavelength = 0

# MODEL PARAMETERS
# ================

#model_libs 			= ['MILES','STELIB','ELODIE','MILES_revisedIRslope','MILES_UVextended']
#imfs 				= ['ss','kr','cha']

#model_libs = ['MILES','STELIB','ELODIE']
model_libs = ['MILES']

imfs = ['kr'] # ss/cha/kr


# Range of metallicites and ages to fit.
Z_limits 			= [-99,99]
#Z_limits 			= [-0.1,0.1]
age_limits 			= [-99,99] 
#age_limits 			= [8.0,9.1] # log yrs
#deltal_libs          = [0.0] # resolution of model / AA
# wave_limits = [3800,6000]
wave_limits = [0,99999990]





# Options specfic to certain data types [DO NOT CHANGE!]:
if data_type == 'ngc':
	max_wavelength = 6000

if data_type == 'manga':
    file_in = '/mnt/lustre/eme/goddard/MPL4_RADIAL/'
    data_format = 'fits'
    observation_type = 'ifu'
    file_dir = '/mnt/lustre/eme/goddard/MPL4_RADIAL/'
    output_dir_prefix = '/mnt/lustre/eme/goddard/MPL4_RADIAL_OUTPUT/'
    bin_number = 50
    milky_way_reddening = True
    data_wave_medium = 'vacuum'

if data_type == 'test_manga':
    file_in = '/mnt/lustre/eme/goddard/data/test_manga/'
    data_format = 'fits'
    observation_type = 'ifu'
    bin_number = 50
    milky_way_reddening = True
    data_wave_medium = 'vacuum'

elif data_type == 'moresco_boss':
    file_in = '/mnt/lustre/eme/goddard/data/moresco_boss/ave_mm1_12vdisp_z0.4752_clipping.dat'
    file_dir = '/mnt/lustre/eme/goddard/data/moresco_boss/'
    data_format = 'ascii'
    observation_type = 'single'
    # output_dir_prefix = './fits/moresco/moresco_restrictage/'
    # restrict_ages = 'strict'
    output_dir_prefix = './fits/moresco/moresco_allages/'
    restrict_ages = 'off'
    milky_way_reddening = False
    wave_limits = [3500,99999999]
    age_limits = [0,999]
    #Z_limits = [0,999]


if data_type == 'sdss_dr7':
    file_in='./data/sdss_dr7/'
    file_dir = './data/sdss_dr7/'
    output_dir_prefix = './fits/sdss_dr7/'
    observation_type = 'single'
    restrict_ages = 'True'
    milky_way_reddening = False
    wave_limits = [3500,99999999]
    age_limits = [0,999]
    data_wave_medium = 'vacuum'

#if data_type == 'custom':
#    redshift    = 0.0
#    vdisp       = 90.0

if data_type == 'matt':
    file_hdu = 1
    if file_hdu == 0:
        vdisp = 250.11
    else:
        vdisp = 293.42
    milky_way_reddening = True
    wave_limits = [0,99995500]

    file_in = './data/matt/'
    data_type = 'custom'
    data_format = 'fits_matt'
    observation_type = 'single'
    file_dir = './data/matt/'
    output_dir_prefix =  './fits/matt/'


deltal_libs = []
if models == 'm11':
    for m in model_libs:
        if m == 'MILES' or m == 'MILES_revisednearIRslope' or m == 'MILES_UVextended':
            deltal_libs.append(2.55)
        elif m == 'STELIB':
            deltal_libs.append(3.40)
        elif m == 'ELODIE':
            deltal_libs.append(0.55)
        elif m == 'MARCS':
            deltal_libs.append(0.1)

elif models=='bc03':
    model_libs = ['STELIB_BC03']
    imfs        = ['cha']
    deltal_libs = [3.00]

elif models == 'm09':
    file_dir = './data/uv_johan/'
    if downgrade_models:
        deltal_libs = [0.4]
    else:
        deltal_libs = [3.6]




if data_type == 'nature':
    file_in = './data/nature/nature08220-s2.dat'
    file_dir = './data/nature/'
    data_format = 'ascii'
    observation_type = 'single'
    # output_dir_prefix = './fits/moresco/moresco_ascii_restrictage_'
    # restrict_ages = 'strict'
    output_dir_prefix = './fits/nature/nature_ascii_'
    restrict_ages = 'default'
    milky_way_reddening = False
    wave_limits = [1700,99999990]
    age_limits = [8.0,999]
    ra=0
    dec=0
    redshift = 2.186
    vdisp = 510

    trust_flag = 0
    objid = 1
    data_type='custom'

    #Z_limits = [-0.01,999]
