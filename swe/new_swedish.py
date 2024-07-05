import os

import conllu
from consts import *
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
    behöva, 
    bli, 
    böra, skola, torde, 
    få, 
    ha, 
    inte, icke, ej, 
    kunna, 
    komma, 
    lär, 
    må, 
    måste, 
    vara, 
    vilja
    '''

    feats = defaultdict(str)

    subj_ids = [child['id'] for child in children if child['deprel'] in {'nsubj', 'expl'}]
    if subj_ids:
        subj_id = min(subj_ids)
        first_aux_id = min([child['id'] for child in aux_nodes])
        if first_aux_id < subj_id:
            if any([child['form'] == '?' for child in children]):
                feats['Mood'] = 'Int'
            else:
                # subject inversion is most likely a question, but it can also signify conditionality or can be done for
                # pragmatical reasons. The annotator decides.
                response = utils.get_response(['q', 'c', 'n'],
                                        f'Är "{head["form"]}" huvud för en fråga i denna mening: "{parse_tree.metadata["text"]}"\nq - fråga, c - villkor, n - ingendera')
                if response == 'q':
                    feats['Mood'] = 'Int'
                elif response == 'c':
                    feats['Mood'] = 'Cnd'
                elif response == 'n':
                    pass
    
    aux_lemmas = {aux['lemma'] for aux in aux_nodes}
    if verb:
        if 'att' in aux_lemmas:
            feats['VerbForm'] = 'Inf'
        else:
            feats['VerbForm'] = 'Fin'
    aux_lemmas.discard('att')

    # setting the polarity of the main verb, assuming that there is no modality that require internal feature structure.
    # down the line this will be rectified if there are modal auxiliaries.
    if any(neg in aux_lemmas for neg in ('inte', 'icke', 'ej')):
        feats['Polarity'] = 'Neg'
    else:
        feats['Polarity'] = 'Pos'
    aux_lemmas.discard('inte')
    aux_lemmas.discard('icke')
    aux_lemmas.discard('ej')

    

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
        head['ms feats'] = deepcopy(head['feats'])
    
    TAM_nodes = [child for child in children if child['upos'] in {'AUX', 'PART'}]
    if TAM_nodes:
        head['ms feats'].update(get_nTAM_feats(TAM_nodes, head['feats'], children, is_verb))

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