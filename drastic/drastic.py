import stimela

INPUT = "input"
OUTPUT = "output"
MSDIR = "msdir"
PREFIX = "calibration"

recipe = stimela.Recipe("Stimela simulation example", ms_dir=MSDIR)


MS_meq = 'meerkat_SourceRecovery_meqtrees.ms'
MS_cub = 'meerkat_SourceRecovery_cubical.ms'
PREFIX_meq = MS_meq[:-3]
PREFIX_cub = MS_cub[:-3]
LSM = 'skymodel.txt'
FREQ0 = '1.42GHz'
PHASE_CENTER = "J2000,0deg,-30deg"

TEL_NAME = 'meerkat'    # Telescope name
SYN_TIME = 2            # Sythesis time in hours
INT_TIME = 60           # Integration time
SMEARING = False        # Source time and bandwidth smearing
SEFD = 551              # Spectral Flux Energy Density
delta_freq = 2          # Channel width in MHz
IN_CHAN = 16            # Number of input channels
OUT_CHAN = 4            # Number of output channels
delta_freq = 2          # Channel width in MHz
POINT_SOURCES = 100     # Number of point source (i.e if 0% only extended sources)
NPIX = 4096             # Number of pixels
CELL_SIZE = 1.0         # Pixel size
NITERS = 20000          # Number of cleaning iterations
LOOP_GAIN = 0.1         # Cleaning loop gain
IM_WEIGHT = 'uniform'   # Imaging weighting
BRIGGS_robust = -2      # Robust parameter
ISL_THRESH = 10.0       # Island detection threshold sigma
PIX_THRESH = 20.0       # Pixel detection threshold in sigma
CATALOG_TYPE = 'gaul'   # Sourcery output catalog type


# 1: Create a telescope measurement set

def makems(recipe, num, parameters):
    params = {
        "msname"    :   MS_cub,
        "telescope" :   TEL_NAME,
        "synthesis" :   SYN_TIME,  # in hours
        "dtime"     :   INT_TIME,  # in seconds
        "freq0"     :   FREQ0,
        "dfreq"     :   "{}MHz".format(delta_freq),
        "nchan"     :   IN_CHAN,
    }
    params.update(parameters)
    recipe.add("cab/simms", "make_simulated_cub_ms",
               params,
               input=INPUT,
               output=OUTPUT,
               label="Making simulated MS = %s" % PREFIX_cub)
    recipe.run()
    recipe.jobs = []


# 2: Simulate visibility data with noise and calibration (propagation) effects

def simulator(recipe, num, parameters):
    params = {
        "msname"    :   MS_meq,
        "skymodel"  :   LSM,
        "addnoise"  :   True,
        "sefd"      :   SEFD,
        "Gjones"    :   True,
        "gain-max-period" : 4,
        "gain-min-period" : 1,
        "phase-max-period": 4,
        "phase-min-period": 1,
        "column"    :   "DATA",
    }
    params.update(parameters)
    recipe.add("cab/simulator",
               "simulate_meq_noise",
               params,
               input=INPUT,
               output=OUTPUT,
               label="Add noise and propagation effects to %s" % PREFIX_meq)
    recipe.run()
    recipe.jobs = []

# 6: Calibration

def meqtrees(recipe, num, parameters):
    params = {
        "skymodel"            : '{0:s}.lsm.html:output'.format(MS_meq[:-3]),
        "model-column"        : "MODEL_DATA",
        "msname"              : MS_meq,
        "threads"             : 4,
        "column"              : "DATA",
        "output-data"         : "CORR_DATA",
        "output-column"       : "CORRECTED_DATA",
        "prefix"              : PREFIX_meq,
        "label"               : "cal{0:d}".format(1),
        "read-flags-from-ms"  : True,
        "read-flagsets"       : "-stefcal",
        "write-flagset"       : "stefcal",
        "write-flagset-policy": "replace",
        "Gjones"              : True,
        "Gjones-solution-intervals" : [30, 0],
        "Gjones-matrix-type"  : "GainDiag",
        "Gjones-ampl-clipping"      : True,
        "Gjones-ampl-clipping-low"  : 0.5,
        "Gjones-ampl-clipping-high" : 1.5,
        "make-plots"          : True,
        "tile-size"           : 4,
        },
    params.update(parameters)
    recipe.add('cab/calibrator',
               'meq_cal',
               params,
               input=INPUT,
               output=OUTPUT,
               label="meq_cal:: Calibrate ms={0:s}".format(MS_meq))
    recipe.run()
    recipe.jobs = []


def cubical(recipe, num, parameters):
    params = {
        "data-ms"             : MS_cub,
        "data-column"         : 'DATA',
        "out-model-column"    : 'MODEL_DATA',
        "sol-term-iters"      : '200',
        "data-time-chunk"     : 32,
        "dist-ncpu"           : 2,
        "sol-jones"           : 'G',
        "model-list"          : '{0:s}.lsm.html:output'.format(MS_cub[:-3]),
        "out-name"            : PREFIX_cub,
        "out-mode"            : 'sr',
        "out-plots"           : True,
        "out-casa-gaintables" : True,
        "weight-column"       : 'WEIGHT',
        "montblanc-dtype"     : 'float',
        "g-solvable"          : True,
        "g-type"              : 'complex-2x2',
        "g-time-int"          : 8,
        "g-freq-int"          : 8,
        "g-clip-low"          : 0.5,
        "g-clip-high"         : 1.5,
        "g-max-prior-error"   : 1000,
        "g-max-post-error"    : 1000
    }
    params.update(parameters)
    recipe.add('cab/cubical',
               'cub_cal',
               params,
               input=INPUT,
               output=OUTPUT,
               shared_memory='2Gb',
               label="cub_cal:: Calibrate ms={0:s}".format(MS_cub))
    recipe.run()
    recipe.jobs = []


# 7: Imaging

def wsclean(recipe, num, parameters):
    params = {
        "msname"                :   MS_meq,
        "prefix"                :   PREFIX_meq+'-cal',
        "column"                :   "CORRECTED_DATA",
        "niter"                 :   20000,
        "auto-threshold"        :   0.5,
        "auto-mask"             :   3,
        "channelsout"           :   OUT_CHAN,
        "npix"                  :   NPIX,
        "cellsize"              :   "%sasec" % CELL_SIZE,
        "weight"                :   IM_WEIGHT,
        "joinchannels"          :   True if OUT_CHAN > 1 else False,
        "weight"                :   'briggs 0'
    }
    params.update(parameters)
    recipe.add('cab/wsclean',
               'image_wsclean',
               params,
               input=INPUT,
               output=OUTPUT,
               label='image_wsclean_meq_cal:: %s image data' % PREFIX_meq)
    recipe.run()
    recipe.jobs = []


def tclean(recipe, num, parameters):
    params = {
        "msname"                :   MS_meq,
        "prefix"                :   PREFIX_meq+'-cal',
        "cellsize"              :   "%sarcsec" % CELL_SIZE,
        "npix"                  :   NPIX,
        "weight"                :   IM_WEIGHT,
        "niter"                 :   NITERS,
        "start"                 :   0,
        "width"                 :   OUT_CHAN,
        "pblimit"               :   0.0,
        "mode"                  :   "cube",
        "nchan"                 :   1,
        "gridmode"              :   "wproject",
        "wprojplanes"           :   128,
        "threshold"             :   "0.001Jy",
        "robust"                :   0
    }
    params.update(parameters)
    recipe.add('cab/casa_tclean',
               'image_tclean',
               params,
               input=INPUT,
               output=OUTPUT,
               label='image_tclean:: %s mage data' % PREFIX_meq)
    recipe.run()
    recipe.jobs = []


# 8: Stack images to create cubes

def fitstools(recipe, num, parameters):
    params = {
     "image"                    : [PREFIX_meq+'-cal-{0:04d}-image.fits:output'.format(d) for d in xrange(OUT_CHAN)],
     "output"                   : PREFIX_meq+'-cal-cube.image.fits',
     "stack"                    : True,
     "delete-files"             : True,
     "fits-axis"                : 'FREQ'
    }
    params.update(parameters)
    recipe.add('cab/fitstool',
               'meq_cal_image_cubes',
               params,
               input=INPUT,
               output=OUTPUT,
               label='meq_cal_image_cubes:: Make {0:s} cube from wsclean'.format(PREFIX_meq))
    recipe.run()
    recipe.jobs = []


# 9: Source Finders

def pybdsm(recipe, num, parameters):
    cub_image = 'meerkat_SourceRecovery_cubical-cube.image.fits'
    params = {
        "filename"              :   '%s:output' % cub_image,
        "outfile"               :   MS_cub[:-3]+'-cal',
        "thresh_pix"            :   PIX_THRESH,
        "thresh_isl"            :   ISL_THRESH,
        "group_by_isl"          :   True,
        "spectralindex_do"      :   True if OUT_CHAN > 1 else False,
        "multi_chan_beam"       :   True if OUT_CHAN > 1 else False,
        "clobber"               :   True,
        "catalog_type"          :   CATALOG_TYPE,
        "adaptive_rms_box"      :   True,
        "blank_limit"           :   1e-9
    }
    params.update(parameters)
    recipe.add('cab/pybdsm',
               'source_finder_cub_cal',
               params,
               input=INPUT,
               output=OUTPUT,
               label='src_finder_cal_%s:: Source finder' % cub_image)
    recipe.run()
    recipe.jobs = []


def aegean(recipe, num, parameters):
    cub_image = 'meerkat_SourceRecovery_cubical-cube.image.fits'
    params = {
        "filename"            :   '%s:output' % meq_image,
        "outfile"             :   MS_meq[:-3]+'.tab:output',
        "slice"               :   0,
        "port2tigger"         :   True
    }
    params.update(parameters)
    recipe.add('cab/aegean',
               'aegean_finder_cub',
               params,
               input=INPUT,
               output=OUTPUT,
               label='src_finder_%s:: aegean finder' % cub_image)
    recipe.run()
    recipe.jobs = []
