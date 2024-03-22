import json


class Params:
    # note: ignoring/skipping steps and warnings are not enabled from the app cell UI
    # but still supported here.

    #*#TOOL_DEFAULTS = {
    #*#    'length': 50000,
    #*#    'processors': 6,
    #*#}

    #*#DEFAULTS = {
    #*#    **TOOL_DEFAULTS,
    #*#    'output_name': 'dRep',
    
    #*#FLAGS = ['ignoreGenomeQuality', 'SkipMash', 'SkipSecondary', 'output_as_assembly']

    #*#PARAM_GROUPS = [
    #*#    'filtering',
    #*#    'genome_comparison',
    #*#    'clustering',
    #*#    'scoring',
    #*#    'warnings',
    #*#]

    #### REMEMBER: obj_refs is input_refs
    REQUIRED = [
        'input_refs',
        'workspace_name',
        'workspace_id',
    ]

    #*#ALL = REQUIRED + list(DEFAULTS.keys()) + PARAM_GROUPS

    def __init__(self, params):
        self._validate(params)
        params = self.flatten(params)

        # internal transformations
        #*#for f in self.FLAGS:
        #*#    if f in params:
        #*#        params[f] = bool(params[f])

        self.params = params

    #*# in this app, 'input_refs' is the name for the refs, not 'obj_refs'
    def _validate(self, params):
        if len(params['input_refs']) == 0:
            raise Exception('No input objects')
        #if len(set(params['input_refs'])) < len(params['input_refs']):
        #    raise Exception('Duplicate input objects')

        #for k, v in params.items():
        #    if k not in self.ALL:
        #        raise Exception(k)

    #*#def get_non_default_tool_params(self):
    #*#    pl = []
    #*#    for k, vd in self.TOOL_DEFAULTS.items():
    #*#        if k in self.params and self.params[k] != vd:
    #*#            pl.append('--' + k)
    #*#            if k not in self.FLAGS:
    #*#                pl.append(str(self.params[k]))
    #*#    return pl

    def __getitem__(self, key):
        """
        For required params (e.g., input UPAs, workspace stuff)
        """
        if key not in self.REQUIRED:
            raise Exception(key)
        return self.params[key]

    #*#def getd(self, key):
    #*#    """
    #*#    For default-backed params (e.g., tunable numbers)
    #*#    Return the user-supplied value, or the default value if none was supplied
    #*#    """
    #*#    if key not in self.DEFAULTS:
    #*#        raise Exception(key)
    #*#    return self.params.get(key, self.DEFAULTS[key])

    def __repr__(self) -> str:
        return 'params wrapper:\n%s' % (json.dumps(self.params, indent=4))

    @staticmethod
    def flatten(d):
        """At most 1 level nesting"""
        d1 = d.copy()
        for k, v in d.items():
            if isinstance(v, dict):
                for k1, v1 in d1.pop(k).items():
                    d1[k1] = v1
        return d1
