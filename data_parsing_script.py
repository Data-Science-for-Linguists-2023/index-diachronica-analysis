from bs4 import BeautifulSoup
from bs4.element import ResultSet, Tag
from typing import Tuple
import pickle
import re
import jsons
import itertools

class Rule:
    id: str # Proto-Omotic-dʒ
    branch_id: str # Proto-Omotic
    from_sound: str # 'dʒ'
    intermediate_steps: list[str] # ['tʃ']
    to_sound: str # 'ʃ'
    original_text: str # dʒ → tʃ → ʃ

class Branch:
    id: str # section's ID field (Proto-Omotic)
    index: str # 6.1
    name: str # Proto-Omotic to Proto-Afro-Asiatic
    source: str # <i>Mecislau</i>, from Ehret, Christopher (1995)[...]

subs = {
    '0': '₀',
    '1': '₁',
    '2': '₂',
    '3': '₃',
    '4': '₄',
    '5': '₅',
    'x': 'ₓ',
    'u': 'ᵤ',
    'n': 'ₙ',
    's': 'ₛ'
}

sups = {
    '0': '⁰',
    '1': '¹',
    '2': '²',
    '3': '³',
    '4': '⁴',
    '5': '⁵',
    'x': 'ˣ',
    'u': 'ᵘ',
    'n': 'ⁿ',
    's': 'ˢ'
}

def remove_combos(string: str, combos: tuple[tuple[int, int, str], ...]) -> str:
    """Removes combos of optionals from a string."""
    removed = string
    for (start, end, optional) in combos:
        removed = removed[:start] + ('�' * (end - start)) + removed[end:]
    
    return removed.replace('�', '')

def split_sounds(sounds: str) -> list[str]:
    """Split the sounds in a rule.

    Requires more than just .split(' ') because of cases like `[+ voice]`.
    """
    return re.findall(r'(?:\[.*?\]|\S)+', sounds)

def handle_brackets(sound: str) -> set[str]:
    """Handles bracketed sounds"""
    sounds: set[str] = set()

    # find innermost bracket and recurse
    bracket_start: int = 0
    bracket_end: int = 0

    # Gotta do bracket matching. Ugh
    for (index, character) in enumerate(sound):
        if character == '{':
            bracket_start = index
        elif character == '}':
            bracket_end = index
            break
    
    if (bracket_start == 0 and bracket_end == 0):
        return set([sound])
    
    # print(sound[bracket_start : bracket_end+1])
    
    inner_sounds = sound[bracket_start + 1 : bracket_end].split(',')

    for inner_sound in inner_sounds:
        repl_sound = sound[:bracket_start] + inner_sound + sound[bracket_end + 1:]
        sounds |= handle_brackets(repl_sound)
    
    return sounds

def parse_rule_steps(steps: str) -> list[Tuple[str, list[str], str]]:
    """Parse out the steps of a rule"""
    rules: list[Tuple[str, list[str], str]] = []

    steps = re.sub(r'^— ', '', steps)

    # split by the rule step separator
    rule_split = [s.strip() for s in steps.split("→")]

    if len(rule_split) < 2:
        print(f'Too few steps in rule: {steps} - skipping')
        return []
    
    if len(rule_split) > 2:
        from_sounds = split_sounds(rule_split[0])
        intermediates = [split_sounds(substr) for substr in rule_split[1:-1]]
        to_sounds = split_sounds(rule_split[-1])
        if (not (
                (len(from_sounds) == len(intermediates[0]) == len(to_sounds))
                and all(len(i) == len(intermediates[0]) for i in intermediates)
            )):
            print(f'Warning: mismatched lengths for rule: {steps} ({from_sounds}, {intermediates}, {to_sounds}) ({len(from_sounds)}, {[len(im) for im in intermediates],}, {len(to_sounds)})')
        
        for index, from_sound in enumerate(from_sounds):
            unbracketed_froms = handle_brackets(from_sound)
            unbracketed_tos = handle_brackets(to_sounds[index])
            for unb_from in unbracketed_froms:
                for unb_to in unbracketed_tos:
                    rules.append((unb_from, [im[index] for im in intermediates], unb_to))
    else:
        from_sounds = split_sounds(rule_split[0])
        to_sounds = split_sounds(rule_split[1])
        if (len(from_sounds) != len(to_sounds)):
            print(f'Warning: mismatched lengths for rule: {steps} ({from_sounds}, {to_sounds}) ({len(from_sounds)}, {len(to_sounds)})')
        
        for index, from_sound in enumerate(from_sounds):
            unbracketed_froms = handle_brackets(from_sound)
            unbracketed_tos = handle_brackets(to_sounds[index])
            for unb_from in unbracketed_froms:
                for unb_to in unbracketed_tos:
                    rules.append((unb_from, [], unb_to))
    
    return rules

def parse_sound_change(rule_string: str, rule_id: str, decoded: str) -> list[Rule]:
    """Parse the rules for a sound change."""
    rules: list[Rule] = []

    # Ignore anything in backticks
    rule_string = re.sub(r'`.*?`', '', rule_string)

    # Ignore "(?)"
    rule_string = rule_string.replace('(?)', '')

    # Split the rule up. This will inevitably include stuff I don't want but we can work out how to remove that stuff later
    # First split by the environment separator
    env_split = rule_string.split(" / ", 1)

    environment = ''

    if len(env_split) > 1:
        environment = env_split[1]
    else:
        # If no environment, but rule ends with some text in parentheses or quotes, consider that the environment
        parens_match = re.search(r'(.+[^→]) (\(.+\)|“.+”)$', rule_string)
        if parens_match:
            env_split[0] = parens_match.group(1)
            environment = parens_match.group(2)
    
    split_rules: list[Tuple[str,list[str],str]] = []

    # if there are any optional bits, run the split with all possible combinations of with and without them
    optionals = [(match.start(), match.end(), match.group(0)) for match in re.finditer(r'(\(.*?\))', env_split[0])]
    if (optionals):
        combinations = list(itertools.chain.from_iterable(itertools.combinations(optionals, l) for l in range(len(optionals) + 1)))
        for combo in combinations:
            combo_string = env_split[0]
            # print(combo)
            combo_string = remove_combos(combo_string, combo)
            combo_string = combo_string.replace('(','').replace(')','')
            # print(combo_string)
            split_rules += parse_rule_steps(combo_string)
    else:
        split_rules += parse_rule_steps(env_split[0])

    # only uniques
    for split_rule in [sr for i, sr in enumerate(split_rules) if sr not in split_rules[:i]]:
        rule = Rule()

        rule.id = rule_id
        rule.original_text = decoded
        rule.environment = environment
        rule.from_sound, rule.intermediate_steps, rule.to_sound = split_rule

        rules.append(rule)

    return rules

def parse_sid() -> None:
    """Parse the Searchable Index Diachronica and write the output."""
    with open('./data/sid-tidy-with-edits.html') as fp:
        soup = BeautifulSoup(fp, 'html.parser')

    # Each branch has a section
    sections: ResultSet = soup.find_all('section')

    branches: list[Branch] = []
    rules: list[Rule] = []

    section: Tag
    for section in sections:
        # Only include sections that have sound changes
        sound_changes = section.select('.schg')

        if not sound_changes:
            continue

        branch = Branch()

        branch.id = section['id']

        # Get header info
        header: Tag = section.h2

        header_match = re.match(r'(\d+(?:\.\d+)*) (.+)', header.decode_contents())
        if not header_match:
            print(f'Section header "{header.decode_contents()}" doesn\'t match format, skipping')
            continue

        branch.index = header_match[1]
        branch.name = header_match[2]

        # Get source
        source: Tag = section.select_one('p:not(.schg)')
        if source:
            branch.source = source.decode_contents()
        
        branches.append(branch)

        # Parse rules!
        # This is the hard part.
        sound_change: Tag
        for sound_change in sound_changes:
            # Replace any <sub> or <sup> tags with Unicode equivalents
            rule_parts: list[str] = []
            for rule_part in sound_change.contents:
                if not rule_part.name:
                    rule_parts.append(rule_part)
                else:
                    if rule_part.name == 'sub':
                        rule_parts.append(subs[rule_part.string])
                    elif rule_part.name == 'sup':
                        rule_parts.append(sups[rule_part.string])
                    elif rule_part.name == 'b': # sometimes stuff is bolded that should be included
                        rule_parts.append(rule_part.string)
                    # leave out anything else weird, for now
            
            rule_string = ''.join(rule_parts)
            rules += parse_sound_change(rule_string, sound_change['id'], sound_change.decode_contents())

    print(f'Finished parsing {len(branches)} branches and {len(rules)} rules.')

    with open('./data/branches.json', 'w+') as branches_file:
        branches_file.write(jsons.dumps(branches, { 'indent': 4, 'ensure_ascii': False }))

    with open('./data/rules.json', 'w+') as rules_file:
        rules_file.write(jsons.dumps(rules, { 'indent': 4, 'ensure_ascii': False }))

    with open('./data/branches.pkl', 'wb+') as branches_file:
        pickle.dump(branches, branches_file)

    with open('./data/rules.pkl', 'wb+') as rules_file:
        pickle.dump(rules, rules_file)

# So I can both run this individually AND import functions into my notebook
if __name__ == '__main__':
    parse_sid()