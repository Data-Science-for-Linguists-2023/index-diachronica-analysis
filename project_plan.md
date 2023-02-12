# Analysis of the *Index Diachronica*

I'm going to take the [Index Diachronica](https://chridd.nfshost.com/diachronica/all) and analyze it to get information about the frequency of different sound changes, find interesting paths of sound changes from combining different languages' sound changes, etc.

### Data

The data I'll use would be the *Index Diachronica*, a reference index of historical sound changes from old or proto-languages to modern languages. This was originally released in PDF form (as documented [here](http://galen.conlang.org/id.html)), but there is now an [online HTML version](https://chridd.nfshost.com/diachronica/all) that is much easier to parse. There are some errors in the data, which are documented in a [124-page PDF](https://drive.google.com/file/d/1veWbeZhXUZjUtGZZezyvCvF6BA103wS8/view?usp=sharing) (which also contains some clarifications, additions, and notes, all in fairly large font, which is why it's so huge), but I think those errors aren't so major that they would have a huge effect. (However, if I have some extra time, I may try to incorporate those changes.)

Parsing the data will be a lot of the effort of this project, but the data is generally in a well-defined format, which makes things a little easier. I can also simplify things by looking at only a subset of the data -- maybe simple changes only, excluding changes like `Vm → Vv → V[+nas]v / _V`.

### Analysis

I'd like to see what types of sound changes are most common, as well as what types of sound changes are very rare. Categorizing sound changes in a way that makes sense may be difficult, though. Looking at individual sound changes (e.g. from /e/) and seeing what's most common at that scale would be easier to do, but may be harder to make conclusions from.

It could also be interesting to try and do a "six degrees of Kevin Bacon"-style analysis, finding possible chains of sound changes from one given sound to another. Is there a chain of sound changes that could morph an /o/ into an /s/? Probably not, but I'm sure there are some weird connections out there. Putting these chains together into a sort of network graph and seeing whether clusters of sounds correspond to existing categories (e.g. front vowels, nasals, etc.) could also be an interesting avenue for analysis.

### Presentation

As I mentioned in the Analysis section, visualizing sound changes as a directed network graph could be very interesting, as well as labelling clusters. I could also probably make it interactive, so you could zoom in, etc.