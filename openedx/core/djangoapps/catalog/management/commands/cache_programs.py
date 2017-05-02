import logging

from django.core.cache import cache
from django.core.management import BaseCommand

from openedx.core.djangoapps.catalog.models import CatalogIntegration


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """Management command used to cache program data.

    This command requests every available program from the discovery
    service, caching each in its own cache entry with an indefinite expiration.
    It is meant to be run on a scheduled basis and should be the only code
    updating these cache entries.
    """
    help = 'Backpopulate missing program credentials.'

    def add_arguments(self, parser):
        parser.add_argument(
            '-c', '--commit',
            action='store_true',
            dest='commit',
            default=False,
            help='Write data to Memcached.'
        )

    def handle(self, *args, **options):
        logger.info('Loading programs from the catalog.')
