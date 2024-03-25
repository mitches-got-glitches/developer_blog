---
date: 2024-03-25
categories:
  - devtools
  - pre-commit
authors:
  - mitches-got-glitches
comments: true
---

# Migrating to `ruff` from `black` and `flake8`

When it comes to linting and formatting Python code, [`ruff`][ruff] is the ultimate swiss army
knife. So next time you venture out into the wilderness of enterprise code bases leave your `black`,
`flake8`, `isort` and `pydocstyle` at home.

<figure markdown="span">
  ![Swiss Army Knife](https://media.wired.com/photos/5b44fed89bc3f356f40592fb/master/w_1600,c_limit/knife2.jpg){ width="400" }
</figure>

<!-- more -->

You can even forget all those plugin attachments for your `flake8`. Yes, `ruff` really does do it
all. There may be a few gaps but they're being plugged faster than you can list all the linting and
formatting tools you had to have before.

And did I mention it was built in rust? This means it's pretty damn fast, even on large monorepo
code bases. So this coupled with fewer dependencies being installed on each CI pipeline run could
potentially save a lot of time over the course of a long project.

But is it painful to switch over? That's what I endeavored to find out by having a go at migrating
to `ruff` in the [`dynaconf`](https://github.com/dynaconf/dynaconf) code base. Why? `dynaconf` wants
a way to standardise docstrings which `ruff` offers - it seemed like a good opportunity to introduce
it for its other linting and formatting capabilities before switching on the docstring checks.

The aim was to keep the formatting as close as possible to the previous configuration, at least as a
start. [Here's the resulting PR][ruff-PR] that was merged (success! 🎉), so let me talk you through
what I learned.

!!! tip
    Add `ruff` to your dev dependencies group so it can be installed and run with your CI pipeline.
    But if you want to avoid installing it in every single one of your virtual environments, you can
    use [`pipx`](https://pipx.pypa.io/). Installing with `pipx` will put `ruff` in an isolated
    virtual environment and add the binaries into a folder that `pipx` has appended to your path.
    This means that you can use CLI tools like `ruff` anywhere, even in your virtual environments,
    with a single install.

## Migration Notes

### Settings file

`dynaconf` doesn't have a `pyproject.toml` file in the code base yet, so I decided to implement
`ruff` in its own config file `ruff.toml`. You can see the [difference between the two options
here][diff-ruff-configs].

```py title="ruff.toml"
--8<-- "https://raw.githubusercontent.com/dynaconf/dynaconf/abb9a7533b164b2b6fe578f6227eca759c475a6d/ruff.toml:0:4"
```

### Line length

Line length in the `dynaconf` code base was set to 79, applying PEP8 more strictly than `black`'s
more forgiving default of 88. I wanted to keep this consistent, and this was easily set at the top
level of the config file.

There were a couple of changes though which needed a bit of explaining:

- [This change][emoji-line-change] where a line with an emoji was moved onto a single line whereas
  previously it was broken across 3. This is because `ruff` [looks at the Unicode
  width][unicode-width] rather than the character width. I think this means that the unicode width
  of this emoji 🎛️ is 1, whereas the character length may be the length of this: `:control_knobs:`.
- [This change][pragma-line-change] where a line with a pragma comment (`#type`, `# noqa`, etc.) is
  moved is explained by [this reasoning][pragma-reasoning]. Basically `ruff` doesn't move pragma
  comments around as this can change their behaviour.

### Use `extend-select` rather than `select`

Using `select` overwrites the default rules(1) with your specified rules rather than extending them.
Therefore, it's better to use `extend-select` rather than repeating the defaults followed by your
specific rules in `select`.
{ .annotate }

1. From ruff docs:
   > By default, Ruff enables Flake8's F rules, along with a subset of the E rules, (`["E4", "E7",
   > "E9", "F"]`) omitting any stylistic rules that overlap with the use of a formatter, like ruff
   > format or Black.

I used this to specify the various plugins and additional tools that were being used in `dynaconf` -
so `ruff` has replaced 6 additional packages on top of `black` and `flake8`!


```py title="ruff.toml"
--8<-- "https://raw.githubusercontent.com/dynaconf/dynaconf/abb9a7533b164b2b6fe578f6227eca759c475a6d/ruff.toml:6:14"
```

### Use `per-file-ignores` rather than a blanket `ignore`

You also want to avoid nesting config files in sub-directories to implement this -
`per-file-ignores` is the way to go. This feature was available in `flake8` and it's great to see it
ported over. Using this allowed us to be less strict in some areas in the test sub-directories, and
to also to ignore some rules in `__init__.py` files that we would want to apply elsewhere.

```py title="ruff.toml"
--8<-- "https://raw.githubusercontent.com/dynaconf/dynaconf/abb9a7533b164b2b6fe578f6227eca759c475a6d/ruff.toml:23:38"
```

!!! note
    I think just `__init__.py` works in the same way as `*/__init__.py` here.

Initially I implemented the nested config files. If you want to see the difference, you can see what
I removed on [this commit][nested-config-removal].

### Mimicking current import sort behaviour in `dynaconf`

I added a few configurations to the `[lint.isort]` section:

```yaml title="ruff.toml"
[lint.isort]
force-single-line = true
order-by-type = false
required-imports = ["from __future__ import annotations"]
known-first-party = ["dynaconf"]
```

- `force-single-line = true` because this is what `dyanconf` had already. It basically forces each
  individual import onto its own line rather than bundling them together. Although this results in
  more lines, it can result in clearer diffs if imports are added or removed in the future (although
  GitHub is quite good now at showing which part of the line has changed).
- `order-by-type = false` to force pure alphabetical sorting rather than grouping functions, classes
  and constants and sorting alphabetically within each group. This was just what was done before.
- `required-imports = ["from __future__ import annotations"]` will add this import to the top of
  every file. `dynaconf` had another tool doing this before.
- `known-first-party = ["dynaconf"]` means that when importing parts of the packages own API in the
  test scripts, these imports are sorted as first party rather than being bundled in with the third
  party libraries which happens when it's not set.

### Sorting imports currently needs another pre-commit hook

[This part of the `ruff` docs][pre-commit-integration] tells you the options for setting up
`pre-commit` hooks. However, the `ruff` [formatter currently doesn't sort imports][sorting-imports]
out of the box - you have to use this command: `ruff check --select I --fix`. It does say that a
unified command for both linting and formatting is in the works though.

```yaml title=".pre-commit-config.yaml"
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
  # Ruff version.
  rev: v0.3.0
  hooks:
    # Sort imports.
    - id: ruff # (2)!
      name: ruff-sort-imports # (1)!
      args: [--select, I, --fix]
    # Run the linter.
    - id: ruff
    # Run the formatter.
    - id: ruff-format
```

1. This will differentiate it from the following call when the hooks are run. I actually forgot to
   add this in the PR!
2. Runs `ruff check`.

Quite a few hooks were removed in `dynaconf`'s `.pre-commit-config.yaml` to be replaced with `ruff`.
You can [view the full changes here][pre-commit-changes].

### Vertical whitespace

`ruff` seems to favour adding an extra blank line after module level docstrings which seems to be a
bit of a deviation from `black`.

### Other deviations

There is [a good section in the docs][ruff-black] highlighting all known deviations from `black`.
And they also have a [list of unintentional deviations][unintentional-deviations] in their issue
tracker, including [this one](https://github.com/astral-sh/ruff/issues/10186) which [came up in the
`dynaconf` changes][ellipsis-oneline].

## Future

Switching on the docstring checks! `ruff` [supports multiple docstring conventions][ruff-docstring].
Most projects I see these days prefer the Google convention, as do I, and here's the simplest setup:

```toml title="ruff.toml"
[tool.ruff.lint]
# Enable all `pydocstyle` rules, limiting to those that adhere to the
# Google convention via `convention = "google"`, below.
extend-select = ["D"]

[lint.pydocstyle]
convention = "google"
```

I'm planning to sweep over the `Dynaconf` code base at some point to apply these rules. I'll put a
link to this commit once I've tackled it.

### What I'm watching out for

[This issue](https://github.com/astral-sh/ruff/issues/8598) was raised to ask for one call per-line
with chained method calls. I think this looks a lot better than the current rules, where something
like this would be valid:

```python title="Example from GitHub user nick4u"
some_query = (
  select(whatever.id, x.something)
  .join(x, x.y == whatever.y)
  .where(x > 12)
  .order_by(whatever.id)
)
```

## Wrap Up

So that's the story of my first `ruff` migration - it took a bit of documentation diving to try and
keep the formatting similar to what it was before but it was worthwhile and I uncovered some great
features and learnt what `ruff` is capable of.

!!! tip
    A final tip (for VS Code users) is to install the [VS Code extension for `ruff`][ruff-extension],
    make this the default formatter for Python and enable "Format on Save". This is great for
    formatting your code on the go and results in your pre-commit checks passing first time much
    more often.

Have you implemented `ruff` in any of your projects yet? How are you finding it and are there any
other features that you're finding invaluable? Please let me know in the comments!

[ruff]: https://docs.astral.sh/ruff/
[pipx]: https://pipx.pypa.io/
[ruff-PR]: https://github.com/dynaconf/dynaconf/pull/1074
[diff-ruff-configs]: https://docs.astral.sh/ruff/faq/#i-want-to-use-ruff-but-i-dont-want-to-use-pyprojecttoml-what-are-my-options
[emoji-line-change]: https://github.com/dynaconf/dynaconf/pull/1074/files#diff-d4d1e188f1582e0dcc9d59f05c3688706aa1f5dafbd605d9ce0f57bfab07aa4dL397-L400
[unicode-width]: https://docs.astral.sh/ruff/formatter/black/#line-width-vs-line-length
[pragma-line-change]: https://github.com/dynaconf/dynaconf/pull/1074/files#diff-24948beaba404665bbac207216fc06c66fcb86a641b9604932f8e15a5cbe2a60L59-L62
[pragma-reasoning]: https://docs.astral.sh/ruff/formatter/black/#pragma-comments-are-ignored-when-computing-line-width
[nested-config-removal]: https://github.com/dynaconf/dynaconf/pull/1074/commits/00a3c6099f729ca662dd272bd286975d63bf60f4
[pre-commit-integration]: https://docs.astral.sh/ruff/integrations/#pre-commit
[sorting-imports]: https://docs.astral.sh/ruff/formatter/#sorting-imports
[pre-commit-changes]: https://github.com/dynaconf/dynaconf/pull/1074/files#diff-63a9c44a44acf85fea213a857769990937107cf072831e1a26808cfde9d096b9R5
[ruff-black]: https://docs.astral.sh/ruff/formatter/black/
[unintentional-deviations]: https://github.com/astral-sh/ruff/issues?q=is%3Aopen+is%3Aissue+label%3Aformatter
[ellipsis-oneline]: https://github.com/dynaconf/dynaconf/pull/1074/files#diff-2bf0e4b7600a8b9bacd98749033f5ad209b918713653b22625bdd76fb9f36fd5L28-R25
[ruff-docstring]: https://docs.astral.sh/ruff/faq/#does-ruff-support-numpy-or-google-style-docstrings
[ruff-extension]: https://marketplace.visualstudio.com/items?itemName=charliermarsh.ruff
