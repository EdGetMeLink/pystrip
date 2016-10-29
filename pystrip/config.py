from config_resolver import Config
import logging


LOG = logging.getLogger(__name__)

def load_config():
    return  Config('mds', 'pystrip')
