<script lang="ts">
  import { page } from '$app/stores';
  import { NAV } from '$lib/nav';

  let path = $derived($page.url.pathname);
</script>

<aside
  class="flex h-screen w-64 shrink-0 flex-col border-r border-line bg-card/60 px-5 py-7"
>
  <!-- Brand -->
  <div class="mb-10 px-1">
    <div class="flex items-center gap-2.5">
      <div
        class="flex h-9 w-9 items-center justify-center rounded-lg bg-ink text-card"
        aria-hidden="true"
      >
        <span class="font-display text-lg leading-none">A</span>
      </div>
      <div class="leading-tight">
        <p class="font-display text-[17px] font-medium text-ink">Sales Intelligence</p>
        <p class="text-[11px] tracking-wide text-ink-mute uppercase">AI Assistant · Demo</p>
      </div>
    </div>
  </div>

  <!-- Nav -->
  <nav class="flex flex-1 flex-col gap-1">
    {#each NAV as item (item.href)}
      {@const active = item.href === '/' ? path === '/' : path.startsWith(item.href)}
      <a
        href={item.href}
        class="group flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm transition-colors
          {active
          ? 'bg-ink text-card'
          : 'text-ink-soft hover:bg-paper hover:text-ink'}"
      >
        <item.icon size={18} strokeWidth={1.8} />
        <span class="font-medium">{item.label}</span>
      </a>
    {/each}
  </nav>

  <!-- Footer -->
  <div class="mt-6 rounded-lg border border-line bg-paper/60 p-3.5">
    <p class="text-[11px] leading-relaxed text-ink-soft">
      Demo-Datensatz · alle Kennzahlen sind <span class="font-medium text-ink">fiktiv</span>.
    </p>
  </div>
</aside>
