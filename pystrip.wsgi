#
# The following two lines are required if you are using a virtual-environment
#
activate_this = '/var/www/pystrip/pystrip/env/bin/activate_this.py'
execfile(activate_this, dict(__file__=activate_this))

import logging
import sys
import os
from os.path import join, dirname
LOG = logging.getLogger(__name__)
logging.basicConfig(stream=sys.stderr, level=logging.WARNING)
logging.getLogger().setLevel(logging.WARNING)
os.environ['PYTHON_EGG_CACHE'] = join(dirname(__file__), '..', 'egg-cache')
os.environ['PYSTRIP_PATH'] = join(dirname(__file__), '..', 'conf')

from auto_icms.webui import app as application

# Send out emails on unhandled errors.
if not application.debug:
   from logging.handlers import SMTPHandler
   mail_handler = SMTPHandler('mail.deltgen.net',
           'pystrip@fearless.vserver.local',
           application.config.get('MAINTAINERS',
               ['mike@deltgen.net']),
           'application error in pystrip on fearless')
   mail_handler.setLevel(logging.ERROR)
   application.logger.addHandler(mail_handler)
