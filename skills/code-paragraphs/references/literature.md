# Literature & sources

Provenance for rules in [SKILL.md](../SKILL.md). Same principles arrived at independently by craft authors, language designers, cognitive psychologists, empirical researchers - convergence makes them worth following.

Authors disagree (sharply, about blank lines inside functions) - both sides presented fairly.

## 1. Unifying principle: code is for humans

Every later rule descends from this:

- **Donald Knuth** (1984, _Literate Programming_) - _"Let us change our traditional attitude to the construction of programs: instead of imagining that our main task is to instruct a computer what to do, let us concentrate rather on explaining to human beings what we want a computer to do."_
- **Martin Fowler**, _Refactoring_ - _"Any fool can write code that a computer can understand. Good programmers write code that humans can understand."_
- **Guido van Rossum** (PEP 8) - _"code is read much more often than it is written."_

> PEP 20 (_Zen of Python_): **"Readability counts."**

## 2. Vertical whitespace: blank lines as paragraph breaks

Mainstream pro-blank position. Doctrine behind every "group fields by role" rule in [`go.md`](./go.md):

- **Robert C. Martin**, _Clean Code_ Ch. 5 - names five concepts: **Vertical Openness Between Concepts, Vertical Density, Vertical Distance, Vertical Ordering, Newspaper Metaphor**. _"Each line represents an expression or clause, and each group of lines represents a complete thought. Those thoughts should be separated from one another with blank lines."_
- **Steve McConnell**, _Code Complete_ 2e, Ch. 31 - **Fundamental Theorem of Formatting**: _"good visual layout shows the logical structure of a program."_ Ties to Gestalt chunking research from 1980s-90s.
- **PEP 8** (Python) - _"Surround top-level function and class definitions with two blank lines. Method definitions inside a class are surrounded by a single blank line. ... Use blank lines in functions, sparingly, to indicate logical sections."_ Note _sparingly_.

## 3. The counterargument: "an empty line is a code smell"

Minority position - but consistent with "small functions" doctrine. Worth understanding before citing Martin:

- **Yegor Bugayenko**, _An Empty Line is a Code Smell_ (2014) - _"A method should not contain 'parts.' A method should always do one thing and its functional decomposition should be done by language constructs (for example, new methods), and never by empty lines."_ Recommends teams _"prohibit them in your automated build."_ - https://www.yegor256.com/2014/11/03/empty-line-code-smell.html
- **Maximiliano Contieri**, _Code Smell 74 - Empty Lines_ - _"Empty lines are harmless, but show us an opportunity to break the code into small steps."_ - https://dev.to/mcsee/code-smell-74-empty-lines-467h
- **Robert C. Martin (steel-manned)** - Martin no bans internal blanks, but his ideal: function _small enough not to need them_. "Anti-blank" camp = extension of Martin's own _"functions should do one thing."_

### Pro-long-function defense: John Carmack

- **John Carmack**, inlining email (13 Mar 2007, re-published with 2014 addendum by Jonathan Blow) - _"If everything is just run out in a 2000 line function, it is obvious which part happens first."_ Aggressive Extract Method _reduces_ readability by hiding state-flow across tiny helpers. Blank-line-separated paragraph in long function = _correct_ tool. - https://cbarrete.com/carmack.html and http://number-none.com/blow/blog/programming/2014/09/26/carmack-on-inlined-code.html

### How to use this debate

- Functions short (\<20 lines, intention-revealing names) -> blanks inside genuinely rare; Bugayenko's rule workable.
- Long imperative bodies legitimate (game loops, hot paths) -> blank-line paragraphs _better_ than fake helpers.
- **PEP 8 compromise** ("use sparingly to indicate logical sections") = working majority view: permitted, but each blank should ask _"could this be a function?"_

## 4. Vertical ordering: high to low

- **Newspaper Metaphor** (Martin) + **Stepdown Rule** (Martin; Kent Beck, _Smalltalk Best Practice Patterns_) - reader skims top-to-bottom, sees decreasing abstraction. Public API at top, private helpers below; caller above callee.
- **goimports / isort / PEP 8** - same idea for imports: stdlib -> third-party -> local, blanks between groups, alphabetical within.

## 5. Horizontal whitespace: formatter owns it

- **Robert C. Martin** - explicit rejection of forced column alignment: _"I found that alignment was not useful. The alignment seemed to emphasize the wrong things and led my eye away from the true intent."_
- **Rob Pike**, Go Proverbs (Gopherfest SV 2015) - _"Gofmt's style is no one's favorite, yet gofmt is everyone's favorite."_ - https://github.com/wayneashleyberry/go-proverbs/blob/main/go-proverbs.go
- **Effective Go** - _"With Go we take an unusual approach and let the machine take care of most formatting issues. ... there's no need to spend time lining up the comments on the fields of a structure. Gofmt will do that for you."_

### Linus Torvalds: whitespace as design constraint

Linux coding style = most opinionated mainstream document on whitespace, most polemical:

- **Indentation = 8-char tabs.** _"Tabs are 8 characters, and thus indentations are also 8 characters. There are heretic movements that try to make indentations 4 (or even 2!) characters deep, and that is akin to trying to define the value of PI to be 3."_
- **Deep indents force refactoring.** _"if you need more than 3 levels of indentation, you're screwed anyway, and should fix your program."_ - clearest example of whitespace as _design constraint_, not decoration.
- **Between functions: one blank.** Short, clean, no ceremony.

Source - https://www.kernel.org/doc/html/v4.10/process/coding-style.html

## 6. Naming complements layout

- **Phil Karlton** (popularised by Fowler) - _"There are only two hard things in Computer Science: cache invalidation and naming things."_ Naming = load-bearing complement to whitespace: good name replaces both blank and comment. - https://martinfowler.com/bliki/TwoHardThings.html
- **Kent Beck** - _Composed Method_ + _Intention-Revealing Selector_ (_Smalltalk Best Practice Patterns_): small methods with names that say what they do > commented or blank-broken block. _"Most importantly, one line methods are there to communicate."_
- **Kernighan & Plauger**, _The Elements of Programming Style_ (1978) - _"Don't comment bad code - rewrite it."_ Blank-line-plus-comment introducing paragraph -> paragraph wants to be Extract Method.

## 7. Empirical & cognitive evidence

Empirical record thinner than prescriptive literature - but where exists, points same direction:

- **Buse & Weimer**, _Learning a Metric for Code Readability_, IEEE TSE 36(4):546-558, 2010 - 120 annotators x 100 Java snippets. Trained model _"80% effective, and better than a human on average, at predicting readability judgments."_ Strongest features: _characters per line_ (100% rel. power), _identifiers per line_ (96%). **Blank-line count = strong positive predictor** - explicitly more important than comment count (33%). _Caveat (often dropped):_ model descriptive; sprinkling blanks no cause readability. - https://web.eecs.umich.edu/~weimerw/p/weimer-tse2010-readability-preprint.pdf
- **Scalabrino et al.**, _A Comprehensive Model for Code Readability_, JSEP 30(6), 2018 - added textual/semantic features to Buse & Weimer; combined model significantly outperforms structural-only. Layout matters; naming + conceptual coherence matter _at least_ as much.
- **Indentation effect, mixed:** Miara et al. (CACM, 1983) found 2-4 spaces optimal on Pascal; Bauer et al. (ICPC 2019, eye-tracking, n=22) failed replicate, called indentation _"a purely stylistic choice in modern programming languages such as Java"_; **Morzeck et al. (ICSoft 2023)** RCT found non-indented Java required **179% more reading time** (p < .001, η² = .832).
- **Eye-tracking, expert vs novice** - Busjahn et al. (ICPC 2015) - _"experts read code less linearly than novices."_ Retroactively justifies Newspaper Metaphor as _novice-friendly_ affordance: structural cues matter most for readers who need them most.

### Cognitive basis

- **Gestalt Law of Proximity** - elements close together perceived as group; separated perceived as distinct. Blanks literally apply proximity to code; grouped struct fields, grouped imports, paragraph-separated statements exploit same wiring. McConnell cites explicitly; Martin invokes implicitly with "Vertical Openness Between Concepts."
- **Miller's 7±2** working-memory limit - standard explanation for why authors converge on ~5-10 line chunks as readable function size.

## 8. Style-guide alignment

| Guide                | Top-level separators            | Inside functions                    | Imports                                 |
| -------------------- | ------------------------------- | ----------------------------------- | --------------------------------------- |
| PEP 8 (Python)       | 2 blank lines                   | sparingly, for logical sections     | 3 groups, blanks between                |
| Google Java/JS/TS    | 1 blank between members         | encouraged between logical sections | grouped, no blanks within               |
| Linux kernel C       | 1 blank between functions       | yes, between logical blocks         | n/a                                     |
| Effective Go / gofmt | 1 blank between top-level decls | tool-controlled                     | goimports: stdlib / third-party / local |
| Airbnb JS            | blank between blocks            | yes                                 | grouped by source                       |

Numbers differ; **abstract pattern identical**: two-level vertical hierarchy (bigger gap between bigger units; smaller between smaller) + semantic grouping with blank-line gutters between groups.

## Honest caveats

- **Most literature prescriptive, not empirical.** Martin, Beck, McConnell, Fowler synthesise expert experience; authority = craft, not lab-tested fact.
- **Buse & Weimer correlation ≠ causation.** Cleaner code also coded by people who think about whitespace; inserting blanks mechanically no produce readable code.
- **Cultural norms differ.** Linux kernel C, Python notebooks, React TSX legitimately have different vertical rhythms; universals _abstract_ (group by meaning, order top-down) - _numbers_ travel less well.
- **Sandi Metz rules heuristic, not law.** Metz herself (Bike Shed LIVE!, RailsConf 2016): rules were _"an antidote for a very specific, bad situation"_ - 5,000-line ActiveRecord models - no universal. Explicit Rule 6 ("can break any rule if pair agrees") part of rule set.
- **Torvalds linked-list "good taste" = eliminating special cases, not whitespace.** Often misquoted - cite for structural clarity, not formatting.

## Further reading

### Books

- Robert C. Martin, _Clean Code_ (Ch. 5: Formatting)
- Steve McConnell, _Code Complete_ 2e (Ch. 31: Layout and Style)
- Kent Beck, _Smalltalk Best Practice Patterns_ (Composed Method, Intention-Revealing Selector)
- Kernighan & Plauger, _The Elements of Programming Style_ (1978)
- Martin Fowler, _Refactoring_ (Extract Method)

### Papers

- Buse & Weimer, _Learning a Metric for Code Readability_, IEEE TSE 2010 - https://web.eecs.umich.edu/~weimerw/p/weimer-tse2010-readability-preprint.pdf
- Scalabrino et al., _A Comprehensive Model for Code Readability_, JSEP 2018
- Miara et al., _Program Indentation and Comprehensibility_, CACM 1983
- Bauer et al., _Indentation: Simply a Matter of Style or Support for Program Comprehension?_, ICPC 2019
- Busjahn et al., _Eye Movements in Code Reading: Relaxing the Linear Order_, ICPC 2015

### Online

- Linux kernel coding style - https://www.kernel.org/doc/html/v4.10/process/coding-style.html
- Go Proverbs - https://github.com/wayneashleyberry/go-proverbs/blob/main/go-proverbs.go
- Effective Go - https://go.dev/doc/effective_go
- PEP 8 - https://peps.python.org/pep-0008/
- Yegor Bugayenko, _An Empty Line is a Code Smell_ - https://www.yegor256.com/2014/11/03/empty-line-code-smell.html
- Maximiliano Contieri, _Code Smell 74 - Empty Lines_ - https://dev.to/mcsee/code-smell-74-empty-lines-467h
- John Carmack on inlining - https://cbarrete.com/carmack.html
- Martin Fowler, _Two Hard Things_ - https://martinfowler.com/bliki/TwoHardThings.html
