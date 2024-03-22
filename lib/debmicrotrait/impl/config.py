from dotmap import DotMap

config = dict(
    debug=True,
)

app = DotMap(config) # global

def reset_globals():
    app.clear()
    app.update(config)

def ref_leaf(ref):
    return ref.split(';')[-1]

def file_safe_ref(ref):
    return ref.replace('/', '.').replace(';', '_')

TRANSFORM_NAME_SEP = '_' # separate UPA, object names, bin name