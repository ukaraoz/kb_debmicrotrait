# -*- coding: utf-8 -*-
#BEGIN_HEADER
import logging
import os
import sys
import shutil
import subprocess
import uuid
import re
import functools
import pprint

from installed_clients.KBaseReportClient import KBaseReport
from installed_clients.DataFileUtilClient import DataFileUtil
from installed_clients.WorkspaceClient import Workspace
from installed_clients.AssemblyUtilClient import AssemblyUtil

from .impl.kb_obj import Assembly, Genome, AssemblySet, GenomeSet
from .util.debug import dprint
from .util.microtrait import get_microtrait_datatables
from .impl.config import app, reset_globals
from .impl.params import Params
from .impl import report
from .impl import report_deb
#END_HEADER


class debmicrotrait:
    '''
    Module Name:
    debmicrotrait

    Module Description:
    A KBase module: debmicrotrait
    '''

    ######## WARNING FOR GEVENT USERS ####### noqa
    # Since asynchronous IO can lead to methods - even the same method -
    # interrupting each other, you must be *very* careful when using global
    # state. A method could easily clobber the state set by another while
    # the latter method is running.
    ######################################### noqa
    VERSION = "0.0.1"
    GIT_URL = "https://github.com/ukaraoz/kb_debmicrotrait.git"
    GIT_COMMIT_HASH = "e86d91dc48c4f582afab0ee6e79b1a3291cdd1af"

    #BEGIN_CLASS_HEADER
    #END_CLASS_HEADER

    # config contains contents of config file in a hash or None if it couldn't
    # be found
    def __init__(self, config):
        #BEGIN_CONSTRUCTOR
        #self.callback_url = os.environ['SDK_CALLBACK_URL']
        callback_url = os.environ['SDK_CALLBACK_URL']
        #self.shared_folder = config['scratch']
        shared_folder = config['scratch']
        workspace_url = config['workspace-url']
        
        reset_globals()
        app.update({ 
            'shared_folder': config['scratch'], 
            'ws': Workspace(workspace_url),
            'dfu': DataFileUtil(callback_url),
            'au': AssemblyUtil(callback_url),
            'kbr': KBaseReport(callback_url),
        })
        logging.basicConfig(format='%(created)s %(levelname)s: %(message)s',
                            level=logging.INFO)
        #END_CONSTRUCTOR
        pass


    def run_debmicrotrait(self, ctx, params):
        """
        This example function accepts any number of parameters and returns results in a KBaseReport
        :param params: instance of mapping from String to unspecified object
        :returns: instance of type "ReportResults" -> structure: parameter
           "report_name" of String, parameter "report_ref" of String
        """
        # ctx is the context object
        # return variables are: output
        #BEGIN run_debmicrotrait
        # params hold
        # 'input_refs': '72942/39/1'
        # 'output_name': 'test'
        # 'variance_interguild': 70
        # 'workspace_name': 'test_ContigFilter_1710549679759'
        # 'workspace_id'

        logging.info(params)
        params = Params(params)
        #pprint.pprint(params)
        #
        app.update({
            'run_dir': os.path.join(app.shared_folder, 'run_microtrait_' + str(uuid.uuid4())), # folder dedicated to this API-method run
            'params': params,
        })
        os.mkdir(app.run_dir)
       
        #
        ##
        ### directories
        ####
        #####

        microtrait_dir = os.path.join(app.run_dir, 'microtrait_dir')
        report_dir = os.path.join(app.run_dir, 'report')
        app.update(
            dict(
                microtrait_dir=microtrait_dir,
                report_dir=report_dir,
            )
        )
        

        #
        ##
        ### load files, obj
        ####
        #####
        #### REMEMBER: obj_refs is input_refs
        ##### get_object_info3 returns:
        # list<object_info> 'infos' - the object_info data for each object.
        ## https://kbase.us/services/ws/docs/Workspace.html#typedefWorkspace.object_info
        # list<list<obj_ref> 'paths' - the path to the object through the object reference graph for
        #   *each object. All the references in the path are absolute.
        # list<ObjectInfo> 'infostructs' - the ObjectInfo data for each object.
        #objs = load_objs(params['obj_refs'])
        ## example
        ## {'infos': [[39,
        ##             'Acidobacteria_HE68_2556921018.assembly',
        ##             'KBaseGenomeAnnotations.Assembly-3.1',
        ##             '2024-03-12T18:43:59+0000',
        ##             1,
        ##             'ukaraoz',
        ##             72942,
        ##             'ukaraoz:narrative_1710267103479',
        ##             '33a893c48e7b62f5f311d99e40702d1f',
        ##             22859,
        ##             None]],
        ## 'paths': [['72942/39/1']]}

        objs = []
        ref = params['input_refs']
        type_ = app.ws.get_object_info3({
            'objects': [{'ref': ref}]
        })['infos'][0][2]

        if type_.startswith(Assembly.TYPE):
            obj = Assembly(ref)
        elif type_.startswith(Genome.TYPE):
            obj = Genome(ref)
        elif type_.startswith(AssemblySet.TYPE):
            obj = AssemblySet(ref=ref)
        elif type_.startswith(GenomeSet.TYPE) or type_.startswith(GenomeSet.LEGACY_TYPE):
            obj = GenomeSet(ref=ref)
        else:
            raise Exception(type_)
        objs.append(obj)
        #
        ##
        ### pool
        ####
        #####
        pooled_fasta_dir = os.path.join(app.run_dir, 'pooled_fasta')
        os.mkdir(pooled_fasta_dir)

        for obj in objs:
            obj.pool_into(pooled_fasta_dir)
        pooled_fasta_fn_l = os.listdir(pooled_fasta_dir)
        pooled_fasta_fp_l = [os.path.join(pooled_fasta_dir, fn) for fn in os.listdir(pooled_fasta_dir)]
        pooled_fasta_pathsfile = os.path.join(pooled_fasta_dir, "pooled_fasta_pathsfile.txt")
        with open(pooled_fasta_pathsfile, mode='wt', encoding='utf-8') as pathsfile:
            pathsfile.write('\n'.join(pooled_fasta_fp_l))

        #pp.pprint(dir(obj))
        #pp.pprint(obj.ref)
        #pprint.pprint(temp)
        test_dir = "/kb/module/test/data/microtrait/rhizosphere"
        shutil.copytree(test_dir, microtrait_dir)

        test_figures_dir = os.path.join(test_dir, 'figures')
        test_datatables_dir = os.path.join(test_dir, 'datatables')
        test_microtraittemp_dir = os.path.join(test_dir, 'microtrait_out')

        test_figure_files = os.listdir(test_figures_dir)
        test_figure_files_fp = [os.path.join(test_figures_dir, fn) for fn in os.listdir(test_figures_dir)]
        #for fp in test_figure_files_fp:
        #    print(fp, end = '\n')
        #print("----------\n")
        test_datatables_files = os.listdir(test_datatables_dir)
        test_datatables_files_fp = [os.path.join(test_datatables_dir, fn) for fn in os.listdir(test_datatables_dir)]
        #for fp in test_datatables_files_fp:
        #    print(fp, end = '\n')
        #print("\n\n")
        print("microtrait_dir:", microtrait_dir, "\n\n\n\n")
        microtrait_dir_files_fp = [os.path.join(microtrait_dir, 'datatables', fn) for fn in os.listdir(os.path.join(microtrait_dir, 'datatables'))]
        for fp in microtrait_dir_files_fp:
            print("$", fp, "$", end = '\n')
        
        
        ##type_ = app.ws.get_object_info3({
        ##    'objects': [{'ref': ref}]
        ##})['infos'][0][2]
        #print("---START---", "\n")
        #pprint.pprint(temp)
        #print("---END---", "\n")
        #print("---START Print params:---", "\n")
        #pprint.pprint(params)
        #print(params['input_refs'])

        # type_ = app.ws.get_object_info3({
        #     'objects': [{'ref': ref}]
        # })['infos'][0][2]
        #elif type_.startswith(Genome.TYPE):
        #    obj = Genome(ref)


        #print("---END print params:---", "\n")

        #print("file_safe_ref", params['input_refs'].replace('/', '.').replace(';', '_'), "\n")
        #print ("input_refs: ",params['input_refs'], "\n")
        #print ("variance_interguild: ",params['variance_interguild'], "\n")
        #print ("output_name: ",params['output_name'], "\n")

        #report = KBaseReport(self.callback_url)
        #report = app.kbr


        #
        ##
        ### html
        ####
        #####
        #pprint.pprint(app)
        hb = report.HTMLBuilder(microtrait_dir, report_dir)
        report_fp = hb.write()
        #print("report_fp: ", report_fp, "\n")

        # file_links/html_links
        ## 1. shock_id: (required string) Shock ID for a file. Not required if path is present.
        ## 2. path: (required string) Full file path for a file (in scratch). Not required if shock_id is present.
        ## 3. name: (required string) name of the file
        ## 4. description: (optional string) Readable description of the file
        ## 5. template: (optional dictionary) A dictionary with keys template_file (required) and template_data_json (optional), specifying a template and accompanying data to be rendered to generate an output file.
        #output_files = get_microtrait_datatables(os.path.join(microtrait_dir, 'datatables'))
        #file_links = [value for key, value in output_files.items() 
        #    if value['path'] is not None]
        #pprint.pprint(file_links)

        file_links = [
        {
            'path': os.path.join(microtrait_dir, 'datatables', 'trait_matrixatgranularity3.txt'),
            'name': 'Microtrait trait matrix at granularity level 3 in tabular format',
            'label': 'trait_matrixatgranularity3.txt',
            'description': 'Microtrait trait matrix at granularity level 3 in tabular format'
        },
        {
            'path': os.path.join(microtrait_dir, 'datatables', 'guild2traitprofile.txt'),
            'name': 'Guild to trait profile in tabular format',
            'label': 'guild2traitprofile.txt',
            'description': 'Guild to trait profile in tabular format'
        },
        {
            'path': os.path.join(microtrait_dir, 'datatables', 'trait_matrixatgranularity2.txt'),
            'name': 'Microtrait trait matrix at granularity level 2 in tabular format',
            'label': 'trait_matrixatgranularity2.txt',
            'description': 'Microtrait trait matrix at granularity level 2 in tabular format'
        },
        {
            'path': os.path.join(microtrait_dir, 'datatables', 'trait_matrixatgranularity1.txt'),
            'name': 'Microtrait trait matrix at granularity level 1 in tabular format',
            'label': 'trait_matrixatgranularity1.txt',
            'description': 'Microtrait trait matrix at granularity level 1 in tabular format'
        },
        {
            'path': os.path.join(microtrait_dir, 'datatables', 'rule_matrix.txt'),
            'name': 'Microtrait rules output in tabular format',
            'label': 'rule_matrix.txt',
            'description': 'Microtrait rules output in tabular format'
        },
        {
            'path': os.path.join(microtrait_dir, 'datatables', 'hmm_matrix.txt'),
            'name': 'Microtrait hmm output in tabular format',
            'label': 'hmm_matrix.txt',
            'description': 'Microtrait hmm output in tabular format'
        },
        {
            'path': os.path.join(microtrait_dir, 'datatables', 'genome2guild.txt'),
            'name': 'Genome to guild table',
            'label': 'genome2guild.txt',
            'description': 'Genome to guild table'
        }]

        print("AAAAA-", os.path.basename(report_fp), "\n")
        html_links = [{
            'path': report_dir,
            'name': os.path.basename(report_fp),
        }]

        report_text = 'Ran microtrait, results are packaged below. \n\n'
        report_params = {
            # report_object_name: 
            ##  (optional string) a name to give the workspace object that stores the report.
            'report_object_name': 'kb_microtrait_report',  
            # message: 
            ##  (optional string) basic result message to show in the report
            'message': report_text,
            #  direct_html_link_index: 
            ##  (optional integer) index in html_links that you want to use as the main/default report view
            'direct_html_link_index': 0,
            #  html_links: 
            ##  (optional list of dicts) HTML files to attach and display in the report (see the additional information below)
            'html_links': html_links,        
            # file_links: 
            ##  (optional list of dicts) files to attach to the report (see the valid key/vals below)
            'file_links': file_links,         
            # workspace_id: 
            ##  (optional integer) id of your workspace. Preferred over workspace_name as it's immutable. Required if workspace_name is absent.
            #'workspace_id': params['workspace_id'],
            # workspace_name: 
            ##  (optional string) string name of your workspace. Requried if workspace_id is absent.
            'workspace_name': params['workspace_name'],
            # objects_created: 
            ##  (optional list of WorkspaceObject) data objects that were created as a result of running your app, such as assemblies or genomes
            #'objects_created': objects_created,
        }
        report_output = app.kbr.create_extended_report(report_params)

        output = {
            'report_name': report_output['name'],
            'report_ref': report_output['ref'],
            'objects_created': [],
        }
        #report_info = report.create({'report': {'objects_created':[],
        #                                        'text_message': params['input_refs']},
        #                                        'workspace_name': params['workspace_name']})
        
        #print ("report_name", output['report_name'])

        # assembly_ref = "170460/216/1"
        # genome_ref = "170460/217/1"
        #END run_debmicrotrait

        # At some point might do deeper type checking...
        if not isinstance(output, dict):
            raise ValueError('Method run_debmicrotrait return value ' +
                             'output is not type dict as required.')
        # return the results
        return [output]

    def run_deb(self, ctx, params):
        """
        :param params: instance of mapping from String to unspecified object
        :returns: instance of type "ReportResults" -> structure: parameter
           "report_name" of String, parameter "report_ref" of String
        """
        # ctx is the context object
        # return variables are: output
        #BEGIN run_deb

        logging.info(params)
        params = Params(params)

        app.update({
            'run_dir': os.path.join(app.shared_folder, 'run_deb_' + str(uuid.uuid4())), # folder dedicated to this API-method run
            'params': params,
        })
        os.mkdir(app.run_dir)

        deb_dir = os.path.join(app.run_dir, 'deb_dir')
        report_dir = os.path.join(app.run_dir, 'report')
        app.update(
            dict(
                deb_dir=deb_dir,
                report_dir=report_dir,
            )
        )

        test_dir = "/kb/module/test/data/deb/rhizosphere"
        shutil.copytree(test_dir, deb_dir)

        test_figures_dir = os.path.join(test_dir, 'figures')
        test_datatables_dir = os.path.join(test_dir, 'datatables')

        hb = report_deb.HTMLBuilder(deb_dir, report_dir)
        report_fp = hb.write()

        html_links = [{
            'path': report_dir,
            'name': os.path.basename(report_fp),
        }]

        report_text = 'Ran deb, results are packaged below. \n\n'
        report_params = {
            # report_object_name: 
            ##  (optional string) a name to give the workspace object that stores the report.
            'report_object_name': 'kb_deb_report',  
            # message: 
            ##  (optional string) basic result message to show in the report
            'message': report_text,
            #  direct_html_link_index: 
            ##  (optional integer) index in html_links that you want to use as the main/default report view
            'direct_html_link_index': 0,
            #  html_links: 
            ##  (optional list of dicts) HTML files to attach and display in the report (see the additional information below)
            'html_links': html_links,        
            # file_links: 
            ##  (optional list of dicts) files to attach to the report (see the valid key/vals below)
            'workspace_name': params['workspace_name'],
            # objects_created: 
            ##  (optional list of WorkspaceObject) data objects that were created as a result of running your app, such as assemblies or genomes
            #'objects_created': objects_created,
        }
        report_output = app.kbr.create_extended_report(report_params)

        output = {
            'report_name': report_output['name'],
            'report_ref': report_output['ref'],
            'objects_created': [],
        }
        #END run_deb

        # At some point might do deeper type checking...
        if not isinstance(output, dict):
            raise ValueError('Method run_deb return value ' +
                             'output is not type dict as required.')
        # return the results
        return [output]
    def status(self, ctx):
        #BEGIN_STATUS
        returnVal = {'state': "OK",
                     'message': "",
                     'version': self.VERSION,
                     'git_url': self.GIT_URL,
                     'git_commit_hash': self.GIT_COMMIT_HASH}
        #END_STATUS
        return [returnVal]
