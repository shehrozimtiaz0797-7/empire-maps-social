# Empire Maps social reels

Copies each new Empire Maps Short to the Empire Maps Facebook Page and Instagram (@empiremaps01) as a Reel,
with a small "More maps on YouTube @empiremaps1857" banner and a 2.5 s end card that sends people to YouTube.

- Reads the newest Short from the `qa` branch of empire-maps-pipeline (read only). The Empire Maps repo,
  its workflow and the YouTube channel are never changed by this repo.
- `make-reel.yml` (started by a scheduled Claude task) builds `reels` branch: reel.mp4 + meta.json.
- The scheduled task then posts it to Facebook and Instagram (marked as AI-made) and records it in posted.json.
