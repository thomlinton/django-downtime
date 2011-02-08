from django.core.management.base import BaseCommand, CommandError
from django.template.loader import render_to_string
from django.template.context import RequestContext
from django.test.client import RequestFactory
from django.conf import settings

from optparse import make_option
import os


SOURCE_TEMPLATE = getattr(settings,'DOWNTIME_SOURCE_TEMPLATE','maintenance.html')
TARGET_TEMPLATE = getattr(settings,'DOWNTIME_TARGET_TEMPLATE','index.html')
TARGET_PATH = getattr(settings,'DOWNTIME_TARGET_PATH','/')
TARGET_ROOT = getattr(settings,'DOWNTIME_TARGET_ROOT',None)


class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('--comment', action="store", dest='comment', default='',
            help='Specify a message to be displayed on the maintenance page.'),
    )
    help = 'Generates a static HTML page from project templates for use while performing maintenance'

    def handle(self, *args, **options):
        root = TARGET_ROOT
        if not root:
            try:
                root = settings.STATIC_ROOT
            except AttributeError:
                # compatibility django < 1.3
                root = settings.MEDIA_ROOT

        path = os.path.join( root, TARGET_TEMPLATE )
        comment = options.get('comment')
        request_factory = RequestFactory()
        request = request_factory.get(TARGET_PATH)
        ctxt = RequestContext(request,{'comment':comment})
        tpl = render_to_string( \
            SOURCE_TEMPLATE,context_instance=ctxt)

        try:
            fd = open(path,'w')
            fd.write( tpl.encode('utf-8') )
            fd.close()
        except IOError, e:
            raise CommandError(str(e))
