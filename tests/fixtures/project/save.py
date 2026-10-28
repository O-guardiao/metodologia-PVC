def save(title):
    if not title:
        raise ValueError('title required')
    return {'title': title}
