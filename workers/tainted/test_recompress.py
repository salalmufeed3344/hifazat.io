"""Recompression survival: does the blue-channel pattern survive WhatsApp/TikTok?

Re-encodes clean + protected videos at CRF 28 and 32 (social-platform range),
then measures perturbation survival/correlation in the centre region.

Signal-level only. Face-swap exposure (Roop/FaceFusion) is a separate test
in TEST-MATRIX.md.

Usage: python test_recompress.py clean.mp4 protected.mp4
"""
import subprocess, sys, tempfile, os
import cv2
import numpy as np


def frames(path, n=30):
    cap = cv2.VideoCapture(path); out = []
    while len(out) < n:
        ok, f = cap.read()
        if not ok: break
        out.append(f)
    cap.release(); return out


def recompress(src, crf):
    fd, dst = tempfile.mkstemp(suffix=".mp4"); os.close(fd)
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", src, "-c:v", "libx264",
                    "-crf", str(crf), "-pix_fmt", "yuv420p", dst], check=True)
    return dst


def centre_blue(f):
    h, w = f.shape[:2]
    return f[h//4:3*h//4, w//4:3*w//4, 0].astype(np.float32).ravel()


def main():
    clean, prot = frames(sys.argv[1]), frames(sys.argv[2])
    n = min(len(clean), len(prot))
    pert = np.concatenate([centre_blue(prot[i]) - centre_blue(clean[i]) for i in range(n)])
    print(f"frames compared: {n}, perturbation energy: {(pert**2).mean():.2f}")
    for crf in (28, 32):
        c2p, p2p = recompress(sys.argv[1], crf), recompress(sys.argv[2], crf)
        c2, p2 = frames(c2p, n), frames(p2p, n)
        m = min(n, len(c2), len(p2))
        pert2 = np.concatenate([centre_blue(p2[i]) - centre_blue(c2[i]) for i in range(m)])
        k = min(len(pert), len(pert2))
        survival = np.sqrt((pert2[:k]**2).mean() / ((pert[:k]**2).mean() + 1e-9))
        corr = np.corrcoef(pert[:k], pert2[:k])[0, 1]
        print(f"crf {crf}: survival={survival:.3f} correlation={corr:.3f} "
              f"({'pattern largely survives' if corr > 0.5 else 'pattern mostly destroyed — raise amplitude/period'})")
        os.remove(c2p); os.remove(p2p)


if __name__ == "__main__":
    main()
