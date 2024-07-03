import os

import conllu
from consts import *
import utils
from typing import List
from copy import deepcopy
from collections import defaultdict
from eng_relations import case_feat_map, marker_feat_map

lang = 'eng'
bank = 'GENTLE'
excluded_genres = ['dictionary', 'proof', 'poetry']

VERBAL = {'VERB'}
NOMINAL = {'NOUN', 'PROPN', 'PRON', 'NUM'}

clausal_rels = {'conj','csubj','xcomp','ccomp','advcl','acl','advcl:relcl','acl:relcl'}


def create_abstract_nsubj(head: conllu.Token, auxes: List[conllu.Token]):
    '''
    When the subject is missing but agreement features appear on its head, an abstract node carrying features only is
    created
    '''
    abstract_nsubj = conllu.Token()
    abstract_nsubj['id'] = head['id'] - 0.9
    abstract_nsubj['form'] = '-'
    abstract_nsubj['lemma'] = '-'
    abstract_nsubj['upos'] = '-'
    abstract_nsubj['xpos'] = '-'
    abstract_nsubj['deps'] = '-'
    abstract_nsubj['misc'] = '-'
    abstract_nsubj['head'] = head['id']
    abstract_nsubj['deprel'] = 'nsubj'
    abstract_nsubj['ms feats'] = {}

    if auxes:
        first_aux_id = min([child['id'] for child in auxes])
        feats_source = [aux for aux in auxes if aux['id'] == first_aux_id][0]
    else:
        feats_source = head

    for attr in ['Number', 'Person', 'Gender']:
        abstract_nsubj['ms feats'][attr] = feats_source['feats'].get(attr, head['feats'].get(attr, None))
    abstract_nsubj['ms feats'] = {k:v for k,v in abstract_nsubj['ms feats'].items() if v}

    # in case of some pragmatical omission of subject with no agreement on the predicate - do not create abstract node
    if not abstract_nsubj['ms feats']:
        return None

    return abstract_nsubj


def get_rel_feat(word):
    return marker_feat_map.get(word, case_feat_map.get(word, word))


def get_relation_feats(relation_nodes: List[conllu.Token], verb=True, clause=False) -> dict:
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
                        if node['deprel'] == 'mark'
                        or node['lemma'] in marker_feat_map]
            case_nodes = [node for node in relation_nodes
                        if (node['deprel'] == 'case'
                        or node['lemma'] in case_feat_map)
                        and node not in marker_nodes]
        else:
            # else, I assume adpositions are defaultly cases
            case_nodes = [node for node in relation_nodes
                        if node['deprel'] == 'case'
                        or node['lemma'] in case_feat_map]
            marker_nodes = [node for node in relation_nodes
                        if (node['deprel'] == 'mark'
                        or node['lemma'] in marker_feat_map)
                        and node not in case_nodes]
        assert not [node for node in relation_nodes if node not in marker_nodes and node not in case_nodes]
        if marker_nodes:
            feats['RelType'] = ','.join([marker_feat_map.get(node['lemma'], node['lemma']) for node in marker_nodes])
        if case_nodes:
            feats['Case'] = ','.join([case_feat_map.get(node['lemma'], node['lemma']) for node in case_nodes])

    else:
        marker_nodes = relation_nodes
        feats['RelType'] = ','.join([get_rel_feat(node['lemma']) for node in marker_nodes])

    return feats


def get_nTAM_feats(aux_nodes: List[conllu.Token], head_feats: dict, verb=True) -> dict:
    '''
    generating morpho-syntactic features for a head node based on its own morphological features (head_feats) and its
    auxiliaries (all concatenated as list in aux_nodes).
    This methods works for both verbal and nominal predicates.
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
                                        f'Does the word "{head["form"]}" heads a question in the sentence "{parse_tree.metadata["text"]}"\nq - question, c - conditional, n - NOTA')
                if response == 'q':
                    feats['Mood'] = 'Int'
                elif response == 'c':
                    feats['Mood'] = 'Cnd'
                elif response == 'n':
                    pass

    aux_lemmas = {aux['lemma'] for aux in aux_nodes}
    if verb:
        if 'to' in aux_lemmas:
            feats['VerbForm'] = 'Inf'
        else:
            feats['VerbForm'] = 'Fin'
    aux_lemmas.discard('to')

    # setting the polarity of the main verb, assuming that there is no modality that require internal feature structure.
    # down the line this will be rectified if there are modal auxiliaries.
    if 'not' in aux_lemmas:
        feats['Polarity'] = 'Neg'
    else:
        feats['Polarity'] = 'Pos'
    # aux_lemmas.discard('not')

    if 'do' in aux_lemmas:
        if not verb:
            raise ValueError('a noun with "do"?!')

        do_node = [aux for aux in aux_nodes if aux['lemma'] == 'do']
        assert len(do_node) == 1
        do_node = do_node[0]
        feats['Tense'] = do_node['feats']['Tense']
    aux_lemmas.discard('do')

    if 'be' in aux_lemmas:
        be_nodes = [aux for aux in aux_nodes if aux['lemma'] == 'be']

        if len(be_nodes) == 1:
            if verb:
                if head_feats['VerbForm'] == 'Ger' or (head_feats['VerbForm'], head_feats['Tense']) == ('Part', 'Pres'):
                    feats['Aspect'] = 'Prog'
                elif (head_feats['VerbForm'], head_feats['Tense']) == ('Part', 'Past'):
                    feats['Voice'] = 'Pass'
                else:
                    raise ValueError('untreated be-type aux')
            higher_be = be_nodes[0]

        elif len(be_nodes) == 2:
            feats['Aspect'] = 'Prog'
            if verb:
                feats['Voice'] = 'Pass'
            higher_be = [node for node in be_nodes if not node['form'].endwith('ing')][0]

        else:
            raise NotImplementedError('too many be-nodes?')

        if 'Voice' not in feats and verb:
            feats['Voice'] = 'Act'

        # if there are no auxiliaries left, copy the remaining TAM feats from the "higher" auxiliary
        if not aux_lemmas-{'be', 'not'} and feats.get('VerbForm', None) != 'Inf':
            if 'Tense' in higher_be['feats']:
                feats['Tense'] = higher_be['feats']['Tense']
            if not verb:
                if 'Mood' not in feats and 'Mood' in higher_be['feats']:
                    feats['Mood'] = higher_be['feats']['Mood']
                if 'VerbForm' not in feats and 'VerbForm' in higher_be['feats']:
                    feats['VerbForm'] = higher_be['feats']['VerbForm']
    aux_lemmas.discard('be')

    if 'get' in aux_lemmas:
        get_node = [aux for aux in aux_nodes if aux['lemma'] == 'get'][0]
        assert 'pass' in get_node['deprel']
        feats['Voice'] = 'Pass'

        if not aux_lemmas-{'get', 'not'}:
            feats['Tense'] = get_node['feats'].get('Tense')
            feats['VerbForm'] = get_node['feats'].get('VerbForm')
    aux_lemmas.discard('get')

    if 'have' in aux_lemmas:
        if not verb or (head_feats['VerbForm'], head_feats['Tense']) == ('Part', 'Past'):
            feats['Aspect'] += ',Perf'
        else:
            raise ValueError('untreated have-type aux')

        # if there are no auxiliaries left, copy the remaining TAM feats from the "higher" auxiliary
        if not aux_lemmas-{'have', 'not'} and feats.get('VerbForm', None) != 'Inf':
            have_node = [aux for aux in aux_nodes if aux['lemma'] == 'have']
            assert len(have_node) == 1
            have_node = have_node[0]
            feats['Tense'] = have_node['feats']['Tense']
    aux_lemmas.discard('have')

    if 'will' in aux_lemmas:
        feats['Tense'] = 'Fut'
    aux_lemmas.discard('will')

    if 'would' in aux_lemmas:
        # Would stands for both conditional and FITP. Let the annotator decide.
        response = utils.get_response(['c', 'f'],
                                f'what does the "would" stand for in this sentence:\n"{parse_tree.metadata["text"]}"\nhead:"{head["form"]}"\nchildren:"{" ".join([child["form"] for child in children])}"\nc - conditional, f - future in the past')
        if response == 'c':
            feats['Mood'] += ',Cnd'
        else:
            feats['Tense'] = 'Past'
            feats['Aspect'] += ',Prosp'
    aux_lemmas.discard('would')

    # treatment of modality
    if aux_lemmas&{'can','could','may','shall','should','must'}:

        if 'can' in aux_lemmas:
            modality = 'Pot'
        aux_lemmas.discard('can')

        if 'could' in aux_lemmas:
            modality = 'Pot'
            response = utils.get_response(['c', 'p'],
                                    f'what does the "could" stand for in this sentence:\n"{parse_tree.metadata["text"]}"\nhead:"{head["form"]}"\nchildren:"{" ".join([child["form"] for child in children])}"\nc - conditional, p - past')
            if response == 'c':
                feats['Mood'] += ',Cnd'
            else:
                feats['Tense'] = 'Pst'
        aux_lemmas.discard('could')

        if 'may' in aux_lemmas or 'might' in aux_lemmas:
            modality = 'Prms'
        aux_lemmas.discard('may')
        aux_lemmas.discard('might')

        if 'shall' in aux_lemmas or 'should' in aux_lemmas:
            modality = 'Des'
        aux_lemmas.discard('shall')
        aux_lemmas.discard('should')

        if 'must' in aux_lemmas:
            modality = 'Nec'
        aux_lemmas.discard('must')

        if 'not' in aux_lemmas:
            modality = f'neg({modality})'
            del feats['Polarity']
        aux_lemmas.discard('not')

        feats['Mood'] += ',' + modality
        feats['Mood'] = feats['Mood'].strip(',')

    else:
        aux_lemmas.discard('not')

    if aux_lemmas:
        raise ValueError(f'untreated auxiliaries. their lemmas: {aux_lemmas}')

    feats = {k: v.strip(',') for k, v in feats.items() if v}

    return feats


def copy_feats(ms_feats, morpho_feats, values):
    '''
    copies features from morpho_feats to ms_feats only is they do not exist in morpho_feats.
    '''
    for value in values:
        ms_feats[value] = ms_feats.get(value, morpho_feats.get(value, None))
    return ms_feats


def set_nodes(nodes):
    '''
    conllu.Token is not hashable so sets consist of ids
    '''
    return {node['id'] for node in nodes}


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


def apply_grammar(head: conllu.Token, children: List[conllu.Token]):
    '''
    The main method combining functional children to create the morpho-syntactic features of head.
    '''

    children = [child for child in children if not child['deprel'] in {'parataxis', 'reparandum', 'punct'}]

    fixed_children = [child for child in children if child['deprel'] == 'fixed']
    head['fixed lemma'] = combine_fixed_nodes(head, fixed_children)
    children = [child for child in children if child['deprel'] != 'fixed']

    added_nodes = []

    verb = head['upos'] in VERBAL
    noun = head['upos'] in NOMINAL

    if verb:
        head['ms feats'] = {}
    else:
        head['ms feats'] = deepcopy(head['feats'])

    # if there are auxiliaries "consume" them to change head's feats
    TAM_nodes = [child for child in children if child['upos'] in {'AUX', 'PART'} and child['lemma'] != "'s"]
    if TAM_nodes:
        head['ms feats'].update(get_nTAM_feats(TAM_nodes, head['feats'], verb=verb))

        if not head['ms feats'].get('Mood', None): head['ms feats']['Mood'] = 'Ind'
        if not head['ms feats'].get('Polarity', None): head['ms feats']['Polarity'] = 'Pos'
        if not head['ms feats'].get('VerbForm', None): head['ms feats']['VerbForm'] = 'Fin'

    # if there are cases or conjunctures "consume" them as well
    # the last condition is complicated to exclude infinitive "to" while allowing case "'s"
    relation_nodes = [child for child in children if
                      (child['deprel'] in {'case', 'mark', 'cc'}
                      or child['lemma'] in marker_feat_map
                      or child['lemma'] in case_feat_map)
                      and (child['upos'] != 'PART' or child['lemma'] == "'s")]
    if relation_nodes:
        to_update = get_relation_feats(relation_nodes, verb=verb, clause=head['deprel'] in clausal_rels)
        if to_update and not head['ms feats']:
            head['ms feats'] = to_update
        else:
            head['ms feats'].update(to_update)

    # make sure we did not use the same node twice
    assert not set_nodes(TAM_nodes) & set_nodes(relation_nodes)
    children = [node for node in children if node not in relation_nodes + TAM_nodes]

    if verb:
        # copy values from the morphological feats if they were not set by now
        head['ms feats'] = copy_feats(head['ms feats'], head['feats'], ['Mood','Tense','Aspect','Voice','VerbForm','Polarity'])

        # set default values for feats underspecified in UD
        if not head['ms feats'].get('Voice', None): head['ms feats']['Voice'] = 'Act'

        # not sure it's needed. eng is not pro-drop so there always should be an nsubj.
        if head['ms feats']['VerbForm'] == 'Fin' and 'nsubj' not in [child['deprel'] for child in children]:
            abstract_nsubj = create_abstract_nsubj(head, TAM_nodes)
            if abstract_nsubj:
                added_nodes.append(abstract_nsubj)

    elif noun or head['upos'] in {'ADV', 'ADJ'}:
        # treat determiners
        det_nodes = [child for child in children if child['deprel'] == 'det']
        if det_nodes:
            assert len(det_nodes) == 1
            det_node = det_nodes[0]
            children = [node for node in children if node != det_node]
            if det_node['lemma'] == 'a':
                head['ms feats']['Definite'] = 'Ind'
            elif det_node['lemma'] == 'the':
                head['ms feats']['Definite'] = 'Def'
            elif det_node['lemma'] == 'another':
                head['ms feats']['Definite'] = 'Ind'
                det_node['lemma'] = 'other'
            elif det_node['lemma'] == 'no':
                head['ms feats']['Definite'] = 'Ind'
                head['ms feats']['Polarity'] = 'Neg'
            elif det_node['lemma'] == 'this':
                head['ms feats']['Dem'] = 'Prox'
            elif det_node['lemma'] == 'that':
                head['ms feats']['Dem'] = 'Dist'
            else:
                print(f'a non treated determiner: "{det_node["lemma"]}"')
                children = [det_node] + children

        if head['upos'] in {'ADV', 'ADJ'} and children:
            child_lemmas = [child['lemma'] for child in children]
            if 'more' in child_lemmas:
                head['ms feats']['Degree'] = 'Cmp'
            elif 'most' in child_lemmas:
                head['ms feats']['Degree'] = 'Sup'
            children = [node for node in children if node['lemma'] not in {'more', 'most'}]

    if head['ms feats']:
        head['ms feats'] = {k: v for k, v in head['ms feats'].items() if v}

    for child in children:
        if child['upos'] in {'ADV', 'ADJ', 'INTJ', 'DET'} | VERBAL | NOMINAL and not child.get('ms feats', None):
            ms_feats = deepcopy(child['feats'])
            if ms_feats is None:
                ms_feats = '|'
            child['ms feats'] = ms_feats

    del head['fixed lemma']

    return added_nodes


def get_where_to_add(added_nodes, id2idx):
    res = []
    for node in added_nodes:
        idx = int(node['id'])
        if idx == 0:
            res.append(-1)
        else:
            res.append(id2idx[idx])
    return res

if __name__ == '__main__':
    filepath = os.path.join(ud_dir, lang, bank, splits[bank]['test'])
    out_path = os.path.join('UD+', lang, bank, 'test.conllu')
    with open(filepath, encoding='utf8') as f:
        parse_trees = list(conllu.parse_tree_incr(f))
        parse_trees = [sent for sent in parse_trees if sent.metadata['sent_id'].split('_')[1] not in excluded_genres]
    with open(filepath, encoding='utf8') as f:
        parse_lists = list(conllu.parse_incr(f))
        parse_lists = [sent for sent in parse_lists if sent.metadata['sent_id'].split('_')[1] not in excluded_genres]

    assert len(parse_lists) == len(parse_trees)
    with open(out_path, 'w', encoding='utf8') as outfile:
        for i in range(len(parse_trees)):
            parse_tree = parse_trees[i]
            parse_list: conllu.TokenList = parse_lists[i]

            id2idx = {token['id']:i for i, token in enumerate(parse_list) if isinstance(token['id'], int)}
            idx2id = [token['id'] if isinstance(token['id'], int) else None for token in parse_list]

            heads = utils.span(parse_tree)
            assert utils.verify_span(heads)
            to_add = []
            for head, children in heads[::-1]:
                head: conllu.Token = parse_list[id2idx[head]]
                children = [parse_list[id2idx[child]] for child in children]
                added_nodes = apply_grammar(head, children)
                if added_nodes:
                    added_idxs = get_where_to_add(added_nodes, id2idx)
                    to_add += list(zip(added_nodes, added_idxs))

            for added_node in to_add[::-1]:
                node, idx = added_node
                parse_list.insert(idx + 1, node)

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
