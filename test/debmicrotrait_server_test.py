# -*- coding: utf-8 -*-
import os
import time
import unittest
import subprocess
import re
import tarfile
import logging
import uuid
from configparser import ConfigParser

from debmicrotrait.impl.config import *
from debmicrotrait.debmicrotraitImpl import debmicrotrait
from debmicrotrait.debmicrotraitServer import MethodContext
from debmicrotrait.authclient import KBaseAuth as _KBaseAuth

from installed_clients.WorkspaceClient import Workspace
from installed_clients.DataFileUtilClient import DataFileUtil
from installed_clients.AssemblyUtilClient import AssemblyUtil


WORK_DIR = '/kb/module/work/tmp'

def get_test_dir(name='test_dir_'):
    # uuid is universally unique identifier
    test_dir = os.path.join(WORK_DIR, name + str(uuid.uuid4()))
    os.mkdir(test_dir)
    return test_dir

def get_cfg():
    config_file = os.environ.get('KB_DEPLOYMENT_CONFIG', None)
    cfg = {}
    config = ConfigParser()
    config.read(config_file)
    for nameval in config.items('kb_dRep'):
        cfg[nameval[0]] = nameval[1]
    return cfg

def get_dfu():
    dfu = DataFileUtil(os.environ['SDK_CALLBACK_URL'])
    return dfu

def get_assembly_util():
    assembly_util = AssemblyUtil(os.environ['SDK_CALLBACK_URL'])
    return assembly_util

def get_ws_client():
    cfg = get_cfg()
    wsClient = Workspace(cfg['workspace-url'])
    return wsClient

class debmicrotraitTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        token = os.environ.get('KB_AUTH_TOKEN', None)
        config_file = os.environ.get('KB_DEPLOYMENT_CONFIG', None)
        cls.cfg = {}
        config = ConfigParser()
        config.read(config_file)
        for nameval in config.items('debmicrotrait'):
            cls.cfg[nameval[0]] = nameval[1]
        # Getting username from Auth profile for token
        authServiceUrl = cls.cfg['auth-service-url']
        auth_client = _KBaseAuth(authServiceUrl)
        user_id = auth_client.get_user(token)
        # WARNING: don't call any logging methods on the context object,
        # it'll result in a NoneType error
        cls.ctx = MethodContext(None)
        cls.ctx.update({'token': token,
                        'user_id': user_id,
                        'provenance': [
                            {'service': 'debmicrotrait',
                             'method': 'please_never_use_it_in_production',
                             'method_params': []
                             }],
                        'authenticated': 1})
        cls.wsURL = cls.cfg['workspace-url']
        cls.wsClient = Workspace(cls.wsURL)
        cls.serviceImpl = debmicrotrait(cls.cfg)
        cls.scratch = cls.cfg['scratch']
        cls.testData_dir = '/kb/module/test/data'
        cls.callback_url = os.environ['SDK_CALLBACK_URL']
        suffix = int(time.time() * 1000)
        cls.wsName = "test_ContigFilter_" + str(suffix)
        ret = cls.wsClient.create_workspace({'workspace': cls.wsName})  # noqa

    @classmethod
    def tearDownClass(cls):
        if hasattr(cls, 'wsName'):
            cls.wsClient.delete_workspace({'workspace': cls.wsName})
            print('Test workspace was deleted')

    # NOTE: According to Python unittest naming rules test method names should start from 'test'. # noqa
    def test_your_method(self):
        # Prepare test objects in workspace if needed using
        # self.getWsClient().save_objects({'workspace': self.getWsName(),
        #                                  'objects': []})
        #
        # Run your method by
        # ret = self.getImpl().your_method(self.getContext(), parameters...)
        #
        # Check returned data with
        # self.assertEqual(ret[...], ...) or other unittest methods
        #ref = "79/16/1"
        #ref = "72942/39/1" # assembly
        #ref = "72942/85/1" # genome, and corresponds to 72942/39/1
        #ref = "72942/212/1"  # assembly set 39
        #ref = "72942/208/1"   # genome set 39
        ref = "72942/214/1" # assembly set 4
        #ref = "72942/216/1" # genome set 4
        # need self.callbackURL or SDK_CALLBACK_URL from the environment
        #assembly_util = get_assembly_util()
        #result = assembly_util.get_assembly_as_fasta({'ref': params['assembly_ref']})
        # input to get_assembly_as_fasta is a dict with keys "ref", and "file" (optional)
        #result = assembly_util.get_assembly_as_fasta(
        #    dict(ref = ref,
        #         filename = file_safe_ref(ref) + TRANSFORM_NAME_SEP)
        #)
        #filepath = result['path']
        #print("-----filepath:", filepath, "-----\n")
        #def _load(self):
        #self.assembly_fp = app.au.get_assembly_as_fasta(
        #    dict(
        #        ref=self.ref,
        #        # def file_safe_ref(ref): return ref.replace('/', '.').replace(';', '_')
        #        # file_safe_ref(self.ref) + TRANSFORM_NAME_SEP + self.name
        #        filename=self._get_transformed_name(),
        #    )
        #)['path']
        #def _get_transformed_name(self):
        #        return file_safe_ref(self.ref) + TRANSFORM_NAME_SEP + self.name
        #
        #assembly_util = AssemblyUtil(self.callbackURL)
        #            result = assembly_util.get_assembly_as_fasta({'ref': params['assembly_ref']})
        #            input_path = result['path']
        result = self.serviceImpl.run_debmicrotrait(self.ctx, {
            'workspace_name': self.wsName,
            'input_refs': ref,
            'variance_interguild': 70,
            'output_name': "test"
        })
        print(result)