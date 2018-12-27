import pytest
from elasticsearch_collectd_utils import remove_deprecated_elements


@pytest.mark.parametrize("deprecated_elements, input_elements, version, expected_elements", [
    (
            [{'major': 1, 'minor': 3, 'revision': 100, 'keys': ['element1', 'element3']}],
            ['element2', 'element3'],
            '1.03.00104',
            ['element2']
    )
])
def test_remove_deprecated_elements(deprecated_elements, input_elements, version, expected_elements):
    print deprecated_elements, input_elements, version, expected_elements
    elements = remove_deprecated_elements(deprecated_elements, input_elements, version)
    assert len(elements) == len(expected_elements)
    for i in range(len(elements)):
        assert elements[i] == expected_elements[i]
