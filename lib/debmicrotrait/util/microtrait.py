import os

def get_microtrait_datatables(datatables_dir, output_files=None):
    if output_files is None:
        output_files = dict()
    hmm_matrix_loc = os.path.join(datatables_dir, 'rhizosphere.hmm_matrix.txt')
    output_files['hmm_matrix'] = {'path': hmm_matrix_loc,
                                   'name': 'hmm_matrix.txt',
                                   'label': 'hmm_matrix.txt',
                                   'description': 'Microtrait hmm output in tabular format'}
    rule_matrix_loc = os.path.join(datatables_dir, 'rhizosphere.rule_matrix.txt')
    output_files['rule_matrix'] = {'path': rule_matrix_loc,
                                   'name': 'rule_matrix.txt',
                                   'label': 'rule_matrix.txt',
                                   'description': 'Microtrait rules output in tabular format'}
    trait_matrixatgranularity1_loc = os.path.join(datatables_dir, 'rhizosphere.trait_matrixatgranularity1.txt')
    output_files['trait_matrixatgranularity1'] = {'path': trait_matrixatgranularity1_loc,
                                   'name': 'trait_matrixatgranularity1.txt',
                                   'label': 'trait_matrixatgranularity1.txt',
                                   'description': 'Microtrait trait matrix at granularity level 1 in tabular format'}
    trait_matrixatgranularity2_loc = os.path.join(datatables_dir, 'rhizosphere.trait_matrixatgranularity2.txt')
    output_files['trait_matrixatgranularity2'] = {'path': trait_matrixatgranularity2_loc,
                                   'name': 'trait_matrixatgranularity2.txt',
                                   'label': 'trait_matrixatgranularity2.txt',
                                   'description': 'Microtrait trait matrix at granularity level 2 in tabular format'}
    trait_matrixatgranularity3_loc = os.path.join(datatables_dir, 'rhizosphere.trait_matrixatgranularity3.txt')
    output_files['trait_matrixatgranularity3'] = {'path': trait_matrixatgranularity3_loc,
                                   'name': 'trait_matrixatgranularity3.txt',
                                   'label': 'trait_matrixatgranularity3.txt',
                                   'description': 'Microtrait trait matrix at granularity level 3 in tabular format'}
    guild2traitprofile_loc = os.path.join(datatables_dir, 'rhizosphere.guild2traitprofile.txt')
    output_files['guild2traitprofile'] = {'path': guild2traitprofile_loc,
                                   'name': 'guild2traitprofile.txt',
                                   'label': 'guild2traitprofile.txt',
                                   'description': 'Guild to trait profile in tabular format'}
    
    return output_files