<script lang="ts">
  import type { TrendPoint } from '$lib/types';

  interface Props {
    data: TrendPoint[];
    /** CSS color for the line/area. Defaults to the brass accent. */
    color?: string;
    valueFormat?: (v: number) => string;
    height?: number;
  }
  let {
    data,
    color = 'var(--color-brass)',
    valueFormat = (v) => String(v),
    height = 200
  }: Props = $props();

  const W = 560;
  const PAD = { top: 16, right: 12, bottom: 28, left: 12 };

  let geo = $derived.by(() => {
    const H = height;
    const values = data.map((d) => d.value);
    const min = Math.min(...values);
    const max = Math.max(...values);
    const range = max - min || 1;
    const innerW = W - PAD.left - PAD.right;
    const innerH = H - PAD.top - PAD.bottom;

    const pts = data.map((d, i) => {
      const x = PAD.left + (data.length === 1 ? innerW / 2 : (i / (data.length - 1)) * innerW);
      // pad the vertical range a touch so the line never hugs the edges
      const y = PAD.top + innerH - ((d.value - min) / range) * innerH * 0.82 - innerH * 0.09;
      return { x, y, d };
    });

    const line = pts.map((p, i) => `${i === 0 ? 'M' : 'L'}${p.x},${p.y}`).join(' ');
    const area = `${line} L${pts[pts.length - 1].x},${H - PAD.bottom} L${pts[0].x},${H - PAD.bottom} Z`;
    return { pts, line, area, H };
  });
</script>

<div class="w-full">
  <svg viewBox="0 0 {W} {geo.H}" class="h-auto w-full" role="img" aria-label="Trendverlauf">
    <defs>
      <linearGradient id="areaFill" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0%" stop-color={color} stop-opacity="0.18" />
        <stop offset="100%" stop-color={color} stop-opacity="0" />
      </linearGradient>
    </defs>

    <!-- gridlines -->
    {#each [0.25, 0.5, 0.75] as g (g)}
      <line
        x1={PAD.left}
        x2={W - PAD.right}
        y1={PAD.top + (geo.H - PAD.top - PAD.bottom) * g}
        y2={PAD.top + (geo.H - PAD.top - PAD.bottom) * g}
        stroke="var(--color-line)"
        stroke-width="1"
        stroke-dasharray="2 4"
      />
    {/each}

    <path d={geo.area} fill="url(#areaFill)" />
    <path
      d={geo.line}
      fill="none"
      stroke={color}
      stroke-width="2.25"
      stroke-linecap="round"
      stroke-linejoin="round"
    />

    {#each geo.pts as p, i (i)}
      <circle cx={p.x} cy={p.y} r="3.5" fill="var(--color-card)" stroke={color} stroke-width="2" />
      <text
        x={p.x}
        y={geo.H - 8}
        text-anchor="middle"
        class="fill-[var(--color-ink-mute)]"
        style="font-size:11px;font-family:var(--font-body)"
      >
        {p.d.label}
      </text>
    {/each}

    <!-- last value label -->
    {#if geo.pts.length}
      {@const last = geo.pts[geo.pts.length - 1]}
      <text
        x={last.x}
        y={last.y - 12}
        text-anchor="end"
        class="fill-[var(--color-ink)]"
        style="font-size:12px;font-weight:600;font-family:var(--font-mono)"
      >
        {valueFormat(last.d.value)}
      </text>
    {/if}
  </svg>
</div>
