<script lang="ts">
  import type { ScatterPoint } from '$lib/types';
  import { formatEurCompact } from '$lib/utils/format';

  interface Props {
    points: ScatterPoint[];
    height?: number;
  }
  let { points, height = 300 }: Props = $props();

  const W = 560;
  const PAD = { top: 20, right: 20, bottom: 42, left: 56 };

  let hovered = $state<ScatterPoint | null>(null);

  let geo = $derived.by(() => {
    const H = height;
    const xs = points.map((p) => p.bot_minutes);
    const ys = points.map((p) => p.revenue);
    const xMin = Math.min(...xs),
      xMax = Math.max(...xs);
    const yMin = Math.min(...ys),
      yMax = Math.max(...ys);
    const innerW = W - PAD.left - PAD.right;
    const innerH = H - PAD.top - PAD.bottom;

    const sx = (x: number) => PAD.left + ((x - xMin) / (xMax - xMin || 1)) * innerW;
    const sy = (y: number) => PAD.top + innerH - ((y - yMin) / (yMax - yMin || 1)) * innerH;

    const dots = points.map((p) => ({ p, cx: sx(p.bot_minutes), cy: sy(p.revenue) }));

    // simple least-squares regression line
    const n = points.length;
    const mx = xs.reduce((a, b) => a + b, 0) / n;
    const my = ys.reduce((a, b) => a + b, 0) / n;
    const slope =
      xs.reduce((a, x, i) => a + (x - mx) * (ys[i] - my), 0) /
      (xs.reduce((a, x) => a + (x - mx) ** 2, 0) || 1);
    const intercept = my - slope * mx;
    const lx1 = xMin,
      lx2 = xMax;
    const reg = { x1: sx(lx1), y1: sy(slope * lx1 + intercept), x2: sx(lx2), y2: sy(slope * lx2 + intercept) };

    return { H, innerH, dots, reg, yMin, yMax };
  });
</script>

<div class="relative w-full">
  <svg
    viewBox="0 0 {W} {geo.H}"
    class="h-auto w-full"
    role="img"
    aria-label="Korrelation Bot-Nutzung und Umsatz"
  >
    <!-- y axis labels -->
    {#each [0, 0.5, 1] as t (t)}
      {@const y = PAD.top + geo.innerH * (1 - t)}
      <line x1={PAD.left} x2={W - PAD.right} y1={y} y2={y} stroke="var(--color-line)" stroke-width="1" />
      <text
        x={PAD.left - 8}
        y={y + 4}
        text-anchor="end"
        class="fill-[var(--color-ink-mute)]"
        style="font-size:10px;font-family:var(--font-mono)"
      >
        {formatEurCompact(geo.yMin + (geo.yMax - geo.yMin) * t)}
      </text>
    {/each}

    <!-- regression line -->
    <line
      x1={geo.reg.x1}
      y1={geo.reg.y1}
      x2={geo.reg.x2}
      y2={geo.reg.y2}
      stroke="var(--color-ink)"
      stroke-width="1.5"
      stroke-dasharray="5 4"
      opacity="0.55"
    />

    <!-- dots -->
    {#each geo.dots as d (d.p.employee_id)}
      <circle
        cx={d.cx}
        cy={d.cy}
        r={hovered === d.p ? 7 : 5}
        fill="var(--color-brass)"
        fill-opacity={hovered === d.p ? 1 : 0.7}
        stroke="var(--color-card)"
        stroke-width="1.5"
        class="cursor-pointer transition-all"
        role="presentation"
        onmouseenter={() => (hovered = d.p)}
        onmouseleave={() => (hovered = null)}
      />
    {/each}

    <text
      x={W / 2}
      y={geo.H - 8}
      text-anchor="middle"
      class="fill-[var(--color-ink-soft)]"
      style="font-size:11px;font-family:var(--font-body)"
    >
      Bot-Nutzung (Minuten / Monat) →
    </text>
  </svg>

  {#if hovered}
    <div
      class="pointer-events-none absolute top-2 right-2 rounded-lg border border-line bg-card px-3 py-2 text-[12px] shadow-lg"
    >
      <p class="font-medium text-ink">{hovered.name}</p>
      <p class="tnum text-ink-soft">{hovered.bot_minutes} min · {formatEurCompact(hovered.revenue)}</p>
    </div>
  {/if}
</div>
