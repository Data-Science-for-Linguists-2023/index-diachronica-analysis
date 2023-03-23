from pytest_unordered import unordered
from gruut_ipa.phonemes import Phone
from ipapy.ipachar import IPAConsonant, IPAVowel, IPAChar
from ipapy.ipastring import IPAString
import vowel_changes as vc

def ipa_str_to_str(ipa_str: IPAString) -> str:
  return ''.join([char.unicode_repr for char in ipa_str.ipa_chars])

def phones_to_strs(phones: tuple[IPAString | None, ...]) -> list[str | None]:
  return [ipa_str_to_str(ipa_str) if ipa_str else None for ipa_str in phones[:4]]

def test_extract_long_vowel():
  phones = vc.extract_from_sound('Caːd')
  assert phones != None
  assert phones_to_strs(phones) == ['C', 'aː', 'd'] 

def test_extract_two_vowels():
  phones = vc.extract_from_sound('Caːde')
  assert phones == None

def test_extract_no_before():
  phones = vc.extract_from_sound('ef')
  assert phones != None
  assert phones_to_strs(phones) == [None, 'e', 'f']

def test_extract_no_after():
  phones = vc.extract_from_sound('fe')
  assert phones != None
  assert phones_to_strs(phones) == ['f', 'e', None]

def test_parse_environment_normal():
  assert vc.parse_environment('_d#') == unordered(['_d#'])

def parse_environment_one_optional():
  assert vc.parse_environment('_(l)d#') == unordered(['_d#', '_ld#'])

def test_parse_environment_mult_optionals():
  assert vc.parse_environment('(b)_(l)d#') == unordered(['_d#', '_ld#', 'b_d#', 'b_ld#'])

def test_parse_environment_bracketed():
  assert vc.parse_environment('_{l,d}#') == unordered(['_l#', '_d#'])

def test_parse_environment_multi_bracketed():
  assert vc.parse_environment('{l,d}_{l,d}#') == unordered(['l_l#', 'l_d#', 'd_l#', 'd_d#'])

def test_parse_environment_nested_bracketed():
  assert vc.parse_environment('_{{l,f},d}#') == unordered(['_l#', '_f#', '_d#'])

def test_extract_change_no_vowels():
  assert vc.extract_vowel_changes('ts', 's', '', '') == None

def test_extract_change_multi_vowels():
  assert vc.extract_vowel_changes('baːde', 'bode', '', '') == None

def test_extract_change_vowel_environment():
  assert vc.extract_vowel_changes('a', 'o', '_u', '') == None

def test_extract_change_no_env():
  phone_tuples = vc.extract_vowel_changes('baːd', 'bod', '', '')
  assert phone_tuples != None
  assert [phones_to_strs(phone_tup) for phone_tup in phone_tuples] == unordered([['b', 'aː', 'o', 'd']])

def test_extract_change_no_to_vowel():
  phone_tuples = vc.extract_vowel_changes('baːd', 'bd', '', '')
  assert phone_tuples != None
  assert [phones_to_strs(phone_tup) for phone_tup in phone_tuples] == unordered([['b', 'aː', None, 'd']])

def test_extract_change_env_before():
  phone_tuples = vc.extract_vowel_changes('aːd', 'od', 'f_', '')
  assert phone_tuples != None
  assert [phones_to_strs(phone_tup) for phone_tup in phone_tuples] == unordered([['f', 'aː', 'o', 'd']])

def test_extract_change_env_after():
  phone_tuples = vc.extract_vowel_changes('daː', 'do', '_f', '')
  assert phone_tuples != None
  assert [phones_to_strs(phone_tup) for phone_tup in phone_tuples] == unordered([['d', 'aː', 'o', 'f']])

def test_extract_change_mult_env():
  phone_tuples = vc.extract_vowel_changes('aː', 'o', '_{w,v}', '')
  assert phone_tuples != None
  assert [phones_to_strs(phone_tup) for phone_tup in phone_tuples] == unordered([[None, 'aː', 'o', 'w'], [None, 'aː', 'o', 'v']])

def test_extract_change_sq_bracket_sound():
  phone_tuples = vc.extract_vowel_changes('B', 'E', '', '')
  assert phone_tuples != None
  assert [phones_to_strs(phone_tup) for phone_tup in phone_tuples] == unordered([[None, 'B', 'E', None]])

def test_extract_change_sq_bracket_env():
  phone_tuples = vc.extract_vowel_changes('a', 'i', '#C_', '')
  assert phone_tuples != None
  assert [phones_to_strs(phone_tup) for phone_tup in phone_tuples] == unordered([['C', 'a', 'i', None]])

def test_extract_change_lots_of_optionals():
  phone_tuples = vc.extract_vowel_changes('aː', 'oː', '#(C)(C)(C)_(C)(C)(C)', '')
  assert phone_tuples != None
  assert [phones_to_strs(phone_tup) for phone_tup in phone_tuples] == unordered([['C', 'aː', 'oː', 'C'], [None, 'aː', 'oː', 'C'], ['C', 'aː', 'oː', None], [None, 'aː', 'oː', None]])