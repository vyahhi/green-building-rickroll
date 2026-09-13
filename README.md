# Green Building Rickroll

A dependency-free, procedural pixel-art Rick Astley dance for the MIT Green
Building simulator. Every frame is exactly 17 rows × 9 columns × `[r, g, b]`.
The loop alternates an oversized Rick-and-microphone portrait with crisp lyric
cards spelling `NEVER / GONNA / GIVE / YOU / UP`. Colors are tuned to remain
legible through the simulator's building-scale bloom effect.

## Play it

From this folder:

```bash
python3 rickroll.py
```

That sends a 30-second animation at 6 FPS to `quiet-fox`. Preview it locally
without sending anything:

```bash
python3 rickroll.py --dry-run --seconds 10
```

Keep the animation running continuously until you press Ctrl-C:

```bash
python3 rickroll.py --loop
```

Duration, frame rate, and destination are configurable:

```bash
python3 rickroll.py --seconds 60 --fps 8 \
  --endpoint https://sundai.willsarg.com/api/i/quiet-fox/frame
```

The implementation uses only Python's standard library, so no install step is
needed. Run the tests with `python3 -m unittest -v`.
