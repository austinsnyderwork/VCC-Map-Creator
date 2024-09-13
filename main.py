from interfacing import interface

vcc_file_name = "/vcc_joined_data.csv"

interface_ = interface.Interface()
interface_.import_data(vcc_file_name=vcc_file_name,
                       variables={'specialty': ['Pediatric Cardiology']})
interface_.create_maps()


