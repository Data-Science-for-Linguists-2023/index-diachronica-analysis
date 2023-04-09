# 2/12/23

Repo created, project plan filled out, other necessary files created.

# 1st Progress Report: 2/24/23

2/20: I didn't commit often enough and accidentally deleted my original `data_parsing.ipynb`, losing an hour or two of work.

2/23 - 2/24: I wrote the parser and refined it to the point that it gets through all the data without erroring! There are still improvements to be made, but it handles probably about 98% of the sound changes correctly. I've put a ton of information on this in [data_parsing.ipynb](data_parsing.ipynb). The output data can be found at [data/rules.json](data/rules.json) and [data/branches.json](data/branches.json), although they're pretty large files.

## Data sharing plan

All of my data will be included under [the data directory](data/), as it is licensed under CC BY-NC-SA 3.0, which allows the sharing of the data, as long as the shared data is also licensed under CC BY-NC-SA 3.0.

# 2nd Progress Report: 3/17/23

3/17: I made a few small improvements to the parsing to address some of the lingering problems I noted in my data parsing script before. I added some information about that at the end of the existing data parsing script.

3/21: I added an entirely new parsing step that pulls out vowel changes and the environments in which those vowel changes occurred. This is because I decided on a new area of analysis - seeing how vowel changes are affected by the neighboring consonants. This required using some additional libraries for getting information about IPA symbols, etc., as well. Information on this parsing is at the end of [data_parsing.ipynb](data_parsing.ipynb). I also started some basic analysis in [analysis.ipynb](analysis.ipynb), but haven't gotten very far in the vowel change analysis.

## Data sharing scheme

I am still sharing my data the way I said I would be in the first progress report.

## License

I went with the GNU GPLv3 license, as I am open to my code being re-used and modified as long as that re-use gives credit to my work.

# 3rd Progress Report: 4/9/23

First, I caught a bug in the vowel change script where characters where a diacritic was combined with the character as a single codepoint were not parsed correctly by ipapy. I had to use `unicodedata` to "normalize" strings and split characters like that into two characters. It also wasn't handling diacritics at all anyway, but that was an easy fix -- I had it treat the values of diacritics as modifiers. In the process of doing this, I realized that affricates weren't being treated as one sound, but were instead being split up (e.g. [ts] becomes [t] + [s]), but this is a limitation of the libraries I'm using and felt like too much work to be worth fixing.

My data files are updated to account for these changes in parsing.

I then did a more analysis, continuing in [analysis.ipynb](analysis.ipynb). I looked at the tendencies for different types of consonants to cause different types of changes in vowels using heatmaps. Still to-do is to look at how modifiers affect / are affected.