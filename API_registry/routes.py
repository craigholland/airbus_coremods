from API_registry import main as API

routes = [
    ('apireg_listall', '/apireg/listall/', API.Listall),
    ('apireg_list', '/apireg/list/', API.List),
    ('apireg_update', '/apireg/list/', API.Update),

]