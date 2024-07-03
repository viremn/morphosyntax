'''
Mappings from prepositions and conjunctions to relation features.
Either arg-pred relation, i.e. case, or pred-pred relation, i.e. marker.
The final list should be updated according to the mapping done by Dan Zeman in this link: https://docs.google.com/spreadsheets/d/1--AkGor1-yQLv_BGnnXYQfekBQvMq7u7/edit?gid=1264268804#gid=1264268804
Whatever adposition or conjunction that can't be mapped to anything on the list, should appear as is as the value of the
relevant feature, transliterated to Latin letter if not already.
'''

case_feat_map = {
    'to': 'Dat',
    'with': 'Com',
    'of': 'Gen',
    "'s": 'Gen',
    'from': 'Abl',
    'for': 'Ben',
    'on': 'Sup',
    'above': 'Sup+Rem',
    'atop': 'Sup+Prox',
    'at': 'Loc',
    'in': 'Ine',
    'into': 'Ine+All',
    'onto': 'Sup+All',
    'through': 'Perl+Ess',
    'by': 'Inst',
    'and': 'Cum',
    'or': 'Alter',
    'nor': 'neg(Alter)',
    'under': 'Sub',
    'near': 'Ade',
    'around': 'Circ',
    'against': 'Rev',
    'without': 'Abe',  # may also be 'neg(Com)'
    'like': 'Comp',
    'as': 'Adv',
    'along': 'Perl',
    'during': 'TempPerl',
    'across': 'Prol',
    'inside': 'Ine+Ess',
    'outside': 'Ela+Ess',
    'after': 'Subseq',  # may also be 'TempPost
    'ago': 'Antr',
    'before': 'Antr',
    'behind': 'Post',
    'amid': '',
    'amidst': '',
    'among': '',
    'upon': '',
    'unto': '',
    'about': '',
    'throughout': '',
    'beyond': '',
}
case_feat_map = {k: v if v else k for k,v in case_feat_map.items()}

marker_feat_map = {
    'when': 'TempCond',
    'whenever': '',
    'where': '',
    'if': 'Cond',
    'so': 'Conseq',
    'and': 'Cum',
    'but': 'Advers',
    'for': 'Ben',
    'or': 'Alter',
    'nor': 'neg(Alter)',
    'because': 'Cause',
    'since': 'TempCause',
    'after': 'Subseq',
    'as': '',
    'while': '',
    'until': '',
    'till': '',
    'everywhere': '',
    'then': 'Res'
}
marker_feat_map = {k: v if v else k for k,v in marker_feat_map.items()}
