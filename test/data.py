from unittest.mock import create_autospec
import os
from pathlib import Path
import sys
import shutil
import logging
import json
import pathlib
import uuid

from installed_clients.DataFileUtilClient import DataFileUtil
from installed_clients.KBaseReportClient import KBaseReport
from installed_clients.AssemblyUtilClient import AssemblyUtil
from installed_clients.MetagenomeUtilsClient import MetagenomeUtils
from installed_clients.WorkspaceClient import Workspace

# these are the W/O/V,
#where W is the numeric workspace ID, O is the numeric object ID, and V is the object version
Acidobacteria_HE68_2556921018_assembly =	'72942/39/1'
Bacillus_HB09_2522572150_assembly =	'72942/58/1'
Blastococcus_HD36_2561511235_assembly =	'72942/3/1'
Bradyrhizobium_HA02_2522572128_assembly =	'72942/62/1'
Bradyrhizobium_HA13_2546825533_assembly =	'72942/43/1'
Bradyrhizobium_HD69_2561511129_assembly =	'72942/5/1'
Burkholderia_HA54_2522572104_assembly =	'72942/61/1'
Caulobacter_HA33_2522572103_assembly =	'72942/63/1'
Cellulomonas_HD24_2522572149_assembly =	'72942/57/1'
Cellulomonas_HE23_2556921112_assembly =	'72942/24/1'
Comamonadaceae_HA28_2523231025_assembly =	'72942/46/1'
Dongia_HE60_2556921676_assembly =	'72942/22/1'
Flavobacterium_HB58_2522572102_assembly =	'72942/65/1'
Geodermatophilaceae_HA31_2556921099_assembly =	'72942/25/1'
Geodermatophilaceae_HB48_2562617054_assembly =	'72942/2/1'
Geodermatophilaceae_HB62_2556921017_assembly =	'72942/40/1'
Intrasporangiaceae_HB13_2558309151_assembly =	'72942/23/1'
Lysobacter_HA19_2523231029_assembly =	'72942/44/1'
Marmoricola_HB36_2523231010_assembly =	'72942/59/1'
Mesorhizobium_HA56_2522572099_assembly =	'72942/76/1'
Mesorhizobium_HB07_2558860968_assembly =	'72942/6/1'
Mesorhizobium_HC08_2556921042_assembly =	'72942/31/1'
Microbacterium_HA36_2522572100_assembly =	'72942/77/1'
Micromonosporaceae_HE70_2558860141_assembly =	'72942/8/1'
Mycobacterium_HB44_2556921043_assembly =	'72942/28/1'
Mycobacterium_HD25_2522572101_assembly =	'72942/66/1'
Nocardioides_HA20_2558860971_assembly =	'72942/4/1'
Nocardioides_HA32_2558860165_assembly =	'72942/7/1'
Paenibacillus_HA14_2556921041_assembly =	'72942/38/1'
Pseudomonas_HB15_2556921040_assembly =	'72942/37/1'
Rhodospirillales_HD17_2590828823_assembly =	'72942/9/1'
Rhodospirillales_HD88_2546825534_assembly =	'72942/45/1'
Solirubrobacter_HD82_2522572155_assembly =	'72942/60/1'
Solirubrobacterales_HD59_2558860160_assembly =	'72942/11/1'
Sphingomonas_HD07_2523231013_assembly =	'72942/55/1'
Sphingomonas_HD57_2556921109_assembly =	'72942/26/1'
Staphylococcus_HA57_2556921095_assembly =	'72942/27/1'
Streptomyces_HA41_2561511090_assembly =	'72942/10/1'
Variovorax_HB20_2556921005_assembly =	'72942/42/1'

Acidobacteria_HE68_2556921018_genome =	'72942/85/1'
Bacillus_HB09_2522572150_genome =	'72942/84/1'
Blastococcus_HD36_2561511235_genome =	'72942/86/1'
Bradyrhizobium_HA02_2522572128_genome =	'72942/87/1'
Bradyrhizobium_HA13_2546825533_genome =	'72942/92/1'
Bradyrhizobium_HD69_2561511129_genome =	'72942/95/1'
Burkholderia_HA54_2522572104_genome =	'72942/98/1'
Caulobacter_HA33_2522572103_genome =	'72942/102/1'
Cellulomonas_HD24_2522572149_genome =	'72942/105/1'
Cellulomonas_HE23_2556921112_genome =	'72942/106/1'
Comamonadaceae_HA28_2523231025_genome =	'72942/113/1'
Dongia_HE60_2556921676_genome =	'72942/112/1'
Flavobacterium_HB58_2522572102_genome =	'72942/117/1'
Geodermatophilaceae_HA31_2556921099_genome =	'72942/119/1'
Geodermatophilaceae_HB48_2562617054_genome =	'72942/121/1'
Geodermatophilaceae_HB62_2556921017_genome =	'72942/128/1'
Intrasporangiaceae_HB13_2558309151_genome =	'72942/129/1'
Lysobacter_HA19_2523231029_genome =	'72942/130/1'
Marmoricola_HB36_2523231010_genome =	'72942/159/1'
Mesorhizobium_HA56_2522572099_genome =	'72942/138/1'
Mesorhizobium_HB07_2558860968_genome =	'72942/138/1'
Mesorhizobium_HC08_2556921042_genome =	'72942/197/1'
Microbacterium_HA36_2522572100_genome =	'72942/142/1'
Micromonosporaceae_HE70_2558860141_genome =	'72942/206/1'
Mycobacterium_HB44_2556921043_genome =	'72942/150/1'
Mycobacterium_HD25_2522572101_genome =	'72942/202/1'
Nocardioides_HA20_2558860971_genome =	'72942/155/1'
Nocardioides_HA32_2558860165_genome =	'72942/163/1'
Paenibacillus_HA14_2556921041_genome =	'72942/165/1'
Pseudomonas_HB15_2556921040_genome =	'72942/170/1'
Rhodospirillales_HD17_2590828823_genome =	'72942/169/1'
Rhodospirillales_HD88_2546825534_genome =	'72942/173/1'
Solirubrobacter_HD82_2522572155_genome =	'72942/175/1'
Solirubrobacterales_HD59_2558860160_genome =	'72942/201/1'
Sphingomonas_HD07_2523231013_genome =	'72942/185/1'
Sphingomonas_HD57_2556921109_genome =	'72942/181/1'
Staphylococcus_HA57_2556921095_genome =	'72942/188/1'
Streptomyces_HA41_2561511090_genome =	'72942/190/1'
Variovorax_HB20_2556921005_genome =	'72942/192/1'

rhizosphere_isolate_assemblyset= '72942/212/1'
rhizosphere_4isolate_assemblyset = '72942/214/1'
rhizosphere_isolate_genomeset = '72942/208/1'
rhizosphere_4isolate_genomeset = '72942/216/1'

TEST_DATA_DIR = '/kb/module/test/data'
GET_OBJECTS_DIR = TEST_DATA_DIR + '/get_objects'
GET_OBJECT_INFO3_DIR = TEST_DATA_DIR + '/get_object_info3'
FASTA_DIR = TEST_DATA_DIR + '/fasta'
WORK_DIR = '/kb/module/work/tmp'
CACHE_DIR = WORK_DIR + '/cache_test_data'

def mock_au_get_assembly_as_fasta(params):
    logging.info('Mocking au.get_assembly_as_fasta(%s)' % str(params))

    upa = ref_leaf(params['ref'])
    work_fn = params['filename']

    save_fp = _glob_upa(FASTA_DIR, upa)

    # Download and cache
    if save_fp is None:
        logging.info('Calling in cache mode `au.get_assembly_as_fasta`')

        au = get_au()
        work_fp = au.get_assembly_as_fasta(params)['path']
        save_fp = os.path.join(
            mkcache(FASTA_DIR),
            file_safe_ref(upa) + '.fa'
        )
        shutil.copyfile(work_fp, save_fp)

    # Pull from cache
    else:
        work_fp = _house_mock_in_work_dir(save_fp, work_fn)

    return {'path': work_fp}