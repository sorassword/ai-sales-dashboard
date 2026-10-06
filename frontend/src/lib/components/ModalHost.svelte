<script lang="ts">
  import { modalState } from '$lib/stores/modal.svelte';
  import StoreDetailModal from '$lib/components/modals/StoreDetailModal.svelte';
  import EmployeeDetailModal from '$lib/components/modals/EmployeeDetailModal.svelte';
  import RevenueTrendModal from '$lib/components/modals/RevenueTrendModal.svelte';
  import BotTrendModal from '$lib/components/modals/BotTrendModal.svelte';
  import CorrelationModal from '$lib/components/modals/CorrelationModal.svelte';
  import DigestModal from '$lib/components/modals/DigestModal.svelte';
  import ReadinessCollectionModal from '$lib/components/modals/ReadinessCollectionModal.svelte';

  // The payload shape is validated by each modal's own props; the dispatch
  // point spreads it loosely.
  let state = $derived($modalState);
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  let payload = $derived(state.payload as any);
</script>

{#if state.open}
  {#if state.type === 'store-detail'}
    <StoreDetailModal {...payload} />
  {:else if state.type === 'employee-detail'}
    <EmployeeDetailModal {...payload} />
  {:else if state.type === 'revenue-trend'}
    <RevenueTrendModal {...payload} />
  {:else if state.type === 'bot-trend'}
    <BotTrendModal {...payload} />
  {:else if state.type === 'correlation'}
    <CorrelationModal {...payload} />
  {:else if state.type === 'digest'}
    <DigestModal {...payload} />
  {:else if state.type === 'readiness-collection'}
    <ReadinessCollectionModal {...payload} />
  {/if}
{/if}
