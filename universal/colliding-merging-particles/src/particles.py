"""Colliding & merging particles — diagonal stream (deterministik murni)."""
import numpy as np

# --- Canvas ---
W, H = 7680, 7680

# --- Gradien diagonal ---
SKY_ANCHORS_H = np.array([0.0, 0.35, 0.7, 1.0], dtype=np.float32)
SKY_ANCHORS_RGB = np.array([
    [ 18,  48, 105],
    [ 80, 135, 190],
    [170, 205, 225],
    [225, 235, 242],
], dtype=np.float32)

A_MOD = 0.02
K_MOD = 2.0
DIAG_W = 0.6


def sky_gradient():
    yy = np.arange(H, dtype=np.float32)[:, None]
    xx = np.arange(W, dtype=np.float32)[None, :]
    d = np.abs(xx / W - yy / H) / DIAG_W
    mod = A_MOD * np.sin(2 * np.pi * K_MOD * xx / W)
    h = np.clip(d + mod, 0.0, 1.0)
    r = np.interp(h, SKY_ANCHORS_H, SKY_ANCHORS_RGB[:, 0])
    g = np.interp(h, SKY_ANCHORS_H, SKY_ANCHORS_RGB[:, 1])
    b = np.interp(h, SKY_ANCHORS_H, SKY_ANCHORS_RGB[:, 2])
    return np.stack([r, g, b], axis=-1).astype(np.uint8)


# --- Partikel: low-discrepancy ---
PHI = (1 + 5 ** 0.5) / 2

CLOUD_N        = 240
CLUSTER_MIN    = 3
CLUSTER_MAX    = 6
CLUSTER_RADIUS = 260


def cloud_ellipses():
    xs, ys, ws, hs, alphas = [], [], [], [], []
    for k in range(CLOUD_N):
        ux = (k * PHI) % 1.0
        uy = (k * PHI * PHI) % 1.0
        t = ux
        cx = W * t
        cy = H * t + H * 0.08 * (uy - 0.5)
        b = 1.0 - abs(2 * t - 1) ** 1.5
        base_size  = 80 + 620 * b
        base_alpha = 30 + 180 * b
        n = CLUSTER_MIN + (k * 7) % (CLUSTER_MAX - CLUSTER_MIN + 1)
        for j in range(n):
            ox = CLUSTER_RADIUS * (((j * PHI + k * 0.13) % 1.0) - 0.5) * 2
            oy = CLUSTER_RADIUS * (((j * PHI * PHI + k * 0.21) % 1.0) - 0.5) * 2
            sj = base_size  * (0.55 + 0.45 * ((j * 0.37 + k * 0.11) % 1.0))
            aj = base_alpha * (0.60 + 0.40 * ((j * 0.53 + k * 0.19) % 1.0))
            xs.append(cx + ox)
            ys.append(cy + oy)
            ws.append(sj)
            hs.append(sj * 0.55)
            alphas.append(aj)
    return (np.array(xs, dtype=np.float32),
            np.array(ys, dtype=np.float32),
            np.array(ws, dtype=np.float32),
            np.array(hs, dtype=np.float32),
            np.array(alphas, dtype=np.float32))
