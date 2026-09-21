from django import template

register = template.Library()


@register.filter
def get_item(dictionary, key):
    """Usage: {{ some_dict|get_item:some_key }} — Django templates can't index
    a dict by a variable key directly, so this fills that gap."""
    if not dictionary:
        return None
    return dictionary.get(key)


@register.filter
def mul(value, arg):
    """Usage: {{ value|mul:24 }} — Django templates have no built-in
    multiplication filter; used to scale mood scores into pixel heights
    for the journal insights bar chart."""
    try:
        return float(value) * float(arg)
    except (TypeError, ValueError):
        return 0
