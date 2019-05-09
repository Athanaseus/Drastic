import stimela
import json

INPUT = "input"
OUTPUT = "output"
MSDIR = "msdir"

MANUAL = False
CONFIG = ''

if MANUAL:
    recipe = stimela.Recipe('Make Pipeline', ms_dir=MSDIR)
    stimela.register_globals()


def json_dump(data_dict, filename='recipes.json', root='output'):
    """Dumps the computed dictionary into a json file.
    Parameters
    ----------
    data_dict : dict
        Dictionary with output results to save.
    filename : file
        Name of file to dump recipes for later runs
    root : str
        Directory to save output json file (default is current directory).
    Note
    ----
    If the `filename` file exists, it will be append, and only
    repeated recipes will be replaced.
    """
    filename = ('{:s}/{:s}'.format(root, filename))
    try:
        # Extract data from the json data file
        with open(filename) as data_file:
            data_existing = json.load(data_file)
            data_existing.update(data_dict)
            data = data_existing
    except IOError:
        data = data_dict
    if data:
        with open(filename, 'w') as f:
            json.dump(data, f)


def get_data(filename='recipes.json', root='output'):
    "Extracts data from the json data file"
    filename = '{:s}/{:s}'.format(root, filename)
    with open(filename) as f:
        data = json.load(f)
    return data


# 1: Create a telescope measurement set

def simms(recipe, num, parameters):
    recipe_params = {}
    step = "{}_simulated_ms".format(num)
    cab = '{}_simms'.format(num)
    recipe.add("cab/simms",
               step,
               parameters,
               input=INPUT,
               output=OUTPUT,
               label="{}_Simulated_MS:: simulate ms".format(num))
    recipe_params[cab] = parameters
    json_dump(recipe_params)


# 2: Simulate visibility data with noise and calibration (propagation) effects

def simulator(recipe, num, parameters):
    recipe_params = {}
    step = "{}_generate_data".format(num)
    cab = '{}_simms'.format(num)
    recipe.add("cab/simulator",
               step,
               parameters,
               input=INPUT,
               output=OUTPUT,
               label="{}_Generate_data:: simulating data".format(num))
    recipe_params[cab] = parameters
    json_dump(recipe_params)


# 3: Calibration

def meqtrees(recipe, num, parameters):
    recipe.add('cab/calibrator',
               '{}_meq_cal'.format(num),
               parameters,
               input=INPUT,
               output=OUTPUT,
               label="{}_meq_cal:: Calibrate".format(num))


def cubical(recipe, num, parameters):
    recipe.add('cab/cubical',
               '{}_cub_cal',
               parameters,
               input=INPUT,
               output=OUTPUT,
               shared_memory='32Gb',
               label="{}_cub_cal:: Calibrate".format(num))


# 7: Imaging

def wsclean(recipe, num, parameters):
    recipe.add('cab/wsclean',
               '{}_image_wsclean'.format(num),
               parameters,
               input=INPUT,
               output=OUTPUT,
               label='{}_image_wsclean:: image data'.format(num))


def casa_tclean(recipe, num, parameters):
    recipe.add('cab/casa_tclean',
               '{}_image_tclean'.format(num),
               parameters,
               input=INPUT,
               output=OUTPUT,
               label='{}_image_tclean:: image data'.format(num))


def casa_cleant(recipe, num, parameters):
    recipe.add('cab/casa_clean',
               '{}_image_clean'.format(),
               parameters,
               input=INPUT,
               output=OUTPUT,
               label='{}_image_ddfacet:: image data'.format(num))


def ddfacet(recipe, num, parameters):
    recipe.add('cab/ddfacet',
               '{}_image_ddfacet'.format(num),
               parameters,
               input=INPUT,
               output=OUTPUT,
               label='image_ddfacet:: image data'.format(num))


def lwimager(recipe, num, parameters):
    recipe.add('cab/lwimager',
               '{}_image_lwimager'.format(num),
               parameters,
               input=INPUT,
               output=OUTPUT,
               label='{}_image_lwimager:: image data'.format(num))


# 9: Make mask to use during deconvolution

def casa_makemask(recipe, num, parameters):
    recipe.add('cab/casa_makemask',
               '{}_MakeMask'.format(num),
               parameters,
               input=INPUT,
               output=OUTPUT,
               label='{}_CASA_MakeMask:: make casa mask'.format(num))


def cleanmask(recipe, num, parameters):
    recipe.add('cab/cleanmask',
               '{}_CleanMask'.format(num),
               parameters,
               input=INPUT,
               output=OUTPUT,
               label='{}_CleanMask:: make clean mask'.format(num))


# 8: Stack images to create cubes

def fitstools(recipe, num, parameters):
    recipe.add('cab/fitstool',
               '{}_make_cubes'.format(num),
               parameters,
               input=INPUT,
               output=OUTPUT,
               label='{}_image_cubes:: make image cube'.format(num))


# 9: Source Finders

def pybdsm(recipe, num, parameters):
    recipe.add('cab/pybdsm',
               '{}_pybdsm__finder'.format(num),
               parameters,
               input=INPUT,
               output=OUTPUT,
               label='{}_pybdsf_src_finder:: pybdsm finder'.format(num))


def aegean(recipe, num, parameters):
    recipe.add('cab/aegean',
               '{}_aegean_finder'.format(num),
               parameters,
               input=INPUT,
               output=OUTPUT,
               label='{}_aegen_src_finders:: aegean finder'.format(num))


def run_all(recipe):
    recipe.run()
    recipe.jobs = []
