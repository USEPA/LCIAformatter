"""Test generation of all available methods including as json."""

import pytest
import lciafmt

skip_list = ['ImpactWorld'] # requires pyodbc

@pytest.mark.generate_methods
def test_generate_methods():
    error_list = []
    for method_id in lciafmt.supported_methods():
        m = lciafmt.util.check_as_class(method_id.get('id'))
        if m.name in skip_list: continue
        df = None
        df = lciafmt.get_mapped_method(m)
        if df is None:
            error_list.append(m.name)
            continue
        lciafmt.util.save_json(m, df, df['Method'].unique()[0])
        
    assert not error_list

if __name__ == "__main__":
    test_generate_methods()