import os


def find_file(directory, string):
    for file in os.listdir(directory):
        if string in file:
            return file


def make_splits(banks, all_banks, ud_dir):
    splits = {bank: {} for bank in all_banks}
    for lang in banks:
        for bank in banks[lang]:
            for split in ['train', 'dev', 'test']:
                filename = find_file(os.path.join(ud_dir, lang, bank), split)
                splits[bank][split] = filename
    return splits


## paths
ud_dir = 'UD'
banks = {'eng': ['GENTLE'], 'heb': ['HTB', 'IAHLTwiki'], 'ypk': ['SLI']}
all_banks = [bank for lang in banks for bank in banks[lang]]

splits = make_splits(banks, all_banks, ud_dir)
