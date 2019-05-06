import stimela

INPUT = "input"
OUTPUT = "output"
MSDIR = "msdir"

MANUAL = False
CONFIG = ''

if MANUAL:
    recipe = stimela.Recipe('Make Pipeline', ms_dir=MSDIR)
    stimela.register_globals()


# 1: Create a telescope measurement set

def simms(recipe, num, parameters):
    recipe.add("cab/simms",
               "{}_simulated_ms".format(num),
               parameters,
               input=INPUT,
               output=OUTPUT,
               label="{}_Simulated_MS:: simulate ms".format(num))


# 2: Simulate visibility data with noise and calibration (propagation) effects

def simulator(recipe, num, parameters):
    recipe.add("cab/simulator",
               "{}_generate_data".format(num),
               parameters,
               input=INPUT,
               output=OUTPUT,
               label="{}_Generate_data:: simulating data".format(num))


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
