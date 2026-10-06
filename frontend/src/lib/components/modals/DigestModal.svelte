<script lang="ts">
  import { get } from 'svelte/store';
  import Modal from '$lib/components/ui/Modal.svelte';
  import ModalSkeleton from '$lib/components/ui/ModalSkeleton.svelte';
  import { api } from '$lib/api/client';
  import { closeModal } from '$lib/stores/modal.svelte';
  import { activePeriod } from '$lib/stores/period.svelte';
  import { formatNum } from '$lib/utils/format';
  import { HelpCircle } from 'lucide-svelte';
  import type { DigestDetail, Period } from '$lib/types';

  interface Props {
    period?: Period;
    detail?: DigestDetail;
  }
  let { period, detail }: Props = $props();

  let fetched = $state<DigestDetail | null>(null);
  let data = $derived(detail ?? fetched);
  let loading = $derived(!data);

  $effect(() => {
    if (detail || fetched) return;
    let cancelled = false;
    api.digestDetail(period ?? get(activePeriod)).then((d) => {
      if (!cancelled) fetched = d;
    });
    return () => {
      cancelled = true;
    };
  });
</script>

<Modal open={true} title="Weekly Digest — Detail" width="max-w-4xl" onClose={closeModal}>
  {#if loading || !data}
    <ModalSkeleton />
  {:else}
    <p class="mb-3 text-[12px] font-medium tracking-wide text-ink-mute uppercase">Top-Fragen der Woche</p>
    <div class="space-y-3">
      {#each data.top_questions as q (q.topic)}
        <div class="rounded-xl border border-gray-100 p-4">
          <div class="flex items-start justify-between gap-4">
            <div class="flex items-start gap-2.5">
              <HelpCircle size={18} class="mt-0.5 shrink-0 text-brass" />
              <div>
                <p class="font-medium text-ink">{q.topic}</p>
                <p class="mt-0.5 text-[13px] text-ink-soft italic">„{q.example_query}“</p>
              </div>
            </div>
            <span class="tnum shrink-0 text-[13px] font-semibold text-ink">{formatNum(q.count)}×</span>
          </div>
          {#if q.top_stores.length}
            <div class="mt-3 flex flex-wrap gap-2">
              {#each q.top_stores as store (store)}
                <span class="rounded-full bg-paper px-2.5 py-0.5 text-[12px] font-medium text-ink-soft">
                  {store}
                </span>
              {/each}
            </div>
          {/if}
        </div>
      {/each}
    </div>

    <p class="mt-6 mb-3 text-[12px] font-medium tracking-wide text-ink-mute uppercase">Readiness-Überblick</p>
    <div class="grid grid-cols-3 gap-3">
      <div class="rounded-xl border border-gray-100 bg-gray-50 p-4 text-center">
        <p class="tnum text-2xl font-semibold text-ink">{data.readiness_summary.avg_score}</p>
        <p class="mt-1 text-[12px] text-ink-soft">Ø Readiness</p>
      </div>
      <div class="rounded-xl border border-gray-100 bg-gray-50 p-4 text-center">
        <p class="tnum text-2xl font-semibold text-signal">{data.readiness_summary.critical_count}</p>
        <p class="mt-1 text-[12px] text-ink-soft">kritisch</p>
      </div>
      <div class="rounded-xl border border-gray-100 bg-gray-50 p-4 text-center">
        <p class="tnum text-2xl font-semibold text-ink">{data.readiness_summary.collections_launching_soon}</p>
        <p class="mt-1 text-[12px] text-ink-soft">Launch &lt; 30 Tage</p>
      </div>
    </div>
  {/if}
</Modal>
