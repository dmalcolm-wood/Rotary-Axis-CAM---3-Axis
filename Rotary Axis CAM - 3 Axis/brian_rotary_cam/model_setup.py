"""Rigid model preparation shared by the preview and CAM calculation."""

import numpy as np
import trimesh


def prepare_mesh(source, setup=None):
    """Return a transformed copy; never modify the source STL or mesh.

    Alignment maps the selected source axis onto +X. Fine rotations are applied
    about the aligned model's bounding-box centre, in fixed X, Y, Z order.
    Centring places the final Y/Z bounding-box midpoint on the rotary centreline;
    X placement is preserved (the post sets longitudinal zero at its first cut).
    """
    if not isinstance(source, trimesh.Trimesh) or not len(source.faces):
        raise ValueError("The STL must contain a non-empty triangular mesh.")
    if not np.isfinite(source.vertices).all():
        raise ValueError("The STL contains non-finite coordinates.")
    setup = setup or {}
    axis = setup.get("source_axis", "X")
    if axis not in ("X", "Y", "Z", "AUTO"):
        raise ValueError("Choose X, Y, Z or automatic model alignment.")
    angles = np.asarray(setup.get("rotation_deg", [0.0, 0.0, 0.0]), dtype=float)
    if angles.shape != (3,) or not np.isfinite(angles).all():
        raise ValueError("Model rotations must be three finite angles.")
    direction = np.eye(3)[("X", "Y", "Z").index(axis)] if axis != "AUTO" else None
    if axis == "AUTO":
        # Unique positions prevent duplicated STL triangle vertices biasing PCA.
        points = np.unique(np.asarray(source.vertices), axis=0)
        centred = points - points.mean(axis=0)
        values, vectors = np.linalg.eigh(centred.T @ centred / len(points))
        if values[-1] <= 0 or values[-1] - values[-2] <= values[-1] * 0.01:
            raise ValueError("No clear long axis. Choose a model axis and use rotation adjustments.")
        direction = vectors[:, -1]
        if direction[np.argmax(np.abs(direction))] < 0:
            direction = -direction
    align = trimesh.geometry.align_vectors(direction, [1.0, 0.0, 0.0])
    result = source.copy()
    result.apply_transform(align)
    pivot = result.bounds.mean(axis=0)
    transform = align.copy()
    for angle, unit in zip(angles, np.eye(3)):
        rotation = trimesh.transformations.rotation_matrix(np.deg2rad(angle), unit, point=pivot)
        result.apply_transform(rotation)
        transform = rotation @ transform
    if setup.get("centre", False):
        shift = np.zeros(3)
        shift[1:] = -result.bounds.mean(axis=0)[1:]
        translation = np.eye(4)
        translation[:3, 3] = shift
        result.apply_transform(translation)
        transform = translation @ transform
    return result, transform
