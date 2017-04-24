"""
Settings for Bok Choy tests that are used when running LMS.

Bok Choy uses two different settings files:
1. test_static_optimized is used when invoking collectstatic
2. bok_choy is used when running the tests

Note: it isn't possible to have a single settings file, because Django doesn't
support both generating static assets to a directory and also serving static
from the same directory.
"""

import os
from path import Path as path
from tempfile import mkdtemp

CONFIG_ROOT = path(__file__).abspath().dirname()
TEST_ROOT = CONFIG_ROOT.dirname().dirname() / "test_root"

########################## Prod-like settings ###################################
# These should be as close as possible to the settings we use in production.
# As in prod, we read in environment and auth variables from JSON files.
# Unlike in prod, we use the JSON files stored in this repo.
# This is a convenience for ensuring (a) that we can consistently find the files
# and (b) that the files are the same in Jenkins as in local dev.
os.environ['SERVICE_VARIANT'] = 'bok_choy'
os.environ['CONFIG_ROOT'] = CONFIG_ROOT

from .aws import *  # pylint: disable=wildcard-import, unused-wildcard-import


######################### Testing overrides ####################################

# Needed for the reset database management command
INSTALLED_APPS += ('django_extensions',)

# Redirect to the test_root folder within the repo
GITHUB_REPO_ROOT = (TEST_ROOT / "data").abspath()
LOG_DIR = (TEST_ROOT / "log").abspath()

# Configure modulestore to use the test folder within the repo
update_module_store_settings(
    MODULESTORE,
    module_store_options={
        'fs_root': (TEST_ROOT / "data").abspath(),
    },
    xml_store_options={
        'data_dir': (TEST_ROOT / "data").abspath(),
    },
    default_store=os.environ.get('DEFAULT_STORE', 'draft'),
)

############################ STATIC FILES #############################

# Enable debug so that static assets are served by Django
DEBUG = True

# Serve static files at /static directly from the staticfiles directory under test root
# Note: optimized files for testing are generated with settings from test_static_optimized
STATIC_URL = "/static/"
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
)
STATICFILES_DIRS = [
    (TEST_ROOT / "staticfiles" / "lms").abspath(),
]

DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'
MEDIA_ROOT = TEST_ROOT / "uploads"

# Don't use compression during tests
PIPELINE_JS_COMPRESSOR = None

################################# CELERY ######################################

CELERY_ALWAYS_EAGER = True
CELERY_RESULT_BACKEND = 'cache+memcached://127.0.0.1:11211/'

BLOCK_STRUCTURES_SETTINGS = dict(
    # We have CELERY_ALWAYS_EAGER set to True, so there's no asynchronous
    # code running and the celery routing is unimportant.
    # It does not make sense to retry.
    TASK_MAX_RETRIES=0,
    # course publish task delay is irrelevant is because the task is run synchronously
    COURSE_PUBLISH_TASK_DELAY=0,
    # retry delay is irrelevent because we never retry
    TASK_DEFAULT_RETRY_DELAY=0,
)

###################### Grade Downloads ######################
GRADES_DOWNLOAD = {
    'STORAGE_TYPE': 'localfs',
    'BUCKET': 'edx-grades',
    'ROOT_PATH': os.path.join(mkdtemp(), 'edx-s3', 'grades'),
}

# Configure the LMS to use our stub XQueue implementation
XQUEUE_INTERFACE['url'] = 'http://localhost:8040'

# Configure the LMS to use our stub EdxNotes implementation
EDXNOTES_PUBLIC_API = 'http://localhost:8042/api/v1'
EDXNOTES_INTERNAL_API = 'http://localhost:8042/api/v1'


EDXNOTES_CONNECT_TIMEOUT = 10  # time in seconds
EDXNOTES_READ_TIMEOUT = 10  # time in seconds


NOTES_DISABLED_TABS = []

# Silence noisy logs
import logging
LOG_OVERRIDES = [
    ('track.middleware', logging.CRITICAL),
    ('edxmako.shortcuts', logging.ERROR),
    ('dd.dogapi', logging.ERROR),
    ('edx.discussion', logging.CRITICAL),
]
for log_name, log_level in LOG_OVERRIDES:
    logging.getLogger(log_name).setLevel(log_level)

# Enable milestones app
FEATURES['MILESTONES_APP'] = True

# Enable oauth authentication, which we test.
FEATURES['ENABLE_OAUTH2_PROVIDER'] = True

# Enable pre-requisite course
FEATURES['ENABLE_PREREQUISITE_COURSES'] = True

# Enable Course Discovery
FEATURES['ENABLE_COURSE_DISCOVERY'] = True

# Enable student notes
FEATURES['ENABLE_EDXNOTES'] = True

# Enable teams feature
FEATURES['ENABLE_TEAMS'] = True

# Enable custom content licensing
FEATURES['LICENSING'] = True

# Use the auto_auth workflow for creating users and logging them in
FEATURES['AUTOMATIC_AUTH_FOR_TESTING'] = True

# Open up endpoint for faking Software Secure responses
FEATURES['ENABLE_SOFTWARE_SECURE_FAKE'] = True

FEATURES['ENABLE_ENROLLMENT_TRACK_USER_PARTITION'] = True

########################### Entrance Exams #################################
FEATURES['ENTRANCE_EXAMS'] = True

FEATURES['ENABLE_SPECIAL_EXAMS'] = True

# Point the URL used to test YouTube availability to our stub YouTube server
YOUTUBE_PORT = 9080
YOUTUBE['TEST_TIMEOUT'] = 5000
YOUTUBE['API'] = "http://127.0.0.1:{0}/get_youtube_api/".format(YOUTUBE_PORT)
YOUTUBE['METADATA_URL'] = "http://127.0.0.1:{0}/test_youtube/".format(YOUTUBE_PORT)
YOUTUBE['TEXT_API']['url'] = "127.0.0.1:{0}/test_transcripts_youtube/".format(YOUTUBE_PORT)

############################# SECURITY SETTINGS ################################
# Default to advanced security in common.py, so tests can reset here to use
# a simpler security model
FEATURES['ENFORCE_PASSWORD_POLICY'] = False
FEATURES['ENABLE_MAX_FAILED_LOGIN_ATTEMPTS'] = False
FEATURES['SQUELCH_PII_IN_LOGS'] = False
FEATURES['PREVENT_CONCURRENT_LOGINS'] = False
FEATURES['ADVANCED_SECURITY'] = False

FEATURES['ENABLE_MOBILE_REST_API'] = True  # Show video bumper in LMS
FEATURES['ENABLE_VIDEO_BUMPER'] = True  # Show video bumper in LMS
FEATURES['SHOW_BUMPER_PERIODICITY'] = 1

PASSWORD_MIN_LENGTH = None
PASSWORD_COMPLEXITY = {}

# Enable courseware search for tests
FEATURES['ENABLE_COURSEWARE_SEARCH'] = True

# Enable dashboard search for tests
FEATURES['ENABLE_DASHBOARD_SEARCH'] = True

# discussion home panel, which includes a subscription on/off setting for discussion digest emails.
FEATURES['ENABLE_DISCUSSION_HOME_PANEL'] = True

# Enable support for OpenBadges accomplishments
FEATURES['ENABLE_OPENBADGES'] = True

# Use MockSearchEngine as the search engine for test scenario
SEARCH_ENGINE = "search.tests.mock_search_engine.MockSearchEngine"
# Path at which to store the mock index
MOCK_SEARCH_BACKING_FILE = (
    TEST_ROOT / "index_file.dat"
).abspath()

# Verify student settings
VERIFY_STUDENT["SOFTWARE_SECURE"] = {
    "API_ACCESS_KEY": "BBBBBBBBBBBBBBBBBBBB",
    "API_SECRET_KEY": "CCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCC",
}

# this secret key should be the same as cms/envs/bok_choy.py's
SECRET_KEY = "very_secret_bok_choy_key"

# Set dummy values for profile image settings.
PROFILE_IMAGE_BACKEND = {
    'class': 'storages.backends.overwrite.OverwriteStorage',
    'options': {
        'location': os.path.join(MEDIA_ROOT, 'profile-images/'),
        'base_url': os.path.join(MEDIA_URL, 'profile-images/'),
    },
}

# Make sure we test with the extended history table
FEATURES['ENABLE_CSMH_EXTENDED'] = True
INSTALLED_APPS += ('coursewarehistoryextended',)

BADGING_BACKEND = 'lms.djangoapps.badges.backends.tests.dummy_backend.DummyBackend'

# Configure the LMS to use our stub eCommerce implementation
ECOMMERCE_API_URL = 'http://localhost:8043/api/v2/'

LMS_ROOT_URL = "http://localhost:8000"
DOC_LINK_BASE_URL = 'http://edx.readthedocs.io/projects/edx-guide-for-students'

# TODO: TNL-6546: Remove this waffle and flag code.
from django.db.utils import ProgrammingError
from waffle.models import Flag
try:
    flag, created = Flag.objects.get_or_create(name='unified_course_view')
    flag.everyone = True
    flag.save
    WAFFLE_OVERRIDE = True
except ProgrammingError:
    # during initial reset_db, the table for the flag doesn't yet exist.
    pass

#####################################################################
# Lastly, see if the developer has any local overrides.
try:
    from .private import *      # pylint: disable=import-error
except ImportError:
    pass
