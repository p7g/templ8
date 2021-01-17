# templ8

This is a really simple templating language for Python. Here are the basics:

1. Code to be evaluated is enclosed in `{{` and `}}`.
1. The content of the braces is just Python.
1. An expression can be emitted directly using `{{=`.
1. A block is entered if the code ends with `:`.
1. Blocks are ended with `{{ end }}`.
1. You can escape double braces (in code or markup) by prefixing them with `\`.
1. Templates are compiled into Python functions.

## Examples

This example generates a markdown ordered list of things:

```
# A list of {{= context["thing_name"] }}:

{{ for i, item in enumerate(context["things"]): }}
{{= i + 1 }}. {{= item }}
{{ end }}
```

It can be used like this:

```python
import templ8

the_template = templ8.compile(the_template_text)
context = {
    "thing_name": "todos",
    "things": ["Do the dishes", "Take out the trash"]
}
print(the_template(context))
```
