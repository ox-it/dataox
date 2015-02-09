import imp
import os
import platform

STATIC_URL = '//static.data.ox.ac.uk/'
STATICFILES_DIRS = (
    os.path.join(imp.find_module('dataox')[1], 'static'),
    os.path.join(imp.find_module('humfrey')[1], 'static'),
)

# OpenLayers should be installed as a system-wide package. To build the Debian
# package, clone git://github.com/ox-it/debian-packaging.git and build the
# package in the openlayers directory.
distname, _, _ = platform.linux_distribution()
if distname == 'Fedora':
    STATICFILES_DIRS += (('lib/openlayers', '/usr/share/openlayers/www'),)
elif distname == 'debian':
    STATICFILES_DIRS += (('lib/openlayers', '/usr/share/javascript/openlayers'),
                         ('lib/jquery', '/usr/share/javascript/jquery'),
                         ('lib/jquery-cookie', '/usr/share/javascript/jquery-cookie'),
                         ('lib/jquery-ui', '/usr/share/javascript/jquery-ui'),
                         ('lib/datatables', '/usr/share/javascript/datatables'))
else:
    raise AssertionError("Unsupported distribution")
del distname

PIPELINE_JS = {
    'dataox': {'source_filenames': ('app/dataox-1.0.js',),
               'output_filename': 'app/dataox-1.0.min.js'},
    'equipment': {'source_filenames': ('equipment/base.js',),
                  'output_filename': 'equipment.min.js'},
    'courses': {'source_filenames': ('app/courses-1.0.js',),
                'output_filename': 'app/courses-1.0.min.js'},
    'html5shiv': {'source_filenames': ('lib/html5shiv.js',),
                  'output_filename': 'lib/html5shiv.min.js'},
    'oauth2': {'source_filenames': ('lib/oauth2/oauth2/oauth2.js',),
               'output_filename': 'lib/oauth2.min.js'},
    'jquery.collapsible': {'source_filenames': ('lib/jquery-collapsible-content/js/jQuery.collapsible.js',),
                           'output_filename': 'lib/jquery.collapsible.min.js'},
}

PIPELINE_JS_COMPRESSOR = 'pipeline.compressors.closure.ClosureCompressor'
PIPELINE_CLOSURE_ARGUMENTS = '--jscomp_off uselessCode'
STATICFILES_STORAGE = 'pipeline.storage.PipelineStorage'

del imp, os, platform
