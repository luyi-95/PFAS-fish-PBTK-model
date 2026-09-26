#!/usr/bin/env python3
"""Frozen read-only PFBS MM finite-difference/SVD analysis (no fitting).

Inputs are the terminal compact run export plus the immutable V2 protocol and
source definitions. All output goes to a new analysis directory; the matrix
runtime and its receipts are never modified.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import itertools
import json
import math
import re
from collections import Counter, defaultdict
from decimal import Decimal
from pathlib import Path

import numpy as np


HARTREE_TO_KCAL = Decimal("627.5094740631")
KJ_PER_KCAL = Decimal("4.184")
EPS = np.finfo(float).eps
OBS_SCALES = {"bond": 0.03, "angle": 3.0, "profile_energy": 1.0, "AB_energy": 1.0}


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def write_tsv(path: Path, rows, columns=None):
    rows = list(rows)
    if columns is None:
        columns = list(rows[0]) if rows else []
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=columns, delimiter="\t", extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({k: json.dumps(row.get(k), sort_keys=True, separators=(",", ":"))
                             if isinstance(row.get(k), (dict, list)) else row.get(k)
                             for k in columns})


def parse_itp_atom_types(itp: Path):
    section = None
    types, charges, masses, names = {}, {}, {}, {}
    for line in itp.read_text(encoding="utf-8").splitlines():
        m = re.match(r"\s*\[\s*([^]]+)\s*\]", line)
        if m:
            section = m.group(1).strip().lower()
            continue
        if section != "atoms" or not line.strip() or line.lstrip().startswith(";"):
            continue
        fields = line.split(";", 1)[0].split()
        if len(fields) < 8 or not fields[0].isdigit():
            continue
        atom = int(fields[0])
        types[atom] = fields[1]
        names[atom] = fields[4]
        charges[atom] = Decimal(fields[6])
        masses[atom] = Decimal(fields[7])
    if len(types) != 17 or set(types) != set(range(1, 18)):
        raise ValueError(f"expected 17 ordered ITP atom records; found {len(types)}")
    return types, charges, masses, names


def topology_terms(itp: Path):
    """Read only the explicit active molecule graph/geometry indices from v1 ITP."""
    section = None
    result = {"bonds": set(), "angles": set(), "dihedrals": set(), "pairs": set(), "exclusions": set()}
    for line in itp.read_text(encoding="utf-8").splitlines():
        match = re.match(r"\s*\[\s*([^]]+)\s*\]", line)
        if match:
            section = match.group(1).strip().lower()
            continue
        if section not in result or not line.strip() or line.lstrip().startswith(";"):
            continue
        fields = line.split(";", 1)[0].split()
        if not fields or not fields[0].isdigit():
            continue
        n = {"bonds": 2, "angles": 3, "dihedrals": 4, "pairs": 2}.get(section)
        if n:
            if len(fields) < n + 1:
                raise ValueError(f"malformed {section} row: {line}")
            atoms = tuple(map(int, fields[:n]))
            if section == "bonds" or section == "pairs":
                atoms = tuple(sorted(atoms))
            elif section in ("angles", "dihedrals"):
                atoms = min(atoms, atoms[::-1])
            result[section].add(atoms)
        elif section == "exclusions":
            atoms = tuple(map(int, fields))
            for other in atoms[1:]:
                result[section].add(tuple(sorted((atoms[0], other))))
    if not result["bonds"] or not result["angles"] or not result["dihedrals"]:
        raise ValueError("v1 ITP topology is missing explicit bond/angle/dihedral graph terms")
    return result


def graph_automorphisms(itp: Path, cs_restraint=False):
    """Enumerate graph/type/charge/mass/proper-preserving PFBS atom maps."""
    types, charges, masses, _ = parse_itp_atom_types(itp)
    base = topology_terms(itp)
    candidates = []
    # One-based ITP atom indices: O1/O2/O3, CF3 F7-F9, and three matched CF2 pairs.
    for osperm in itertools.permutations((11, 12, 13)):
        for cf3perm in itertools.permutations((8, 9, 10)):
            for flips in itertools.product((False, True), repeat=3):
                p = list(range(1, 18))
                for target, perm in (((11, 12, 13), osperm), ((8, 9, 10), cf3perm)):
                    for old, new in zip(target, perm):
                        p[old - 1] = new
                for (a, b), flip in zip(((2, 3), (4, 5), (6, 7)), flips):
                    if flip:
                        p[a - 1], p[b - 1] = p[b - 1], p[a - 1]
                if len(set(p)) != 17:
                    continue
                if cs_restraint and p[10] != 11:  # O1 (atom 11) stays the restrained oxygen.
                    continue
                if any(types[i] != types[p[i-1]] or charges[i] != charges[p[i-1]] or masses[i] != masses[p[i-1]]
                       for i in range(1, 18)):
                    continue
                mapped = {}
                for sec, terms in base.items():
                    transformed = set()
                    for term in terms:
                        mapped_term = tuple(p[i-1] for i in term)
                        if sec in ("bonds", "pairs", "exclusions"):
                            mapped_term = tuple(sorted(mapped_term))
                        else:
                            mapped_term = min(mapped_term, mapped_term[::-1])
                        transformed.add(mapped_term)
                    mapped[sec] = transformed
                if mapped == base:
                    candidates.append(tuple(p))
    if not candidates:
        raise ValueError("no topology-preserving atom automorphisms found")
    return sorted(set(candidates))


def vector(row, atom_name):
    item = next(x for x in row["final_coordinates_nm"] if x["atom"] == atom_name)
    return np.asarray([float(v) for v in item["xyz_raw_nm"]], dtype=float)


def vector_from_coords(coords, index):
    return np.asarray([float(v) for v in coords[index - 1]["xyz_raw_nm"]], dtype=float)


def bond_length_nm(a, b):
    return float(np.linalg.norm(a - b))


def angle_deg(a, b, c):
    u, v = a - b, c - b
    # atan2 form is stable near 0/180 degrees.
    return float(math.degrees(math.atan2(float(np.linalg.norm(np.cross(u, v))), float(np.dot(u, v)))))


def wrap_deg(x):
    return (float(x) + 180.0) % 360.0 - 180.0


def dihedral_deg(coords, atom_indices):
    p0, p1, p2, p3 = [vector_from_coords(coords, i) for i in atom_indices]
    sub = lambda a, b: a - b
    dot = lambda a, b: float(np.dot(a, b))
    cross = lambda a, b: np.cross(a, b)
    b0, b1, b2 = sub(p0, p1), sub(p2, p1), sub(p3, p2)
    norm = float(np.linalg.norm(b1))
    if norm == 0 or not math.isfinite(norm):
        raise ValueError(f"undefined dihedral {atom_indices}")
    b1 = b1 / norm
    v = b0 - dot(b0, b1) * b1
    w = b2 - dot(b2, b1) * b1
    value = math.degrees(math.atan2(dot(cross(b1, v), w), dot(v, w)))
    if not math.isfinite(value):
        raise ValueError(f"nonfinite dihedral {atom_indices}")
    return value


def decimal_places(text):
    d = Decimal(text.strip())
    return max(0, -d.as_tuple().exponent)


def potential_decimal(record):
    raw = record.get("raw_energy_xvg_last_line") or record.get("xvg_last_line")
    if not raw:
        raise ValueError(f"missing raw XVG line for {record.get('state_key')} {record.get('source_id')}")
    fields = raw.split()
    if len(fields) < 2:
        raise ValueError(f"malformed XVG row: {raw!r}")
    return Decimal(fields[1]), fields[1], raw


def xvg_quantum_bound(raw_energy_string):
    places = decimal_places(raw_energy_string)
    return Decimal("0.5") * (Decimal(10) ** (-places))


def geometry_rows(reference_tsv: Path, atom_types):
    data = list(csv.DictReader(reference_tsv.open(encoding="utf-8-sig", newline=""), delimiter="\t"))
    selected = [row for row in data if row.get("geometry") == "GEO_A"]
    bonds, angles = [], []
    for row in selected:
        kind = row["class"].strip().lower()
        term = row["term"]
        if kind == "bonds":
            match = re.search(r"\((\d+)-(\d+)\)$", term)
            if not match:
                raise ValueError(f"cannot parse bond atom indices from {term}")
            i, j = map(int, match.groups())
            family = "-".join(sorted((atom_types[i], atom_types[j])))
            bonds.append({"kind": "bond", "names": term.split("(")[0], "indices": (i, j), "family": family,
                          "unit": "angstrom", "block": "bond"})
        elif kind == "angles":
            names = term.split("(")[0].split("-")
            if len(names) != 3:
                raise ValueError(f"cannot parse angle atom names from {term}")
            angle_atom = {"S1": 1, **{f"F{i}": i+1 for i in range(1,10)},
                          "O1": 11, "O2": 12, "O3": 13, "C1": 14, "C2": 15, "C3": 16, "C4": 17}
            ids = tuple(angle_atom[n] for n in names)
            endtypes = sorted((atom_types[ids[0]], atom_types[ids[2]]))
            family = f"{endtypes[0]}-{atom_types[ids[1]]}-{endtypes[1]}"
            angles.append({"kind": "angle", "names": term, "indices": ids, "family": family,
                           "unit": "degree", "block": "angle"})
        else:
            raise ValueError(f"unrecognized geometry observable class {kind!r}")
    if len(bonds) != 16 or len(angles) != 30:
        raise ValueError(f"expected 16 bonds+30 angles, got {len(bonds)}+{len(angles)}")
    if len({x["family"] for x in bonds}) != 6 or len({x["family"] for x in angles}) != 11:
        raise ValueError("geometry type-family cardinality differs from preregistered 6/11")
    return bonds, angles


def observable_catalog(export, binding, geometry_tsv, itp):
    atom_types, _, _, _ = parse_itp_atom_types(itp)
    bonds, angles = geometry_rows(geometry_tsv, atom_types)
    point_rows = binding["points"]
    cc = [x for x in point_rows if x["series"] == "T_CC" and x["point_id"] != "T_CC_300"]
    cs = [x for x in point_rows if x["series"] == "T_CS"]
    if len(cc) != 11 or len(cs) != 13:
        raise ValueError(f"expected 11 non-anchor CC plus the CC300 anchor, and 13 CS rows; got {len(cc)}+{len(cs)}")
    rows = []
    for geometry, source_id in (("A", "GEO_A"), ("B", "GEO_B_REVISED")):
        for item in bonds:
            row = dict(item, observable_id=f"BOND|{geometry}|{item['names']}", geometry=geometry,
                       source_id=source_id, obs_scale=OBS_SCALES["bond"])
            rows.append(row)
        for item in angles:
            row = dict(item, observable_id=f"ANGLE|{geometry}|{item['names']}", geometry=geometry,
                       source_id=source_id, obs_scale=OBS_SCALES["angle"])
            rows.append(row)
    for x in cc + cs:
        axis = x["series"]
        rows.append({"kind": "profile_energy", "observable_id": f"PES|{x['point_id']}",
                     "source_id": x["point_id"], "axis": axis, "family": axis, "unit": "kcal/mol",
                     "block": "PES", "obs_scale": OBS_SCALES["profile_energy"],
                     "qm_energy_hartree": x["qm_energy_hartree"]})
    # CC300 is part of the frozen 25-row PES block and is also the common
    # zero-relative-energy anchor; its row is exactly zero in every state.
    anchor = next(x for x in point_rows if x["point_id"] == "T_CC_300")
    rows.append({"kind": "profile_anchor", "observable_id": "PES|T_CC_300_ANCHOR_ZERO",
                 "source_id": "T_CC_300", "axis": "T_CC", "family": "T_CC",
                 "unit": "kcal/mol", "block": "PES", "obs_scale": OBS_SCALES["profile_energy"],
                 "qm_energy_hartree": anchor["qm_energy_hartree"]})
    rows.append({"kind": "AB_energy", "observable_id": "AB_ENERGY|GEO_B_REVISED-GEO_A",
                 "source_id": "GEO_B_REVISED-GEO_A", "family": "AB_energy", "unit": "kcal/mol",
                 "block": "AB_energy", "obs_scale": OBS_SCALES["AB_energy"]})
    if sum(x.get("primary", True) for x in rows) != 118 or len(rows) != 118:
        raise ValueError("expected 118 primary observables including the CC300 zero anchor")
    bond_counts = Counter(x["family"] for x in bonds)
    angle_counts = Counter(x["family"] for x in angles)
    for row in rows:
        if row["kind"] == "bond":
            row["row_weight"] = 1.0 / math.sqrt(2.0 * 6.0 * bond_counts[row["family"]])
        elif row["kind"] == "angle":
            row["row_weight"] = 1.0 / math.sqrt(2.0 * 11.0 * angle_counts[row["family"]])
        elif row["kind"] in ("profile_energy", "profile_anchor"):
            n = 12 if row["axis"] == "T_CC" else 13
            row["row_weight"] = 1.0 / math.sqrt(2.0 * n)
        else:
            row["row_weight"] = 1.0
    # The fixed weights must sum to one squared within each declared block.
    for block in ("bond", "angle", "PES", "AB_energy"):
        mass = sum(x["row_weight"]**2 for x in rows if x["block"] == block and x.get("primary", True))
        if abs(mass - 1.0) > 1e-12:
            raise ValueError(f"frozen {block} weights do not sum to one: {mass}")
    return rows, bonds, angles


def geometry_value(record, row):
    coords = record["final_coordinates_nm"]
    inds = row["indices"]
    xyz = [vector_from_coords(coords, i) for i in inds]
    if row["kind"] == "bond":
        value = bond_length_nm(*xyz) * 10.0
        # Each Cartesian coordinate is serialized to 9 decimals in nm; each
        # atom coordinate contributes +/- half a unit to the displacement.
        bound = math.sqrt(3.0) * 1e-9 * 10.0
        raw_inputs = ";".join(f"{coords[i-1]['atom']}:{','.join(coords[i-1]['xyz_raw_nm'])}" for i in inds)
    else:
        value = angle_deg(*xyz)
        arm1 = float(np.linalg.norm(xyz[0] - xyz[1]))
        arm2 = float(np.linalg.norm(xyz[2] - xyz[1]))
        if min(arm1, arm2) <= 0:
            raise ValueError(f"degenerate angle geometry: {row['observable_id']}")
        arm_jitter = math.sqrt(3.0) * 1e-9
        bound = math.degrees(arm_jitter / arm1 + arm_jitter / arm2)
        raw_inputs = ";".join(f"{coords[i-1]['atom']}:{','.join(coords[i-1]['xyz_raw_nm'])}" for i in inds)
    bound += 32.0 * EPS * max(1.0, abs(value))
    return float(value), float(bound), raw_inputs


def energy_value(records_by_source, row):
    if row["kind"] == "profile_anchor":
        # It is exactly the shared energy anchor subtracted from itself.
        return 0.0, 0.0, "anchor=raw_same_record_minus_itself;exact_zero"
    if row["kind"] == "profile_energy":
        profile = records_by_source[row["source_id"]]
        anchor = records_by_source["T_CC_300"]
        e1, s1, raw1 = potential_decimal(profile)
        e0, s0, raw0 = potential_decimal(anchor)
        value = float((e1 - e0) / KJ_PER_KCAL)
        bound = float((xvg_quantum_bound(s1) + xvg_quantum_bound(s0)) / KJ_PER_KCAL)
        bound += 16.0 * EPS * max(1.0, abs(value))
        return value, bound, f"profile={s1};anchor={s0}"
    a, sa, _ = potential_decimal(records_by_source["GEO_A"])
    b, sb, _ = potential_decimal(records_by_source["GEO_B_REVISED"])
    value = float((b - a) / KJ_PER_KCAL)
    bound = float((xvg_quantum_bound(sa) + xvg_quantum_bound(sb)) / KJ_PER_KCAL)
    bound += 16.0 * EPS * max(1.0, abs(value))
    return value, bound, f"GEO_B_REVISED={sb};GEO_A={sa}"


def build_observations(export, catalog):
    records = export["rows"]
    by_state = defaultdict(dict)
    for rec in records:
        if rec.get("status") != "DONE":
            raise ValueError(f"non-DONE run in matrix: {rec.get('state_key')} {rec.get('source_id')} {rec.get('status')}")
        by_state[rec["state_key"]][rec["source_id"]] = rec
    if len(by_state) != 62 or any(len(v) != 28 for v in by_state.values()):
        raise ValueError("terminal run export is not a complete 62x28 matrix")
    observations = {}
    raw_rows = []
    for state_key, source_records in by_state.items():
        obs = {}
        for row in catalog:
            if row["kind"] in ("bond", "angle"):
                rec = source_records[row["source_id"]]
                value, bound, raw = geometry_value(rec, row)
                run_sha = rec["final_g96_sha256"]
                source_sha = rec["source_geometry_sha256"]
            else:
                value, bound, raw = energy_value(source_records, row)
                if row["kind"] in ("profile_energy", "profile_anchor"):
                    run_sha = source_records[row["source_id"]]["xvg_sha256"]
                    source_sha = source_records[row["source_id"]]["source_geometry_sha256"]
                else:
                    run_sha = hashlib.sha256((source_records["GEO_A"]["xvg_sha256"] + source_records["GEO_B_REVISED"]["xvg_sha256"]).encode()).hexdigest()
                    source_sha = "A=" + source_records["GEO_A"]["source_geometry_sha256"] + ";B=" + source_records["GEO_B_REVISED"]["source_geometry_sha256"]
            obs[row["observable_id"]] = {"value": value, "rounding_bound": bound, "raw_inputs": raw}
            raw_rows.append({"state_key": state_key, "source_id": row["source_id"],
                             "observable_id": row["observable_id"], "kind": row["kind"],
                             "block": row["block"], "family": row["family"], "unit": row["unit"],
                             "raw_value": format(value, ".17g"), "raw_input_numeric_strings": raw,
                             "serialized_input_sha256": run_sha, "source_geometry_sha256": source_sha,
                             "row_weight": row["row_weight"], "observable_scale": row["obs_scale"]})
        observations[state_key] = obs
    return by_state, observations, raw_rows


def calculate_derivatives(by_state, observations, catalog, variables):
    obs_ids = [x["observable_id"] for x in catalog]
    raw = {tag: np.zeros((len(catalog), len(variables))) for tag in ("h", "2h", "tight")}
    raw_round_h = np.zeros((len(catalog), len(variables)))
    raw_round_2h = np.zeros((len(catalog), len(variables)))
    raw_round_tight = np.zeros((len(catalog), len(variables)))
    raw_h_endpoints = {}
    details = []
    for j, var in enumerate(variables):
        vid, h = var["id"], float(var["h"])
        keys = {
            "ph": f"primary__{vid}_+1h", "mh": f"primary__{vid}_-1h",
            "p2": f"primary__{vid}_+2h", "m2": f"primary__{vid}_-2h",
            "pt": f"tight_audit__{vid}_+1h", "mt": f"tight_audit__{vid}_-1h",
        }
        for k in keys.values():
            if k not in observations:
                raise KeyError(f"missing preregistered derivative state {k}")
        raw_h_endpoints[vid] = keys
        for i, oid in enumerate(obs_ids):
            plus, minus = observations[keys["ph"]][oid], observations[keys["mh"]][oid]
            plus2, minus2 = observations[keys["p2"]][oid], observations[keys["m2"]][oid]
            plust, minust = observations[keys["pt"]][oid], observations[keys["mt"]][oid]
            raw["h"][i, j] = (plus["value"] - minus["value"]) / (2.0*h)
            raw["2h"][i, j] = (plus2["value"] - minus2["value"]) / (4.0*h)
            raw["tight"][i, j] = (plust["value"] - minust["value"]) / (2.0*h)
            # Endpoint serialization/coordinate uncertainty propagates through
            # the central difference; no Richardson discount is applied.
            raw_round_h[i, j] = (plus["rounding_bound"] + minus["rounding_bound"])/(2.0*h)
            raw_round_2h[i, j] = (plus2["rounding_bound"] + minus2["rounding_bound"])/(4.0*h)
            raw_round_tight[i, j] = (plust["rounding_bound"] + minust["rounding_bound"])/(2.0*h)
            details.append({"observable_id": oid, "variable_id": vid,
                            "J_h_raw": raw["h"][i,j], "J_2h_raw": raw["2h"][i,j],
                            "J_h_tight_raw": raw["tight"][i,j],
                            "rounding_bound_h_raw": raw_round_h[i,j],
                            "rounding_bound_2h_raw": raw_round_2h[i,j],
                            "rounding_bound_tight_raw": raw_round_tight[i,j],
                            "step_disagreement_raw": abs(raw["h"][i,j]-raw["2h"][i,j]),
                            "convergence_disagreement_raw": abs(raw["h"][i,j]-raw["tight"][i,j])})
    weights = np.asarray([x["row_weight"] for x in catalog])
    obs_scale = np.asarray([x["obs_scale"] for x in catalog])
    pscale = np.asarray([float(x["normalization_scale"]) for x in variables])
    fac = weights[:,None] * pscale[None,:] / obs_scale[:,None]
    norm = {key: raw[key] * fac for key in raw}
    # Bound binary floating point arithmetic in raw finite differences; the
    # larger additive envelope is conservative relative to 17-digit parsing.
    eps_h = np.zeros_like(raw_round_h)
    eps_2h = np.zeros_like(raw_round_h)
    eps_tight = np.zeros_like(raw_round_h)
    for j, var in enumerate(variables):
        h=float(var["h"])
        for i, oid in enumerate(obs_ids):
            if catalog[i]["kind"] == "profile_anchor":
                # Same raw anchor record is subtracted from itself at every stencil.
                continue
            keys=raw_h_endpoints[var["id"]]
            ep={tag:observations[keys[key]][oid]["value"] for tag,key in
                (("ph","ph"),("mh","mh"),("p2","p2"),("m2","m2"),("pt","pt"),("mt","mt"))}
            eps_h[i,j]=8.0*EPS*(abs(ep["ph"])+abs(ep["mh"])+1.0)/(2.0*h)
            eps_2h[i,j]=8.0*EPS*(abs(ep["p2"])+abs(ep["m2"])+1.0)/(4.0*h)
            eps_tight[i,j]=8.0*EPS*(abs(ep["pt"])+abs(ep["mt"])+1.0)/(2.0*h)
    # Bound the two disagreement terms by triangle inequality: 2*b_h+b_2h+b_tight.
    rounding_raw=2.0*raw_round_h+raw_round_2h+raw_round_tight
    eps_raw=2.0*eps_h+eps_2h+eps_tight
    uncertainty_raw=np.abs(raw["h"]-raw["2h"])+np.abs(raw["h"]-raw["tight"])+rounding_raw
    uncertainty_norm=uncertainty_raw*fac
    return raw, norm, uncertainty_raw, uncertainty_norm, rounding_raw, eps_raw, details, raw_h_endpoints


def row_sets(catalog, lowtier_spec, minimal_spec):
    ids=[x["observable_id"] for x in catalog]
    selected=set(x["primary_energy_source_id"] for x in lowtier_spec["selected_energy_rows"])
    masks={
        "FULL_PRIMARY_118": np.asarray([x.get("primary", True) for x in catalog],dtype=bool),
        "LOW_TIER_FULL_99": np.asarray([x["kind"] in ("bond","angle") or
              (x["kind"] in ("profile_energy","profile_anchor") and x["source_id"] in selected) or x["kind"]=="AB_energy" for x in catalog]),
        "GEOMETRY_ONLY_92": np.asarray([x["kind"] in ("bond","angle") for x in catalog]),
        "PES_ONLY_25": np.asarray([x["kind"] in ("profile_energy","profile_anchor") for x in catalog]),
        "A_BASIN_GEOMETRY_ONLY_46": np.asarray([x["kind"] in ("bond","angle") and x.get("geometry")=="A" for x in catalog]),
        "B_BASIN_GEOMETRY_ONLY_46": np.asarray([x["kind"] in ("bond","angle") and x.get("geometry")=="B" for x in catalog]),
        "REMOVE_BONDS": np.asarray([x["kind"]!="bond" for x in catalog]),
        "REMOVE_ANGLES": np.asarray([x["kind"]!="angle" for x in catalog]),
        "REMOVE_CC": np.asarray([not (x["kind"]=="profile_energy" and x.get("axis")=="T_CC") for x in catalog]),
        "REMOVE_CS": np.asarray([not (x["kind"]=="profile_energy" and x.get("axis")=="T_CS") for x in catalog]),
        "REMOVE_AB_ENERGY": np.asarray([x["kind"]!="AB_energy" for x in catalog]),
    }
    for key,mask in masks.items():
        expected={"FULL_PRIMARY_118":118,"LOW_TIER_FULL_99":99,"GEOMETRY_ONLY_92":92,
                  "PES_ONLY_25":25,"A_BASIN_GEOMETRY_ONLY_46":46,"B_BASIN_GEOMETRY_ONLY_46":46}.get(key)
        if expected is not None and int(mask.sum()) != expected:
            raise ValueError(f"row set {key} expected {expected}, got {mask.sum()}")
    return masks


def svd_metrics(matrix, error):
    m,n=matrix.shape
    u,s,vt=np.linalg.svd(matrix,full_matrices=True)
    sigma_max=float(s[0]) if len(s) else 0.0
    delta=float(np.linalg.norm(error,ord="fro"))
    machine=float(max(m,n)*EPS*sigma_max)
    threshold=5.0*max(delta,machine)
    rank=int(np.sum(s>threshold))
    numeric_rank=int(np.sum(s>machine))
    cond=float(sigma_max/s[-1]) if len(s) and s[-1]>0 else math.inf
    raw_nonzero_cond=cond
    cov=np.zeros((n,n),dtype=float)
    if rank:
        vr=vt[:rank,:].T
        cov=(vr/(s[:rank]**2))@vr.T
    vnull=vt[rank:,:].T if rank<n else np.zeros((n,0))
    null_proj=np.linalg.norm(vnull,axis=1) if vnull.shape[1] else np.zeros(n)
    return {"u":u,"s":s,"vt":vt,"rank":rank,"numeric_rank":numeric_rank,
            "delta":delta,"machine":machine,"threshold":threshold,"condition":cond,
            "cov_supported":cov,"null_projection":null_proj,"null_vectors":vt[rank:,:]}


def run_svd_sets(catalog, normalized, uncertainty, variables, masks, minimal_spec):
    normalized_h=normalized["h"]
    uncertainty_h=uncertainty
    var_ids=[v["id"] for v in variables]
    results=[];vectors=[];summaries=[];matrices={}
    matrix_defs=[(name,mask,var_ids) for name,mask in masks.items()]
    for block in minimal_spec["ordered_blocks"]:
        matrix_defs.append((block["id"],masks["FULL_PRIMARY_118"],block["variables"]))
    for name,mask,cols in matrix_defs:
        colidx=[var_ids.index(v) for v in cols]
        matrix=normalized_h[mask,:][:,colidx]
        error=uncertainty_h[mask,:][:,colidx]
        metrics=svd_metrics(matrix,error)
        matrices[name]=(matrix,error,cols,metrics,mask)
        sigmas=metrics["s"]
        cond=metrics["condition"]
        summaries.append({"matrix_id":name,"n_rows":int(mask.sum()),"n_columns":len(cols),
                          "numerical_rank_machine_only":metrics["numeric_rank"],
                          "effective_supported_rank":metrics["rank"],"effective_threshold":metrics["threshold"],
                          "spectral_uncertainty_frobenius_delta":metrics["delta"],
                          "machine_only_tolerance":metrics["machine"],
                          "sigma_max":float(sigmas[0]) if len(sigmas) else 0.0,
                          "sigma_min":float(sigmas[-1]) if len(sigmas) else 0.0,
                          "condition_number_2":cond,
                          "condition_number_supported":float(sigmas[0]/sigmas[metrics['rank']-1]) if metrics['rank'] else math.inf,
                          "rank_status":"ALL_COLUMNS_SUPPORTED" if metrics["rank"]==len(cols) else "UNRESOLVED_DIRECTION(S)"})
        for k, sigma in enumerate(sigmas):
            results.append({"matrix_id":name,"n_rows":int(mask.sum()),"n_columns":len(cols),
                            "singular_index_1based":k+1,"singular_value":float(sigma),
                            "effective_threshold":metrics["threshold"],"supported":bool(sigma>metrics["threshold"]),
                            "effective_supported_rank":metrics["rank"],"spectral_uncertainty_delta":metrics["delta"],
                            "machine_only_tolerance":metrics["machine"],"condition_number_2":cond})
        for k, vec in enumerate(metrics["vt"]):
            supported=bool(k<metrics["rank"])
            for local_j, variable in enumerate(cols):
                coeff=float(vec[local_j])
                vectors.append({"matrix_id":name,"singular_index_1based":k+1,
                                "singular_value":float(sigmas[k]) if k<len(sigmas) else 0.0,
                                "supported":supported,"variable_id":variable,"right_singular_coefficient":coeff,
                                "absolute_coefficient":abs(coeff),"null_highlight_abs_ge_0_25":bool((not supported) and abs(coeff)>=0.25)})
    return results,vectors,summaries,matrices


def stability_rows(normalized, uncertainty_norm, variables, masks):
    rows=[]
    for matrix_id,mask in masks.items():
        for j,var in enumerate(variables):
            h=normalized["h"][mask,j]; two=normalized["2h"][mask,j]; tight=normalized["tight"][mask,j]
            uncertainty=uncertainty_norm[mask,j]
            nh, n2, nt=float(np.linalg.norm(h)),float(np.linalg.norm(two)),float(np.linalg.norm(tight))
            denom_step=max(nh,n2);denom_conv=max(nh,nt)
            step=float(np.linalg.norm(h-two)/denom_step) if denom_step>0 else None
            conv=float(np.linalg.norm(h-tight)/denom_conv) if denom_conv>0 else None
            en=float(np.linalg.norm(uncertainty))
            uncertain=(max(nh,n2,nt)<=en)
            rows.append({"row_set":matrix_id,"variable_id":var["id"],"row_count":int(mask.sum()),
                         "norm_J_h":nh,"norm_J_2h":n2,"norm_J_h_tight":nt,
                         "R_step":step,"R_step_limit":0.10,"R_step_pass":bool(step is not None and step<=0.10),
                         "R_conv":conv,"R_conv_limit":0.05,"R_conv_pass":bool(conv is not None and conv<=0.05),
                         "elementwise_uncertainty_column_norm":en,"signal_at_or_below_uncertainty":uncertain,
                         "stability_status":"UNIDENTIFIABLE_NOISE_DOMINATED" if uncertain else
                             "PASS" if step is not None and conv is not None and step<=0.10 and conv<=0.05 else "STEP_OR_CONVERGENCE_REVIEW"})
    return rows


def write_matrix(path, catalog, variables, matrix, field_suffix, mask=None):
    rows=[]
    for i, obs in enumerate(catalog):
        if mask is not None and not mask[i]:
            continue
        row={"observable_id":obs["observable_id"],"kind":obs["kind"],"block":obs["block"],
             "family":obs["family"],"geometry":obs.get("geometry"),"source_id":obs["source_id"],
             "unit":obs["unit"],"row_weight":obs["row_weight"],"observable_scale":obs["obs_scale"]}
        for j,var in enumerate(variables): row[f"{field_suffix}__{var['id']}"]=float(matrix[i,j])
        rows.append(row)
    write_tsv(path,rows)


def scan_angle_drift(by_state, binding):
    rows=[]
    for state_key, sources in by_state.items():
        for source_id, rec in sources.items():
            center=rec.get("qm_scanned_deg")
            if center is None:
                continue
            if source_id.startswith("T_CC"):
                axis="T_CC";indices=(16,14,15,1)
            elif source_id.startswith("T_CS"):
                axis="T_CS";indices=(11,1,15,14)
            else:
                continue
            final=dihedral_deg(rec["final_coordinates_nm"],indices)
            drift=wrap_deg(final-float(center))
            rows.append({"state_key":state_key,"state_stage":rec["state_stage"],"state_id":rec["state_id"],
                         "variable_id":rec.get("variable_id"),"multiplier":rec.get("multiplier"),
                         "source_id":source_id,"axis":axis,"target_deg":rec.get("target_scanned_deg"),
                         "accepted_qm_center_deg":float(center),"final_mm_torsion_deg":final,
                         "wrapped_drift_vs_accepted_qm_center_deg":drift,"absolute_drift_deg":abs(drift),
                         "gate_limit_deg":0.020,"gate_pass":abs(drift)<=0.020,
                         "start_g96_sha256":rec.get("start_g96_sha256"),"final_g96_sha256":rec.get("final_g96_sha256")})
    return rows


def pair_distance_diagnostics(by_state):
    rows=[]
    for state_key, sources in by_state.items():
        for source_id in ("GEO_A", "GEO_B_REVISED"):
            rec=sources[source_id]
            for phase,key in (("START","start_coordinates_nm"),
                              ("LBFGS_FINAL","lbfgs_final_coordinates_nm"),
                              ("CG_FINAL","final_coordinates_nm")):
                coords=rec[key]
                xyz=[np.asarray([float(v) for v in atom["xyz_raw_nm"]],dtype=float) for atom in coords]
                if len(xyz)!=17 or not np.isfinite(np.asarray(xyz)).all():
                    raise ValueError(f"invalid 17-atom {phase} coordinate set {state_key}/{source_id}")
                max_value=-1.0;max_pair=None
                for i in range(17):
                    for j in range(i+1,17):
                        dist=float(np.linalg.norm(xyz[i]-xyz[j]))
                        if not math.isfinite(dist):
                            raise ValueError(f"nonfinite pair distance {state_key}/{source_id}/{phase}")
                        a,b=coords[i],coords[j]
                        rows.append({"state_key":state_key,"source_id":source_id,"phase":phase,
                                     "atom_i_1based":i+1,"atom_i_name":a["atom"],
                                     "atom_i_xyz_raw_nm":a["xyz_raw_nm"],"atom_j_1based":j+1,
                                     "atom_j_name":b["atom"],"atom_j_xyz_raw_nm":b["xyz_raw_nm"],
                                     "distance_nm":format(dist,".17g"),"coordinate_g96_sha256":
                                     rec[{"START":"start_pair_domain","LBFGS_FINAL":"lbfgs_pair_domain",
                                          "CG_FINAL":"cg_final_pair_domain"}[phase]]["coordinate_sha256"]})
                        if dist>max_value: max_value,max_pair=dist,(a["atom"],b["atom"])
                domain=rec[{"START":"start_pair_domain","LBFGS_FINAL":"lbfgs_pair_domain",
                            "CG_FINAL":"cg_final_pair_domain"}[phase]]
                if not domain["box_matches_10nm"] or domain["atom_count"]!=17 or domain["pair_count"]!=136:
                    raise ValueError(f"stored source/domain gate failed at {state_key}/{source_id}/{phase}")
                if abs(max_value-float(domain["max_all_pair_distance_nm"]))>2e-8:
                    raise ValueError(f"computed/stored pair-domain maximum mismatch at {state_key}/{source_id}/{phase}")
                if max_value>2.0:
                    raise ValueError(f"all-pair isolated-domain limit crossed at {state_key}/{source_id}/{phase}")
    return rows


def local_proper_torsion_domain(by_state, variables, itp):
    terms=topology_terms(itp)
    torsions=sorted(terms["dihedrals"])
    automorphisms={"GENERAL":graph_automorphisms(itp,False),"T_CS":graph_automorphisms(itp,True)}
    baseline_key="primary__BASE"
    output=[]
    endpoint_suffixes=("_+1h","_-1h","_+2h","_-2h")
    for var in variables:
        vid=var["id"]
        endpoint_keys=(f"primary__{vid}_+1h",f"primary__{vid}_-1h",
                       f"primary__{vid}_+2h",f"primary__{vid}_-2h",
                       f"tight_audit__{vid}_+1h",f"tight_audit__{vid}_-1h")
        for source_id in sorted(by_state[baseline_key]):
            if source_id.startswith("T_CS_"):
                axis="T_CS";restraint_bond=(1,15)
            elif source_id.startswith("T_CC_"):
                axis="T_CC";restraint_bond=(14,15)
            else:
                axis="UNRESTRAINED";restraint_bond=None
            unrestrained=[q for q in torsions if restraint_bond is None or tuple(sorted((q[1],q[2])))!=restraint_bond]
            if not unrestrained:
                output.append({"variable_id":vid,"source_id":source_id,"axis":axis,
                               "status":"NOT_INFORMATIVE_NO_UNRESTRAINED_PROPER","gate_pass":False})
                continue
            pset=automorphisms[axis] if axis in automorphisms else automorphisms["GENERAL"]
            base_coords=by_state[baseline_key][source_id]["final_coordinates_nm"]
            baseline={q:dihedral_deg(base_coords,q) for q in unrestrained}
            endpoint_coords=[]
            for state in endpoint_keys:
                if state not in by_state or source_id not in by_state[state]:
                    raise ValueError(f"missing frozen branch endpoint {state}/{source_id}")
                rec=by_state[state][source_id]
                if rec["status"]!="DONE" or not rec.get("cg_converged",False):
                    raise ValueError(f"branch gate endpoint not terminal-converged {state}/{source_id}")
                endpoint_coords.append((state,rec["final_coordinates_nm"]))
            best=None
            for perm in pset:
                deltas=[]
                for state,coords in endpoint_coords:
                    for q in unrestrained:
                        mapped=tuple(perm[i-1] for i in q)
                        delta=wrap_deg(dihedral_deg(coords,mapped)-baseline[q])
                        deltas.append((abs(delta),delta,state,q,mapped))
                candidate=(max(deltas,key=lambda d:(d[0],d[2],d[3])),perm,deltas)
                key=(candidate[0][0],candidate[1])
                if best is None or key<(best[0],best[1]):
                    best=(key[0],key[1],candidate[2])
            max_abs,perm,deltas=best
            defining=max(deltas,key=lambda d:(d[0],d[2],d[3]))
            output.append({"variable_id":vid,"source_id":source_id,"axis":axis,
                           "restraint_central_bond_1based":restraint_bond,
                           "unrestrained_proper_count":len(unrestrained),"endpoint_count":len(endpoint_keys),
                           "permitted_automorphism_count":len(pset),"chosen_atom_map_1based":perm,
                           "minimax_max_abs_wrapped360_change_deg":max_abs,
                           "maximum_defining_endpoint_state":defining[2],
                           "maximum_defining_baseline_quartet_1based":defining[3],
                           "maximum_defining_endpoint_mapped_quartet_1based":defining[4],
                           "maximum_defining_signed_change_deg":defining[1],
                           "all_torsion_changes_deg":[{"endpoint_state":d[2],"baseline_quartet_1based":d[3],
                                "endpoint_quartet_1based":d[4],"signed_wrapped360_change_deg":d[1]}
                                for d in deltas],
                           "gate_limit_deg":30.0,"gate_pass":max_abs<=30.0,
                           "status":"PASS_LOCAL_SMOOTH_DOMAIN" if max_abs<=30.0 else "BRANCH_OR_LARGE_ROTAMER_RESPONSE_REVIEW"})
    return output


def export(args):
    output=args.output_dir.resolve()
    if output.exists() and any(output.iterdir()):
        raise FileExistsError(f"analysis output directory must be fresh: {output}")
    output.mkdir(parents=True,exist_ok=True)
    export_path=args.export_json.resolve(strict=True)
    run_export=json.loads(export_path.read_text(encoding="utf-8"))
    if run_export.get("run_control",{}).get("record",{}).get("status")!="COMPLETE":
        raise ValueError("analysis requires terminal COMPLETE matrix")
    if run_export.get("counts",{}).get("by_status")!={"DONE":1736}:
        raise ValueError("analysis requires all 1,736 runs DONE; no partial-column rescue")
    work=args.work_root.resolve(strict=True)
    prereg=work/"preregistered_inputs"
    spec_path=prereg/"MM_IDENTIFIABILITY_VARIABLE_SPEC.json"
    protocol_path=prereg/"NUMERICAL_IDENTIFIABILITY_PROTOCOL.md"
    binding_path=work/"executor"/"inputs"/"QM_SOURCE_BINDING.json"
    manifest_path=work/"executor"/"inputs"/"MM_RUN_MANIFEST.json"
    geometry_path=work/"package"/"reference_v1"/"failure_evidence"/"FULL_A_B_BOND_ANGLE_COMPARISON.tsv"
    itp_path=work.parent/"broad_pre_qm_audit_work_20260926"/"package"/"current_parameters"/"pfbs_ani.itp"
    lowtier_path=prereg/"MVP_LOW_TIER_ROW_DIAGNOSTIC_SPEC.json"
    minimal_path=prereg/"MVP_MINIMAL_SUBMATRIX_PREDECLARATION.json"
    for path in (spec_path,protocol_path,binding_path,manifest_path,geometry_path,itp_path,lowtier_path,minimal_path):
        if not path.is_file(): raise FileNotFoundError(path)
    spec=json.loads(spec_path.read_text(encoding="utf-8")); binding=json.loads(binding_path.read_text(encoding="utf-8"))
    manifest=json.loads(manifest_path.read_text(encoding="utf-8"));lowtier=json.loads(lowtier_path.read_text(encoding="utf-8"));minimal=json.loads(minimal_path.read_text(encoding="utf-8"))
    variables=spec["variables"]
    if len(variables)!=10 or len(manifest.get("states",[]))!=62 or manifest.get("expected_runs")!=1736:
        raise ValueError("frozen variable/state/run cardinality mismatch")
    catalog,bond_defs,angle_defs=observable_catalog(run_export,binding,geometry_path,itp_path)
    by_state,observations,raw_obs_rows=build_observations(run_export,catalog)

    raw,norm,unc_raw,unc_norm,round_raw,eps_raw,details,endpoints=calculate_derivatives(by_state,observations,catalog,variables)
    masks=row_sets(catalog,lowtier,minimal)
    primary_mask=masks["FULL_PRIMARY_118"]
    raw_matrices={key:value for key,value in raw.items()}
    norm_matrices={key:value for key,value in norm.items()}

    # Matrix tables carry all three preregistered stencils; no state or row is removed.
    for key,label in (("h","J_h_raw"),("2h","J_2h_raw"),("tight","J_h_tight_raw")):
        write_matrix(output/f"NUMERICAL_JACOBIAN_RAW_{key.upper()}.tsv",catalog,variables,raw[key],label,primary_mask)
        write_matrix(output/f"NUMERICAL_JACOBIAN_NORMALIZED_{key.upper()}.tsv",catalog,variables,norm[key],label.replace("raw","normalized"),primary_mask)
    write_matrix(output/"NUMERICAL_JACOBIAN_RAW.tsv",catalog,variables,raw["h"],"J_h_raw",primary_mask)
    write_matrix(output/"NUMERICAL_JACOBIAN_NORMALIZED.tsv",catalog,variables,norm["h"],"J_h_normalized",primary_mask)
    write_matrix(output/"NUMERICAL_JACOBIAN_UNCERTAINTY_RAW.tsv",catalog,variables,unc_raw,"E_raw",primary_mask)
    write_matrix(output/"NUMERICAL_JACOBIAN_UNCERTAINTY_NORMALIZED.tsv",catalog,variables,unc_norm,"E_normalized",primary_mask)
    write_tsv(output/"RAW_OBSERVABLES.tsv",raw_obs_rows)

    stability=stability_rows(norm,unc_norm,variables,masks)
    write_tsv(output/"DERIVATIVE_STEP_STABILITY.tsv",stability)
    noise_rows=[]
    for i,row in enumerate(catalog):
        for j,var in enumerate(variables):
            noise_rows.append({"observable_id":row["observable_id"],"kind":row["kind"],"family":row["family"],
                               "variable_id":var["id"],"J_h_raw":raw["h"][i,j],"J_2h_raw":raw["2h"][i,j],
                               "J_h_tight_raw":raw["tight"][i,j],"endpoint_rounding_raw":round_raw[i,j],
                               "binary_arithmetic_bound_raw":eps_raw[i,j],"uncertainty_envelope_raw":unc_raw[i,j],
                               "J_h_normalized":norm["h"][i,j],"J_2h_normalized":norm["2h"][i,j],
                               "J_h_tight_normalized":norm["tight"][i,j],
                               "uncertainty_envelope_normalized":unc_norm[i,j],
                               "step_disagreement_normalized":abs(norm["h"][i,j]-norm["2h"][i,j]),
                               "convergence_disagreement_normalized":abs(norm["h"][i,j]-norm["tight"][i,j])})
    write_tsv(output/"UNCERTAINTY_NOISE_DIAGNOSTICS.tsv",noise_rows)

    svd_rows,svd_vectors,svd_summaries,matrices=run_svd_sets(catalog,norm,unc_norm,variables,masks,minimal)
    write_tsv(output/"SVD_RESULTS.tsv",svd_rows)
    write_tsv(output/"SVD_RIGHT_SINGULAR_VECTORS.tsv",svd_vectors)
    write_tsv(output/"MATRIX_SUPPORT_SUMMARY.tsv",svd_summaries)
    scan_rows=scan_angle_drift(by_state,binding)
    write_tsv(output/"SCAN_ANGLE_DRIFT.tsv",scan_rows)
    pair_rows=pair_distance_diagnostics(by_state)
    write_tsv(output/"AB_PAIR_DISTANCE_DIAGNOSTICS.tsv",pair_rows)
    branch_rows=local_proper_torsion_domain(by_state,variables,itp_path)
    write_tsv(output/"LOCAL_PROPER_TORSION_DOMAIN.tsv",branch_rows)
    branch_summary={"count":len(branch_rows),"failed":sum(not r.get("gate_pass",False) for r in branch_rows),
                    "max_minimax_change_deg":max((r.get("minimax_max_abs_wrapped360_change_deg",0.0) for r in branch_rows),default=None),
                    "threshold_deg":30.0,"automorphisms_general":len(graph_automorphisms(itp_path,False)),
                    "automorphisms_CS_O1_fixed":len(graph_automorphisms(itp_path,True)),
                    "torsion_indices_source":"unique reverse-canonical proper quartets from original v1 ITP"}
    (output/"LOCAL_PROPER_TORSION_DOMAIN_SUMMARY.json").write_text(json.dumps(branch_summary,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    pair_summary={"rows":len(pair_rows),"expected_rows":62*2*3*136,
                  "scope":"all 136 atom pairs for GEO_A and GEO_B_REVISED at start, LBFGS final, and CG final across 62 states",
                  "max_distance_nm":max(float(r["distance_nm"]) for r in pair_rows),"isolated_domain_limit_nm":2.0,
                  "box_nm":[10.0,10.0,10.0],"all_pair_domain_pass":len(pair_rows)==62*2*3*136 and max(float(r["distance_nm"]) for r in pair_rows)<=2.0}
    (output/"AB_PAIR_DISTANCE_SUMMARY.json").write_text(json.dumps(pair_summary,indent=2,sort_keys=True)+"\n",encoding="utf-8")

    # Full normalized covariance proxy; never turn unresolved null coordinates
    # into finite pseudoinverse variances or correlations.
    full=matrices["FULL_PRIMARY_118"][3]
    cols=[v["id"] for v in variables]
    nullproj=full["null_projection"]
    corr_rows=[]
    cov=full["cov_supported"]
    for i,vi in enumerate(cols):
        for j,vj in enumerate(cols):
            denom=math.sqrt(max(cov[i,i],0)*max(cov[j,j],0))
            resolved_i=bool(nullproj[i] <= 1e-8)
            resolved_j=bool(nullproj[j] <= 1e-8)
            corr=(float(cov[i,j]/denom) if denom>0 and resolved_i and resolved_j else None)
            corr_rows.append({"variable_i":vi,"variable_j":vj,"C_supported_subspace_ij":float(cov[i,j]),
                              "correlation_if_null_resolved":corr,"null_projection_i":float(nullproj[i]),
                              "null_projection_j":float(nullproj[j]),"both_coordinates_resolved":resolved_i and resolved_j,
                              "interpretation":"unit-normalized response covariance proxy; not statistical covariance"})
    write_tsv(output/"PARAMETER_CORRELATION.tsv",corr_rows)
    cov_rows=[]
    for i,vi in enumerate(cols):
        resolved=bool(nullproj[i]<=1e-8)
        cov_rows.append({"variable_id":vi,"C_supported_subspace_diagonal":float(cov[i,i]),
                         "sqrt_C_if_resolved":math.sqrt(max(cov[i,i],0)) if resolved else None,
                         "null_projection_norm":float(nullproj[i]),"coordinate_variance_status":"FINITE_SUPPORTED_PROXY" if resolved else "UNRESOLVED_NULL_COMPONENT_NO_FINITE_VARIANCE"})
    write_tsv(output/"NORMALIZED_UNIT_NOISE_COVARIANCE_PROXY.tsv",cov_rows)

    # Compact eligibility evidence, intentionally not a final reviewer ruling.
    full_st={r["variable_id"]:r for r in stability if r["row_set"]=="FULL_PRIMARY_118"}
    geom_st={r["variable_id"]:r for r in stability if r["row_set"]=="GEOMETRY_ONLY_92"}
    pes_st={r["variable_id"]:r for r in stability if r["row_set"]=="PES_ONLY_25"}
    action=[]
    for i,var in enumerate(variables):
        unresolved=float(nullproj[i])>1e-8
        s=full_st[var["id"]]
        relevant=geom_st[var["id"]] if var["parameter_class"] in ("BOND_EQUILIBRIUM","ANGLE_EQUILIBRIUM") else pes_st[var["id"]]
        covscale=math.sqrt(max(cov[i,i],0)) if not unresolved else None
        branch_pass=all(r.get("gate_pass",False) for r in branch_rows if r["variable_id"]==var["id"])
        numeric_supported=(branch_pass and not unresolved and covscale is not None and covscale<=1 and
                           s["R_step_pass"] and s["R_conv_pass"] and not s["signal_at_or_below_uncertainty"] and
                           relevant["norm_J_h"]>relevant["elementwise_uncertainty_column_norm"])
        if var["parameter_class"]=="GROUPED_TORSION_DIAGNOSTIC_ONLY":
            evidence="CONDITIONAL_AFTER_HESSIAN_BY_PREREG_POLICY"
        elif not branch_pass:
            evidence="BRANCH_GATE_FAILED_REVIEW_INVALID_SMOOTH_DERIVATIVE"
        elif unresolved:
            evidence="GROUP_OR_FREEZE_REVIEW_NULL_DIRECTION"
        elif numeric_supported:
            evidence="RELEASE_ELIGIBLE_EVIDENCE_ONLY_PENDING_SOL_REVIEW"
        else:
            evidence="FREEZE_OR_CONDITIONAL_REVIEW_INSUFFICIENT_NUMERICAL_SUPPORT"
        action.append({"variable_id":var["id"],"parameter_class":var["parameter_class"],
                       "base":var["base"],"unit":var["unit"],"parameter_normalization_scale":var["normalization_scale"],
                       "full_supported_rank":full["rank"],"full_variable_null_projection":float(nullproj[i]),
                       "sqrt_C_supported_if_resolved":covscale,"R_step":s["R_step"],"R_conv":s["R_conv"],
                       "full_signal_at_or_below_uncertainty":s["signal_at_or_below_uncertainty"],
                       "all_source_local_domain_gate_pass":branch_pass,
                       "relevant_block":relevant["row_set"],"relevant_block_signal_norm":relevant["norm_J_h"],
                       "relevant_block_noise_norm":relevant["elementwise_uncertainty_column_norm"],
                       "evidence_bucket_not_final_verdict":evidence})
    write_tsv(output/"VARIABLE_ACTION_EVIDENCE.tsv",action)

    low=matrices["LOW_TIER_FULL_99"][3]
    minimal_summaries=[x for x in svd_summaries if x["matrix_id"].startswith("MVP_")]
    md=[]
    md.append("# Numerical null-direction and support diagnostics\n")
    md.append("This is a preregistered MM numerical-identifiability analysis package. It does not fit parameters, edit force-field files, adopt a parameter set, or issue Sol's final acceptance decision. Covariance values are unit-normalized response proxies, not statistical uncertainty estimates.\n")
    md.append(f"- Terminal matrix: {run_export['counts']['rows']} unique state/source cells; controller status `{run_export['controller_status']}`.\n- Primary observable vector: {len(catalog)} rows; low-tier diagnostic: {int(masks['LOW_TIER_FULL_99'].sum())} rows.\n- Full primary effective supported rank: {full['rank']}/10 at threshold {full['threshold']:.8g}; Frobenius uncertainty bound δ={full['delta']:.8g}; machine-only tolerance={full['machine']:.8g}.\n- Low-tier full diagnostic effective supported rank: {low['rank']}/10 at threshold {low['threshold']:.8g}; δ={low['delta']:.8g}.\n")
    md.append("## Full-primary right singular vectors\n")
    for k,vec in enumerate(full["vt"]):
        sigma=float(full["s"][k]); supported=k<full["rank"]
        label="supported" if supported else "unresolved / below preregistered 5δ threshold"
        coeffs=", ".join(f"{cols[i]}={float(vec[i]):+.4f}" for i in range(len(cols)))
        md.append(f"- σ{k+1}={sigma:.8g} ({label}): {coeffs}\n")
    md.append("## Preregistered low-tier and fixed reduced blocks\n")
    for r in minimal_summaries:
        md.append(f"- `{r['matrix_id']}`: {r['effective_supported_rank']}/{r['n_columns']} supported; n={r['n_rows']}, δ={r['spectral_uncertainty_frobenius_delta']:.8g}, threshold={r['effective_threshold']:.8g}; status `{r['rank_status']}`.\n")
    md.append("## Interpretation boundaries\n")
    md.append("- The reported unsupported right-singular vectors identify parameter combinations not resolved by the selected MM observables at the preregistered noise envelope. A highlighted |coefficient|≥0.25 is a readability aid only.\n- Every block-removal result uses unchanged original row weights; subsets were not renormalized. The low-tier set preserves the common CC300 energy anchor and uses the predeclared six profile rows plus all A/B geometry and the A/B energy row.\n- Step/convergence ratios and branch/constraint gates remain separate evidence. A numerically high rank does not override a failed derivative stability or local-domain screen. No parameter release/adoption follows from this package alone.\n")
    (output/"NULL_DIRECTION_ANALYSIS.md").write_text("".join(md),encoding="utf-8")

    # Preregistered branch-center control is a separate gate from SVD.
    scan_fails=[x for x in scan_rows if not x["gate_pass"]]
    scan_summary={"count":len(scan_rows),"failed":len(scan_fails),
                  "max_abs_drift_deg":max((x["absolute_drift_deg"] for x in scan_rows),default=None),
                  "threshold_deg":0.020}
    (output/"SCAN_ANGLE_DRIFT_SUMMARY.json").write_text(json.dumps(scan_summary,indent=2,sort_keys=True)+"\n",encoding="utf-8")

    input_paths={"terminal_compact_export":export_path,"protocol":protocol_path,"variable_spec":spec_path,
                 "low_tier_spec":lowtier_path,"minimal_submatrix_spec":minimal_path,
                 "manifest":manifest_path,"source_binding":binding_path,"geometry_observable_definitions":geometry_path,
                 "baseline_topology_atom_types":itp_path,
                 "branch_classifier_addendum":prereg/"BRANCH_CLASSIFIER_PREREGISTRATION_ADDENDUM.md"}
    input_hashes={name:{"path":str(path),"sha256":sha(path)} for name,path in input_paths.items()}
    input_hashes["launch_record"]={"path":run_export["launch_record"]["path"],"sha256":run_export["launch_record"]["sha256"]}
    input_hashes["runner"]={"path":run_export["run_control"]["record"].get("runner_path"),"sha256":run_export["run_control"]["record"].get("runner_sha256")}
    output_files={p.name:sha(p) for p in sorted(output.iterdir()) if p.is_file() and p.name!="SOURCE_PROVENANCE_MANIFEST.json"}
    provenance={"schema":"PFBS_MM_NUMERICAL_IDENTIFIABILITY_ANALYSIS_PROVENANCE_v1",
                "protocol_id":manifest["protocol_id"],"protocol_hash":manifest["protocol_hash"],
                "variable_spec_hash":sha(spec_path),
                "matrix_launch_attempt":"matrix_20260926T092541Z_v8",
                "matrix_run_control_status":run_export["controller_status"],
                "matrix_expected_and_observed_runs":1736,"matrix_status_counts":run_export["counts"]["by_status"],
                "analysis_method":"frozen finite difference and weighted SVD; no fitting",
                "primary_rows":int(masks["FULL_PRIMARY_118"].sum()),
                "low_tier_rows":int(masks["LOW_TIER_FULL_99"].sum()),
                "catalog_rows_including_primary_anchor_zero":len(catalog),
                "primary_matrix_shape":[118,10],"stencil":"central +/-h, +/-2h, independent tight +/-h",
                "energy_anchor":"T_CC_300 within the same parameter state; one common anchor for CC and CS",
                "energy_conversion":"kJ/mol / 4.184 to kcal/mol; raw XVG numeric strings retained",
                "row_weights":"frozen squared block mass 1 each; no subset renormalization",
                "uncertainty":"abs(J_h-J_2h)+abs(J_h-J_h_tight)+endpoint serialization and arithmetic bound",
                "rank_rule":"strict sigma > 5*max(Frobenius envelope delta, max(m,n)*eps*sigma_max)",
                "parameter_changes_fit_or_adoption":"NONE",
                "input_hashes":input_hashes,"output_hashes_sha256":output_files,
                "scan_angle_gate_summary":scan_summary}
    provenance["local_proper_torsion_domain_summary"]=branch_summary
    provenance["A_B_all_pair_distance_summary"]=pair_summary
    (output/"SOURCE_PROVENANCE_MANIFEST.json").write_text(json.dumps(provenance,indent=2,sort_keys=True,allow_nan=False)+"\n",encoding="utf-8")
    print(json.dumps({"output_dir":str(output),"primary_rank":full["rank"],"low_tier_rank":low["rank"],
                      "primary_delta":full["delta"],"primary_threshold":full["threshold"],
                      "scan_angle_drift":scan_summary,"files":len(output_files)+1},indent=2))


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--export-json",type=Path,required=True)
    parser.add_argument("--work-root",type=Path,required=True)
    parser.add_argument("--output-dir",type=Path,required=True)
    args=parser.parse_args()
    export(args)


if __name__=="__main__":
    main()
