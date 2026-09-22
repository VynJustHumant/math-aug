"""Sky — gradien siang + awan low-discrepancy (deterministik murni)."""
import numpy as np

# --- Canvas ---
W, H   = 7680, 4320
Y1, Y2 = 1000, 3320
Y_MID  = (Y1 + Y2) // 2      # 2160
H_SKY  = Y2 - Y1             # 2320

# --- Gradient: biru tua di zenith, pucat di horizon ---
SKY_ANCHORS_H = np.array([0.0, 0.45, 0.85, 1.0], dtype=np.float32)
SKY_ANCHORS_RGB = np.array([
    [ 18,  48, 105],   # zenith  — biru tua
    [ 80, 135, 190],   # mid     — biru
    [170, 205, 225],   # transisi
    [225, 235, 242],   # horizon — pucat berkabut
], dtype=np.float32)

A_MOD = 0.02      # modulasi horizontal sangat halus
K_MOD = 2.0
HAZE_WIDTH = 60   # lebar fade kabut di ujung atas & bawah langit


def sky_gradient():
    """Pixel network RGB(x, y). t=0 zenith, t=1 horizon."""
    yy = np.arange(Y1, Y2, dtype=np.float32)[:, None]
    xx = np.arange(W, dtype=np.float32)[None, :]

    t = np.abs(yy - Y_MID) / (H_SKY / 2.0)

    # Modulasi horizontal sangat halus (bukan zebra)
    mod = A_MOD * np.sin(2 * np.pi * K_MOD * xx / W)
    h = np.clip(t + mod, 0.0, 1.0)

    r = np.interp(h, SKY_ANCHORS_H, SKY_ANCHORS_RGB[:, 0])
    g = np.interp(h, SKY_ANCHORS_H, SKY_ANCHORS_RGB[:, 1])
    b = np.interp(h, SKY_ANCHORS_H, SKY_ANCHORS_RGB[:, 2])
    rgb = np.stack([r, g, b], axis=-1)

    # --- Fade kabut di ujung atas & bawah langit ---
    # Menghindari pembatas keras. Warna bergerak ke arah abu-biru pucat.
    dist_top = (yy - Y1)
    dist_bot = (Y2 - yy)
    edge = np.minimum(dist_top, dist_bot) / HAZE_WIDTH       # 0 di ujung
    edge = np.clip(edge, 0.0, 1.0)
    haze_rgb = np.array([210, 222, 232], dtype=np.float32)
    weight = (1.0 - edge) ** 2       # 1 di ujung, 0 di tengah
    rgb = rgb * (1 - weight[..., None]) + haze_rgb * weight[..., None]

    return rgb.astype(np.uint8)


# --- Awan: low-discrepancy (golden ratio) ---
PHI = (1 + 5 ** 0.5) / 2       # 1.618...

CLOUD_N        = 220
CLUSTER_MIN    = 3
CLUSTER_MAX    = 5
CLUSTER_RADIUS = 240
MARGIN_FRAC    = 0.10          # 10% margin atas/bawah band langit


def cloud_ellipses():
    """Kembalikan array elips (x, y, w, h, alpha). Deterministik."""
    xs, ys, ws, hs, alphas = [], [], [], [], []

    for k in range(CLOUD_N):
        # Posisi klaster via golden ratio
        ux = (k * PHI) % 1.0
        uy = (k * PHI * PHI) % 1.0
        cx = W * ux
        cy = Y1 + H_SKY * (MARGIN_FRAC + (1 - 2 * MARGIN_FRAC) * uy)

        # Ukuran & alpha bergantung jarak ke tepi langit
        d_top = (cy - Y1) / H_SKY
        d_bot = (Y2 - cy) / H_SKY
        d = min(d_top, d_bot) * 2.0      # 0 di horizon, 1 di tengah
        base_size  = 90 + 420 * (d ** 1.6)
        base_alpha = 25 + 150 * (d ** 1.6)

        # Cluster 3–5 elips
        n = CLUSTER_MIN + (k * 7) % (CLUSTER_MAX - CLUSTER_MIN + 1)
        for j in range(n):
            ox = CLUSTER_RADIUS * (((j * PHI + k * 0.13) % 1.0) - 0.5) * 2
            oy = CLUSTER_RADIUS * (((j * PHI * PHI + k * 0.21) % 1.0) - 0.5) * 2
            sj = base_size  * (0.55 + 0.45 * ((j * 0.37 + k * 0.11) % 1.0))
            aj = base_alpha * (0.60 + 0.40 * ((j * 0.53 + k * 0.19) % 1.0))
            xs.append(cx + ox)
            ys.append(cy + oy)
            ws.append(sj)
            hs.append(sj * 0.42)         # pipih
            alphas.append(aj)

    return (np.array(xs, dtype=np.float32),
            np.array(ys, dtype=np.float32),
            np.array(ws, dtype=np.float32),
            np.array(hs, dtype=np.float32),
            np.array(alphas, dtype=np.float32))
