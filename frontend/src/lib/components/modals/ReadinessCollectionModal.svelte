<script lang="ts">
  import Modal from '$lib/components/ui/Modal.svelte';
  import ModalSkeleton from '$lib/components/ui/ModalSkeleton.svelte';
  import Avatar from '$lib/components/ui/Avatar.svelte';
  import { api } from '$lib/api/client';
  import { closeModal } from '$lib/stores/modal.svelte';
  import { formatDate } from '$lib/utils/format';
  import type { Employee, ReadinessItem } from '$lib/types';

  interface Props {
    collection_name: string;
    items: ReadinessItem[];
  }
  let { collection_name, items }: Props = $props();

  let item = $derived(items.find((i) => i.collection === collection_name) ?? items[0]);

  let employees = $state<Employee[] | null>(null);
  $effect(() => {
    let cancelled = false;
    api.employees().then((list) => {
      if (!cancelled) employees = list;
    });
    return () => {
      cancelled = true;
    };
  });

  // Deterministic split of the tracked roster by the readiness ratio.
  let split = $derived.by(() => {
    if (!employees) return { prepared: [] as Employee[], pending: [] as Employee[] };
    const sorted = [...employees].sort((a, b) => a.name.localeCompare(b.name));
    const n = Math.round((item.readiness_score / 100) * sorted.length);
    return { prepared: sorted.slice(0, n), pending: sorted.slice(n) };
  });

  const alertMap: Record<string, { label: string; banner: string; bar: string }> = {
    critical: { label: 'Kritisch', banner: 'bg-[#B91C1C] text-white', bar: '#DC2626' },
    warning: { label: 'Rückstand', banner: 'bg-[#D97706] text-white', bar: '#D97706' },
    ok: { label: 'Bereit', banner: 'bg-positive text-white', bar: 'var(--color-ink)' }
  };
</script>

<Modal open={true} title={collection_name} width="max-w-4xl" onClose={closeModal}>
  {#if !employees}
    <ModalSkeleton />
  {:else}
    {@const al = alertMap[item.alert_level] ?? alertMap.ok}

    <!-- Alert banner -->
    <div class="flex flex-col gap-1 rounded-lg px-5 py-3 sm:flex-row sm:items-center sm:justify-between {al.banner}">
      <p class="font-semibold">{al.label} · Launch am {formatDate(item.launch_date)}</p>
      <p class="text-sm font-medium">
        {item.prepared_employees} von {item.total_employees} eingearbeitet
      </p>
    </div>

    <!-- Progress bar -->
    <div class="mt-4 flex items-center gap-3">
      <div class="h-3 flex-1 overflow-hidden rounded-full bg-paper">
        <div class="h-full rounded-full" style="width:{item.readiness_score}%;background:{al.bar}"></div>
      </div>
      <span class="tnum text-lg font-semibold text-ink">{item.readiness_score}<span class="text-sm text-ink-mute">/100</span></span>
    </div>

    <!-- Two-column employee breakdown -->
    <div class="mt-6 grid grid-cols-1 gap-6 sm:grid-cols-2">
      <div>
        <p class="mb-3 text-[12px] font-medium tracking-wide text-positive uppercase">
          Eingearbeitet ({split.prepared.length})
        </p>
        <div class="space-y-2">
          {#each split.prepared as e (e.id)}
            <div class="flex items-center gap-2.5">
              <Avatar initials={e.initials} hue={e.avatar_hue} size={28} />
              <span class="text-[13px] text-ink">{e.name}</span>
            </div>
          {/each}
        </div>
      </div>
      <div>
        <p class="mb-3 text-[12px] font-medium tracking-wide text-ink-mute uppercase">
          Noch ausstehend ({split.pending.length})
        </p>
        <div class="space-y-2">
          {#each split.pending as e (e.id)}
            <div class="flex items-center gap-2.5 opacity-70">
              <Avatar initials={e.initials} hue={e.avatar_hue} size={28} />
              <span class="text-[13px] text-ink-soft">{e.name}</span>
            </div>
          {/each}
        </div>
      </div>
    </div>
  {/if}
</Modal>
