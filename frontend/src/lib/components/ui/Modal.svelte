<script lang="ts">
  import { X } from 'lucide-svelte';
  import type { Snippet } from 'svelte';

  interface Props {
    open: boolean;
    title: string;
    width?: string;
    onClose?: () => void;
    children: Snippet;
  }
  let { open, title, width = 'max-w-4xl', onClose, children }: Props = $props();

  function close() {
    onClose?.();
  }

  // ESC to close + lock body scroll while the modal is open.
  $effect(() => {
    if (!open) return;
    const onKey = (e: KeyboardEvent) => {
      if (e.key === 'Escape') close();
    };
    window.addEventListener('keydown', onKey);
    document.body.style.overflow = 'hidden';
    return () => {
      window.removeEventListener('keydown', onKey);
      document.body.style.overflow = '';
    };
  });
</script>

{#if open}
  <!-- Overlay: click to close -->
  <div
    class="modal-overlay fixed inset-0 z-50 flex items-start justify-center overflow-y-auto bg-black/50 p-4 sm:p-8"
    onclick={close}
    onkeydown={(e) => e.key === 'Escape' && close()}
    role="presentation"
  >
    <!-- Panel: stop propagation so inner clicks don't close -->
    <div
      class="modal-panel relative my-auto max-h-[90vh] w-full {width} overflow-y-auto rounded-xl bg-white shadow-2xl"
      onclick={(e) => e.stopPropagation()}
      onkeydown={(e) => e.stopPropagation()}
      role="dialog"
      aria-modal="true"
      aria-label={title}
      tabindex="-1"
    >
      <div
        class="sticky top-0 z-10 flex items-center justify-between gap-4 border-b border-gray-100 bg-white px-6 py-4"
      >
        <h2 class="text-lg font-semibold text-ink">{title}</h2>
        <button
          onclick={close}
          class="cursor-pointer rounded-lg p-1.5 text-gray-400 transition-colors duration-150 hover:bg-gray-100 hover:text-ink"
          aria-label="Schließen"
        >
          <X size={20} />
        </button>
      </div>
      <div class="px-6 py-5">
        {@render children()}
      </div>
    </div>
  </div>
{/if}

<style>
  .modal-overlay {
    animation: overlay-in 200ms ease-out;
  }
  .modal-panel {
    animation: panel-in 250ms ease-out;
  }
  @keyframes overlay-in {
    from {
      opacity: 0;
    }
    to {
      opacity: 1;
    }
  }
  @keyframes panel-in {
    from {
      opacity: 0;
      transform: translateY(16px);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }
</style>
