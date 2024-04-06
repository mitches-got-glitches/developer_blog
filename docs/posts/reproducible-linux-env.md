---
date: 2024-04-05
categories:
  - linux
  - bash
authors:
  - mitches-got-glitches
comments: true
draft: true
---

# Creating a portable Python development environment

I set out on writing this post with a dream... A dream that whenever I was working in a shell
environment, I would always have access to the aliases and commands that I'm used to, and that
things would look exactly how I want them to. Whether that be at work, on my personal device or
logging in to remote compute environments in the cloud.

Luckily I am not the first to have this dream, and through [the guidance of Jake
Wiesler][portable-env] I've been able to make this dream a reality and set up my own portable
development environment.

<!-- more -->

The result is a [dotfiles repo][my-dotfiles] that stores all my config files and an install script
for `bash` to get everything setup. As you can see in the README, all that's needed is git and an
internet connection to clone the repo, then to run `install.sh` and I should be all setup and ready
to go.

I wanted to write about my experience setting it up because I've made a couple of different choices:

* I've chosen [`brew`](https://brew.sh/) as my cross-platform installer rather than `nix`.
  [`nix`](https://nixos.org/) looks cool (it's a whole OS) but `brew` has been around longer and
  still does the job as far as I'm concerned.
* I wanted to use `pyenv` and `pipx` to set everything up for Python development.

I also wanted to touch on some of the other tools I've included and changes I might make in the
future.

## Using `stow` to setup a portable config

GNU's [`stow`](https://www.gnu.org/software/stow/) (`brew install stow`) enables you to manage your
config files through GitHub and provides some simple commands to symlink these files where they need
to be to configure your programs. Because they are symlinked, any changes are still picked up by
version control which is great.

I don't want to write a full guide here since many good one's already exist - once again I refer you
to [a Jake Wiesler post][jake-dotfiles] which helped me out. Very simply, once you've created your
own dotfiles repo, you move the config for each of your apps into named sub-directories with the
nesting that you want from your `$HOME` (or wherever your config files usually exist).

I'll just show you the commands that I've put in my `install.sh` to configure new environments.

```bash title="install.sh"
# Adopt allows stow if .bashrc already exists. We just restore back to what we had with Git.
stow --adopt bash # (1)!
git restore .
stow vim
stow git
stow nu
source ~/.bashrc # (2)!
```

1. There may already be a `.bashrc`. The `--adopt` option combines yours with the existing and
   creates the symlink. I `git restore .` in the following line to restore it to the version stored
   on GitHub and we are left with the symlink - this is a bit of a workaround.
2. I source my new config to apply the changes straight away.

## Installing `brew`

First I install some basic `apt-get` dependencies to make sure `brew` gets installed correctly, and
then just install `brew` in the recommended manner.

```bash title="install.sh"
# Install brew dependencies
sudo apt-get update
sudo apt-get install build-essential procps curl file git -y

# Download Brew
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
eval "$(/home/linuxbrew/.linuxbrew/bin/brew shellenv)" # (1)!
```

1. Evaluating this command makes sure that `brew` is available in the shell so we can call it later in the shell script.

## Install packages with `brew`

```bash title="install.sh"
# Installing gcc is recommended
brew update
brew install \
        gcc \
        git \
        stow \
        pyenv \
        pipx \
        node \
        yarn \
        keychain \
        bat \
        nushell \
        jandedobbeleer/oh-my-posh/oh-my-posh
```

Let me run you through a few of these:

* `gcc` is recommended following installation of `brew`
* We already installed `git` with `apt-get`, but installing with `brew` makes it easier to update
  to the latest version.
* `stow` we will need for the config files as mentioned in the earlier section.
* `pyenv` and `pipx` are for my Python setup, they will allow us to install Python and useful CLI
  dev tools respectively.
* `node` and `yarn` for installing [Node.js packages](https://www.codecademy.com/article/what-is-node)
* `keychain` which starts an ssh-agent in a long running process that persists between logins. This
  means that when an SSH key (with a password!) is setup for pushing and pulling from GitHub, you
  don't need to put in your password everytime. This is a bit less secure, but if you're happy to
  lose a little you gain some convenience while still staying pretty protected.
* [`bat`](https://github.com/sharkdp/bat) - this is `cat` "with wings" (on steroids)
* [`nushell`](https://www.nushell.sh/) - a new (🤔) shell that I'm experimenting with. You can see
  in the `stow` section that I stow config for this.
* [`oh-my-posh`](https://ohmyposh.dev/) - this gives you access to useful and aesthetically pleasing
  prompt themes.

??? note "Updating `git` with `apt-get` as an alternative"

    If you want to stick with `apt-get` for `git`, then you need to do the following to get the latest
    version:

    ```bash
    # Update Git to latest version
    sudo apt-add-repository ppa:git-core/ppa
    sudo apt-get update
    sudo apt-get install git
    ```

## Installing Python

To install and manage Python version I use [`pyenv`](https://github.com/pyenv/pyenv). You may be
working on different projects with different Python versions, `pyenv` provides an easy way to
install and switch between the versions you need.

To get going, I need a few more dependencies installed before I attempt to install Python with
`pyenv`:

```bash title="install.sh"
# Install Python dependencies in Brew
brew install openssl readline sqlite3 xz zlib tcl-tk
```

And because I have installed these dependencies with `brew`, I need to set the C compiler to `gcc`
(which I also installed earlier with `brew`).

```bash title="install.sh"
# Set the compiler to Brew gcc, pyenv installs will fail without this.
export CC=/home/linuxbrew/.linuxbrew/bin/gcc-13
```

??? note "Alternative: Installing build dependencies with `apt`"
    I was getting some issues installing some Python versions with `brew` GCC compiler. Rather than
    completing the steps above you could install Python's build dependencies with `apt` instead:

    ```bash
    sudo apt update; sudo apt install build-essential libssl-dev zlib1g-dev \
    libbz2-dev libreadline-dev libsqlite3-dev curl \
    libncursesw5-dev xz-utils tk-dev libxml2-dev libxmlsec1-dev libffi-dev liblzma-dev
    ```

## Installing Python script

This bit is probably a bit over-engineered, but I created a bash script to grab the latest available
minor versions of Python with the latest patch. The script takes a single positional argument `n`
which indicates how many minor versions you want to go back.

For example, as of time of writing, `3.12.2` is the latest stable release, so if I passed `4` the
following versions would be installed:

```txt
3.12.2
3.11.8
3.10.13
3.9.18
```

It then sets the latest Python version as the global default for `pyenv`, so `3.12.2` in this case.
I've setup my `install.sh` script to execute this script with `n=2`.

This was mainly a bit of fun and the chance to learn & practice some bash skills. You can check out
the script below:

??? quote "install_python_versions.sh"
    ```py
    --8<-- "https://raw.githubusercontent.com/mitches-got-glitches/dotfiles/main/install_python_versions.sh"
    ```

It basically works by parsing the output of `pyenv install --list` to get the latest versions. I also
added a `help` function which works in both the following scenarios:

```bash
./install_python_versions.sh -h     # (1)!
./install_python_versions.sh -h 2   # (2)!
```

1. Without a positional argument.
2. With the positional argument, it will still print help rather than running.

## Installing Python CLI dev tools with `pipx`

[`pipx`](https://pipx.pypa.io/stable/) installs and runs your Python apps in isolated environments.
The shims for each app are all added to a single location (defaults to `~/.local/bin`) which is
added to your path. Why is this cool?

* Install tools once, and use them anywhere - no need to install in every virtual environment.
* You can upgrade to the latest versions of apps without worrying about causing dependency issues
  with you current project packages (`pipx upgrade-all`)

Following an install of `pipx` (which I installed with `brew`), you need to run the following to
ensure the shims location is on your path with an aptly named command:

```bash
pipx ensurepath
```

So I end up with the following section in my `install.sh`:

```bash title="install.sh"
# Install Python tools using pipx.
pipx ensurepath
pipx install black
pipx install typos
pipx install ipython
pipx install ruff
pipx install uvicorn
pipx install cookiecutter
pipx install pre-commit
pipx install mypy
pipx install poetry
pipx install mkdocs
pipx inject mkdocs mkdocs-material[imaging]
pipx inject mkdocs mkdocstrings[python]
pipx inject mkdocs mkdocs-glightbox
pipx install jupyter
pipx install asciinema
```

I'm not going to go into each of those tools (feel free to ask in the comments), but I will point
out that I'm now able to serve this blog locally to view my changes using the `mkdocs serve`
command, without having to activate a virtual environment first.

This is because I've injected the extra dependencies `mkdocs` needs with `pipx inject` - another
cool feature of `pipx`.

## Generating an SSH key

The final section of my file just creates an SSH key and prints out the public key with a reminder
to add it to my GitHub account.

```bash title="install.sh"
# Generate SSH key for GitHub
ssh-keygen -t ed25519
cat ~/.ssh/id_ed25519.pub
echo 'Add this public SSH key to GitHub account'
```

## Testing out the full file

With all these steps I have my final `install.sh` file:

??? quote "install_python_versions.sh"
    ```py
    --8<-- "https://raw.githubusercontent.com/mitches-got-glitches/dotfiles/main/install.sh"
    ```

And to test it out I'm going to run it in a fresh Ubuntu container with `docker`.

```bash
docker run -it ubuntu bash
```

This enters a bash terminal as the root user. To simulate properly, I need to setup a new user with
`sudo` access and switch to that user. I also need to make sure `git` is installed, before cloning
my dotfiles repo and entering the directory. You can see all the steps lain out in [my `dotfiles`
repo][my-dotfiles].

Now I can run the whole script and check that it runs without any issues!

```bash
sudo ./install.sh
```

## Future considerations

* Splitting installs into smaller scripts so I have more fine-grained control of what's installed.
* Creating a more lightweight install script where necessary.
* Creating different versions on different branches to try out new setups or configs.

## Closing remarks

I got onto [this while setting up a WSL development environment on my new Windows
laptop](windows-laptop-setup.md). It's taken a bit of pain setting up but I've learnt a lot along
the way (and gone down some rabbit holes as usual). I'm pretty happy with the outcome and hopefully
it's pain that I won't have to repeat.

One notable tool that is missing from this installable script is `docker`. In my setup I've got
Docker Desktop hooked up to WSL, which when running starts up a `docker` engine and puts the app in
`/usr/bin/docker`, so I don't need to install it again. You can see my full Windows with WSL setup
by following the link in the first paragraph of this section.

---

*I'm interested to hear what you think. How would your install scripts differ from mine? Did you
learn anything useful? Please let me know in the comments below.*

[portable-env]: https://www.jakewiesler.com/blog/portable-development-environment
[jake-dotfiles]: https://www.jakewiesler.com/blog/managing-dotfiles
[my-dotfiles]: https://github.com/mitches-got-glitches/dotfiles
*[OS]: Operating System
