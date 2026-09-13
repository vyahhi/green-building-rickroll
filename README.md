# Green Building Rickroll

A dependency-free, procedural pixel-art Rick Astley dance for the MIT Green
Building simulator. Every frame is exactly 17 rows × 9 columns × `[r, g, b]`.

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

Duration, frame rate, and destination are configurable:

```bash
python3 rickroll.py --seconds 60 --fps 8 \
  --endpoint https://sundai.willsarg.com/api/i/quiet-fox/frame
```

The implementation uses only Python's standard library, so no install step is
needed. Run the tests with `python3 -m unittest -v`.
