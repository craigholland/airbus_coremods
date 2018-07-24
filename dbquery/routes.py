from dbquery.main import Build
from dbquery.main import List

routes = [
    ('model_build', '/dbquery/build/', Build),
    ('model_list', '/dbquery/list/', List)
]