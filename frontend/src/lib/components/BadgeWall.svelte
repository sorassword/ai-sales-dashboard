<script lang="ts">
  import type { EarnedBadge } from '$lib/types';
  import { slugify } from '$lib/utils/format';
  import Avatar from '$lib/components/ui/Avatar.svelte';
  import { openModal } from '$lib/stores/modal.svelte';
  import { Euro, Flame, Brain, Star, Zap, Crown, Clock, Trophy, Award } from 'lucide-svelte';

  interface Props {
    badges: EarnedBadge[];
    limit?: number;
    /** Retained for backwards compatibility; the wall is always a compact list now. */
    layout?: 'row' | 'grid';
  }
  let { badges, limit }: Props = $props();
  let visible = $derived(limit ? badges.slice(0, limit) : badges);

  // icon_key → lucide icon component.
  const iconMap = {
    euro: Euro,
    fire: Flame,
    brain: Brain,
    star: Star,
    lightning: Zap,
    crown: Crown,
    clock: Clock,
    trophy: Trophy
  } as const;
  const iconFor = (key: string) => iconMap[key as keyof typeof iconMap] ?? Award;

  // EarnedBadge carries no avatar info, so derive initials + hue from the name.
  const initialsFor = (name: string) => {
    const parts = name.split(' ');
    return ((parts[0]?.[0] ?? '') + (parts[parts.length - 1]?.[0] ?? '')).toUpperCase();
  };
  const hueFor = (name: string) => [...name].reduce((acc, ch) => (acc + ch.charCodeAt(0)) % 360, 0);

  const rarityIcon: Record<string, string> = {
    common: 'text-gray-500',
    rare: 'text-[#7C3AED]',
    legendary: 'text-[#B45309]'
  };
</script>

<!-- Compact vertical list: avatar (initials) + badge name + icon. No description. -->
<div class="max-h-[600px] overflow-y-auto rounded-xl border border-gray-100">
  {#each visible as b, i (b.badge.id + b.employee_id)}
    {@const Icon = iconFor(b.badge.icon_key)}
    <button
      class="flex h-[80px] min-w-[160px] w-full cursor-pointer items-center gap-3 px-3 py-2 text-left transition-colors duration-150 hover:bg-gray-50 {i %
        2 ===
      1
        ? 'bg-[#FAFAFA]'
        : 'bg-white'}"
      onclick={() => openModal('employee-detail', { employee_id: slugify(b.employee_name) })}
    >
      <Avatar initials={initialsFor(b.employee_name)} hue={hueFor(b.employee_name)} size={32} />

      <div class="flex min-w-0 flex-1 items-center gap-2">
        <Icon size={16} strokeWidth={1.8} class={rarityIcon[b.badge.rarity]} />
        <span class="truncate text-xs font-medium text-ink">{b.badge.name}</span>
      </div>
    </button>
  {/each}
</div>
