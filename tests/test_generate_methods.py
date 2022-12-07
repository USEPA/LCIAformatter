"""Test generation of all available methods including as json."""

import pytest
import lciafmt
from lciafmt.util import store_method

skip_list = ['ImpactWorld'] # requires pyodbc

@pytest.mark.generate_methods
def test_generate_methods():
    error_list = []
    for method_id in lciafmt.supported_methods():
        m = lciafmt.util.check_as_class(method_id.get('id'))
        if m.name in skip_list: continue
        df = None
        df = lciafmt.get_mapped_method(m)
        lciafmt.util.compare_to_remote(df, m)
        if df is None:
            error_list.append(m.name)
            continue
        lciafmt.util.save_json(m, df, df['Method'].unique()[0])
        
    assert not error_list


def test_endpoint_method():
    method = lciafmt.generate_endpoints('Weidema_valuation',
                                        name='Weidema Valuation',
                                        matching_fields=['Indicator unit'])
    store_method(method, method_id=None)
    assert method is not None

if __name__ == "__main__":
    test_generate_methods()
