"""Sky generation — pusaran-magma-air (deterministik murni)."""
import numpy as np

# --- Canvas spec ---
W, H   = 7680, 4320
Y1, Y2 = 1000, 3320
Y_MID  = (Y1 + Y2) // 2      # 2160
H_SKY  = Y2 - Y1             # 2320

# --- Sky gradient params ---
A_MOD = 0.05
K_MOD = 10.0

# Daytime sky palette: h=0 -> deep blue, h=1 -> white
SKY_ANCHORS_H = np.array([0.0, 0.5, 1.0], dtype=np.float32)
SKY_ANCHORS_RGB = np.array([
    [ 30,  80, 170],   # deep blue
    [135, 190, 230],   # light blue
    [240, 248, 255],   # near white
], dtype=np.float32)

# --- Cloud params ---
CLOUD_N         = 500
CLOUD_A1        = 300.0
CLOUD_A2        = 200.0
CLOUD_S_MIN     = 150.0
CLOUD_S_MAX     = 500.0
CLOUD_P         = 4.0    # spatial compression exponent
CLOUD_RHO       = 0.35
CLOUD_ALPHA_MIN = 20
CLOUD_ALPHA_MAX = 100
CLOUD_Q         = 2.0


def sky_gradient():
    """Pixel network: RGB(x, y) untuk tiap piksel langit."""
    yy = np.arange(Y1, Y2, dtype=np.float32)[:, None]
    xx = np.arange(W, dtype=np.float32)[None, :]
    t   = np.abs(yy - Y_MID) / (H_SKY / 2.0)
    mod = A_MOD * np.sin(2.0 * np.pi * K_MOD * xx / W)
    h   = np.clip(t + mod, 0.0, 1.0)
    r = np.interp(h, SKY_ANCHORS_H, SKY_ANCHORS_RGB[:, 0])
    g = np.interp(h, SKY_ANCHORS_H, SKY_ANCHORS_RGB[:, 1])
    b = np.interp(h, SKY_ANCHORS_H, SKY_ANCHORS_RGB[:, 2])
    return np.stack([r, g, b], axis=-1).astype(np.uint8)


def cloud_params():
    """Parameter elips awan, deterministik dari indeks i."""
    i = np.arange(CLOUD_N, dtype=np.float32)
    u = i / (CLOUD_N - 1)
    x = W * u
    y = Y_MID + CLOUD_A1 * np.sin(3.0 * np.pi * u) \
              + CLOUD_A2 * np.sin(7.0 * np.pi * u)
    sx    = CLOUD_S_MIN + CLOUD_S_MAX * np.power(np.sin(np.pi * u), CLOUD_P)
    sy    = CLOUD_RHO * sx
    alpha = CLOUD_ALPHA_MIN + CLOUD_ALPHA_MAX * np.power(np.sin(np.pi * u), CLOUD_Q)
    return x, y, sx, sy, alpha
