from bs4 import BeautifulSoup
from bs4.element import ResultSet, Tag
import re
import jsons

class Rule:
    id: str # Proto-Omotic-dʒ
    branch_id: str # Proto-Omotic
    from_sound: list[str] # ['dʒ']
    intermediate_steps: list[list[str]] # [['tʃ ']]
    to_sound: list[str] # ['ʃ']
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

with open('./data/sid-tidy.html') as fp:
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
        rule = Rule()

        rule.id = sound_change['id']
        rule.original_text = sound_change.decode_contents()

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
                # leave out anything else weird, for now
        
        rule_string = ''.join(rule_parts)

        # Split the rule up. This will inevitably include stuff I don't want but we can work out how to remove that stuff later
        # First split by the environment separator
        env_split = rule_string.split(" / ", 1)

        if len(env_split) > 1:
            rule.environment = env_split[1]
        else:
            # If no environment, but rule ends with some text in parentheses, consider that the environment
            parens_match = re.search(r'(.+) (\(.+\))$', rule_string)
            if parens_match:
                env_split[0] = parens_match.group(1)
                rule.environment = parens_match.group(2)

        # Then split by the rule step separator
        rule_split = [s.strip() for s in env_split[0].split("→")]

        if len(rule_split) < 2:
            raise Exception(f"Too few steps in rule: {rule_string}")
        
        if len(rule_split) > 2:
            rule.from_sound = rule_split[0].split(' ')
            rule.intermediates = [substr.split(' ') for substr in rule_split[1:-1]]
            rule.to_sound = rule_split[-1].split(' ')
        else:
            rule.from_sound = rule_split[0].split(' ')
            rule.to_sound = rule_split[1].split(' ')

        rules.append(rule)


with open('./data/branches.json', 'w+') as branches_file:
    branches_file.write(jsons.dumps(branches, { 'indent': 4, 'ensure_ascii': False }))

with open('./data/rules.json', 'w+') as rules_file:
    rules_file.write(jsons.dumps(rules, { 'indent': 4, 'ensure_ascii': False }))