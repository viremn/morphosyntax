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

def get_rel_feat(word):
    return marker_feat_map.get(word, case_feat_map.get(word, word))

def get_conj_feat(word): 
    return conjtype_feat_map.get(word, case_feat_map.get(word, word))

def get_relation_feats(relation_nodes: list[conllu.Token], verb=True, clause=False) -> dict:
    '''
    Generating morpho_syntactic features for relations. For nominals, cases are put under the 'Case' feature, and
    conjunctions under 'RelType'. For verbs, all values are under 'RelType'.
    The mapping from words to features is in 'eng_relations.py' and should be updated there.
    '''
    feats = {}

    relation_nodes = deepcopy(relation_nodes)
    for node in relation_nodes:
        node['lemma'] = node.get('fixed lemma', node.get('lemma'))

    if not verb:
        if clause:
            # if it's a noun heading a clause I assume adpositions are defaultly markers
            marker_nodes = [node for node in relation_nodes
                        if (node['deprel'] == 'mark'
                        or node['lemma'] in marker_feat_map) 
                        and node['deprel'] != 'cc']
            case_nodes = [node for node in relation_nodes
                        if (node['deprel'] == 'case'
                        or node['lemma'] in case_feat_map)
                        and node not in marker_nodes
                        and node['deprel'] != 'cc']
            cc_nodes = [node for node in relation_nodes 
                        if (node['deprel'] == 'cc' 
                            or node['lemma'] in conjtype_feat_map)
                            and node not in marker_nodes
                            and node not in case_nodes]
        else:
            # else, I assume adpositions are defaultly cases
            case_nodes = [node for node in relation_nodes
                        if (node['deprel'] == 'case'
                        or node['lemma'] in case_feat_map) 
                        and node['deprel'] != 'cc']
            marker_nodes = [node for node in relation_nodes
                        if (node['deprel'] == 'mark'
                        or node['lemma'] in marker_feat_map)
                        and node not in case_nodes
                        and node['deprel'] != 'cc']
            cc_nodes = [node for node in relation_nodes 
                        if (node['deprel'] == 'cc' 
                            or node['lemma'] in conjtype_feat_map)
                            and node not in marker_nodes
                            and node not in case_nodes]
        
        if [node for node in relation_nodes 
                    if node not in marker_nodes 
                    and node not in case_nodes 
                    and node not in cc_nodes]:
            print("ERROR:", [node for node in relation_nodes 
                    if node not in marker_nodes 
                    and node not in case_nodes 
                    and node not in cc_nodes])
        assert not [node for node in relation_nodes 
                    if node not in marker_nodes 
                    and node not in case_nodes 
                    and node not in cc_nodes]

        if marker_nodes:
            feats['RelType'] = ','.join([marker_feat_map.get(node['lemma'], node['lemma']) for node in marker_nodes])
        if case_nodes:
            feats['Case'] = ','.join([case_feat_map.get(node['lemma'], node['lemma']) for node in case_nodes])
        if cc_nodes:
            feats['ConjType'] = ','.join([conjtype_feat_map.get(node['lemma'], node['lemma']) for node in cc_nodes])

    else:
        marker_nodes = [node for node in relation_nodes if node['deprel'] != 'cc']
        feats['RelType'] = ','.join([get_rel_feat(node['lemma']) for node in marker_nodes])
    
    print("RelNodes:", [node['lemma'] for node in relation_nodes], feats)
    return feats


def get_nTAM_feats(aux_nodes: list[conllu.Token],
                   head_feats: dict,
                   children: list[conllu.Token],
                   verb=True) -> dict:

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

    print("nTAM:", [node['lemma'] for node in aux_nodes], feats)

    return feats

def copy_feats(ms_feats, morpho_feats, values):
    '''
    copies features from morpho_feats to ms_feats only is they do not exist in morpho_feats.
    '''
    for value in values:
        ms_feats[value] = ms_feats.get(value, morpho_feats.get(value, None))
    
    print("Copy feats from head:", ms_feats)
    return ms_feats

def set_nodes(nodes):
    '''
    conllu.Token is not hashable so sets consist of ids
    '''
    return {node['id'] for node in nodes}

def apply_grammar(head: conllu.Token, children: list[conllu.Token]):

    # remove children that are not of interest
    children = [child for child in children if not child['deprel'] in {'parataxis', 'reparandum', 'punct'}]

    fixed_children = [child for child in children if child['deprel'] == 'fixed']
    head['fixed lemma'] = combine_fixed_nodes(head, fixed_children)
    children = [child for child in children if child['deprel'] != 'fixed']

    is_verb = head['upos'] in VERBAL
    is_noun = head['upos'] in NOMINAL

    print(head)
    print(parse_tree.metadata["text"])

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

    relation_nodes = [child for child in children if
                      (child['deprel'] in {'case', 'mark', 'cc'}
                      or child['lemma'] in marker_feat_map
                      or child['lemma'] in case_feat_map
                      or child['lemma'] in conjtype_feat_map) 
                      and child not in TAM_nodes]
    
    if relation_nodes:
        to_update = get_relation_feats(relation_nodes, verb=is_verb, clause=head['deprel'] in clausal_rels)
        # if to_update and not head['ms feats']:
        #     head['ms feats'] = to_update
        # else:
        head['ms feats'].update(to_update)


    
    if set_nodes(TAM_nodes) & set_nodes(relation_nodes):
        for id in set_nodes(TAM_nodes) & set_nodes(relation_nodes):
            print(parse_list[id2idx[id]])
    assert not set_nodes(TAM_nodes) & set_nodes(relation_nodes)

    children = [node for node in children if node not in relation_nodes + TAM_nodes]

    if is_verb:
        # copy values from the morphological feats if they were not set by now
        head['ms feats'] = copy_feats(head['ms feats'], head['feats'], ['Mood','Tense','Aspect','Voice','VerbForm','Polarity'])

        # set default values for feats underspecified in UD
        if not head['ms feats'].get('Voice', None): 
            print('Setting default voice: ACT')
            head['ms feats']['Voice'] = 'Act'

    elif is_noun or head['upos'] in {'ADV', 'ADJ'}:
        # treat determiners
        foreign = {'a', 'the', 'this', 'that', 'die', 'el', 'la', 'las', 'le'}
        det_nodes = [child for child in children if child['deprel'] == 'det' and not child['form'].lower() in foreign]
        children = [node for node in children if node['deprel'] != 'det']
        if det_nodes:
            for det_node in det_nodes:
                if det_node['form'].lower() == 'en':
                    head['ms feats']['Definite'] = 'Ind'
                    head['ms feats']['Gender'] = 'Com'
                    head['ms feats']['Number'] = 'Sing'

                elif det_node['form'].lower() == 'ett':
                    head['ms feats']['Definite'] = 'Ind'
                    head['ms feats']['Gender'] = 'Neut'
                    head['ms feats']['Number'] = 'Sing'

                elif det_node['form'].lower() == 'den':
                    head['ms feats']['Definite'] = 'Def'
                    head['ms feats']['Gender'] = 'Com'
                    head['ms feats']['Number'] = 'Sing'

                elif det_node['form'].lower() == 'det':
                    head['ms feats']['Definite'] = 'Def'
                    head['ms feats']['Gender'] = 'Neut'
                    head['ms feats']['Number'] = 'Sing'

                elif det_node['form'].lower() == 'de':
                    head['ms feats']['Definite'] = 'Def'
                    head['ms feats']['Number'] = 'Plur'

                elif det_node['form'].lower() == 'denna':
                    head['ms feats']['Definite'] = 'Def'
                    head['ms feats']['Gender'] = 'Com'
                    head['ms feats']['Number'] = 'Sing'
                    head['ms feats']['Dem'] = 'Prox'

                elif det_node['form'].lower() == 'denne':
                    head['ms feats']['Definite'] = 'Def'
                    head['ms feats']['Gender'] = 'Com'
                    head['ms feats']['Number'] = 'Sing'
                    head['ms feats']['Dem'] = 'Prox'

                elif det_node['form'].lower() == 'detta':
                    head['ms feats']['Definite'] = 'Def'
                    head['ms feats']['Gender'] = 'Neut'
                    head['ms feats']['Number'] = 'Sing'
                    head['ms feats']['Dem'] = 'Prox'

                elif det_node['form'].lower() == 'dessa':
                    head['ms feats']['Definite'] = 'Def'
                    head['ms feats']['Number'] = 'Plur'
                    head['ms feats']['Dem'] = 'Prox' 
                
                elif det_node['form'].lower() in {'båda', 'bägge'}:
                    head['ms feats']['Definite'] = 'Def'
                    head['ms feats']['Number'] = 'Plur'
                    head['ms feats']['PronType'] = 'Tot'

                elif det_node['form'].lower() in {'var', 'vart', 'varje', 'varenda', 'vardera'}:
                    head['ms feats']['Definite'] = 'Ind'
                    head['ms feats']['Number'] = 'Sing'
                    head['ms feats']['PronType'] = 'Tot'

                    if det_node['form'].lower() == 'vart':
                        head['ms feats']['Gender'] = 'Neut'
                    elif det_node['form'].lower() == 'var':
                        head['ms feats']['Gender'] = 'Com'

                elif det_node['form'].lower() in {'varannan', 'varannat'}:
                    head['ms feats']['Definite'] = 'Ind'
                    head['ms feats']['Number'] = 'Sing'
                    head['ms feats']['PronType'] = 'Ind'

                    if det_node['form'].lower() == 'varannat':
                        head['ms feats']['Gender'] = 'Neut'
                    elif det_node['form'].lower() == 'varannan':
                        head['ms feats']['Gender'] = 'Com'
                
                elif det_node['form'].lower() == 'all':
                    head['ms feats']['Definite'] = 'Ind'
                    head['ms feats']['Gender'] = 'Com'
                    head['ms feats']['Number'] = 'Sing'
                    head['ms feats']['PronType'] = 'Tot'
                
                elif det_node['form'].lower() == 'allt':
                    head['ms feats']['Definite'] = 'Ind'
                    head['ms feats']['Gender'] = 'Neut'
                    head['ms feats']['Number'] = 'Sing'
                    head['ms feats']['PronType'] = 'Tot'
                
                elif det_node['form'].lower() == 'alla':
                    head['ms feats']['Definite'] = 'Ind'
                    head['ms feats']['Number'] = 'Plur'
                    head['ms feats']['PronType'] = 'Tot'

                elif det_node['form'].lower() in {'min', 'mitt', 'mina',
                                                  'din', 'ditt', 'dina',
                                                  'sin', 'sitt', 'sina',
                                                  # 'hans', 'hennes',
                                                  'deras'}:
                    head['ms feats']['Definite'] = 'Def'
                    head['ms feats']['Poss'] = 'Yes'
                    head['ms feats']['PronType'] = 'Prs'
                    
                    if det_node['form'].lower() in {'min', 'mitt',
                                                    'din', 'ditt',
                                                    'sin', 'sitt'}:
                        head['ms feats']['Number'] = 'Sing'
                        if det_node['form'].lower().endswith('tt'):
                            head['ms feats']['Gender'] = 'Neut'
                        else:
                            head['ms feats']['Gender'] = 'Com'
                    
                    elif det_node['form'].lower() in {'mina',
                                                  'dina',
                                                  'sina'}:
                        head['ms feats']['Number'] = 'Plur'
                    
                    if det_node['form'].lower()[0] == 'm':
                        head['ms feats']['Person'] = '1'
                    elif det_node['form'].lower()[0:2] == 'di':
                        head['ms feats']['Person'] = '2'
                    elif det_node['form'].lower()[0:2] in {'si', 'de'}:
                        head['ms feats']['Person'] = '3'

                elif det_node['form'].lower() in {'vilken', 
                                                  'vilket',
                                                  'vilka'}:
                    head['ms feats']['Definite'] = 'Ind'
                    head['ms feats']['PronType'] = 'Int,Rel'
                    
                    if det_node['form'].lower() == 'vilka':
                        head['ms feats']['Number'] = 'Plur'
                    else:
                        head['ms feats']['Number'] = 'Sing'
                    
                    if det_node['form'].lower() == 'vilken':
                        head['ms feats']['Gender'] = 'Com'
                    elif det_node['form'].lower() == 'vilket':
                        head['ms feats']['Gender'] = 'Neut'

                elif det_node['form'].lower() in {'någon', 
                                                  'något',
                                                  'några'}:
                    head['ms feats']['Definite'] = 'Ind'
                    if det_node['form'].lower().endswith('n'):
                        head['ms feats']['Gender'] = 'Com'
                        head['ms feats']['Number'] = 'Sing'
                    elif det_node['form'].lower().endswith('t'):
                        head['ms feats']['Gender'] = 'Neut'
                        head['ms feats']['Number'] = 'Sing'
                    else:
                        head['ms feats']['Number'] = 'Plur'

                elif det_node['form'].lower() in {'ingen', 
                                                  'inget',
                                                  'inga'}:
                    head['ms feats']['Definite'] = 'Ind'
                    head['ms feats']['PronType'] = 'Neg'

                    if det_node['form'].lower().endswith('n'):
                        head['ms feats']['Gender'] = 'Com'
                        head['ms feats']['Number'] = 'Sing'
                    elif det_node['form'].lower().endswith('t'):
                        head['ms feats']['Gender'] = 'Neut'
                        head['ms feats']['Number'] = 'Sing'
                    else:
                        head['ms feats']['Number'] = 'Plur'

                else:
                    print(f'a non treated determiner: "{det_node["lemma"]}"')
                    children = [det_node] + children

        if head['upos'] in {'ADV', 'ADJ'} and children:
            advj_children = [child['form'].lower() for child in children]
            if 'mer' in advj_children:
                head['ms feats']['Degree'] = 'Cmp'
                print('Found "mer"', head['ms feats'])
              
            elif 'mest' in advj_children:
                head['ms feats']['Degree'] = 'Sup'
                print('Found "mest"', head['ms feats'])

            children = [node for node in children if node['form'].lower() not in {'mer', 'mest'}]

    if head['ms feats']:
        head['ms feats'] = {k: v for k, v in head['ms feats'].items() if v}

    for child in children:
        if child['upos'] in {'ADV', 'ADJ', 'INTJ', 'DET'} | VERBAL | NOMINAL and not child.get('ms feats', None):
            ms_feats = deepcopy(child['feats'])
            if ms_feats is None:
                ms_feats = '|'
            child['ms feats'] = ms_feats
            print('Child:', child['lemma'], ms_feats)
    
    print()

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
            
            for node in parse_list:
                # setting ms-feats for content nodes that were not dealt with earlier
                if node['upos'] in {'ADJ', 'INTJ'} | VERBAL | NOMINAL and not node.get('ms feats', None):
                    ms_feats = deepcopy(node['feats'])
                    if ms_feats is None:
                        ms_feats = '|'
                    node['ms feats'] = ms_feats
                # function nodes end up with empty ms-feats
                else:
                    node['ms feats'] = node.get('ms feats', None)
            
            assert utils.verify_treeness(parse_list)
            
            to_write = parse_list.serialize()
            outfile.write(to_write + '\n')
                
        