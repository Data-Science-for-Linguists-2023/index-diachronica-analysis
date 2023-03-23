import pandas as pd
import numpy as np
from gruut_ipa.phonemes import Pronunciation, Phone
# Using my own fork, which adds some additional descriptors
from ipapy import UNICODE_TO_IPA
from ipapy.ipachar import IPAConsonant, IPAVowel, IPAChar, IPASuprasegmental
from ipapy.ipastring import IPAString
import re
import itertools
from data_parsing_script import Branch, Rule, remove_combos, handle_brackets
import pickle
from typing import cast

# add abbreviations from https://chridd.nfshost.com/diachronica/all#Abbreviations to UNICODE_TO_IPA
u_to_ipa_ext: dict[str, IPAChar] = UNICODE_TO_IPA.copy()
u_to_ipa_ext[u'A'] = IPAConsonant(name='affricate', voicing=u'anyv', place=u'anyp', manner=u'sibilant-affricate', unicode_repr=u'A')
u_to_ipa_ext[u'B'] = IPAVowel(name='back vowel', height=u'anyh', backness=u'back', roundness=u'anyr', unicode_repr=u'B')
u_to_ipa_ext[u'C'] = IPAConsonant(name='consonant', voicing=u'anyv', place=u'anyp', manner=u'anym', unicode_repr=u'C')
u_to_ipa_ext[u'D'] = IPAConsonant(name='voiced plosive', voicing=u'voiced', place=u'anyp', manner=u'plosive', unicode_repr=u'D')
u_to_ipa_ext[u'E'] = IPAVowel(name='front vowel', height=u'anyh', backness=u'front', roundness=u'anyr', unicode_repr=u'E')
u_to_ipa_ext[u'F'] = IPAConsonant(name='fricative', voicing=u'anyv', place=u'anyp', manner=u'sibilant-fricative', unicode_repr=u'F')
u_to_ipa_ext[u'H'] = IPAConsonant(name='laryngeal', voicing=u'anyv', place=u'laryngeal', manner=u'anym', unicode_repr=u'H')
u_to_ipa_ext[u'J'] = IPAConsonant(name='approximant', voicing=u'anyv', place=u'anyp', manner=u'approximant', unicode_repr=u'J')
u_to_ipa_ext[u'K'] = IPAConsonant(name='velar', voicing=u'anyv', place=u'velar', manner=u'anym', unicode_repr=u'K')
u_to_ipa_ext[u'Ḱ'] = IPAConsonant(name='palatal', voicing=u'anyv', place=u'palatal', manner=u'anym', unicode_repr=u'Ḱ')
u_to_ipa_ext[u'L'] = IPAConsonant(name='liquid', voicing=u'anyv', place=u'anyp', manner=u'liquid', unicode_repr=u'L')
u_to_ipa_ext[u'M'] = IPAVowel(name='diphthong', height=u'anyh', backness=u'anyb', roundness=u'anyr', modifiers=[u'diphthong'], unicode_repr=u'M')
u_to_ipa_ext[u'N'] = IPAConsonant(name='nasal', voicing=u'anyv', place=u'anyp', manner=u'nasal', unicode_repr=u'N')
u_to_ipa_ext[u'O'] = IPAConsonant(name='obstruent', voicing=u'anyv', place=u'anyp', manner=u'obstruent', unicode_repr=u'O')
u_to_ipa_ext[u'P'] = IPAConsonant(name='labial/bilabial', voicing=u'anyv', place=u'bilabial', manner=u'anym', unicode_repr=u'O')
u_to_ipa_ext[u'Q'] = IPAConsonant(name='uvular (click in Khoisan)', voicing=u'anyv', place=u'uvular', manner=u'anym', unicode_repr=u'Q')
u_to_ipa_ext[u'R'] = IPAConsonant(name='resonant/sonorant', voicing=u'anyv', place=u'anyp', manner=u'sonorant', unicode_repr=u'R')
u_to_ipa_ext[u'S'] = IPAConsonant(name='plosive', voicing=u'anyv', place=u'anyp', manner=u'plosive', unicode_repr=u'S')
u_to_ipa_ext[u'V'] = IPAVowel(name='vowel', height=u'anyh', backness=u'anyb', roundness=u'anyr', unicode_repr=u'V')
u_to_ipa_ext[u'W'] = IPAConsonant(name='semivowel/glide', voicing=u'anyv', place=u'anyp', manner=u'glide', unicode_repr=u'W')
u_to_ipa_ext[u'Z'] = IPAConsonant(name='continuant', voicing=u'anyv', place=u'anyp', manner=u'continuant', unicode_repr=u'Z')

def replace_abbreviations(sound: str, vowels_only: bool = False) -> tuple[str, list[str]]:
  """Replaces abbreviations in a sound with indices to be replaced back and handled later"""
  replaced = []
  # maybe handle brackets later
  for char in sound:
    if char.isupper() and (char in u_to_ipa_ext):
      if (not vowels_only) or u_to_ipa_ext[char].is_vowel:
        sound = sound.replace(char, str(len(replaced)))
        replaced.append(char)
        
  return (sound, replaced)

def phone_to_ipastring(phone: Phone, replacements: list[str] = []) -> IPAString | None:
  ipachars: list[IPAChar] = []
  for char in phone.text:
    if char.isdecimal():
      ipachars.append(u_to_ipa_ext[replacements[int(char)]])
    elif char in u_to_ipa_ext:
      ipachars.append(u_to_ipa_ext[char])
  if len(ipachars) == 0:
    return None
  return IPAString(ipachars)

def extract_from_sound(sound: str) -> tuple[IPAString | None, IPAString | None, IPAString | None] | None:
  sound = re.sub(pattern=r'\[.+?\]', repl='', string=sound)
  (abbev_parsed_sound, replacements) = replace_abbreviations(sound, True)
  pron = Pronunciation.from_string(abbev_parsed_sound)
  # print(pron)
  before = None
  vowel = None
  after = None
  for index, phone in enumerate(pron.phones):
    if phone.is_vowel or phone.text.isnumeric():
      if vowel != None:
        # multiple vowels, bail!!
        return None
      
      if index > 0:
        before = phone_to_ipastring(pron.phones[index - 1], replacements)

      if index < (len(pron.phones) - 1):
        after = phone_to_ipastring(pron.phones[index + 1], replacements)
      
      vowel = phone_to_ipastring(phone, replacements)

  return (before, vowel, after)

def parse_environment(environment: str) -> list[str]:
  environments: list[str] = []
  
  optionals = [(match.start(), match.end(), match.group(0)) for match in re.finditer(r'(\(.*?\))', environment)]
  if optionals:
    combinations = list(itertools.chain.from_iterable(itertools.combinations(optionals, l) for l in range(len(optionals) + 1)))
    for combo in combinations:
      combo_string = environment
      # print(combo)
      combo_string = remove_combos(combo_string, combo)
      combo_string = combo_string.replace('(','').replace(')','')
      # print(combo_string)
      environments += handle_brackets(combo_string)
  else:
    # print(environment)
    environments += handle_brackets(environment)
  
  return environments

def extract_from_environment(environment: str) -> tuple[IPAString | None, IPAString | None] | None:
  environment = re.sub(r'/\[.+?\]', '', environment)
  (abbev_parsed_environment, replacements) = replace_abbreviations(environment)
  pron = Pronunciation.from_string(abbev_parsed_environment)
  before = None
  after = None
  found = False
  for index, phone in enumerate(pron.phones):
    if phone.text == '_':
      if found:
        # multiple spaces, bail!!
        return None
      
      if index > 0:
        if pron.phones[index - 1].is_vowel:
          return None # ignore environments where before/after a vowel
        before = phone_to_ipastring(pron.phones[index - 1], replacements)

      if index < (len(pron.phones) - 1):
        if pron.phones[index + 1].is_vowel:
          return None # ignore environments where before/after a vowel
        after = phone_to_ipastring(pron.phones[index + 1], replacements)
      
      found = True
  
  return (before, after)

def extract_vowel_changes(from_sound: str, to_sound: str, environment: str, original_text: str) -> list[tuple[IPAString | None, IPAString, IPAString | None, IPAString | None, str]] | None:
  from_tuple = extract_from_sound(from_sound)
  if from_tuple == None:
    return None
  before, from_vowel, after = from_tuple
  if from_vowel == None:
    return None

  to_tuple = extract_from_sound(to_sound)
  if to_tuple == None:
    return None
  _, to_vowel, _ = to_tuple

  if (before == None) or (after == None):
    changes = []
    for parsed_env in parse_environment(environment):
      env_extract = extract_from_environment(parsed_env)
      if env_extract:
        env_before, env_after = env_extract
        if before:
          env_before = before
        if after:
          env_after = after
        change_tup = (env_before, from_vowel, to_vowel, env_after, original_text)
        if not any(str(change) == str(change_tup) for change in changes):
          changes.append((env_before, from_vowel, to_vowel, env_after, original_text))
    if len(changes) == 0:
      return None
    return changes
  else:
    return [(before, from_vowel, to_vowel, after, original_text)]

def get_cons_feats(row, col: str) -> tuple[str | None, str | None, str | None, list[str] | None]:
  voicing: str = ''
  place: str = ''
  manner: str = ''
  modifiers: list[str] = []

  consonant: IPAString = row[col]

  if not consonant:
    return (None, None, None, None)

  chars: list[IPAChar] = consonant.ipa_chars
  for char in chars:
    if char.is_consonant:
      voicing = cast(IPAConsonant, char).voicing
      place = cast(IPAConsonant, char).place
      manner = cast(IPAConsonant, char).manner
      modifiers = cast(IPAConsonant, char).modifiers
  
  return (voicing, place, manner, modifiers)


def get_vowel_feats(row, col: str) -> tuple[str | None, str | None, str | None, list[str] | None, str | None]:
  height: str = ''
  backness: str = ''
  roundness: str = ''
  modifiers: list[str] = []
  length: str = ''

  vowel: IPAString = row[col]

  if not vowel:
    return (None, None, None, None, None)

  chars: list[IPAChar] = vowel.ipa_chars
  for char in chars:
    if char.is_vowel:
      height = cast(IPAVowel, char).height
      backness = cast(IPAVowel, char).backness
      roundness = cast(IPAVowel, char).roundness
      modifiers = cast(IPAVowel, char).modifiers
    elif char.is_suprasegmental:
      length = cast(IPASuprasegmental, char).length or ''
  
  return (height, backness, roundness, modifiers, length)


def run_extraction():
  rules: list[Rule] = pd.read_pickle('./data/rules.pkl')
  rules_df = pd.DataFrame.from_records([vars(rule) for rule in rules])

  extract_vowel_changes_vec = np.vectorize(extract_vowel_changes)
  extracted = extract_vowel_changes_vec(rules_df['from_sound'], rules_df['to_sound'], rules_df['environment'], rules_df['original_text'])
  extracted = extracted[extracted != None]
  extracted_flat = [item for sublist in extracted for item in sublist]
  extracted_df = pd.DataFrame(extracted_flat, columns=['before', 'from_vowel', 'to_vowel', 'after', 'original_text'])

  # Add columns for individual features of vowels
  extracted_df[['before_voicing', 'before_place', 'before_manner', 'before_modifiers']] = extracted_df.apply(get_cons_feats, axis=1, result_type='expand', col='before')
  extracted_df[['from_height', 'from_backness', 'from_roundness', 'from_modifiers', 'from_length']] = extracted_df.apply(get_vowel_feats, axis=1, result_type='expand', col='from_vowel')
  extracted_df[['to_height', 'to_backness', 'to_roundness', 'to_modifiers', 'to_length']] = extracted_df.apply(get_vowel_feats, axis=1, result_type='expand', col='to_vowel')
  extracted_df[['after_voicing', 'after_place', 'after_manner', 'after_modifiers']] = extracted_df.apply(get_cons_feats, axis=1, result_type='expand', col='after')

  print(extracted_df.describe())

  with open('./data/vowel_changes.pkl', 'wb+') as vowel_changes_file:
    pickle.dump(extracted_df, vowel_changes_file)

# So I can both run this individually AND import functions into my notebook
if __name__ == '__main__':
  run_extraction()