def strip_enclosing_characters(tag):
    if (tag.startswith('(') and tag.endswith(')')) or (tag.startswith('[') and tag.endswith(']')):
        return tag[1:-1]
    return tag

def add_enclosing_characters(tag, original_tag):
    if original_tag.startswith('(') and original_tag.endswith(')'):
        return f'({tag})'
    if original_tag.startswith('[') and original_tag.endswith(']'):
        return f'[{tag}]'
    return tag
