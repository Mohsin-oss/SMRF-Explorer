#!/usr/bin/env python3
"""SMRF local project-pack runner. Standard library; optional user-supplied SWMM CLI."""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
import math
import re
import shlex
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ACRE_HA = 0.40468564224
SI_UNITS = {'CMS', 'LPS', 'MLD'}
US_UNITS = {'CFS', 'GPM', 'MGD'}


def digest(text):
    return hashlib.sha256(text.encode('utf-8')).hexdigest()


def number(value, label, minimum=-math.inf, maximum=math.inf):
    if isinstance(value, bool) or value is None or value == '':
        raise ValueError(f'{label} is missing or invalid')
    try:
        result = float(value)
    except (TypeError, ValueError):
        raise ValueError(f'{label} is not numeric') from None
    if not math.isfinite(result) or not minimum <= result <= maximum:
        raise ValueError(f'{label} is outside the accepted range')
    return result


def tokens(line):
    lexer = shlex.shlex(line, posix=True)
    lexer.whitespace_split = True
    lexer.commenters = ';'
    return list(lexer)


def parse_model(text):
    sections = {}
    section = ''
    for line in text.lstrip('\ufeff').splitlines():
        row = tokens(line)
        if not row:
            continue
        if re.fullmatch(r'\[[A-Za-z_]+\]', row[0]):
            section = row[0][1:-1].upper()
            sections.setdefault(section, [])
        elif section:
            sections[section].append(row)
    options = {r[0].upper(): r[1].upper() for r in sections.get('OPTIONS', []) if len(r) > 1}
    units = options.get('FLOW_UNITS', 'CFS')
    if units not in SI_UNITS | US_UNITS:
        raise ValueError('Unknown FLOW_UNITS')
    area_factor = 1.0 if units in SI_UNITS else ACRE_HA
    catchments = []
    unique = {'catchments': set(), 'nodes': set(), 'links': set()}

    def add_id(name, kind):
        key = name.upper()
        if not name or len(name) > 200 or key in unique[kind]:
            raise ValueError(f'Duplicate or invalid {kind} ID: {name}')
        unique[kind].add(key)

    for row in sections.get('SUBCATCHMENTS', []):
        if len(row) < 7:
            raise ValueError('Incomplete SUBCATCHMENTS row')
        add_id(row[0], 'catchments')
        catchments.append({'id': row[0], 'outlet': row[2],
                           'area_ha': number(row[3], 'Area', sys.float_info.min) * area_factor,
                           'impervious_pct': number(row[4], '%Imperv', 0, 100)})
    if not catchments:
        raise ValueError('No subcatchments found')
    nodes, outfalls, links = [], set(), []
    for section in ('JUNCTIONS', 'OUTFALLS', 'STORAGE', 'DIVIDERS'):
        for row in sections.get(section, []):
            if len(row) < 2:
                raise ValueError('Incomplete node row')
            add_id(row[0], 'nodes')
            number(row[1], 'Node elevation')
            nodes.append(row[0])
            if section == 'OUTFALLS':
                outfalls.add(row[0].upper())
    for section in ('CONDUITS', 'PUMPS', 'WEIRS', 'ORIFICES', 'OUTLETS'):
        for row in sections.get(section, []):
            if len(row) < 3:
                raise ValueError('Incomplete link row')
            add_id(row[0], 'links')
            if row[1].upper() not in unique['nodes'] or row[2].upper() not in unique['nodes']:
                raise ValueError(f'{row[0]} references an absent node')
            links.append((row[0], row[1], row[2]))
    for c in catchments:
        if c['outlet'].upper() not in unique['nodes'] | unique['catchments']:
            raise ValueError(f"{c['id']} references an absent runoff outlet")
    return {'catchments': catchments, 'flow_units': units, 'nodes': nodes, 'links': links}


def calculate(model, settings, surfaces):
    if not isinstance(settings, dict) or settings.get('source') not in ('baseline', 'inventory', 'manual'):
        raise ValueError('Unknown refinement method')
    for key in ('parking', 'green', 'streets', 'verified', 'terrain', 'alignment'):
        if not isinstance(settings.get(key), bool):
            raise ValueError(f'Invalid {key} setting')
    width = number(settings.get('width_m'), 'Proposed street width', 0.1, 100)
    if not isinstance(surfaces, dict):
        raise ValueError('Invalid surfaces table')
    known = {c['id'] for c in model['catchments']}
    if set(surfaces) - known or set(settings.get('manual', {})) - known:
        raise ValueError('Refinement values reference unknown catchments')
    rows = []
    for c in model['catchments']:
        name, gross, pct = c['id'], c['area_ha'], c['impervious_pct']
        surface = surfaces.get(name, {})
        if not isinstance(surface, dict):
            raise ValueError(f'{name}: invalid surface row')
        for key, value in surface.items():
            if value is not None:
                if key not in ('roof_ha', 'road_ha', 'parking_ha', 'green_correction_ha', 'baseline_road_width_m'):
                    raise ValueError(f'{name}: unsupported surface field')
                number(value, f'{name} {key}', sys.float_info.min if key == 'baseline_road_width_m' else 0,
                       math.inf if key == 'baseline_road_width_m' else gross + 1e-8)

        def area(key):
            return number(surface.get(key), f'{name} {key}', 0, gross + 1e-8)

        base = gross * pct / 100
        proposed = base
        source = settings['source']
        if source == 'manual':
            proposed = gross * number(settings.get('manual', {}).get(name, pct), f'{name} manual %', 0, 100) / 100
        else:
            uses_surfaces = source == 'inventory' or any(settings[k] for k in ('parking', 'green', 'streets'))
            if uses_surfaces and not settings['verified']:
                raise ValueError('Surface coverage and overlap verification is required')
            if source == 'inventory':
                if settings['green']:
                    raise ValueError('Green correction applies only to the baseline method')
                proposed = area('roof_ha') + area('road_ha')
            if settings['streets']:
                original_width = number(surface.get('baseline_road_width_m'), f'{name} baseline road width', sys.float_info.min)
                proposed += area('road_ha') * (width / original_width - 1)
            if settings['parking']:
                proposed += area('parking_ha')
            if settings['green']:
                proposed -= area('green_correction_ha')
        if not -1e-8 <= proposed <= gross + 1e-8:
            raise ValueError(f'{name}: proposed impervious area is outside 0–gross area')
        proposed = min(gross, max(0.0, proposed))
        rows.append({'id': name, 'area_ha': gross, 'baseline_pct': pct,
                     'proposed_pct': proposed / gross * 100, 'delta_pp': proposed / gross * 100 - pct})
    return rows


def write_refined(text, rows):
    values = {r['id'].upper(): r['proposed_pct'] for r in rows}
    section = ''
    result = []
    for line in text.splitlines(keepends=True):
        row = tokens(line.lstrip('\ufeff'))
        if row and re.fullmatch(r'\[[A-Za-z_]+\]', row[0]):
            section = row[0][1:-1].upper()
        elif section == 'SUBCATCHMENTS' and row:
            # The fifth token is %Imperv. Preserve all other text and comments.
            spans = list(re.finditer(r'"[^"]*"|\'[^\']*\'|[^\s]+', line))
            item = spans[4]
            line = line[:item.start()] + format(values[row[0].upper()], '.10g') + line[item.end():]
        result.append(line)
    return ''.join(result)


def run_engine(executable, model_path, output, label, working_dir):
    report = output / f'{label}.rpt'
    binary = output / f'{label}.out'
    completed = subprocess.run([str(executable), str(model_path), str(report), str(binary)],
                               cwd=working_dir, capture_output=True, text=True, timeout=1800)
    report_text = report.read_text(errors='replace') if report.exists() else ''
    errors = bool(re.search(r'^\s*ERROR\s+\d+', report_text, re.M))
    ok = completed.returncode == 0 and report.exists() and binary.exists() and binary.stat().st_size > 0 and not errors
    return {'status': 'completed' if ok else 'failed', 'returncode': completed.returncode,
            'report': report.name, 'binary_output': binary.name,
            'log_excerpt': (completed.stdout + completed.stderr)[-2000:],
            'report_contains_errors': errors}


def process(request, output, executable=None, engine_cwd=None):
    if request.get('schema') != 'smrf-processing-request/v1':
        raise ValueError('Use a processing request exported by the SMRF Custom project workspace')
    text = request.get('source_inp')
    if not isinstance(text, str) or len(text) > 20 * 1024 * 1024:
        raise ValueError('Invalid or oversized INP source')
    if digest(text) != request.get('baseline_sha256'):
        raise ValueError('Baseline fingerprint mismatch; source text was changed')
    model = parse_model(text)
    settings = request.get('settings', {})
    rows = calculate(model, settings, request.get('surfaces', {}))
    refined = write_refined(text, rows)
    verified = parse_model(refined)
    if len(verified['catchments']) != len(rows):
        raise ValueError('Refined model validation failed')
    for actual, expected in zip(verified['catchments'], rows):
        if actual['id'] != expected['id'] or abs(actual['impervious_pct'] - expected['proposed_pct']) > 1e-5:
            raise ValueError('Refined %Imperv values did not round-trip')
    output = Path(output).resolve()
    names = ['baseline.inp', 'refined.inp', 'smrf-result.json', 'surface-comparison.csv',
             'baseline.rpt', 'baseline.out', 'refined.rpt', 'refined.out']
    if any((output / name).exists() for name in names):
        raise ValueError('Output files already exist. Choose a new output directory to preserve previous versions.')
    output.mkdir(parents=True, exist_ok=True)
    (output / 'baseline.inp').write_bytes(text.encode('utf-8'))
    (output / 'refined.inp').write_bytes(refined.encode('utf-8'))
    with (output / 'surface-comparison.csv').open('w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['id', 'area_ha', 'baseline_pct', 'proposed_pct', 'delta_pp'])
        writer.writeheader()
        writer.writerows(rows)
    engine = {'status': 'not_requested', 'note': 'No hydraulic simulation was executed.'}
    if executable:
        try:
            exe = Path(executable).resolve()
            if not exe.is_file():
                raise ValueError('SWMM executable was not found')
            cwd = Path(engine_cwd).resolve() if engine_cwd else output
            runs = {name: run_engine(exe, output / f'{name}.inp', output, name, cwd)
                    for name in ('baseline', 'refined')}
            engine = {'status': 'completed' if all(r['status'] == 'completed' for r in runs.values()) else 'failed',
                      'runs': runs, 'note': 'Inspect reports and continuity errors before judging hydraulic performance.'}
        except (ValueError, OSError, subprocess.TimeoutExpired) as e:
            engine = {'status': 'failed', 'note': str(e)}
    pending = []
    if settings.get('terrain'):
        pending.append('terrain redelineation — GIS adapter required')
    if settings.get('alignment'):
        pending.append('street graph regeneration — SWMManywhere adapter required')
    result = {'schema': 'smrf-processing-result/v1', 'request_id': request.get('request_id'),
              'created_at': datetime.now(timezone.utc).isoformat(), 'runner_version': '0.2.0',
              'baseline_sha256': digest(text), 'request_settings': settings,
              'catchments': rows, 'refined_inp': refined, 'refined_inp_sha256': digest(refined),
              'geometry_regenerated': False, 'pending_operations': pending, 'engine': engine,
              'notes': ['Only SUBCATCHMENTS %Imperv was changed; the original baseline text was preserved.',
                        'Surface data were supplied by the user, not measured from GIS by this runner.',
                        'No calibration, benchmark comparison or hydraulic improvement is inferred.']}
    (output / 'smrf-result.json').write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding='utf-8')
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--request', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--swmm-executable', type=Path, help='Optional EPA SWMM command-line executable; runs baseline and refined models')
    parser.add_argument('--engine-cwd', type=Path, help='Folder containing external rainfall and other referenced input files')
    args = parser.parse_args()
    try:
        if args.request.stat().st_size > 30 * 1024 * 1024:
            raise ValueError('Request exceeds 30 MB')
        request = json.loads(args.request.read_text(encoding='utf-8-sig'))
        if not isinstance(request, dict):
            raise ValueError('Request must be a JSON object')
        result = process(request, args.output, args.swmm_executable, args.engine_cwd)
        print('Surface refinement written to:', args.output.resolve() / 'refined.inp')
        print('Import into the explorer:', args.output.resolve() / 'smrf-result.json')
        print('SWMM execution:', result['engine']['status'])
        if result['pending_operations']:
            print('Pending:', '; '.join(result['pending_operations']))
        return 2 if result['engine']['status'] == 'failed' else 0
    except (OSError, ValueError, KeyError, IndexError, TypeError) as error:
        print('Processing failed:', error, file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
