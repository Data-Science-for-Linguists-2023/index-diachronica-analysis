from pytest_unordered import unordered
import data_parsing_script as dps

def test_remove_combos():
  assert dps.remove_combos('abcabcabc', ((0, 1, 'a'), (6, 7, 'a'), (4, 6, 'bc'), (1, 2, 'b'))) == 'cabc'

def test_handle_brackets_multiple():
  assert dps.handle_brackets('{e,i}w{e,i}') == set(['ewe', 'iwe', 'ewi', 'iwi'])

def test_handle_brackets_nested():
  assert dps.handle_brackets('{e,w{æ,i}}') == set(['e', 'wæ', 'wi'])

def test_parse_basic_match():
  assert dps.parse_rule_steps('z zː → j dʒː') == unordered([('z', [], 'j'), ('zː', [], 'dʒː')])

def test_parse_square_bracketed():
  assert dps.parse_rule_steps('S → [+ voice]') == unordered([('S', [], '[+ voice]')])

def test_parse_stray_leading_dash():
  assert dps.parse_rule_steps('— j w → i u') == unordered([('j', [], 'i'), ('w', [], 'u')])

def test_parse_square_bracketed_modifier():
  assert dps.parse_rule_steps('V[- high - long] → ∅') == unordered([('V[- high - long]', [], '∅')])

def test_parse_curly_brackets():
  assert dps.parse_rule_steps('{s3,ʒ} → ʃ') == unordered([('s3', [], 'ʃ'), ('ʒ', [], 'ʃ')])

def test_parse_optional_step():
  parsed_change = dps.parse_sound_change('ew (→ øj) → yj', '', '')
  assert len(parsed_change) == 2
  assert parsed_change[0].from_sound == 'ew'
  assert parsed_change[0].intermediate_steps == unordered(['øj'])
  assert parsed_change[0].to_sound == 'yj'
  assert parsed_change[1].from_sound == 'ew'
  assert parsed_change[1].intermediate_steps == unordered([])
  assert parsed_change[1].to_sound == 'yj'

def test_parse_optional_step():
  parsed_change = dps.parse_sound_change('ew (→ øj) → yj', '', '')
  assert len(parsed_change) == 2
  assert parsed_change[0].from_sound == 'ew'
  assert parsed_change[0].intermediate_steps == unordered(['øj'])
  assert parsed_change[0].to_sound == 'yj'
  assert parsed_change[1].from_sound == 'ew'
  assert parsed_change[1].intermediate_steps == unordered([])
  assert parsed_change[1].to_sound == 'yj'

def test_parse_optional_sounds():
  parsed_change = dps.parse_sound_change('(C)x(C) → (C)a(C)', '', '')
  change_tuples = [(rule.from_sound, rule.intermediate_steps, rule.to_sound) for rule in parsed_change]
  assert change_tuples.count(('CxC', [], 'CaC'))
  assert change_tuples.count(('CxC', [], 'Ca'))
  assert change_tuples.count(('CxC', [], 'aC'))
  assert change_tuples.count(('CxC', [], 'a'))
  assert change_tuples.count(('Cx', [], 'CaC'))
  assert change_tuples.count(('Cx', [], 'Ca'))
  assert change_tuples.count(('Cx', [], 'aC'))
  assert change_tuples.count(('Cx', [], 'a'))
  assert change_tuples.count(('xC', [], 'CaC'))
  assert change_tuples.count(('xC', [], 'Ca'))
  assert change_tuples.count(('xC', [], 'aC'))
  assert change_tuples.count(('xC', [], 'a'))
  assert change_tuples.count(('x', [], 'CaC'))
  assert change_tuples.count(('x', [], 'Ca'))
  assert change_tuples.count(('x', [], 'aC'))
  assert change_tuples.count(('x', [], 'a'))

def test_parse_curly_bracket_to():
  parsed_change = dps.parse_sound_change('rdʒ → {rdʒ,rdz}', '', '')
  change_tuples = [(rule.from_sound, rule.intermediate_steps, rule.to_sound) for rule in parsed_change]
  assert change_tuples.count(('rdʒ', [], 'rdʒ'))
  assert change_tuples.count(('rdʒ', [], 'rdz'))

def test_parse_extra_text():
  parsed_change = dps.parse_sound_change('d ɡ → t k (may have been part of a more sweeping merger; Firespeaker calls it “lenis-fortis”)', '', '')
  change_tuples = [(rule.from_sound, rule.intermediate_steps, rule.to_sound) for rule in parsed_change]
  assert change_tuples.count(('d', [], 't'))
  assert change_tuples.count(('ɡ', [], 'k'))

def test_parse_ignore_backticked():
  parsed_change = dps.parse_sound_change('r → *L `(some sort of lateral?)` / occasionally', '', '')
  change_tuples = [(rule.from_sound, rule.intermediate_steps, rule.to_sound) for rule in parsed_change]
  assert change_tuples.count(('r', [], '*L'))

def test_parse_partial_curly_bracket():
  parsed_change = dps.parse_sound_change('{æ,e}i → eː', '', '')
  change_tuples = [(rule.from_sound, rule.intermediate_steps, rule.to_sound) for rule in parsed_change]
  assert change_tuples.count(('æi', [], 'eː'))
  assert change_tuples.count(('ei', [], 'eː'))

def test_parse_nested_curly_brackets():
  parsed_change = dps.parse_sound_change('{e,w{æ,i}} → ø', '', '')
  change_tuples = [(rule.from_sound, rule.intermediate_steps, rule.to_sound) for rule in parsed_change]
  assert change_tuples.count(('e', [], 'ø'))
  assert change_tuples.count(('wæ', [], 'ø'))
  assert change_tuples.count(('wi', [], 'ø'))