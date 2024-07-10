import os

import conllu
# from consts import *
import utils
from copy import deepcopy
from collections import defaultdict

from swe_relations import case_feat_map, marker_feat_map, conjtype_feat_map

VERBAL = {'VERB'}
NOMINAL = {'NOUN', 'PROPN', 'PRON', 'NUM'}

clausal_rels = {'conj','csubj','xcomp','ccomp','advcl','acl','advcl:relcl','acl:relcl'}

def combine_fixed_nodes(head, fixed_children):
    '''
    In cases where several function words are combined to one meaning (e.g., because of, more then) they are tagged with
     a 'fixed' deprel and are combined to one temporary lemma to look for in the relevant map in 'eng_relations.py'.
    '''
    if not fixed_children:
        return head['lemma']

    l = [head] + fixed_children
    l.sort(key=lambda node: node['id'])
    return ' '.join([node['lemma'] for node in l])

def get_nTAM_feats(aux_nodes: list[conllu.Token],
                   head_feats: dict,
                   children: list[conllu.Token],
                   verb=True) -> dict:
    '''
    att,


    bli (PASS),
    ha,

    INF
    böra,
    skola,
    torde,
    kunna,
    lär,
    komma,
    må,
    behöva,
    måste,
    vilja

    PART/INF
    få,

    NEG
    inte, icke, ej,

    COP
    vara,

    '''

    feats = defaultdict(str)
    modality = ''

    foreign = {'do', 'not'}

    aux_lemmas = {aux['lemma'] for aux in aux_nodes if aux['lemma'] not in foreign}
    
    if 'att' in aux_lemmas:
        feats['VerbForm'] = 'Inf'
        aux_lemmas.discard('att')
    else:
        feats['VerbForm'] = 'Fin'
    
    # subj_ids = [child['id'] for child in children if child['deprel'] in {'nsubj', 'expl'}]
    # if subj_ids:
    #     subj_id = min(subj_ids)
    #     first_aux_id = min([child['id'] for child in aux_nodes])
    #     if first_aux_id < subj_id:
    #         if any([child['form'] == '?' for child in children]):
    #             feats['Mood'] = 'Int'
    #         else:
    #             # subject inversion is most likely a question, but it can also signify conditionality or can be done for
    #             # pragmatical reasons. The annotator decides.
    #             response = utils.get_response(['q', 'c', 'n'],
    #                                     f'Är "{head["form"]}" huvud för en fråga i denna mening: "{parse_tree.metadata["text"]}"\nq - fråga, c - villkor, n - ingendera')
    #             if response == 'q':
    #                 feats['Mood'] = 'Int'
    #             elif response == 'c':
    #                 feats['Mood'] = 'Cnd'
    #             elif response == 'n':
    #                 pass

    if 'bli' in aux_lemmas:
        node = [node for node in aux_nodes if node['lemma'] == 'bli']
        assert len(node) == 1
        node = node[0]

        feats['Voice'] = 'Pass'

        if node['feats'].get('VerbForm', None) == 'Sup':
            feats['Aspect'] += ',Perf'

        if node['feats'].get('VerbForm', None) == 'Fin':
            feats['Tense'] = node['feats'].get('Tense', feats['Tense'])
            if not feats['Mood']: feats['Mood'] = node['feats'].get('Mood', 'Ind')
        aux_lemmas.discard('bli')

    if 'få' in aux_lemmas: # Nec or Prms
        modality += ',Prms' # Oklart om den finns

        node = [node for node in aux_nodes if node['lemma'] == 'få']
        assert len(node) == 1
        node = node[0]

        if node['feats'].get('VerbForm', None) == 'Sup':
            feats['Aspect'] += ',Perf'

        elif node['feats'].get('VerbForm', None) == 'Fin':
            feats['Tense'] = node['feats'].get('Tense', feats['Tense'])         
            if not feats['Mood']: feats['Mood'] = node['feats'].get('Mood', 'Ind')
        aux_lemmas.discard('få')

    if 'vara' in aux_lemmas:
        node = [node for node in aux_nodes if node['lemma'] == 'vara']
        assert len(node) == 1
        node = node[0]

        if node['feats'].get('VerbForm', None) == 'Sup':
            feats['Aspect'] += ',Perf'

        elif node['feats'].get('VerbForm', None) == 'Fin':
            feats['Tense'] = node['feats'].get('Tense', feats['Tense'])         
            if not feats['Mood']: feats['Mood'] = node['feats'].get('Mood', 'Ind')
            if node['feats'].get('Mood', 'Ind') == 'Sub': feats['Aspect'] += ',Prosp'

        aux_lemmas.discard('vara')

    if 'komma' in aux_lemmas:
        node = [node for node in aux_nodes if node['lemma'] == 'komma']
        assert len(node) == 1
        node = node[0]

        if node['feats'].get('VerbForm', None) == 'Sup':
            feats['Aspect'] += ',Perf'

        if node['feats'].get('VerbForm', None) == 'Fin':
            feats['Tense'] = 'Fut' if node['feats'].get('Tense', None) == 'Pres' else 'Past'
            if not feats['Mood']: feats['Mood'] = node['feats'].get('Mood', 'Ind')

        aux_lemmas.discard('komma')

    if 'måste' in aux_lemmas:
        modality += ',Nec'

        feats['Tense'] = 'Pres'
        if not feats['Mood']: feats['Mood'] = 'Ind'

        aux_lemmas.discard('måste')

    if 'torde' in aux_lemmas:
        modality += ',Nec' # osäker

        feats['Tense'] = 'Past'
        if not feats['Mood']: feats['Mood'] = 'Ind'

        aux_lemmas.discard('torde')

    if 'böra' in aux_lemmas:
        node = [node for node in aux_nodes if node['lemma'] == 'böra']
        assert len(node) == 1
        node = node[0]

        modality += ',Nec'

        if node['feats'].get('VerbForm', None) == 'Fin':
            feats['Tense'] = node['feats'].get('Tense', feats['Tense'])
            if not feats['Mood']: feats['Mood'] = node['feats'].get('Mood', 'Ind')

        aux_lemmas.discard('böra')

    if 'behöva' in aux_lemmas:
        node = [node for node in aux_nodes if node['lemma'] == 'behöva']
        assert len(node) == 1
        node = node[0]

        modality += ',Nec' 

        if node['feats'].get('VerbForm', None) == 'Sup':
            feats['Aspect'] += ',Perf'

        elif node['feats'].get('VerbForm', None) == 'Fin':
            feats['Tense'] = node['feats'].get('Tense', feats['Tense'])
            if not feats['Mood']: feats['Mood'] = node['feats'].get('Mood', 'Ind')

        aux_lemmas.discard('behöva')

    if 'kunna' in aux_lemmas:
        node = [node for node in aux_nodes if node['lemma'] == 'kunna']
        assert len(node) == 1
        node = node[0]

        modality += ',Pot'

        if node['feats'].get('VerbForm', None) == 'Sup':
            feats['Aspect'] += ',Perf'

        elif node['feats'].get('VerbForm', None) == 'Fin':
            feats['Tense'] = node['feats'].get('Tense', feats['Tense'])
            if not feats['Mood']: feats['Mood'] = node['feats'].get('Mood', 'Ind')

        aux_lemmas.discard('kunna')

    if 'lär' in aux_lemmas:
        modality += ',Nec' # osäker (Nec)

        feats['Tense'] = 'Pres'
        if not feats['Mood']: feats['Mood'] = 'Ind'

        aux_lemmas.discard('lär')

    if 'vilja' in aux_lemmas:
        node = [node for node in aux_nodes if node['lemma'] == 'vilja']
        assert len(node) == 1
        node = node[0]

        modality += ',Des'

        if node['feats'].get('VerbForm', None) == 'Sup':
            feats['Aspect'] += ',Perf'

        elif node['feats'].get('VerbForm', None) == 'Fin':
            feats['Tense'] = node['feats'].get('Tense', feats['Tense'])
            if not feats['Mood']: feats['Mood'] = node['feats'].get('Mood', 'Ind')

        aux_lemmas.discard('vilja')

    if 'må' in aux_lemmas:
        node = [node for node in aux_nodes if node['lemma'] == 'må']
        assert len(node) == 1
        node = node[0]
        
        modality += ',Pot' # or maybe Jus/Prms/Opt?

        if node['feats'].get('VerbForm', None) == 'Fin':
            feats['Tense'] = node['feats'].get('Tense', feats['Tense'])
            if not feats['Mood']: feats['Mood'] = node['feats'].get('Mood', 'Ind')
            # if node['feats'].get('Mood', 'Ind') == 'Sub': feats['Aspect'] += ',Prosp'

        aux_lemmas.discard('må')

    # if 'tänka' in aux_lemmas:
    #     node = [node for node in aux_nodes if node['lemma'] == 'tänka']
    #     assert len(node) == 1
    #     node = node[0]

    #     feats['Aspect'] += ',Prosp'

    #     if node['feats'].get('VerbForm', None) == 'Fin':
    #         feats['Tense'] = 'Fut' if node['feats'].get('Tense', None) == 'Pres' else 'Past'
    #         if not feats['Mood']: feats['Mood'] = node['feats'].get('Mood', 'Ind')
            
    #     aux_lemmas.discard('tänka')

    if 'skola' in aux_lemmas:
        node = [node for node in aux_nodes if node['lemma'] == 'skola']
        assert len(node) == 1
        node = node[0]

        # feats['Aspect'] += ',Prosp'

        if node['feats'].get('VerbForm', None) == 'Fin':
            feats['Tense'] = 'Fut' if node['feats'].get('Tense', None) == 'Pres' else 'Past'
            if not feats['Mood']: feats['Mood'] = node['feats'].get('Mood', 'Ind')
            
        aux_lemmas.discard('skola')



    if 'ha' in aux_lemmas:
        node = [node for node in aux_nodes if node['lemma'] == 'ha']
        assert len(node) == 1
        node = node[0]

        if 'Perf' not in feats['Aspect']:
            feats['Aspect'] += ',Perf'

        if node['feats'].get('VerbForm', None) == 'Fin':
            feats['Tense'] = node['feats'].get('Tense', feats['Tense'])
            if not feats['Mood']: feats['Mood'] = node['feats'].get('Mood', 'Ind')
        aux_lemmas.discard('ha')


    if aux_lemmas&{'inte', 'icke', 'ej'}:
        if modality:
            modality = f',neg({"+".join(sorted(list(set([m for m in modality.split(",") if i])))).strip("+")})'
        elif not modality:
            feats['Polarity'] = 'Neg'
        aux_lemmas.discard('inte')
        aux_lemmas.discard('icke')
        aux_lemmas.discard('ej')

    else:
        feats['Polarity'] = 'Pos'
    
    feats['Mood'] += modality
    feats['Mood'] = feats['Mood'].strip(',')

    if aux_lemmas:
        raise ValueError(f'untreated auxiliaries. their lemmas: {aux_lemmas}')

    feats = {k: ','.join(sorted(list(set([i for i in v.split(',') if i])))) for k, v in feats.items() if v}
    if 'Mood' in feats:
        feats['Mood'] = feats['Mood'].replace('+', ',')

    return feats

def apply_grammar(head: conllu.Token, children: list[conllu.Token]):

    # remove children that are not of interest
    children = [child for child in children if not child['deprel'] in {'parataxis', 'reparandum', 'punct'}]

    fixed_children = [child for child in children if child['deprel'] == 'fixed']
    head['fixed lemma'] = combine_fixed_nodes(head, fixed_children)
    children = [child for child in children if child['deprel'] != 'fixed']

    is_verb = head['upos'] in VERBAL
    is_noun = head['upos'] in NOMINAL

    if is_verb:
        head['ms feats'] = {}
    else:
        if head['feats']:
            head['ms feats'] = deepcopy(head['feats'])
        else:
            head['ms feats'] = {}

    TAM_nodes = [child for child in children if child['upos'] in {'AUX', 'PART'}]

    if TAM_nodes:
        head['ms feats'].update(get_nTAM_feats(TAM_nodes, head['feats'], children, is_verb))

        if not head['ms feats'].get('Mood', None): head['ms feats']['Mood'] = 'Ind'
        if not head['ms feats'].get('Polarity', None): head['ms feats']['Polarity'] = 'Pos'
        if not head['ms feats'].get('VerbForm', None): head['ms feats']['VerbForm'] = 'Fin'
        if not head['ms feats'].get('Voice', None): head['ms feats']['Voice'] = 'Act'

        print(parse_tree.metadata["text"])
        print(f"{head['form']=}\n{head['feats']=}\n{head['ms feats']=}\n{[child['lemma']+' '+'feats='+str(child['feats']) for child in TAM_nodes]}\n\n")

    relation_nodes = [child for child in children if
                      (child['deprel'] in {'case', 'mark', 'cc'}
                      or child['lemma'] in marker_feat_map
                      or child['lemma'] in case_feat_map)]
    
    if relation_nodes:
        pass

    #######################################################################################
    
    del head['fixed lemma']


if __name__ == '__main__':
    filepath = '/home/norrman/GitHub/morphosyntax/swe/UD/swe/PUD/sv_pud-ud-test.conllu'
    out_path = '/home/norrman/GitHub/morphosyntax/swe/UD+/swe/PUD/test.conllu'

    with open(filepath, encoding='utf8') as f:
        parse_trees = list(conllu.parse_tree_incr(f))
    with open(filepath, encoding='utf8') as f:
        parse_lists = list(conllu.parse_incr(f))

    assert len(parse_lists) == len(parse_trees)
    with open(out_path, 'w', encoding='utf8') as outfile:
        for i in range(len(parse_trees)):
            parse_tree = parse_trees[i]
            parse_list: conllu.TokenList = parse_lists[i]

            id2idx = {token['id']:i for i, token in enumerate(parse_list) if isinstance(token['id'], int)}
            idx2id = [token['id'] if isinstance(token['id'], int) else None for token in parse_list]

            # utils.span() descends the tree and creates a flat list of all nodes in the tree
            # that have children
            heads = utils.span(parse_tree)
            # checks that each child appears as a child before it appears as a head?
            assert utils.verify_span(heads)
            for head, children in heads[::-1]:
                head: conllu.Token = parse_list[id2idx[head]]
                children = [parse_list[id2idx[child]] for child in children]
                apply_grammar(head, children)
                
        