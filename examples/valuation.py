import lciafmt
from lciafmt.util import store_method

def main():

    methods = lciafmt.generate_endpoints('Weidema_valuation', name = 'Weidema Valuation',
                                        matching_fields=['Indicator unit'])
    # matching_fields = ['Indicator unit'] is used to avoid listing all 
    # indicators separately in source data file
    
    store_method(methods, method_id = None)

if __name__ == "__main__":
    main()
