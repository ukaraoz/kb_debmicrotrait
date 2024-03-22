import os
import shutil
import logging
import copy

from ..util.debug import dprint
from .config import app, file_safe_ref, ref_leaf, TRANSFORM_NAME_SEP

class Obj:
    def _validate_set_init_params(self, **kw):
        assert 'ref' in kw or 'ref_l' in kw
        assert not ('ref' in kw and 'ref_l' in kw)

    def _load_full(self):
        obj = app.dfu.get_objects({
            'object_refs': [self.ref]
        })

        self._check_type(obj['data'][0]['info'][2])

        self.name = obj['data'][0]['info'][1]
        self.obj = obj['data'][0]['data']

    def _load_metadata(self):
        oi = app.ws.get_object_info3({
            'objects': [{'ref': self.ref}],
            'includeMetadata': 1,
        })

        self._check_type(oi['infos'][0][2])

        self.name = oi['infos'][0][1]
        self.metadata = oi['infos'][0][10]

    def _check_type(self, type_):
        if type_.startswith('KBaseSearch.GenomeSet'):
            assert type_.startswith(self.LEGACY_TYPE)
        else:
            assert type_.startswith(self.TYPE), '%s vs %s' % (type_, self.TYPE)

    def __lt__(self, other):
        """Testing"""
        return ref_leaf(self.ref) < ref_leaf(other.ref)


class Indiv:
    def _get_transformed_name(self):
        return file_safe_ref(self.ref) + TRANSFORM_NAME_SEP + self.name


class Set:
    def _create(self, ref_l):
        self.obj = dict(
            description='microtrait results',
            items=[
                dict(ref=ref)
                for ref in ref_l
            ]
        )

    def save(self, name, workspace_id):
        """
        Called by GenomeSet and AssemblySet, and all obj refs are already rooted
        """
        info = app.dfu.save_objects({
            'id': workspace_id,
            'objects': [{
                'type': self.TYPE,
                'data': copy.deepcopy(self.obj),
                'name': name,
            }]
        })[0]

        upa_new = "%s/%s/%s" % (info[6], info[0], info[4])

        return upa_new

    @property
    def length(self):
        """Testing"""
        return len(self.obj['items'])


class Assembly(Obj, Indiv):
    TYPE = 'KBaseGenomeAnnotations.Assembly'

    # example
    ## 'assembly_fp': '/kb/module/work/tmp/72942.39.1_Acidobacteria_HE68_2556921018.assembly',
	## 'metadata': {'GC content': '0.60201',
	## 				'MD5': 'de7c455b6b2c002e6dd1191032dcfff4',
	##				'N Contigs': '83',
	##				'Size': '6679185'},
	## 'name': 'Acidobacteria_HE68_2556921018.assembly',
	## 'ref': '72942/39/1'}
    def __init__(self, ref, get_fasta=True):
        self.ref = ref # full path if from Genome, AssemblySet, or GenomeSet
        self.name = None
        self.metadata = None
        self.assembly_fp = None
        #self.in_derep = None

        super()._load_metadata()
        if get_fasta: self._load()

    def _load(self):
    	# here the assembly object is converted into fasta, and the path is returned
    	# and stored in this object
        self.assembly_fp = app.au.get_assembly_as_fasta(
            dict(
                ref=self.ref,
                filename=self._get_transformed_name(),
            )
        )['path']

    def pool_into(self, pooled_dir):
        dst_fp = os.path.join(
            pooled_dir,
            os.path.basename(self.assembly_fp)
        )

        if os.path.exists(dst_fp):
            raise Exception('%s, %s' % (self.ref, self.name))

        shutil.copyfile(
            self.assembly_fp,
            dst_fp,
        )

    #def identify_dereplicated(self, derep_l):
    #    self.in_derep = self._get_transformed_name() in derep_l

    #def get_in_derep(self):
    #    if self.in_derep is None: raise Exception('%s, %s' % (self.ref, self.name))
    #    return self.in_derep

    #def get_derep_assembly_refs(self):
    #    return [self.ref] if self.get_in_derep() else []

    #def get_derep_member_refs(self):
    #    return self.get_derep_assembly_refs()

class Genome(Obj, Indiv):
    TYPE = 'KBaseGenomes.Genome'

    # example
    ## 'assembly': Assembly object
    ## 'name': Acidobacteria_HE68_2556921018.genome
    ## 'obj': long list of stuff from the genome, annotations etc.
    ## 'pool_into': bound method Genome.pool_into of <ukaraozContigFilter.impl.kb_obj.Genome object at 0x400b2c2da0
    ## 'ref':
    def __init__(self, ref, get_fasta=True):
        self.ref = ref # full path if from GenomeSet
        self.name = None
        self.obj = None
        self.assembly = None

        super()._load_full()
        self._load(get_fasta)

    def _load(self, get_fasta):
    	# from Genome object, the assembly is pulled and saved as an assembly
        self.assembly = Assembly(self.ref + ';' + self.obj['assembly_ref'], get_fasta)

    def pool_into(self, pooled_dir):
        self.assembly.pool_into(pooled_dir)

    #def identify_dereplicated(self, derep_l):
    #    self.assembly.identify_dereplicated(derep_l)

    #def get_derep_assembly_refs(self):
    #    return self.assembly.get_derep_assembly_refs() 

    #def get_derep_member_refs(self):
    #    return [self.ref] if self.assembly.get_in_derep() else []

class AssemblySet(Obj, Set):
    TYPE = 'KBaseSets.AssemblySet'

    def __init__(self, get_fasta=True, **kw):
        """
        :params ref: if given, load mode
        :params ref_l: if given, create mode
        """
        self.ref = kw.get('ref') 
        self.name = None
        self.obj = None
        self.assembly_l = None

        self._validate_set_init_params(**kw)
        ref, ref_l = kw.get('ref'), kw.get('ref_l')

        if ref is not None:
            super()._load_full()
            self._load(get_fasta)

        elif ref_l is not None:
            self._create(ref_l)

    def _load(self, get_fasta):
        assembly_ref_l = [
            d['ref']
            for d in self.obj['items']
        ]

        self.assembly_l = [
            Assembly(self.ref + ';' + ref, get_fasta)
            for ref in assembly_ref_l
        ]

    def pool_into(self, pooled_dir):
        for assembly in self.assembly_l:
            assembly.pool_into(pooled_dir)

    #def identify_dereplicated(self, derep_l):
    #    for assembly in self.assembly_l:
    #        assembly.identify_dereplicated(derep_l)

    #def get_derep_assembly_refs(self):
    #    return [a.ref for a in self.assembly_l if a.get_in_derep()]

    #def get_derep_member_refs(self):
    #    return self.get_derep_assembly_refs()


class GenomeSet(Obj, Set):
    TYPE = 'KBaseSets.GenomeSet'
    LEGACY_TYPE = 'KBaseSearch.GenomeSet'

    def __init__(self, get_fasta=True, **kw):
        """
        :params ref: if given, load mode
        :params ref_l: if given, create mode
        """
        self.ref = kw.get('ref')
        self.name = None
        self.obj = None
        self.genome_l = None

        self._validate_set_init_params(**kw)
        ref, ref_l = kw.get('ref'), kw.get('ref_l')

        if ref is not None:
            super()._load_full()
            self._load(get_fasta)

        elif ref_l is not None:
            self._create(ref_l)

    def _detect_type(self):
        if 'items' in self.obj:
            return self.TYPE
        elif 'elements' in self.obj:
            return self.LEGACY_TYPE
        else:
            raise Exception()

    def _load(self, get_fasta):
        if self._detect_type() == self.TYPE:
            genome_ref_l = [
                el['ref']
                for el in self.obj['items']
            ]
        elif self._detect_type() == self.LEGACY_TYPE:
            for el in self.obj['elements'].values():
                if 'data' in el and el['data'] is not None:
                    raise NotImplementedError('Embedded Genome in GenomeSet not supported')

            genome_ref_l = [
                el['ref']
                for el in self.obj['elements'].values()
            ]

        self.genome_l = []
        for ref in genome_ref_l:
            self.genome_l.append(
                Genome(self.ref + ';' + ref, get_fasta)
            )

    def pool_into(self, pooled_dir):
        for g in self.genome_l:
            g.pool_into(pooled_dir)

    #def identify_dereplicated(self, derep_l):
    #    for g in self.genome_l:
    #        g.identify_dereplicated(derep_l)

    #def get_derep_member_refs(self):
    #    return [g.ref for g in self.genome_l if g.assembly.get_in_derep()]

    #def get_derep_assembly_refs(self):
    #    return [g.assembly.ref for g in self.genome_l if g.assembly.get_in_derep()]
 
