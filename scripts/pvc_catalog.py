"""Text catalog validation, inventory and bounded, generated views (stdlib only)."""
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import subprocess


class CatalogError(ValueError):
    pass


def need(ok, message):
    if not ok:
        raise CatalogError(message)


def canonical(obj):
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode('utf-8')


def fingerprint(obj):
    return hashlib.sha256(canonical(obj)).hexdigest()


def read_json(path):
    try:
        return json.loads(Path(path).read_text(encoding='utf-8'))
    except (OSError, ValueError) as exc:
        raise CatalogError(f'Cannot read JSON {path}: {exc}') from exc


EXCLUDED = {'.git', '.pvc-map', '.pvc-method', '.venv', 'venv', 'node_modules', '__pycache__'}


def relative(name):
    need(isinstance(name, str) and name and '\\' not in name and ':' not in name and not any(ord(c) < 32 for c in name), 'Invalid relative path')
    parts = PurePosixPath(name).parts
    need(not name.startswith('/') and '..' not in parts and '.' not in parts, f'Unsafe path: {name}')
    need(not any(p in EXCLUDED for p in parts), f'Control/generated path excluded: {name}')
    need(str(PurePosixPath(name)) == name, f'Noncanonical path: {name}')
    return name


def file_hash(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def inventory(root):
    """All nonexcluded files; no implicit Git-ignore hiding. Reject symlinks."""
    result = {}
    for base, dirs, files in os.walk(root, followlinks=False):
        dirs[:] = sorted(d for d in dirs if d not in EXCLUDED)
        for name in dirs:
            need(not (Path(base) / name).is_symlink(), f'Symlink directory unsupported: {name}')
        for name in sorted(files):
            if name in EXCLUDED:
                continue
            path = Path(base) / name
            rel = relative(path.relative_to(root).as_posix())
            need(not path.is_symlink(), f'Symlink file unsupported: {rel}')
            need(path.is_file(), f'Nonregular file unsupported: {rel}')
            result[rel] = {'sha256': file_hash(path), 'bytes': path.stat().st_size}
    return result


def strings(value, label, allow_empty=True):
    need(isinstance(value, list) and all(isinstance(v, str) and v.strip() for v in value), f'{label}: string list required')
    need(len(set(value)) == len(value), f'{label}: duplicates')
    need(allow_empty or value, f'{label}: empty')


def validate_catalog(data, files):
    need(isinstance(data, dict) and data.get('schema_version') == 1, 'Catalog schema_version must be 1')
    for key in ('catalogs', 'symbols'):
        need(isinstance(data.get(key), list) and all(isinstance(v, dict) for v in data[key]), f'{key}: object array required')
        ids = [v.get('id') for v in data[key]]
        need(all(isinstance(v, str) and re.fullmatch('[A-Za-z0-9_-]{1,80}', v) for v in ids), f'{key}: invalid ID')
        need(len(ids) == len(set(ids)), f'{key}: duplicate ID')
    groups = {g['id']: g for g in data['catalogs']}
    need(groups, 'At least one catalog required')
    for group in groups.values():
        for key in ('title', 'purpose'):
            need(isinstance(group.get(key), str) and group[key].strip(), f'Catalog {key} required')
        parent = group.get('parent')
        need(parent is None or isinstance(parent, str) and parent in groups, 'Unknown catalog parent')
    for group in groups.values():
        seen, cursor = set(), group['id']
        while cursor is not None:
            need(cursor not in seen, 'Catalog hierarchy cycle')
            seen.add(cursor)
            cursor = groups[cursor].get('parent')
    symbols = {s['id']: s for s in data['symbols']}
    for symbol in symbols.values():
        for key in ('name', 'path', 'kind', 'catalog', 'purpose'):
            need(isinstance(symbol.get(key), str) and symbol[key].strip(), f'{symbol["id"]}.{key} required')
        relative(symbol['path'])
        need(symbol['path'] in files, f'Symbol file absent: {symbol["path"]}')
        need(symbol['catalog'] in groups, 'Unknown catalog')
        need(symbol.get('confidence') in ('declared', 'reviewed', 'unknown'), 'Invalid confidence')
        if symbol['confidence'] == 'reviewed':
            need(symbol.get('reviewed_sha256') == files[symbol['path']]['sha256'], 'Reviewed purpose must cite current source hash')
        for key in ('inputs', 'outputs', 'invariants', 'depends_on', 'aliases', 'tests', 'unknown_dependencies'):
            strings(symbol.get(key), f'{symbol["id"]}.{key}')
        for dep in symbol['depends_on']:
            need(dep in symbols, f'Unknown dependency: {dep}; describe uncertainty in unknown_dependencies')
        for path in symbol['tests']:
            relative(path)
            need(path in files, f'Test file absent: {path}')
    return data


def clip(text, length=240):
    return text if len(text) <= length else text[:length] + '… [excerpt]'


def page(items, limit, offset):
    need(type(limit) is int and 1 <= limit <= 100 and type(offset) is int and offset >= 0, 'Invalid pagination')
    return {'items': items[offset:offset + limit], 'total': len(items), 'offset': offset,
            'next_offset': offset + limit if offset + limit < len(items) else None}


def summary(symbol):
    return {key: clip(symbol[key]) for key in ('id', 'name', 'path', 'catalog', 'purpose', 'confidence')}


def query(catalog, text, group=None, limit=10, offset=0):
    terms = text.casefold().split()
    records = []
    for symbol in catalog['symbols']:
        haystack = ' '.join([symbol['id'], symbol['name'], symbol['path'], symbol['purpose'], *symbol['aliases']]).casefold()
        if (group is None or symbol['catalog'] == group) and all(t in haystack for t in terms):
            row = summary(symbol)
            row['detail'] = f'catalogs/{symbol["catalog"]}.md#symbol-{symbol["id"].lower()}'
            records.append(row)
    return page(sorted(records, key=lambda x: x['id']), limit, offset)


def render(catalog, files):
    """Return deterministic Markdown and Mermaid projections from one catalog."""
    symbols = {s['id']: s for s in catalog['symbols']}
    groups = {g['id']: g for g in catalog['catalogs']}
    def esc(value):
        return str(value).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;').replace('\n', ' ')
    def plain(value):
        return str(value).replace('\n', ' ').replace('|', '\\|')
    outputs = {}
    root = ['# PVC — índice validado', '', 'Mapa declarado, não extração semântica. Consulte status antes de alterar.', '', '## Catálogos', '']
    for group in sorted(groups.values(), key=lambda g: g['id']):
        root += [f'- [{plain(group["title"])}](catalogs/{group["id"]}.md): {plain(group["purpose"])}']
    root += ['', '## Hierarquia', '', '```mermaid', 'flowchart TD']
    for group in sorted(groups.values(), key=lambda g: g['id']):
        root += [f'  g_{group["id"]}["{esc(group["title"])}"]']
        if group.get('parent'):
            root += [f'  g_{group["parent"]} -->|contém| g_{group["id"]}']
    edges = {(s['catalog'], symbols[d]['catalog']) for s in symbols.values()
             for d in s['depends_on'] if s['catalog'] != symbols[d]['catalog']}
    for source, target in sorted(edges):
        root += [f'  g_{source} -.->|depende: declarado| g_{target}']
    root += ['```', '', f'Inventário: {len(files)} arquivos. Símbolos declarados: {len(symbols)}.',
             'Cobertura funcional completa não é inferida da existência deste catálogo.']
    outputs['INDEX.md'] = '\n'.join(root) + '\n'
    for group in sorted(groups.values(), key=lambda g: g['id']):
        own = sorted((s for s in symbols.values() if s['catalog'] == group['id']), key=lambda s: s['id'])
        lines = [f'# {plain(group["title"])}', '', group['purpose'], '', '[Índice raiz](../INDEX.md)', '', '## Subcatálogos', '']
        lines += [f'- [{plain(g["title"])}]({g["id"]}.md)' for g in sorted(groups.values(), key=lambda g: g['id']) if g.get('parent') == group['id']]
        lines += ['', '## Conexões declaradas', '', '```mermaid', 'flowchart LR']
        touched = {s['id'] for s in own} | {d for s in own for d in s['depends_on']}
        for sid in sorted(touched):
            lines += [f'  s_{sid}["{esc(symbols[sid]["name"])}"]']
        for s in own:
            lines += [f'  s_{s["id"]} -->|depende: declarado| s_{dep}' for dep in s['depends_on']]
        lines += ['```', '', 'Arestas são declarações; chamadas dinâmicas e dependências omitidas exigem inspeção.', '']
        for s in own:
            consumers = sorted(x['id'] for x in symbols.values() if s['id'] in x['depends_on'])
            lines += [f'## Symbol {s["id"]}', '', f'Nome: {plain(s["name"])}', f'Arquivo: `{s["path"]}`',
                      f'Tipo: {s["kind"]}; confiança: {s["confidence"]}', '', s['purpose'], '']
            for key, label in [('inputs', 'Entradas'), ('outputs', 'Saídas'), ('invariants', 'Invariantes'), ('depends_on', 'Depende de'), ('tests', 'Testes'), ('unknown_dependencies', 'Dependências desconhecidas')]:
                lines += [f'- {label}: ' + ('; '.join(plain(v) for v in s[key]) or '(nenhum declarado)')]
            lines += ['- Consumidores: ' + (', '.join(consumers) or '(nenhum declarado)'), '']
        outputs[f'catalogs/{group["id"]}.md'] = '\n'.join(line.rstrip() for line in lines).rstrip() + '\n'
    return outputs


def git(root, *args):
    try:
        proc = subprocess.run(['git', '-C', str(root), *args], capture_output=True, text=True, timeout=30)
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise CatalogError(f'Git unavailable: {exc}') from exc
    need(proc.returncode == 0, f'Git failed: {proc.stderr.strip()}')
    return proc.stdout.strip()
