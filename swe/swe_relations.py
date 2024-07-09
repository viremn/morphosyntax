'''
Mappings from prepositions and conjunctions to relation features.
Either arg-pred relation, i.e. case, or pred-pred relation, i.e. marker.
The final list should be updated according to the mapping done by Dan Zeman in this link: https://docs.google.com/spreadsheets/d/1--AkGor1-yQLv_BGnnXYQfekBQvMq7u7/edit?gid=1264268804#gid=1264268804
Whatever adposition or conjunction that can't be mapped to anything on the list, should appear as is as the value of the
relevant feature, transliterated to Latin letter if not already.
'''

case_feat_map = {
    'vid': 'Loc',

    'i': 'Ine',
    'inom': 'Ine',
    'innanför': 'Ine',

    'bland': 'Ces',

    'mellan': 'Int',
    'emellan': 'Int',

    'utanför': 'Ext',
    'utom': 'Ext',
    'utåt': 'Ext',

    'på': 'Ade',

    'bredvid': 'Apu',
    'intill': 'Apu',
    
    'kring': 'Cir',
    'omkring': 'Cir',
    'runt': 'Cir',
    'runtomkring': 'Cir',

    'nära': 'Prx',
    'närmare': 'Prx',

    'ovanför': 'Sup',
    'ovanpå': 'Sup',

    'nedanför': 'Sub',
    'nedom': 'Sub',
    'under': 'Sub',

    'framför': 'Ant',
    'inför': 'Ant',

    'bak': 'Pst',
    'bakom': 'Pst',
    'förbi': 'Pst',
    
    'från': 'Abl',
    'alltifrån': 'Abl',
    
    'ifrån': 'Ela',

    'genom': 'Per',

    'tvärsigenom': 'Crs',

    'längs': 'Lng',

    'via': 'Pro',

    'över': 'Spx',

    'gentemot': 'Lat',

    'inpå': 'Ill',

    'till': 'Apl',
    
    '-': 'Itl',

    'förrän': 'Tan',
    'innan': 'Tan',

    'tills': 'Ttr',

    'senast': 'Lim',

    'framemot': 'Tpx',

    'efter': 'Tps',
    'tidigast': 'Tps',

    'sedan': 'Teg',

    'per': 'Dis',
    '/': 'Dis',
    'a': 'Dis',

    'med': 'Com',
    'jämte': 'Com',

    'utan': 'Abe',
    
    'inklusive': 'Inc',

    'förutan': 'Add',
    'förutom': 'Add',
    'utom': 'Add',
    'utöver': 'Add',

    'exklusive': 'Exc',
    'frånsett': 'Exc',

    'såsom': 'Ess',

    'liksom': 'Sem',

    'tvärtemot': 'Dsm',

    'än': 'Cmp',

    'medan': 'Cmt',

    'då': 'Cau', 
    'eftersom': 'Cau', 
    'emedan': 'Cau', 
    'igenom': 'Cau',

    'att': 'Pur',

    'oavsett': 'Ign',

    'trots': 'Ccs', 
    'ehuruväl': 'Ccs', 
    'fast': 'Ccs', 
    'fastän': 'Ccs',

    'allteftersom': 'Cnd', 
    'när': 'Cnd', 
    'såvida': 'Cnd',

    'apropå': 'The',
    'angående': 'The', 
    'beträffande': 'The',

    'alltefter': 'Quo', 
    'all': 'Quo',
    'enligt': 'Quo',

    'för': 'Ben',

    'mot': 'Adv', 
    'emot': 'Adv', 
    'kontra': 'Adv',


}
case_feat_map = {k: v if v else k for k,v in case_feat_map.items()}


conjtype_feat_map = {
    'och': 'Conj',
    '+': 'Conj',
    'som': 'Conj',

    'varken': 'Nnor',

    'eller': 'Disj',

    'men': 'Advs',

    'för': 'Reas',
    'ty': 'Reas',

    'därför': 'Consq',
    'så': 'Consq',

    'vid': 'test'

}

conjtype_feat_map = {k: v if v else k for k,v in conjtype_feat_map.items()}

marker_feat_map = {
    
}
marker_feat_map = {k: v if v else k for k,v in marker_feat_map.items()}


if __name__ == '__main__':
    print(set(case_feat_map.keys()))
    print(set(conjtype_feat_map.keys()))
    print(set(marker_feat_map.keys()))
    print(set(case_feat_map.keys()) & set(conjtype_feat_map.keys()))
    print(set(case_feat_map.keys()) & set(marker_feat_map.keys()))
    print(set(conjtype_feat_map.keys()) & set(marker_feat_map.keys()))

