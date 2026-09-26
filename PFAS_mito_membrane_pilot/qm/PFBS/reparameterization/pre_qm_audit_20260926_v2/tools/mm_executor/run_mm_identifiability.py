#!/usr/bin/env python3
"""Bounded GROMACS MM sensitivity runner for the frozen PFBS V2 protocol.

This script is staged to a new remote runtime. It only creates isolated MM
parameter copies and runs the preregistered minimizations; it never calls QM.
"""
from __future__ import annotations

import argparse
import concurrent.futures
import hashlib
import json
import math
import os
import re
import shutil
import subprocess
import sys
import time
from decimal import Decimal, InvalidOperation
from pathlib import Path

ROOT = Path('/home/ls/projects/PFAS_mito_membrane_pilot/qm/PFBS/pre_qm_v2_mm_identifiability_20260926/executor_runtime')
SOURCE = ROOT / 'immutable_sources'
MANIFEST = SOURCE / 'MM_RUN_MANIFEST.json'
GMX = Path('/home/ls/projects/PFAS_mito_membrane_pilot/qm/PFBS/phase3_mm_relaxed_profiles_20260926_v1/gromacs_double_build/bin/gmx_d')
ORIGINAL_FF = Path('/home/ls/projects/PFAS_mito_membrane_pilot/qm/PFBS/phase3_mm_relaxed_profiles_20260926_v1/parameter_source_copies/charmm36-feb2026_ljpme_cgenff-5.0.ff')
GMX_SHA = '910c195c43f12f35e44ff5ccfdafd3236bf86c6afb0774b550e0ccb5d5148c2d'
REVERSE_BINDING_SHA = '4b61e7ee08b9c03b33314eb869953ec9afa472b5926a00948abc8bf2d46a9620'
PROFILE_BINDING_SHA = '315a741f8441c0bf37657f2e6e477691ed85e78cdc8e6213de8e53d369bb8ded'
TERMINAL_ADDENDUM_SHA = 'aff3752034f2aa0d85bce0d46094d9c3a4e7c25954e8809b35704e4d9e617cc4'
TERMINAL_RECEIPT_SHA = '9441594207c52f8238bee81db4af7b518337ea3083cc8a6348b26624192fbf61'
FAILURE_SCOPE_ADDENDUM_SHA = 'a7f5751163adda6fd1e399149c76c7b81244812c84dffc96f749d59e85064608'
FAILURE_SCOPE_RECEIPT_SHA = '499ff91182912e34c31f2de4768f73d803e51ce5693ad485e1c6411aad2ee561'
REFERENCE_DP_BASELINE_TPR_SHA = '6f608585ecc607220692fbe875b4e07000c64d14bb5093c5af7130367ca7adc4'
REFERENCE_DP_BASELINE_DUMP_SHA = '2ec1f2360523c920d1f4c60f915f355300cb5a04ff0d20874dfa765d23f8600b'
REFERENCE_DP_BINDING_SHA = '96e04470e77a4f48ee34c99005fb7c7d75b91b52223357590de0ec79c6f35b07'
REFERENCE_DP_RECORD_SHA = 'f0eba98150199209e89b64744c29f012fdf68a3b5a0919001594ff0460096084'
REFERENCE_DP_TPR_PATH = '/home/ls/projects/PFAS_mito_membrane_pilot/qm/PFBS/task1_bonded_candidate_20260926_v1/formal_dp_v2/runs/GEO_A/base/lbfgs.tpr'
REFERENCE_DP_BASELINE_TPR = SOURCE/'reference_dp_formal_GEO_A_base_lbfgs.tpr'
REFERENCE_DP_BASELINE_DUMP = SOURCE/'reference_dp_formal_GEO_A_base_lbfgs.tpr.dump'
REFERENCE_DP_BINDING = SOURCE/'reference_dp_formal_GEO_A_base_tpr_dump_bindings.json'
REFERENCE_DP_RECORD = SOURCE/'reference_dp_formal_GEO_A_base_run_record.json'
FF_NAME = 'charmm36-feb2026_ljpme_cgenff-5.0.ff'
WARNING = 'For efficient BFGS minimization, use switch/shift/pme instead of cut-off.'
K_RESTRAINT = 500000.0
NCPU = 16
active_preflight_path = None


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(1 << 20), b''):
            h.update(block)
    return h.hexdigest()


def tree_sha(root: Path):
    files = {}
    for p in sorted(root.rglob('*')):
        if p.is_file():
            files[p.relative_to(root).as_posix()] = sha(p)
    packed = json.dumps(files, sort_keys=True, separators=(',', ':')).encode()
    return hashlib.sha256(packed).hexdigest(), files


def write_json(path: Path, obj):
    tmp = path.with_suffix(path.suffix + '.tmp')
    tmp.write_text(json.dumps(obj, indent=2, sort_keys=True) + '\n')
    os.replace(tmp, path)


def state_key(row):
    return f"{row['stage']}__{row['state_id']}"


def verify_sources(manifest):
    expected = {
        'pfbs_ani.itp': 'c736e8e20ee778fd64dfc2b95da13040b6a49404c78dc1cf46dd7368b016aeca',
        'pfbs_ani.prm': '24baf41553845380e9905f7419ca85cb0528dcd7652d596ca6ba83e003d05a56',
        'ffbonded.itp': 'cda750df0be35f862599f276f667be608b266a7a0aee085d2f623e82796403cf',
    }
    actual = {
        'pfbs_ani.itp': sha(SOURCE / 'pfbs_ani.itp'),
        'pfbs_ani.prm': sha(SOURCE / 'pfbs_ani.prm'),
        'ffbonded.itp': sha(SOURCE / 'ffbonded.itp'),
        'gromacs_double_binary': sha(GMX),
    }
    if any(actual[k] != v for k, v in expected.items()) or actual['gromacs_double_binary'] != GMX_SHA:
        raise RuntimeError(f'input or executable hash mismatch: {actual}')
    for filename, expected_hash in [
        ('NUMERICAL_IDENTIFIABILITY_PROTOCOL.md', manifest['protocol_hash']),
        ('MM_IDENTIFIABILITY_VARIABLE_SPEC.json', manifest['variable_spec_hash']),
        ('INITIAL_DIAGNOSTIC_VARIABLES.tsv', 'afb72bd4cbade810c005d0c9f1496883f7ed614c68542fc0d05d63fec7863db7'),
        ('BRANCH_CLASSIFIER_PREREGISTRATION_ADDENDUM.md', manifest['branch_addendum_hash']),
        ('BASIN_AND_MATHEMATICAL_RATIONALE_ADDENDUM.md', manifest['math_addendum_hash']),
    ]:
        if sha(SOURCE / filename) != expected_hash:
            raise RuntimeError(f'preregistration hash mismatch: {filename}')
    if manifest['expected_total_sources'] != 28 or manifest['expected_runs'] != 1736:
        raise RuntimeError('frozen matrix size mismatch')
    gate = json.loads((SOURCE/'GEOMETRY_SOURCE_GATE.json').read_text())
    if gate.get('status') != 'PASS':
        raise RuntimeError('authoritative geometry source gate is not PASS')
    gate_rows = {x['source_id']: x for x in gate['sources']}
    if gate_rows['GEO_A']['g96_sha256'] != 'bf6d3b621559c8a9eab217fdb97f1679c9dff8be0a8702542092e3f650516442':
        raise RuntimeError('GEO_A source does not match geometry gate')
    if gate_rows['GEO_B_REVISED']['g96_sha256'] != 'fc99a7915d74ebe8529d1f6619ca528a33b14c721384b3fe84f65a1cf1678cb3':
        raise RuntimeError('revised GEO_B source does not match geometry gate')
    source_ff_sha, source_ff_files = tree_sha(ORIGINAL_FF)
    staged_ff_sha, staged_ff_files = tree_sha(SOURCE/FF_NAME)
    if source_ff_files != staged_ff_files:
        raise RuntimeError('full force-field tree differs from accepted read-only source')
    actual['full_forcefield_tree_sha256'] = source_ff_sha
    actual['full_forcefield_file_count'] = len(source_ff_files)
    if sha(SOURCE/'REVERSE_QM_BINDING.json') != REVERSE_BINDING_SHA:
        raise RuntimeError('accepted reverse-QM binding hash mismatch')
    if sha(SOURCE/'QM_SOURCE_BINDING.json') != PROFILE_BINDING_SHA:
        raise RuntimeError('accepted profile source binding hash mismatch')
    reference_hashes = {
        'formal_dp_baseline_tpr_sha256': (REFERENCE_DP_BASELINE_TPR, REFERENCE_DP_BASELINE_TPR_SHA),
        'formal_dp_baseline_tpr_dump_sha256': (REFERENCE_DP_BASELINE_DUMP, REFERENCE_DP_BASELINE_DUMP_SHA),
        'formal_dp_baseline_binding_sha256': (REFERENCE_DP_BINDING, REFERENCE_DP_BINDING_SHA),
        'formal_dp_baseline_run_record_sha256': (REFERENCE_DP_RECORD, REFERENCE_DP_RECORD_SHA),
    }
    for label, (path, expected_hash) in reference_hashes.items():
        if sha(path) != expected_hash:
            raise RuntimeError(f'provenance-bound formal-DP baseline reference hash mismatch: {label}')
        actual[label] = expected_hash
    ref_binding = json.loads(REFERENCE_DP_BINDING.read_text())
    ref_record = json.loads(REFERENCE_DP_RECORD.read_text())
    required_binding = {
        'baseline_tpr': REFERENCE_DP_TPR_PATH,
        'baseline_tpr_sha256': REFERENCE_DP_BASELINE_TPR_SHA,
        'baseline_tpr_dump_sha256': REFERENCE_DP_BASELINE_DUMP_SHA,
        'gmx_sha256': GMX_SHA,
        'prm_sha256': expected['pfbs_ani.prm'],
    }
    if any(ref_binding.get(k) != v for k, v in required_binding.items()):
        raise RuntimeError('formal-DP baseline TPR/dump binding does not match its frozen source identity')
    if (ref_record.get('case') != 'GEO_A' or ref_record.get('variant') != 'base' or
            ref_record.get('executable') != str(GMX) or
            ref_record.get('gmx_sha256') != GMX_SHA or
            ref_record.get('candidate_parameters_sha256') != {'itp': expected['pfbs_ani.itp'], 'prm': expected['pfbs_ani.prm']} or
            ref_record.get('stages', {}).get('lbfgs', {}).get('tpr_sha256') != REFERENCE_DP_BASELINE_TPR_SHA):
        raise RuntimeError('formal-DP baseline run record is not bound to the original-source GEO_A/base TPR')
    frozen_clarifications = {
        'TERMINAL_CONVERGENCE_AND_PHYSICAL_ENERGY_ADDENDUM.md': TERMINAL_ADDENDUM_SHA,
        'TERMINAL_CONVERGENCE_AND_PHYSICAL_ENERGY_RECEIPT.json': TERMINAL_RECEIPT_SHA,
        'FAILURE_SCOPE_PREREGISTRATION_ADDENDUM.md': FAILURE_SCOPE_ADDENDUM_SHA,
        'FAILURE_SCOPE_PREREGISTRATION_RECEIPT.json': FAILURE_SCOPE_RECEIPT_SHA,
    }
    for filename, expected_hash in frozen_clarifications.items():
        if sha(SOURCE/filename) != expected_hash:
            raise RuntimeError(f'frozen clarification hash mismatch: {filename}')
        actual[filename] = expected_hash
    starts = SOURCE / 'starts'
    expected_starts = {x.stem for x in starts.glob('*.g96')}
    if len(expected_starts) != 28:
        raise RuntimeError(f'expected 28 staged source structures; found {len(expected_starts)}')
    return actual


def g96_xyz(path):
    lines = path.read_text().splitlines()
    s = lines.index('POSITION') + 1
    e = lines.index('END', s)
    rows = []
    for line in lines[s:e]:
        fields = line.split()
        if len(fields) != 7:
            raise ValueError(f'{path}: malformed POSITION row: {line!r}')
        rows.append((fields[2], [float(x) for x in fields[4:7]]))
    if len(rows) != 17:
        raise ValueError(f'{path}: expected 17 atoms, got {len(rows)}')
    expected = ['S1'] + [f'F{i}' for i in range(1,10)] + [f'O{i}' for i in range(1,4)] + [f'C{i}' for i in range(1,5)]
    if [x[0] for x in rows] != expected:
        raise ValueError(f'{path}: atom sequence mismatch: {[x[0] for x in rows]}')
    return rows


def pair_domain_receipt(path):
    """Validate the frozen isolated-box domain and report all 136 pairs."""
    lines = path.read_text().splitlines()
    try:
        bi = lines.index('BOX')
        be = lines.index('END', bi + 1)
    except ValueError as exc:
        raise ValueError(f'{path}: missing/invalid BOX section') from exc
    box_rows = [line.split() for line in lines[bi + 1:be] if line.strip()]
    if len(box_rows) != 1 or len(box_rows[0]) != 3:
        raise ValueError(f'{path}: expected one orthorhombic BOX row')
    box = [float(x) for x in box_rows[0]]
    if any(not math.isfinite(x) for x in box):
        raise ValueError(f'{path}: nonfinite box')
    # G96 source serialization is nine decimal places in nm.
    if any(abs(x - 10.0) > 5.1e-9 for x in box):
        raise ValueError(f'{path}: isolated box changed from 10.000000000 nm: {box}')
    rows = g96_xyz(path)
    coords = [xyz for _, xyz in rows]
    if not all(math.isfinite(v) for xyz in coords for v in xyz):
        raise ValueError(f'{path}: nonfinite coordinate')
    best = (-1.0, None)
    pair_count = 0
    for i in range(len(coords)):
        for j in range(i + 1, len(coords)):
            d = math.sqrt(sum((coords[i][k] - coords[j][k]) ** 2 for k in range(3)))
            if not math.isfinite(d):
                raise ValueError(f'{path}: nonfinite pair distance at {i+1},{j+1}')
            pair_count += 1
            if d > best[0]:
                best = (d, [rows[i][0], rows[j][0]])
    if pair_count != 136:
        raise ValueError(f'{path}: expected 136 pair distances, got {pair_count}')
    if best[0] > 2.0:
        raise ValueError(f'{path}: max all-pair distance {best[0]:.12f} nm exceeds 2.0 nm')
    return {'coordinate_file': path.name, 'coordinate_sha256': sha(path),
            'atom_count': len(coords), 'pair_count': pair_count,
            'box_nm': box, 'box_matches_10nm': True,
            'max_all_pair_distance_nm': best[0], 'max_distance_pair': best[1],
            'all_pairs_within_2nm': True}


def read_positionred(path):
    lines = path.read_text().splitlines()
    marker = 'POSITIONRED' if 'POSITIONRED' in lines else 'POSITION' if 'POSITION' in lines else None
    if marker is None:
        raise ValueError(f'{path}: no G96 POSITION/POSITIONRED section')
    start = lines.index(marker) + 1
    end = lines.index('END', start)
    xyz = []
    for line in lines[start:end]:
        fields = line.split()
        if len(fields) < 3:
            raise ValueError(f'{path}: malformed coordinate row {line!r}')
        xyz.append([float(x) for x in fields[-3:]])
    if len(xyz) != 17:
        raise ValueError(f'{path}: expected 17 position rows, got {len(xyz)}')
    return xyz


def named_g96_text(source_path, xyz, title):
    source_lines = source_path.read_text().splitlines()
    atoms = g96_xyz(source_path)
    bi = source_lines.index('BOX')
    be = source_lines.index('END', bi+1)
    boxlines = source_lines[bi+1:be]
    out = ['TITLE', title, 'END', 'POSITION']
    for i, ((atom, _), pos) in enumerate(zip(atoms, xyz), 1):
        out.append(f'{1:5d} {"PFBS":<5s} {atom:<5s}{i:6d}{pos[0]:15.9f}{pos[1]:15.9f}{pos[2]:15.9f}')
    out += ['END', 'BOX'] + boxlines + ['END']
    return '\n'.join(out)+'\n'


def _sub(a,b): return [a[i]-b[i] for i in range(3)]
def _dot(a,b): return sum(a[i]*b[i] for i in range(3))
def _cross(a,b): return [a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]]


def dihedral_from_g96(path, idx):
    xyz = [row[1] for row in g96_xyz(path)]
    p0,p1,p2,p3 = [xyz[i-1] for i in idx]
    b0,b1,b2 = _sub(p0,p1),_sub(p2,p1),_sub(p3,p2)
    n = math.sqrt(_dot(b1,b1))
    b1 = [x/n for x in b1]
    v = [b0[i]-_dot(b0,b1)*b1[i] for i in range(3)]
    w = [b2[i]-_dot(b2,b1)*b1[i] for i in range(3)]
    return math.degrees(math.atan2(_dot(_cross(b1,v),w),_dot(v,w)))


def mdp(integrator, job, emtol, nsteps=30000):
    return f'''integrator = {integrator}
nsteps = {nsteps}
emtol = {emtol:.8g}
emstep = 0.001
include = -I{job.parent.parent / "parameters"} -I{job}
periodic-molecules = no
coulombtype = Cut-off
coulomb-modifier = None
epsilon-r = 1
vdwtype = Cut-off
vdw-modifier = None
DispCorr = no
constraints = none
tcoupl = no
pcoupl = no
gen-vel = no
comm-mode = None
nstcalcenergy = 1
nstenergy = 1
nstlog = 100
nstxout = 0
nstvout = 0
nstfout = 0
pbc = xyz
cutoff-scheme = Verlet
nstlist = 10
rlist = 2.0
verlet-buffer-tolerance = -1
rcoulomb = 2.0
rvdw = 2.0
'''


def warning_blocks(text):
    lines = text.splitlines()
    blocks = []
    i = 0
    while i < len(lines):
        if re.match(r'^\s*(?:WARNING\s+\d+\b|Warning:)\s*', lines[i], re.I):
            block = [lines[i].strip()]
            i += 1
            while i < len(lines) and lines[i].strip() and not re.match(r'^\s*(?:WARNING\s+\d+\b|Warning:)\s*', lines[i], re.I):
                block.append(lines[i].strip())
                i += 1
            blocks.append(' '.join(block))
        else:
            i += 1
    return blocks


def approved_warning_set(blocks, stem):
    if not blocks:
        return True
    if len(blocks) != 1 or 'lbfgs' not in stem.lower():
        return False
    block = blocks[0]
    block = re.sub(r'^\s*WARNING\s+\d+\s*(?:\[[^\]]*\])?\s*:\s*', '', block, flags=re.I)
    block = re.sub(r'^\s*Warning:\s*', '', block, flags=re.I)
    return block.strip() == WARNING


def command(args, cwd, stem, stdin=None, allow_warning=False, timeout=300):
    p = subprocess.run(args, cwd=cwd, input=stdin, text=True, capture_output=True, timeout=timeout)
    combined = p.stdout + p.stderr
    (cwd / f'{stem}.stdout_stderr.txt').write_text(combined)
    blocks = warning_blocks(combined)
    if blocks and not approved_warning_set(blocks, stem):
        raise RuntimeError(f'{stem} has unapproved warning block(s): {blocks!r}')
    if p.returncode:
        if allow_warning and p.returncode != 0:
            if len(blocks) == 1 and approved_warning_set(blocks, stem):
                args2 = list(args)
                if '-maxwarn' in args2:
                    args2[args2.index('-maxwarn') + 1] = '1'
                else:
                    args2 += ['-maxwarn', '1']
                p2 = subprocess.run(args2, cwd=cwd, input=stdin, text=True, capture_output=True, timeout=timeout)
                retry_text = p2.stdout + p2.stderr
                (cwd / f'{stem}.retry_maxwarn1.stdout_stderr.txt').write_text(retry_text)
                retry_blocks = warning_blocks(retry_text)
                if len(retry_blocks) != 1 or not approved_warning_set(retry_blocks, stem):
                    raise RuntimeError(f'{stem} retry has unapproved warning block(s): {retry_blocks!r}')
                if p2.returncode == 0:
                    return {'returncode': 0, 'stdout': p2.stdout, 'stderr': p2.stderr,
                            'warning_exception': WARNING, 'warning_count': 1, 'maxwarn': 1}
                raise RuntimeError(f'{stem} failed on authorized one-warning retry: {(p2.stdout+p2.stderr)[-1500:]}')
        raise RuntimeError(f'{stem} failed ({p.returncode}): {combined[-1500:]}')
    return {'returncode': 0, 'stdout': p.stdout, 'stderr': p.stderr,
            'warning_exception': None, 'warning_count': 0, 'maxwarn': 0}


def patch_state(state, state_row, manifest):
    # Always create each state independently from the immutable source bytes.
    out = state / 'parameters'
    out.mkdir(parents=True, exist_ok=False)
    ffdir = out / FF_NAME
    ffdir.mkdir()
    source_ff = SOURCE / FF_NAME
    for entry in source_ff.iterdir():
        dest = ffdir / entry.name
        if entry.name == 'ffbonded.itp':
            shutil.copyfile(SOURCE / 'ffbonded.itp', dest)
        else:
            os.symlink(entry, dest)
    prm_lines = (SOURCE / 'pfbs_ani.prm').read_text().splitlines(keepends=True)
    itp_lines = (SOURCE / 'pfbs_ani.itp').read_text().splitlines(keepends=True)
    ffb_lines = (SOURCE / 'ffbonded.itp').read_text().splitlines(keepends=True)
    ffb_original = list(ffb_lines)
    prm_original = list(prm_lines)
    itp_original = list(itp_lines)
    var_by_id = {v['id']: v for v in manifest['variables']}
    for v in manifest['variables']:
        if state_row['variable_id'] != v['id']:
            continue
        delta = state_row['multiplier'] * v['h']
        scale = 1.0 + delta if v['field'] == 'proportional_amplitude_scale' else None
        for row in v['source_rows']:
            name = row['source_file']
            lines = {'ffbonded.itp': ffb_lines, 'pfbs_ani.prm': prm_lines, 'pfbs_ani.itp': itp_lines}[name]
            line_idx = row['source_line_1based'] - 1
            line = lines[line_idx]
            nl = '\r\n' if line.endswith('\r\n') else '\n' if line.endswith('\n') else ''
            content = line[:-len(nl)] if nl else line
            body, sep, comment = content.partition(';')
            tokens = body.split()
            token_idx = row['parameter_token_index_0based']
            if token_idx >= len(tokens):
                raise RuntimeError(f'bad token index in {v["id"]} {row}')
            expected_tokens = row['source_values_exact'].split()
            if not any(tokens[i:i+len(expected_tokens)] == expected_tokens
                       for i in range(max(0, len(tokens)-len(expected_tokens)+1))):
                raise RuntimeError(f"source value string changed for {v['id']} row {row}")
            if v['field'] == 'proportional_amplitude_scale':
                newval = float(tokens[token_idx]) * scale
            else:
                newval = float(tokens[token_idx]) + delta
            tokens[token_idx] = f'{newval:.10f}'
            prefix = re.match(r'\s*', body).group(0)
            lines[line_idx] = prefix + ' '.join(tokens) + (sep + comment if sep else '') + nl
    (out / 'pfbs_ani.prm').write_text(''.join(prm_lines))
    (out / 'pfbs_ani.itp').write_text(''.join(itp_lines))
    (ffdir / 'ffbonded.itp').write_text(''.join(ffb_lines))
    # Write a source-change receipt: exactly the preregistered rows may differ.
    changed = {}
    for name, original, altered in [('ffbonded.itp', ffb_original, ffb_lines),
                                    ('pfbs_ani.prm', prm_original, prm_lines),
                                    ('pfbs_ani.itp', itp_original, itp_lines)]:
        diffs = [i + 1 for i, (a, b) in enumerate(zip(original, altered)) if a != b]
        changed[name] = diffs
    allowed = {n: [] for n in changed}
    if state_row['variable_id']:
        v = var_by_id[state_row['variable_id']]
        for r in v['source_rows']:
            allowed[r['source_file']].append(r['source_line_1based'])
    if any(sorted(changed[n]) != sorted(allowed[n]) for n in changed):
        raise RuntimeError(f'perturbation changed unexpected source lines: {state_row["state_id"]} {changed} != {allowed}')
    receipt = {
        'state': state_row,
        'baseline_hashes': {'pfbs_ani.itp': sha(SOURCE/'pfbs_ani.itp'),
                            'pfbs_ani.prm': sha(SOURCE/'pfbs_ani.prm'),
                            'ffbonded.itp': sha(SOURCE/'ffbonded.itp')},
        'effective_hashes': {'pfbs_ani.itp': sha(out/'pfbs_ani.itp'),
                             'pfbs_ani.prm': sha(out/'pfbs_ani.prm'),
                             'ffbonded.itp': sha(ffdir/'ffbonded.itp')},
        'changed_source_lines': changed,
        'allowed_source_lines': allowed,
    }
    write_json(state / 'STATE_PARAMETER_RECEIPT.json', receipt)
    return receipt


def make_topologies(state, job, source, manifest):
    params = state / 'parameters'
    prefix = f'#include "{FF_NAME}/forcefield.itp"\n#include "pfbs_ani.prm"\n'
    suffix = '\n[ system ]\nPFBS isolated intrinsic torsion MM identifiability\n\n[ molecules ]\nPFBS_ani 1\n'
    scanned = source.get('series')
    if scanned:
        torsion = (16, 14, 15, 1) if scanned == 'T_CC' else (14, 15, 1, 11)
        phi = float(source['qm_final_scanned_deg'])
        restraint = ('\n[ dihedral_restraints ]\n; isolated MM scan control only\n'
                     f' {torsion[0]} {torsion[1]} {torsion[2]} {torsion[3]} 1 {phi:.9f} 0.0 {K_RESTRAINT:.1f}\n')
        (job/'pfbs_ani_restraint.itp').write_text((params/'pfbs_ani.itp').read_text() + restraint)
        (job/'topol_min.top').write_text(prefix + '#include "pfbs_ani_restraint.itp"\n' + suffix)
    else:
        (job/'topol_min.top').write_text(prefix + '#include "pfbs_ani.itp"\n' + suffix)
    (job/'topol_physical.top').write_text(prefix + '#include "pfbs_ani.itp"\n' + suffix)


def build_matrix(manifest, source_binding):
    starts = SOURCE / 'starts'
    source_map = []
    for p in source_binding['points']:
        p2 = dict(p)
        p2['start_name'] = p['point_id']
        p2['start_path'] = str(starts / (p['point_id'] + '.g96'))
        if sha(Path(p2['start_path'])) != p['g96_sha256']:
            raise RuntimeError(f'profile start hash mismatch: {p["point_id"]}')
        source_map.append(p2)
    # The reverse branch is a distinct input geometry, but excluded from the
    # primary observable vector by downstream protocol analysis.
    rev = next(x for x in source_binding['points'] if x['point_id'] == 'T_CC_240')
    reverse_rows = json.loads((SOURCE/'REVERSE_QM_BINDING.json').read_text())
    reverse_row = next(x for x in reverse_rows if x['reverse_point'] == 'T_CC_REV_240')
    if reverse_row['reverse_state_original'] != 'PASS' or reverse_row['convergence_and_geometry_status'] != 'PASS':
        raise RuntimeError('reverse CC240 source is not accepted')
    reverse = {'point_id':'T_CC_240_FROM_REVERSE_QM','start_name':'T_CC_240_FROM_REVERSE_QM',
               'start_path':str(starts/'T_CC_240_FROM_REVERSE_QM.g96'),'g96_sha256':None,
               'series':'T_CC','target_deg':float(reverse_row['target_deg']),
               'qm_final_scanned_deg':float(reverse_row['reverse_final_torsion_deg']),
               'qm_energy_hartree':float(reverse_row['reverse_QM_energy_hartree']),
               'source_checkpoint_sha256':reverse_row['reverse_chk_sha256'],
               'source_fchk_sha256':reverse_row['reverse_fchk_sha256'],
               'branch_only':True}
    if sha(Path(reverse['start_path'])) != '8af7af63d19b53cffc32f9eda8be8acabcdedd5642a150991c618d46afeeece1':
        raise RuntimeError('reverse CC240 G96 source hash mismatch')
    reverse['g96_sha256'] = sha(Path(reverse['start_path']))
    reverse_angle = dihedral_from_g96(Path(reverse['start_path']), (16,14,15,1))
    if abs(((reverse_angle-reverse['qm_final_scanned_deg']+180.0)%360.0)-180.0) > 0.01:
        raise RuntimeError(f'reverse G96 torsion differs from accepted reverse binding: {reverse_angle}')
    reverse['qm_final_scanned_deg'] = reverse_angle
    source_map.append(reverse)
    for name, series in [('GEO_A', None), ('GEO_B_REVISED', None)]:
        path = starts / (name + '.g96')
        expected = {'GEO_A':'bf6d3b621559c8a9eab217fdb97f1679c9dff8be0a8702542092e3f650516442',
                    'GEO_B_REVISED':'fc99a7915d74ebe8529d1f6619ca528a33b14c721384b3fe84f65a1cf1678cb3'}[name]
        if sha(path) != expected:
            raise RuntimeError(f'geometry source hash mismatch: {name}')
        source_map.append({'point_id': name, 'start_name': name, 'start_path': str(path),
                           'g96_sha256': expected, 'series': series, 'qm_final_scanned_deg': None,
                           'target_deg': None, 'branch_only': False, 'geometry_only': True})
    if len(source_map) != 28 or len({x['start_name'] for x in source_map}) != 28:
        raise RuntimeError(f'source map invalid: {len(source_map)}')
    return source_map


def make_job(state_path, state_row, source, manifest):
    job = state_path / 'runs' / source['start_name']
    job.mkdir(parents=True, exist_ok=False)
    shutil.copyfile(source['start_path'], job/'start.g96')
    make_topologies(state_path, job, source, manifest)
    tolerance = float(state_row['tolerance'])
    for stem, integ in [('lbfgs', 'l-bfgs'), ('cg', 'cg')]:
        (job/f'{stem}.mdp').write_text(mdp(integ, job, tolerance))
    (job/'physical.mdp').write_text(physical_mdp(job))
    rec = {'state_id': state_row['state_id'], 'state_stage': state_row['stage'],
           'variable_id': state_row['variable_id'], 'multiplier': state_row['multiplier'],
           'emtol_kj_mol_nm': tolerance, 'source_id': source['point_id'],
           'source_geometry_sha256': sha(job/'start.g96'), 'start_g96_sha256': sha(job/'start.g96'),
           'state_key': state_key(state_row),
           'parameter_receipt_sha256': sha(state_path/'STATE_PARAMETER_RECEIPT.json'),
           'branch_only': bool(source.get('branch_only', False)),
           'geometry_only': bool(source.get('geometry_only', False)),
           'target_scanned_deg': source.get('target_deg'), 'qm_scanned_deg': source.get('qm_final_scanned_deg'),
           'status': 'PREPARED'}
    write_json(job/'RUN_RECEIPT.json', rec)
    return job


def grompp_only(job, stem, top, coord, emtol, physical=False):
    if physical:
        (job/'physical.mdp').write_text(physical_mdp(job))
    command([str(GMX), 'grompp', '-f', f'{stem}.mdp', '-c', coord, '-p', top,
             '-o', f'{stem}.tpr', '-po', f'{stem}_processed.mdp', '-maxwarn', '0'],
            job, f'grompp_{stem}', allow_warning=True)


def physical_mdp(job):
    return mdp('md', job, 1.0, nsteps=1)


def dump_tpr(job, stem):
    p = subprocess.run([str(GMX), 'dump', '-s', f'{stem}.tpr'], cwd=job,
                       text=True, capture_output=True, timeout=120)
    combined = p.stdout + p.stderr
    (job/f'{stem}_dump.txt').write_text(combined)
    if p.returncode:
        raise RuntimeError(f'gmx dump {stem} failed: {combined[-1200:]}')


def dump_reference_tpr():
    if sha(REFERENCE_DP_BASELINE_TPR) != REFERENCE_DP_BASELINE_TPR_SHA:
        raise RuntimeError('formal-DP baseline TPR changed after source verification')
    if sha(REFERENCE_DP_BASELINE_DUMP) != REFERENCE_DP_BASELINE_DUMP_SHA:
        raise RuntimeError('formal-DP baseline TPR dump changed after source verification')
    return REFERENCE_DP_BASELINE_DUMP


def topology_signature(dump_path):
    lines = dump_path.read_text(errors='replace').splitlines()
    try:
        start = next(i for i,x in enumerate(lines) if x.strip() == 'topology:')
    except StopIteration:
        raise RuntimeError(f'no topology block in {dump_path}')
    end = next((i for i in range(start+1,len(lines)) if re.match(r'^\s*x\s*\(', lines[i])), None)
    if end is None:
        raise RuntimeError(f'no end of topology block in {dump_path}')
    out=[]
    for line in lines[start:end]:
        if len(out) == 1 and re.match(r'^\s*name=', line):
            line = re.sub(r'\bname="[^"]*"', 'name="SYSTEM_TITLE_NORMALIZED"', line)
        out.append(line.rstrip())
    return out


def _decimal(value):
    try:
        out = Decimal(value.strip())
    except (InvalidOperation, AttributeError) as exc:
        raise RuntimeError(f'non-numeric GROMACS coefficient: {value!r}') from exc
    if not out.is_finite():
        raise RuntimeError(f'nonfinite GROMACS coefficient: {value!r}')
    return out


def _canonical_atoms(atoms):
    forward = tuple(atoms)
    reverse = tuple(reversed(atoms))
    return min(forward, reverse)


def _topology_semantics(dump_path):
    lines = dump_path.read_text(errors='replace').splitlines()
    top_start = next((i for i, line in enumerate(lines) if line.strip() == 'topology:'), None)
    if top_start is None:
        raise RuntimeError(f'no topology block in {dump_path}')
    top_end = next((i for i in range(top_start + 1, len(lines))
                    if re.match(r'^\s*x\s*\(', lines[i])), None)
    if top_end is None:
        raise RuntimeError(f'no end of topology block in {dump_path}')
    top_lines = lines[top_start:top_end]
    functypes = {}
    for line in top_lines:
        match = re.match(r'^\s*functype\[(\d+)\]=(.*)$', line)
        if not match:
            continue
        idx, payload = match.group(1), match.group(2).strip()
        class_token, sep, rest = payload.partition(',')
        if not sep:
            raise RuntimeError(f'malformed functype line: {line}')
        coeffs = {}
        for part in rest.split(','):
            field = re.match(r'^\s*([A-Za-z][A-Za-z0-9_]*)\s*=\s*([-+\d.eE]+)\s*$', part)
            if not field:
                raise RuntimeError(f'malformed functype coefficient: {line}')
            coeffs[field.group(1)] = field.group(2)
        if idx in functypes:
            raise RuntimeError(f'duplicate functype index {idx}')
        functypes[idx] = (class_token.strip(), coeffs)

    interaction_re = re.compile(r'^\s*\d+\s+type=(\d+)\s+\(([^)]+)\)\s+(.+?)\s*$')
    interactions = {}
    occurrences = {}
    used_type_indices = set()
    skeleton = []
    for line in top_lines:
        if re.match(r'^\s*functype\[\d+\]=', line):
            continue
        if re.match(r'^\s*ntypes\s*=\s*\d+\s*$', line):
            continue
        match = interaction_re.match(line)
        if match:
            type_idx, class_token = match.group(1), match.group(2).strip()
            if type_idx not in functypes:
                raise RuntimeError(f'active interaction references missing functype[{type_idx}]')
            actual_class, coeffs = functypes[type_idx]
            if actual_class != class_token:
                raise RuntimeError(f'active interaction class {class_token} disagrees with functype[{type_idx}] class {actual_class}')
            atoms = tuple(int(x) for x in match.group(3).split())
            if len(atoms) not in (2, 3, 4) or len(set(atoms)) != len(atoms):
                raise RuntimeError(f'invalid active interaction atom tuple: {line}')
            canonical = _canonical_atoms(atoms)
            occurrence_key = (class_token, canonical)
            occurrence = occurrences.get(occurrence_key, 0)
            occurrences[occurrence_key] = occurrence + 1
            key = (class_token, canonical, occurrence)
            interactions[key] = {'class': class_token, 'atoms': canonical,
                                 'occurrence': occurrence, 'coefficients': dict(coeffs)}
            used_type_indices.add(type_idx)
            continue
        skeleton.append(line.rstrip())

    nonbonded_table = {}
    for idx, (class_token, coeffs) in functypes.items():
        if class_token in ('LJ_SR', 'LJ14'):
            signature = (class_token, tuple(sorted((name, _decimal(value)) for name, value in coeffs.items())))
            nonbonded_table[signature] = nonbonded_table.get(signature, 0) + 1
    # Preserve the complete dump outside topology too, which binds the TPR's
    # nonbonded settings, box, and all other run-control inputs.
    outer_before = tuple(lines[:top_start])
    outer_after = tuple(lines[top_end:])
    inputrec = {}
    in_inputrec = False
    for line in lines[:top_start]:
        if line.strip() == 'inputrec:':
            in_inputrec = True
            continue
        if in_inputrec:
            match = re.match(r'^\s*([A-Za-z][A-Za-z0-9_-]*)\s*=\s*(.*?)\s*$', line)
            if match:
                inputrec[match.group(1).lower()] = match.group(2).strip().lower()
    return {'interactions': interactions, 'nonbonded_table': nonbonded_table,
            'skeleton': tuple(skeleton), 'outer_before': outer_before,
            'outer_after': outer_after, 'inputrec': inputrec,
            'functype_count': len(functypes), 'used_functype_count': len(used_type_indices)}


def _processed_mdp_settings(dump_path):
    mdp_path = Path(dump_path).with_name('physical_processed.mdp')
    if not mdp_path.is_file():
        raise RuntimeError(f'physical processed MDP required to bind ld-seed use context: {mdp_path}')
    settings = {}
    for line in mdp_path.read_text(errors='replace').splitlines():
        body = line.partition(';')[0].strip()
        if not body or '=' not in body:
            continue
        key, value = body.split('=', 1)
        key = key.strip().lower()
        if key in settings:
            raise RuntimeError(f'duplicate setting {key} in {mdp_path}')
        settings[key] = value.strip().lower()
    return mdp_path, settings


def _seed_context(base_dump, candidate_dump, base, cand):
    base_path, base_mdp = _processed_mdp_settings(base_dump)
    cand_path, cand_mdp = _processed_mdp_settings(candidate_dump)
    keys = ('integrator','nsteps','gen-vel','tcoupl','pcoupl','bd-fric')
    base_context = {key:base_mdp.get(key) for key in keys}
    cand_context = {key:cand_mdp.get(key) for key in keys}
    if base_context != cand_context:
        raise RuntimeError(f'physical MDP seed-use/stochastic context changed: {base_context} != {cand_context}')
    required = {'integrator':'md','nsteps':'1','gen-vel':'no','tcoupl':'no','pcoupl':'no','bd-fric':'0'}
    physical_inputrec = ('integrator','nsteps','tcoupl','pcoupl','bd-fric')
    dump_context = [{key:base['inputrec'].get(key) for key in physical_inputrec},
                    {key:cand['inputrec'].get(key) for key in physical_inputrec}]
    if any(context != {key:required[key] for key in physical_inputrec} for context in dump_context):
        raise RuntimeError(f'physical TPR inputrec does not prove the frozen nonstochastic ld-seed-unused context: {dump_context}')
    approved = base_context == required
    return {'unused_ld_seed_context_proven':approved,
            'context_keys':keys,'baseline_processed_mdp_sha256':sha(base_path),
            'candidate_processed_mdp_sha256':sha(cand_path),
            'baseline_context':base_context,'candidate_context':cand_context,
            'inputrec_context':dump_context}


def _tpr_body_size_binding(dump_path, dump_lines, label):
    """Bind GROMACS's printed TPR body length to its exact physical.tpr file."""
    topology_positions = [i for i,line in enumerate(dump_lines) if line.strip() == 'topology:']
    if len(topology_positions) != 1:
        raise RuntimeError(f'{label} dump must contain exactly one topology header')
    topology_index = topology_positions[0]
    candidate_positions = [i for i,line in enumerate(dump_lines)
                           if re.match(r'^\s*buffer\s+size\b', line)]
    if len(candidate_positions) != 1:
        raise RuntimeError(f'{label} dump must contain exactly one TPR buffer size field')
    line_index = candidate_positions[0]
    raw_line = dump_lines[line_index]
    match = re.fullmatch(r'(\s*buffer size\s*=\s*)(\d+)(\s*)', raw_line)
    if not match:
        raise RuntimeError(f'{label} TPR buffer size must be one positive decimal integer: {raw_line!r}')
    if line_index != topology_index - 1:
        raise RuntimeError(f'{label} TPR buffer size field is not immediately before topology')
    body_size = int(match.group(2))
    if body_size <= 0:
        raise RuntimeError(f'{label} TPR buffer size must be positive: {body_size}')
    dump_path = Path(dump_path)
    tpr_path = dump_path.with_name('physical.tpr')
    if not tpr_path.is_file():
        raise RuntimeError(f'{label} physical TPR required to bind printed buffer size: {tpr_path}')
    tpr_size = tpr_path.stat().st_size
    size_minus_body = tpr_size - body_size
    if size_minus_body != 107:
        raise RuntimeError(f'{label} TPR file-size/body-size relation is {size_minus_body}, expected 107: '
                           f'file={tpr_size}, body={body_size}')
    return {
        'raw_line': raw_line,
        'line_number_1based': line_index + 1,
        'body_size_bytes': body_size,
        'tpr_path_name': tpr_path.name,
        'tpr_file_size_bytes': tpr_size,
        'tpr_bytes_minus_body_size': size_minus_body,
        'tpr_sha256': sha(tpr_path),
        'dump_sha256': sha(dump_path),
        'normalized_as_bound_tpr_serialization_metadata': True,
        'normalized_line': match.group(1) + '<TPR_BODY_SIZE>' + match.group(3),
    }


def _normalize_dump_metadata(base_dump, candidate_dump, base, cand):
    context = _seed_context(base_dump, candidate_dump, base, cand)
    before_b, before_c = list(base['outer_before']), list(cand['outer_before'])
    after_b, after_c = list(base['outer_after']), list(cand['outer_after'])
    metadata = {}
    base_lines = Path(base_dump).read_text(errors='replace').splitlines()
    candidate_lines = Path(candidate_dump).read_text(errors='replace').splitlines()
    base_tpr_size = _tpr_body_size_binding(base_dump, base_lines, 'baseline')
    candidate_tpr_size = _tpr_body_size_binding(candidate_dump, candidate_lines, 'candidate')
    metadata['tpr_body_size'] = {'baseline':base_tpr_size, 'candidate':candidate_tpr_size}
    # Normalize only the integer in the validated, exact-position TPR header
    # field. Every adjacent header field and all remaining outer data stay exact.
    before_b[-1] = base_tpr_size['normalized_line']
    before_c[-1] = candidate_tpr_size['normalized_line']
    seed_re = re.compile(r'^\s*ld-seed\s*=\s*([-+]?\d+)\s*$')
    bseed = [line for line in before_b if seed_re.match(line)]
    cseed = [line for line in before_c if seed_re.match(line)]
    if len(bseed) != 1 or len(cseed) != 1:
        raise RuntimeError('expected exactly one inputrec ld-seed in each physical TPR dump')
    metadata['ld_seed'] = {'baseline_raw':bseed[0], 'candidate_raw':cseed[0],
                           'baseline_raw_sha256':hashlib.sha256(bseed[0].encode()).hexdigest(),
                           'candidate_raw_sha256':hashlib.sha256(cseed[0].encode()).hexdigest(),
                           'normalized_as_unused_metadata':context['unused_ld_seed_context_proven'],
                           'context':context}
    if context['unused_ld_seed_context_proven']:
        seed_value_re = re.compile(r'^(\s*ld-seed\s*=\s*)[-+]?\d+(\s*)$')
        before_b = [seed_value_re.sub(r'\g<1><UNUSED_GENERATED_SEED>\g<2>', line) if seed_re.match(line) else line for line in before_b]
        before_c = [seed_value_re.sub(r'\g<1><UNUSED_GENERATED_SEED>\g<2>', line) if seed_re.match(line) else line for line in before_c]

    def footer(lines, label):
        work = [i for i,line in enumerate(lines) if re.match(r'^Working dir:\s+.*$',line)]
        reminders = [i for i,line in enumerate(lines) if re.match(r'^GROMACS reminds you:\s+.*$',line)]
        if len(work) != 1 or len(reminders) != 1:
            raise RuntimeError(f'{label} dump must have one Working dir and one GROMACS reminder footer line')
        wi, ri = work[0], reminders[0]
        # These are the only path/quote fields excluded by V4; all surrounding
        # executable, version, data-prefix, command and read-file lines remain exact.
        raw_work, raw_reminder = lines[wi], lines[ri]
        lines[wi] = re.sub(r'^(Working dir:\s+).+$', r'\g<1><WORKING_DIRECTORY>', raw_work)
        lines[ri] = re.sub(r'^(GROMACS reminds you:\s+).+$', r'\g<1><REMINDER_QUOTE>', raw_reminder)
        removed_trailing_blank = bool(lines and lines[-1] == '')
        if removed_trailing_blank:
            lines.pop()  # at most the single optional final blank footer line
        return {'working_dir_raw':raw_work,'working_dir_raw_sha256':hashlib.sha256(raw_work.encode()).hexdigest(),
                'reminder_raw':raw_reminder,'reminder_raw_sha256':hashlib.sha256(raw_reminder.encode()).hexdigest(),
                'optional_final_blank_removed':removed_trailing_blank}

    metadata['baseline_footer'] = footer(after_b,'baseline')
    metadata['candidate_footer'] = footer(after_c,'candidate')
    return tuple(before_b),tuple(before_c),tuple(after_b),tuple(after_c),metadata


def _target_interactions(variable, multiplier, baseline_interactions):
    class_token = {'BOND_EQUILIBRIUM':'BONDS','ANGLE_EQUILIBRIUM':'UREY_BRADLEY',
                   'GROUPED_TORSION_DIAGNOSTIC_ONLY':'PDIHS'}[variable['parameter_class']]
    target_labels = {'BOND_EQUILIBRIUM':('b0A','b0B'),
                     'ANGLE_EQUILIBRIUM':('thetaA','thetaB'),
                     'GROUPED_TORSION_DIAGNOSTIC_ONLY':('cpA','cpB')}[variable['parameter_class']]
    targets = {}
    for term in variable.get('terms', []):
        base_value = float(term.get('base_amplitude_kJ_mol', term.get('base')))
        delta = multiplier * float(variable['h'])
        endpoint = base_value * (1.0 + delta) if variable['field'] == 'proportional_amplitude_scale' else base_value + delta
        instance_text = term.get('instances', '')
        instances = [tuple(int(x) - 1 for x in token.split('-'))
                     for token in instance_text.split(';') if token]
        if not instances:
            raise RuntimeError(f"variable term has no declared active atom instances: {variable['id']} {term}")
        for atoms in instances:
            canonical = _canonical_atoms(atoms)
            candidates = [(key, rec) for key, rec in baseline_interactions.items()
                          if key[0] == class_token and key[1] == canonical]
            if 'multiplicity' in term:
                candidates = [(key, rec) for key, rec in candidates
                              if 'mult' in rec['coefficients'] and
                              _decimal(rec['coefficients']['mult']) == Decimal(str(term['multiplicity']))]
            if 'phase_deg' in term:
                candidates = [(key, rec) for key, rec in candidates
                              if 'phiA' in rec['coefficients'] and
                              _decimal(rec['coefficients']['phiA']) == Decimal(str(term['phase_deg']))]
            if len(candidates) != 1:
                raise RuntimeError(f"declared instance {atoms} maps to {len(candidates)} active baseline {class_token} records for {variable['id']}")
            key, rec = candidates[0]
            if key in targets:
                raise RuntimeError(f"duplicate target interaction mapping for {variable['id']}: {key}")
            for label in target_labels:
                if label not in rec['coefficients']:
                    raise RuntimeError(f"target A/B coefficient {label} missing from active instance {key}")
                baseline_value = _decimal(rec['coefficients'][label])
                if abs(float(baseline_value) - base_value) > max(2e-6, abs(base_value)*2e-7):
                    raise RuntimeError(f"baseline active instance {key} {label}={baseline_value} does not match source base {base_value}")
            targets[key] = {'target_labels':target_labels, 'base_value':base_value,
                            'endpoint':endpoint, 'term_id':term['term_id']}
    if not targets:
        raise RuntimeError(f"no active atom-instance targets declared for {variable['id']}")
    return targets


def tpr_parameter_diff(base_dump, candidate_dump, variable, multiplier, manifest):
    base = _topology_semantics(base_dump)
    cand = _topology_semantics(candidate_dump)
    outer_before_b,outer_before_c,outer_after_b,outer_after_c,metadata = _normalize_dump_metadata(
        base_dump,candidate_dump,base,cand)
    if outer_before_b != outer_before_c or outer_after_b != outer_after_c:
        raise RuntimeError('perturbed TPR changed non-topology run-control, nonbonded settings, box, or coordinate data')
    if base['skeleton'] != cand['skeleton']:
        raise RuntimeError('perturbed TPR changed atom identity/type/charge/mass, exclusions, topology counts, or other fixed topology structure')
    if base['nonbonded_table'] != cand['nonbonded_table']:
        raise RuntimeError('perturbed TPR changed LJ_SR/LJ14 nonbonded coefficient inventory')
    bmap, cmap = base['interactions'], cand['interactions']
    if set(bmap) != set(cmap):
        missing = sorted(set(bmap)-set(cmap))
        extra = sorted(set(cmap)-set(bmap))
        raise RuntimeError(f'perturbed TPR changed active interaction instance graph/count: missing={missing}, extra={extra}')
    targets = _target_interactions(variable, multiplier, bmap)
    if not set(targets).issubset(bmap):
        raise RuntimeError('declared target active interaction is absent from baseline interaction graph')
    observed = {}
    for key in bmap:
        before = bmap[key]['coefficients']
        after = cmap[key]['coefficients']
        target = targets.get(key)
        ignored = set(target['target_labels']) if target else set()
        before_frozen = {name:value for name,value in before.items() if name not in ignored}
        after_frozen = {name:value for name,value in after.items() if name not in ignored}
        if before_frozen.keys() != after_frozen.keys():
            raise RuntimeError(f'active coefficient inventory changed for interaction {key}')
        if any(_decimal(before_frozen[name]) != _decimal(after_frozen[name]) for name in before_frozen):
            raise RuntimeError(f'non-target active coefficient changed for interaction {key}')
        if target:
            for label in target['target_labels']:
                if label not in after:
                    raise RuntimeError(f'perturbed active target field {label} missing for interaction {key}')
                actual = float(_decimal(after[label]))
                expected = target['endpoint']
                if abs(actual-expected) > max(2e-6, abs(actual)*2e-7):
                    raise RuntimeError(f'active instance {key} {label}={actual} does not match endpoint {expected}')
            observed[str(key)] = {label:float(_decimal(after[label])) for label in target['target_labels']}
        elif before.keys() != after.keys() or any(_decimal(before[name]) != _decimal(after[name]) for name in before):
            raise RuntimeError(f'non-target active interaction coefficient changed for {key}')
    return {'variable_id':variable['id'],'multiplier':multiplier,
            'target_active_instance_count':len(targets),
            'target_active_instances':[{'class':key[0],'atoms_0based':list(key[1]),'occurrence':key[2],
                                        **targets[key]} for key in sorted(targets)],
            'observed_target_values_by_instance':observed,
            'active_interaction_count':len(bmap),
            'nonbonded_lj_table_entry_count':sum(base['nonbonded_table'].values()),
            'normalized_nonsemantic_dump_metadata':metadata,
            'active_instance_graph_unchanged':True,
            'fixed_topology_and_run_controls_unchanged':True}


def preflight(manifest, source_map):
    global active_preflight_path
    states = {state_key(s): s for s in manifest['states']}
    primary_ids = {s['state_id'] for s in manifest['states'] if s['stage']=='primary' and s['variable_id'] and abs(s['multiplier'])==1}
    audit_ids = {s['state_id'] for s in manifest['states'] if s['stage']=='tight_audit' and s['variable_id'] and abs(s['multiplier'])==1}
    chosen = ['primary__BASE'] + [f'primary__{sid}' for sid in sorted(primary_ids)] + ['tight_audit__BASE'] + [f'tight_audit__{sid}' for sid in sorted(audit_ids)]
    jobs = []
    attempt_id = time.strftime('attempt_%Y%m%dT%H%M%S_UTC', time.gmtime()) + f'_{time.time_ns()%1000000:06d}'
    pfroot = ROOT/'preflight'/attempt_id/'states'
    pfroot.mkdir(parents=True, exist_ok=False)
    active_preflight_path = ROOT/'receipts'/f'PREFLIGHT_GROMPP_ONLY_{attempt_id}.json'
    write_json(active_preflight_path, {'status':'IN_PROGRESS_GROMPP_ONLY','attempt_id':attempt_id,
        'protocol_hash':manifest['protocol_hash'],'variable_spec_hash':manifest['variable_spec_hash'],
        'scope':'NO_MDRUN'})
    for skey in chosen:
        state_row = states[skey]
        state = pfroot/skey
        state.mkdir(parents=True, exist_ok=False)
        state_receipt = patch_state(state, state_row, manifest)
        # Include one geometry and one profile TPR for baseline; one geometry
        # and one profile TPR for each perturbed state.
        chosen_sources = [next(x for x in source_map if x['point_id'] == 'GEO_A'),
                          next(x for x in source_map if x['point_id'] == 'T_CC_300')]
        for source in chosen_sources:
            job = make_job(state, state_row, source, manifest)
            start_domain = pair_domain_receipt(job/'start.g96')
            # Geometry/profile minimization TPRs test topology and tolerance.
            grompp_only(job, 'lbfgs', 'topol_min.top', 'start.g96', float(state_row['tolerance']))
            dump_tpr(job, 'lbfgs')
            grompp_only(job, 'physical', 'topol_physical.top', 'start.g96', float(state_row['tolerance']), physical=True)
            dump_tpr(job, 'physical')
            if source.get('series'):
                restraint_text=(job/'pfbs_ani_restraint.itp').read_text()
                if restraint_text.count('[ dihedral_restraints ]') != 1 or f'{K_RESTRAINT:.1f}' not in restraint_text:
                    raise RuntimeError(f'profile restraint semantics malformed for {source["point_id"]}')
                if '[ dihedral_restraints ]' in (job/'topol_physical.top').read_text() or 'pfbs_ani_restraint.itp' in (job/'topol_physical.top').read_text():
                    raise RuntimeError('physical topology contains scan restraint')
            elif '[ dihedral_restraints ]' in (job/'topol_min.top').read_text():
                raise RuntimeError('unrestrained geometry source acquired scan restraint')
            jobs.append({'state_key': skey, 'source_id': source['point_id'], 'job': str(job),
                         'state_hashes': state_receipt['effective_hashes'],
                         'start_pair_domain': start_domain,
                         'tpr_hashes': {x: sha(job/(x+'.tpr')) for x in ('lbfgs','physical')},
                         'dump_hashes': {x: sha(job/(x+'_dump.txt')) for x in ('lbfgs','physical')}})
    reference_dump = dump_reference_tpr()
    case_by_key_source={(x['state_key'],x['source_id']):x for x in jobs}
    base_primary=case_by_key_source[('primary__BASE','T_CC_300')]
    ref_sig=topology_signature(reference_dump)
    base_sig=topology_signature(Path(base_primary['job'])/'physical_dump.txt')
    if ref_sig != base_sig:
        raise RuntimeError('new BASE physical TPR active topology differs from the provenance-bound formal-DP original-source baseline')
    semantic_audits=[]
    by_variable={v['id']:v for v in manifest['variables']}
    for state_row in manifest['states']:
        if not state_row['variable_id'] or abs(state_row['multiplier']) != 1:
            continue
        skey=state_key(state_row)
        base_key=f"{state_row['stage']}__BASE"
        for source in ('GEO_A','T_CC_300'):
            b=case_by_key_source[(base_key,source)]
            c=case_by_key_source[(skey,source)]
            semantic_audits.append(tpr_parameter_diff(Path(b['job'])/'physical_dump.txt',
                Path(c['job'])/'physical_dump.txt',by_variable[state_row['variable_id']],
                state_row['multiplier'],manifest))
    report = {'status': 'PASS_ACTIVE_TPR_SEMANTIC_PREFLIGHT', 'mode': 'GROMPP_ONLY_NO_MINIMIZATION',
              'attempt_id': attempt_id,
              'terminal_addendum_sha256': TERMINAL_ADDENDUM_SHA,
              'terminal_receipt_sha256': TERMINAL_RECEIPT_SHA,
              'failure_scope_addendum_sha256': FAILURE_SCOPE_ADDENDUM_SHA,
              'failure_scope_receipt_sha256': FAILURE_SCOPE_RECEIPT_SHA,
              'protocol_hash': manifest['protocol_hash'], 'variable_spec_hash': manifest['variable_spec_hash'],
              'source_count': len(source_map), 'preflight_state_keys': chosen,
              'cases': jobs, 'machine': os.uname().nodename,
              'formal_dp_original_source_reference': {
                  'tpr_sha256': REFERENCE_DP_BASELINE_TPR_SHA,
                  'tpr_dump_sha256': REFERENCE_DP_BASELINE_DUMP_SHA,
                  'binding_sha256': REFERENCE_DP_BINDING_SHA,
                  'run_record_sha256': REFERENCE_DP_RECORD_SHA,
                  'tpr_remote_path': REFERENCE_DP_TPR_PATH},
              'base_physical_tpr_topology_signature_matches_formal_dp_reference': True,
              'typed_tpr_semantic_audit_cases': len(semantic_audits),
              'typed_tpr_semantic_audit': semantic_audits,
              'pair_domain_gate': {'status':'PASS','box_nm':[10.0,10.0,10.0],
                  'max_all_pair_distance_nm':2.0,'pair_count_per_structure':136,
                  'coordinate_stages':'Preflight verifies every selected start; runtime verifies start, LBFGS terminal, and CG final coordinates for every state/source.'},
              'active_topology_invariant_check':'All non-functype topology lines, including atom charges/types, active terms, exclusions and 1-4 interactions are byte-identical; only the preregistered matching interaction functype rows differ.',
              'gromacs_binary_sha256': sha(GMX), 'workers_planned': NCPU,
              'warning_exception_exact_text': WARNING}
    write_json(active_preflight_path, report)
    return report


def fmax(path):
    text = path.read_text(errors='replace')
    matches = re.findall(r'Maximum force\s*=\s*([-+\d.eE]+)', text)
    if not matches:
        raise RuntimeError(f'Fmax not found in {path}')
    return float(matches[-1])


def positionred_g96(src, out):
    # Preserve raw POSITIONRED output, then map with the verified source atom order.
    job = src.parent
    command([str(GMX), 'trjconv', '-f', 'lbfgs.trr', '-s', 'lbfgs.tpr', '-o', 'lbfgs_positionred.g96', '-ndec', '9'],
            job, 'trjconv_lbfgs', stdin='0\n')
    xyz = read_positionred(job/'lbfgs_positionred.g96')
    (job/'lbfgs_final.g96').write_text(named_g96_text(job/'start.g96', xyz, 'LBFGS terminal coordinates mapped by verified source atom order'))
    return job/'lbfgs_final.g96'


def read_final_xyz(job):
    command([str(GMX), 'trjconv', '-f', 'cg.trr', '-s', 'cg.tpr', '-o', 'final_positionred.g96', '-ndec', '9'],
            job, 'trjconv_cg', stdin='0\n')
    xyz = read_positionred(job/'final_positionred.g96')
    (job/'final.g96').write_text(named_g96_text(job/'start.g96', xyz, 'CG final frame mapped by verified source atom order'))
    return job/'final.g96'


def energy_potential(job):
    out = job/'physical_potential.xvg'
    p = subprocess.run([str(GMX), 'energy', '-dp', '-f', 'physical.edr', '-o', str(out)], cwd=job,
                       input='Potential\n', text=True, capture_output=True, timeout=90)
    text = p.stdout + p.stderr
    (job/'energy_physical.stdout_stderr.txt').write_text(text)
    if p.returncode:
        raise RuntimeError(f'gmx energy failed: {text[-1000:]}')
    raw = [x for x in out.read_text().splitlines() if x.strip() and not x.startswith(('#','@'))]
    if not raw:
        raise RuntimeError('no numeric Potential values in XVG')
    row = raw[-1].split()
    return {'potential_kj_mol': float(row[1]), 'xvg_last_line': raw[-1],
            'xvg_last_time_ps': float(row[0]), 'energy_output_option_dp': True,
            'xvg_sha256': sha(out), 'xvg_precision_decimal_digits': _decimal_places(row[1])}


def check_trr(job):
    p = subprocess.run([str(GMX), 'check', '-f', 'cg.trr'], cwd=job,
                       text=True, capture_output=True, timeout=90)
    combined = p.stdout + p.stderr
    (job/'gmx_check_cg_trr.txt').write_text(combined)
    if p.returncode:
        raise RuntimeError(f'gmx check cg.trr failed: {combined[-1000:]}')
    m = re.search(r'Last frame\s+(\d+)\s+time\s+([-+\d.eE]+)', combined)
    if not m:
        raise RuntimeError('could not parse last cg.trr frame/time from gmx check')
    return {'last_frame_index': int(m.group(1)), 'last_frame_time_ps': float(m.group(2)),
            'check_output_sha256': sha(job/'gmx_check_cg_trr.txt')}


def _decimal_places(s):
    if 'e' in s.lower():
        mantissa, exp = re.split('[eE]', s)
        return max(0, len(mantissa.partition('.')[2]) - int(exp))
    return len(s.partition('.')[2]) if '.' in s else 0


def run_job(task):
    state, source, job = task
    started = time.time()
    receipt_path = job/'RUN_RECEIPT.json'
    rec = json.loads(receipt_path.read_text())
    rec['status'] = 'RUNNING'
    rec['started_epoch'] = started
    write_json(receipt_path, rec)
    try:
        # Same-state only LBFGS -> CG; each state/source starts from original QM input.
        rec['start_pair_domain'] = pair_domain_receipt(job/'start.g96')
        grompp_only(job, 'lbfgs', 'topol_min.top', 'start.g96', float(state['tolerance']))
        command([str(GMX), 'mdrun', '-deffnm', 'lbfgs', '-nt', '1', '-ntmpi', '1', '-ntomp', '1', '-nb', 'cpu'], job, 'mdrun_lbfgs', timeout=1800)
        rec['lbfgs_fmax_kj_mol_nm'] = fmax(job/'lbfgs.log')
        if not math.isfinite(rec['lbfgs_fmax_kj_mol_nm']):
            raise RuntimeError('nonfinite LBFGS Fmax')
        rec['lbfgs_termination_log_tail'] = '\n'.join((job/'lbfgs.log').read_text(errors='replace').splitlines()[-15:])
        pos = positionred_g96(job/'lbfgs.trr', job/'lbfgs_final.g96')
        rec['lbfgs_positionred_g96_sha256'] = sha(job/'lbfgs_positionred.g96')
        rec['lbfgs_final_g96_sha256'] = sha(pos)
        rec['lbfgs_pair_domain'] = pair_domain_receipt(pos)
        grompp_only(job, 'cg', 'topol_min.top', pos.name, float(state['tolerance']))
        command([str(GMX), 'mdrun', '-deffnm', 'cg', '-nt', '1', '-ntmpi', '1', '-ntomp', '1', '-nb', 'cpu'], job, 'mdrun_cg', timeout=1800)
        rec['cg_fmax_kj_mol_nm'] = fmax(job/'cg.log')
        if not math.isfinite(rec['cg_fmax_kj_mol_nm']):
            raise RuntimeError('nonfinite CG Fmax')
        rec['cg_termination_log_tail'] = '\n'.join((job/'cg.log').read_text(errors='replace').splitlines()[-15:])
        final = read_final_xyz(job)
        rec['cg_final_positionred_g96_sha256'] = sha(job/'final_positionred.g96')
        rec['final_g96_sha256'] = sha(final)
        rec['cg_final_pair_domain'] = pair_domain_receipt(final)
        rec['final_g96_coordinate_decimal_digits'] = 9
        traj = check_trr(job)
        rec['cg_trr_sha256'] = sha(job/'cg.trr')
        rec['cg_trr_last_frame_index'] = traj['last_frame_index']
        rec['cg_trr_last_frame_time_ps'] = traj['last_frame_time_ps']
        rec['cg_trr_check_sha256'] = traj['check_output_sha256']
        rec['physical_topology_sha256'] = sha(job/'topol_physical.top')
        grompp_only(job, 'physical', 'topol_physical.top', final.name, float(state['tolerance']), physical=True)
        command([str(GMX), 'mdrun', '-deffnm', 'physical', '-rerun', 'cg.trr', '-nt', '1', '-ntmpi', '1', '-ntomp', '1', '-nb', 'cpu'], job, 'mdrun_physical', timeout=300)
        rec.update(energy_potential(job))
        if abs(rec['xvg_last_time_ps'] - traj['last_frame_time_ps']) > 1e-6:
            raise RuntimeError(f"physical energy time {rec['xvg_last_time_ps']} differs from final cg.trr frame time {traj['last_frame_time_ps']}")
        rec['lbfgs_fmax_within_tolerance_diagnostic'] = rec['lbfgs_fmax_kj_mol_nm'] <= float(state['tolerance'])
        rec['cg_converged'] = rec['cg_fmax_kj_mol_nm'] <= float(state['tolerance'])
        rec['minimization_converged'] = rec['cg_converged']
        rec['warning_events'] = []
        for logp in sorted(job.glob('*.stdout_stderr.txt')):
            logtext = logp.read_text(errors='replace')
            for block in warning_blocks(logtext):
                rec['warning_events'].append({'log':logp.name,'raw_block':block,
                                              'approved':approved_warning_set([block], logp.name)})
        if any(not x['approved'] for x in rec['warning_events']):
            raise RuntimeError(f"post-run warning audit failed: {rec['warning_events']}")
        rec['completed_epoch'] = time.time()
        rec['elapsed_seconds'] = rec['completed_epoch'] - started
        rec['status'] = 'DONE' if rec['minimization_converged'] else 'NUMERICAL_NONCONVERGENCE'
    except Exception as e:
        rec.update(status='FAILED', error=f'{type(e).__name__}: {e}', completed_epoch=time.time(),
                   elapsed_seconds=time.time()-started)
    write_json(receipt_path, rec)
    return rec


def run_all(manifest, source_map):
    tasks = []
    for state_row in manifest['states']:
        state = ROOT/'states'/state_key(state_row)
        if not state.exists():
            state.mkdir(parents=True, exist_ok=False)
            patch_state(state, state_row, manifest)
        for source in source_map:
            job = state/'runs'/source['start_name']
            if not job.exists():
                tasks.append((state_row, source, make_job(state, state_row, source, manifest)))
            else:
                rec_path = job/'RUN_RECEIPT.json'
                rec = json.loads(rec_path.read_text()) if rec_path.exists() else {}
                if rec.get('status') == 'DONE':
                    continue
                raise RuntimeError(f'pre-existing/incomplete run dir requires manual preservation: {job}')
    ROOT.joinpath('receipts','RUN_CONTROL.json').write_text(json.dumps({
        'status':'RUNNING','total':manifest['expected_runs'],'pending':len(tasks),
        'workers':NCPU,'thread_cap':1,'gpu':False,'started_epoch':time.time(),
        'protocol_hash':manifest['protocol_hash']},indent=2)+'\n')
    finished = 0
    errors = 0
    elapsed = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=NCPU) as pool:
        task_iter = iter(tasks)
        pending = set()
        for _ in range(min(NCPU, len(tasks))):
            pending.add(pool.submit(run_job, next(task_iter)))
        stopped = False
        while pending:
            done, pending = concurrent.futures.wait(pending, return_when=concurrent.futures.FIRST_COMPLETED)
            results = [(fut, fut.result()) for fut in done]
            if any(rec['status'] == 'FAILED' for _, rec in results):
                stopped = True
            for fut, rec in results:
                finished += 1
                elapsed.append(rec.get('elapsed_seconds', 0))
                errors += rec['status'] in ('FAILED','NUMERICAL_NONCONVERGENCE')
                if rec['status'] != 'FAILED' and not stopped:
                    try:
                        pending.add(pool.submit(run_job, next(task_iter)))
                    except StopIteration:
                        pass
            if stopped:
                for fut in pending:
                    fut.cancel()
                concurrent.futures.wait(pending)
                break
            control = {'status':'RUNNING','total':manifest['expected_runs'],
                       'completed_this_invocation':finished,'pending_this_invocation':len(tasks)-finished,
                       'failures_or_nonconverged':errors,'workers':NCPU,'thread_cap':1,'gpu':False,
                       'elapsed_wall_seconds':time.time()-tasks_started,
                       'median_completed_job_seconds':sorted(elapsed)[len(elapsed)//2] if elapsed else None,
                       'remaining_jobs':len(tasks)-finished,
                       'eta_seconds_at_observed_rate':(len(tasks)-finished)*(time.time()-tasks_started)/max(finished,1),
                       'protocol_hash':manifest['protocol_hash']}
            write_json(ROOT/'receipts'/'RUN_CONTROL.json', control)
            if finished % 16 == 0 or finished == len(tasks):
                print(f"completed={finished}/{len(tasks)} issues={errors} median_s={control['median_completed_job_seconds']:.1f} eta_s={control['eta_seconds_at_observed_rate']:.0f}", flush=True)
    status = 'COMPLETE' if finished == len(tasks) and errors == 0 else 'COMPLETE_WITH_NUMERICAL_NONCONVERGENCE' if finished == len(tasks) else 'STOPPED_ON_EXECUTION_FAILURE' if errors else 'INCOMPLETE'
    write_json(ROOT/'receipts'/'RUN_CONTROL.json', {'status':status,'total':manifest['expected_runs'],
        'completed_this_invocation':finished,'failures_or_nonconverged':errors,'workers':NCPU,
        'elapsed_wall_seconds':time.time()-tasks_started,'protocol_hash':manifest['protocol_hash']})
    return status


def main():
    global tasks_started
    tasks_started = time.time()
    ap = argparse.ArgumentParser()
    ap.add_argument('--preflight-only', action='store_true')
    ap.add_argument('--run', action='store_true')
    args = ap.parse_args()
    manifest = json.loads(MANIFEST.read_text())
    input_hashes = verify_sources(manifest)
    binding = json.loads((SOURCE/'QM_SOURCE_BINDING.json').read_text())
    source_map = build_matrix(manifest, binding)
    if args.preflight_only:
        report = preflight(manifest, source_map)
        report['input_hashes'] = input_hashes
        print(json.dumps({'status':report['status'],'mode':report['mode'],'cases':len(report['cases']),
                          'hashes':input_hashes},indent=2), flush=True)
        return 0
    if args.run:
        status = run_all(manifest, source_map)
        return 0 if status == 'COMPLETE' else 2
    ap.error('select --preflight-only or --run')


if __name__ == '__main__':
    try:
        sys.exit(main())
    except Exception as exc:
        if active_preflight_path is not None and active_preflight_path.exists():
            try:
                failed = json.loads(active_preflight_path.read_text())
                if failed.get('status') == 'IN_PROGRESS_GROMPP_ONLY':
                    failed.update(status='FAILED_GROMPP_PREFLIGHT',
                                  failure=f'{type(exc).__name__}: {exc}',
                                  failed_epoch=time.time())
                    write_json(active_preflight_path, failed)
            except Exception as receipt_exc:
                print(f'PREFLIGHT_RECEIPT_UPDATE_FAILED {type(receipt_exc).__name__}: {receipt_exc}',
                      file=sys.stderr, flush=True)
        print(f'FATAL {type(exc).__name__}: {exc}', file=sys.stderr, flush=True)
        raise
