from jinja2 import (
    Environment,
    FileSystemLoader,
)

env = Environment(loader=FileSystemLoader('templates'))
template = env.get_template('index.html')

with open('templates/ammo_plot.html', 'r', encoding='utf-8') as f:
    plot = f.read()

data = {'plot': plot}
rendered = template.render(data)
with open('docs/index.html', 'w', encoding='utf-8') as f:
    f.write(rendered)
