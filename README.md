# news-image-20261123

[![make.fun bounty](https://img.shields.io/badge/make.fun-bounty-2b6cb0)](https://make.fun/bounty/news-image-20261123?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261123)
[![rank on make.fun](https://img.shields.io/badge/rank-make.fun%20leaderboard-38a169)](https://make.fun/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261123)
[![github](https://img.shields.io/badge/github-KenIDN24%2Fnews--image--20261123-24292e)](https://github.com/KenIDN24/news-image-20261123?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261123)

A one-page newspaper front page summing up the world's news of
**Monday, 23 November 2026**, drawn entirely in code.

## What it shows

Lead story: the COP31 climate summit in Antalya collapses with no
deal — the longest UN climate conference ever, ending without any
mention of fossil fuels. Also on the page: the Russian cargo ship
Sparta II still burning off Finland, 14 missing after a drone strike
near Kyiv, 50 missing after a candy-factory fire in Banten,
Indonesia, Nepal's PM meeting Modi in New Delhi, plus briefs on UN
lethal-AI talks, Seoul, Lisbon, Myanmar and the US House, and a
sport strip (Liverpool 4-0 Man Utd, India's record 720/9d, Wembanyama's 50).

See [SOURCES.md](SOURCES.md) for the reported facts behind every story.

## How it is built

`main.py` is pure Python 3 standard library. It draws the whole page
procedurally — a hand-written 5x7 bitmap font, flat vector shapes for
the globe, the ship and the flames — and writes a deterministic PNG
to `/output/entry.png`. No network, no randomness, no clock: two runs
produce byte-identical output.

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
```

Entry for the [make.fun](https://make.fun/bounty/news-image-20261123?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261123)
news-image-20261123 bounty ($100, top 50).
