from API_registry import main as API

routes = [
    ('apireg_listall', '/apireg/listall/', API.Listall),
    ('apireg_list', '/apireg/list/{mod}', API.List),
    ('apireg_offline', '/apireg/offline/{mod}', API.HostOffline),
    ('apireg_regserv', '/apireg/regsrv/{mod}', API.RegisterService),
    ('apireg_listregsrv', '/apireg/listregsrc', API.getRegServicesList)


]