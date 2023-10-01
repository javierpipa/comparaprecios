import os, sys
PWD = os.getenv('PWD')

PROJ_MISSING_MSG = """Set an enviroment variable:\n
`DJANGO_PROJECT=your_project_name`\n
or call:\n
`init_django(your_project_name)`
"""
print(PWD)
def init_django(project_name='myproject'):
    # os.chdir(PWD)
    os.chdir('/home/javier/hd1/Codigo/JAVIER/test1/comparaprecios-1')
    project_name = project_name or os.environ.get('DJANGO_PROJECT') or None
    if project_name == None:
        raise Exception(PROJ_MISSING_MSG)
    sys.path.insert(0, os.getenv('PWD'))
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', f'{project_name}.settings')
    os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", f'{project_name}.settings')
    import django
    django.setup()