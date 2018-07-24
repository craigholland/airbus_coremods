from dbquery import main


routes = [
    ('model_build', '/dbquery/build/', main.Build),
    ('model_list', '/dbquery/list/', main.List),
    ('model_exists', '/dbquery/exists/{mod}', main.ModelExist)
]