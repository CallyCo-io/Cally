=====
Why??
=====
If you have come across this project, you may be asking why, what's the point? Which
is entirely valid. The CDK for Terraform strives to solves one of the challenges with
HCL, in that HCL is a declarative language. And you can do some pretty complex things
with plain HCL, and there is a wealth of tooling out there to make that all robust.

Except most of those tools are either paid for, alternatives to Terraform, or suffer
from one of the things that the CDK for Terraform **doesn't** solve.

This is the way
---------------
Though providing an Imperitive interface, it requires you to do things the CDKTF way.
Whilst this library expects things to be done the 'Cally' way, it is intended to allow
you to consruct things without needing to think about the ins and outs of what is
expected, along without feeling like writing TypeScript [#ts]_ in Python.

Boiler plate
------------
Terraform expects **every** stack, to be carefully setup and configured. This was possibly
super useful when it was mostly run locally, and there might be an argument
to be made for HCL projects, but this has carried over to the CDK for Terraform. Meaning
you are just getting a Python like interface to run terraform the same way as you would
as if you were writing HCL, including setting up the project the same way. Which arguably
diminishes the point of using something other than HCL.

What this leads to is:

- Big stacks - which means big problems to solve when something goes wrong, or conflicts when
  multiple people are working in the same area.
- Configuration Repos - It might be a controversial opinon, but I am firm in that your projects
  IAC should live with the project. If you need to depend on a queue/bucket etc, you don't want
  to be waiting on a config repo to be deployed before your app. In this modern world, you are
  leaving a lot on the table if you aren't considering infrastructure as *part* of your
  application. Gone are the days where you produced a binary, and threw it over the fence to
  the ops team.

It's possible that a former role in my career has had  some influence here, in that we grew
tired of hand building Cloudformation yaml by hand. My boss at the time found `Troposphere <https://troposphere.readthedocs.io/>`_,
which is a Python based tool for generating valid cloudformation templates. The great thing
about it is, that it just gets out of the way and generates yaml or json, that you can pass
to Cloudformation.

Unit testing / Linting / Packaging
----------------------------------
There are a wealth of tools out there that have been built to support making deploying Terraform
changes more robust. Including some now native to Terraform

Some examples include

- https://terragrunt.gruntwork.io/
- https://developer.hashicorp.com/terraform/language/tests

These are no doubt useful. But most languages have tools builtin, or well developed frameworks
available. One of the benefits from using something like Python is, that you can unittest your
stacks. Forming a contract based approach to your IAC.

With the appropriate test coverage, you get the following demarcation points:

- Configuration - This is your contract with the consumer, promising that the provided config
  will output the same terraform template every time.
- Output Template - This is your contract with Terraform, promising that the template is correct
  for a given input.
- Terraform - This provides the contract with the service provider

This is important because it keeps your problem domains distinctly separated. A config problem is
a config problem, a code problem is firmly a code problem, and a Terraform problem is downstream
of you. It avoids spending hours in the code / templates, only to find out it's a provider problem.

Not only all of the above, you can also distribute your packaged IDP, and so long as your team keeps
their tooling up to date, you can guarantee whatever your CI/CD is doing, you can do locally. Which
makes it much easier to debug, as debugging workflows can be really unforgiving, especially when you
find something trivial like a typo, that would have been quickly revealed with a local validation.

Closing
-------
Hopefully that gives some background to the reasons behind this project. It is inspired by an internal
tool I wrote for my workplace, and I've long wanted something for my own projects and share withfriends.
The tooling at work performs in the realms of 100,000 checks of our infrastructure a year, around 15,000
changes, and is maintained by just four people. Some teams have 100s of discrete services they maintain,
blissfully unaware of the amount of Terraform that is generated, planned, and applied everytime they merge
a PR.

.. [#ts] No shade to TypeScript, it just feels *very* weird when you're writing Python
