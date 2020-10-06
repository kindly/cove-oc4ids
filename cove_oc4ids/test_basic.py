import pytest
from cove.input.models import SuppliedData
from django.core.files.base import ContentFile


@pytest.mark.django_db
@pytest.mark.parametrize('json_data', [
    # A selection of JSON strings we expect to give a 200 status code, even
    # though some of them aren't valid BODS
    'true',
    'null',
    '1',
    '{}',
    None,
])
def test_explore_page(client, json_data):
    if json_data is None:
        with open('data.json') as f:
            json_data = f.read()

    data = SuppliedData.objects.create()
    data.original_file.save('test.json', ContentFile(json_data))
    data.current_app = 'cove_oc4ids'
    resp = client.get(data.get_absolute_url())
    assert resp.status_code == 200
