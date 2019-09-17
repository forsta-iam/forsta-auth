#!/usr/bin/env python3

import ast
import os
import pathlib
import re

import astor

settings_path = pathlib.Path(os.path.dirname(__file__)) / '..' / 'forsta_auth' / 'settings.py'
settings = settings_path.read_text()

readme_path = pathlib.Path(os.path.dirname(__file__)) / '..' / 'README.md'

vars = []

for match in re.finditer(r'\W(?P<env>env(?P<db>\.db)?\(.*\)),?([ \t]*#[ \t]*(?P<comment>.*))?$', settings, re.MULTILINE):
    var = match.groupdict()

    call = ast.parse(match['env']).body[0].value
    args, kwargs = call.args, call.keywords

    if var['db']:
        var['name'] = 'DATABASE_URL'
    else:
        var['name'] = args[0].s

    for kwarg in kwargs:
        value = astor.to_source(kwarg.value).strip()
        if value.startswith('(') and value.endswith(')'):
            value = value[1:-1]
        if value.startswith('"""') and value.endswith('"""'):
            value = value[2:-2]
        if value.startswith('"') and value.endswith('"') and "'" not in value:
            value = "'" + value[1:-1] + "'"
        if kwarg.arg in ('default', 'cast'):
            var[kwarg.arg] = '`' + value.replace('|', '\\|').replace('`', '\\`') + '`'

    vars.append(var)

new_readme = []

with readme_path.open() as readme:
    for line in readme:
        new_readme.append(line)
        if line == '## Environment variables\n':
            break

    new_readme.extend([
        "\n",
        "Name | Cast | Default | Description\n",
        "---- | ---- | ------- | -----------\n",
    ])

    for var in vars:
        name = var['name'].replace('|', '\|')
        if not var.get('default'):
            name = f'**{name}**'
        new_readme.append("{} | {} | {} | {}".format(
            name,
            var.get('cast') or '',
            var.get('default') or '',
            (var.get('comment') or '').replace('|', '\|'),
        ).strip() + '\n')

    resume = False
    for line in readme:
        if line.startswith('## '):
            resume = True
        if resume:
            new_readme.append(line)

readme_path.write_text(''.join(new_readme))
