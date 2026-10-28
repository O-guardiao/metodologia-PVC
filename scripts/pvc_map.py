#!/usr/bin/env python3
"""PVC textual catalog: explicit, bounded operations with local Git checkpoints."""
import argparse
import json
import sys

from pvc_catalog import CatalogError, read_json, query, need
from pvc_map_workflow import Workflow, locked


def parser():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--project', required=True)
    commands = p.add_subparsers(dest='command', required=True)
    for name in ('init', 'candidate'):
        commands.add_parser(name).add_argument('--catalog', required=True)
    for name in ('entry', 'status', 'query', 'show'):
        c = commands.add_parser(name)
        c.add_argument('--limit', type=int, default=10)
        c.add_argument('--offset', type=int, default=0)
        if name == 'show':
            c.add_argument('--symbol', required=True)
        if name == 'query':
            c.add_argument('text')
            c.add_argument('--catalog')
    commands.add_parser('plan').add_argument('--spec', required=True)
    commands.add_parser('checkpoint')
    commands.add_parser('relocate').add_argument('--expected-head', required=True)
    test = commands.add_parser('test')
    test.add_argument('--run-reviewed-tests', action='store_true')
    test.add_argument('--timeout', type=int, default=120)
    test.add_argument('--reconciled-effects')
    review = commands.add_parser('review')
    review.add_argument('--reviewer', required=True)
    review.add_argument('--note', required=True)
    commands.add_parser('promote')
    commands.add_parser('recover')
    return p


def run(args):
    workflow = Workflow(args.project)
    if args.command == 'init':
        return workflow.init(read_json(args.catalog))
    if args.command == 'status':
        return workflow.bounded_status(args.limit, args.offset)
    if args.command == 'entry':
        with locked(workflow.control):
            return workflow.entry(args.limit, args.offset)
    if args.command == 'show':
        return workflow.show(args.symbol, args.limit, args.offset)
    if args.command == 'query':
        gen, manifest, catalog = workflow.baseline()
        workflow.require_entry(gen, manifest)
        result = query(catalog, args.text, args.catalog, args.limit, args.offset)
        result.update(generation=gen, index=f'.pvc-map/generations/{gen}/INDEX.md',
                      warning='Baseline view. Run status to detect pending code changes before acting.')
        return result
    with locked(workflow.control):
        if args.command == 'relocate':
            return workflow.relocate(args.expected_head)
        if args.command == 'plan':
            return workflow.plan(read_json(args.spec))
        if args.command == 'checkpoint':
            return workflow.checkpoint()
        if args.command == 'candidate':
            return workflow.candidate(read_json(args.catalog))
        if args.command == 'test':
            need(1 <= args.timeout <= 3600, 'Timeout must be 1..3600 seconds')
            return workflow.test(args.run_reviewed_tests, args.timeout, args.reconciled_effects)
        if args.command == 'review':
            return workflow.review(args.reviewer, args.note)
        if args.command == 'promote':
            return workflow.promote()
        return workflow.recover()


def main(argv=None):
    try:
        result = run(parser().parse_args(argv))
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 2 if result.get('passed') is False or result.get('blocked') else 0
    except (CatalogError, OSError, ValueError) as exc:
        print(json.dumps({'error': str(exc), 'result': 'not completed'}, ensure_ascii=False), file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
