---
date: 2024-03-12
categories:
  - python
  - windows
authors:
  - mitches-got-glitches
comments: true
draft: true
---

# Setting up a new Windows laptop for Python development

## The Backstory

I've been doing a bit more development on my personal laptop lately and I was starting to brush up
against the limits of my hardware. I have a Thinkpad X270, and although it comes with the renowned
keyboard and a sturdy (not quite) bullet-proof chassis, I was starting to question the other parts
of the spec... 8GB of RAM, an Intel i5-62000U processor and only 155GB of usable disk... I quickly
ran out of space after setting up Windows Subsystem for Linux, a few versions of Python and some
virtual environments.

Fair enough, I had a bit of bloat that I could slim down but I didn't want to have to make this a
regular occurrence. Also, being a bit of a tab whore I was starting to experience a bit of slowness
as I switched contexts between VS Code and my browser. Frankly, I could do with an upgrade. And
although it had absolutely zero influence over this decision I was also experiencing a few ping
issues when playing Age of Empires II: Definitive Edition online despite good ping and speeds on the
internet tests... nope, no sway at all.

<!-- more -->

<figure markdown="span">
  ![ping speeds](../img/ping-speeds.png)
  <figcaption>Wireless speeds</figcaption>
</figure>

Although I was tempted by some new shiny models, I didn't want to break the bank. And although Macs
are touted for development, I will forever be a Windows child - I just can't seem to break
through my frustrations with the Apple UX. Plus, with Windows Subsystem for Linux now a thing and
Windows 11 actually looking quite sleek I didn't feel the need to finally get over my Macphobia. If
I had the money, (I think it would be funny...🎵), I would have probably went for a souped up Dell
XPS 15 after seeing [some pretty solid reviews][dell-xps-15-review-2023]. It seemed to offer good
performance for programming and creative workloads while also having a decent graphics card.

As it happens, I spotted a refurbed model of the XPS 15 (9570) on ebay which was packing a 1TB SSD
and 32GB of RAM for just shy of £500. This model [seemed to review pretty
well][dell-xps-15-review-2018] at the time, and I was happy with this spec at the price point so I
decided to purchase. I'm not very tuned in to the world of CPU processors, but it came with an
i7-8750H which, while not world-leading, seems [to offer a considerable improvement][cpu-benchmark]
over the i5-62000U of my Thinkpad. And on top of that it came equipped with a Nvidia GTX 1050Ti 4GB
graphics card, so if Age of Empires did happen to fire up then I should have fewer online teammates
complaining about my lag...

[dell-xps-15-review-2023]: https://uk.pcmag.com/laptops/147048/dell-xps-15-9530-2023
[dell-xps-15-review-2018]: https://www.expertreviews.co.uk/dell/1407577/dell-xps-15-9570-review-2018
[cpu-benchmark]: https://cpu.userbenchmark.com/Compare/Intel-Core-i7-8750H-vs-Intel-Core-i5-6200U/m470418vsm36796

## Setup Goals

So it arrived and on unboxing first thoughts were it's a bit chunkier, but then I'm intending to use
it mainly as a desktop, and I'll probably hang on to the Thinkpad for a more portable work machine
anyway.

We're getting onto why I actually wanted to write this post, and that's to run through my
development setup on a new Windows machine, mainly so that when I have to go through this again I
have a good point to start from, but also to hopefully demonstrate some good practices for creating
a productive development experience on Windows.

Let me run through a few of my main goals:

1. **Using WSL2 for my main development environment**

    Linux is probably the most common build environment when building applications, and as such, it
    makes sense to develop in Linux if we can. [Windows Subsystem for Linux][what-is-wsl] offers an
    awesome way to run a Linux environment on Windows without a virtual machine. It's pretty simple
    to do and it automatically mounts your Windows drive. The WSL extension for VS Code is going to
    provide a seamless development experience between the Windows and Linux environments.

2. **Using virtual environments where possible to keep my base installs unpolluted**

    This should make libraries/tools easy to purge or upgrade and to prevent any base installations
    from getting corrupted. I also want to keep project environments separate, and only install what
    I need to with as few duplicate installs as necessary.

    Two great tools for this in Python are `pyenv`, which allows for easy installation and switching
    between different Python versions, and `pipx`, which installs CLI tools in their own virtual
    environments and adds them to your path for use anywhere.

3. **Using the command-line and package managers**

    The aim is to automate much of this in the future by putting a bunch of commands into a script,
    so using the command-line is a must. I also want to make use of some useful package managers:

    * [chocolatey][choco] (`choco`) for Windows
    * `apt` for Linux
    * Also [Homebrew](https://brew.sh/) (`brew`) for Linux (yes it works on Linux too)

I also want to get everything configured the way I like it and to make sure all of the essential
environment variables I need for my tools are set. Anyway, enough goal-setting, let's get
cracking...

[what-is-wsl]: https://learn.microsoft.com/en-us/windows/wsl/about#what-is-wsl-2

## The Setup

note: Add tooltip

### WSL

First on my list is installing WSL. This can take a few hours so it's best to get started with early.
Open Powershell with admin privileges and type in the following command:

```ps
wsl --install
```

That easy! Leave that to brew while we move onto some of our Windows installs.

### Chocolatey

[Chocolatey][choco] is a modern package manager for Windows - I suppose you could compare it with
Homebrew on Linux or Mac.

Open up another Powershell with admin privileges, and paste in the following:

```ps
Set-ExecutionPolicy AllSigned; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
```

Confirm the prompts as necessary (trying to figure out a way to skip these temporarily). You should
now have Chocolatey installed, you can check by running `choco` from the command line.

!!! Warning

    The [install guide](https://chocolatey.org/install) says to inspect their `install.ps1` script
    before running, even though they take security seriously. Personally, I'm happy to go ahead with
    it and I'm not quite sure what I'm looking for anyway.




[choco]: https://chocolatey.org/
