import json
import logging
from decimal import Decimal

from cove.views import cove_web_input_error, explore_data_context
from django.shortcuts import render
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from libcove.lib.converters import convert_spreadsheet
from libcoveoc4ids.common_checks import common_checks_oc4ids
from libcoveoc4ids.config import LibCoveOC4IDSConfig
from libcoveoc4ids.schema import SchemaOC4IDS

from cove_project import settings

logger = logging.getLogger(__name__)


@cove_web_input_error
def explore_oc4ids(request, pk):
    context, db_data, error = explore_data_context(request, pk)
    if error:
        return error

    lib_cove_oc4ids_config = LibCoveOC4IDSConfig(config=settings.COVE_CONFIG)

    upload_dir = db_data.upload_dir()
    upload_url = db_data.upload_url()
    file_name = db_data.original_file.file.name
    file_type = context['file_type']

    if file_type == 'json':
        # open the data first so we can inspect for record package
        with open(file_name, encoding='utf-8') as fp:
            try:
                json_data = json.load(fp, parse_float=Decimal)
            except ValueError as err:
                context = {
                    'sub_title': _("Sorry, we can't process that data"),
                    'link': 'index',
                    'link_text': _('Try Again'),
                    'msg': format_html(_('We think you tried to upload a JSON file, but it is not well formed JSON.'
                                         '\n\n<span class="glyphicon glyphicon-exclamation-sign" aria-hidden="true">'
                                         '</span> <strong>Error message:</strong> {}'), err),
                    'error': format(err)
                }
                return render(request, 'error.html', context=context)

            if not isinstance(json_data, dict):
                context = {
                    'sub_title': _("Sorry, we can't process that data"),
                    'link': 'index',
                    'link_text': _('Try Again'),
                    'msg': _('OC4IDS JSON should have an object as the top level, the JSON you supplied does not.'),
                }
                return render(request, 'error.html', context=context)

        schema_oc4ids = SchemaOC4IDS(lib_cove_oc4ids_config=lib_cove_oc4ids_config)

        # Flatten Tool has catastrophically bad performance on even a 50 MB file (uses 3 GB). In the last 14 days as of
        # 2020-10-06, `flattened.xlsx` has been requested only once. As such, this feature is disabled.
        # context.update(convert_json(upload_dir, upload_url, file_name, lib_cove_oc4ids_config,
        #                             schema_url=schema_oc4ids.schema_url, replace=True,
        #                             request=request, flatten=True))
    else:
        schema_oc4ids = SchemaOC4IDS(lib_cove_oc4ids_config=lib_cove_oc4ids_config)
        context.update(convert_spreadsheet(
                upload_dir, upload_url,
                file_name, file_type,
                lib_cove_oc4ids_config,
                schema_url=schema_oc4ids.schema_url,
                pkg_schema_url=schema_oc4ids.pkg_schema_url))

        with open(context['converted_path'], encoding='utf-8') as fp:
            json_data = json.load(fp, parse_float=Decimal)

    context = common_checks_oc4ids(context, upload_dir, json_data,
                                   schema_oc4ids, lib_cove_oc4ids_config)

    if not db_data.rendered:
        db_data.rendered = True
    db_data.save()

    template = 'cove_oc4ids/explore.html'

    return render(request, template, context)
