<script lang="ts">
  interface Props {
    initials: string;
    hue: number;
    size?: number;
  }
  let { initials, hue, size = 34 }: Props = $props();
</script>

<div
  class="flex shrink-0 items-center justify-center rounded-full font-medium"
  style="
    width:{size}px;height:{size}px;
    font-size:{size * 0.38}px;
    background:hsl({hue} 32% 90%);
    color:hsl({hue} 45% 32%);
  "
  aria-hidden="true"
>
  {initials}
</div>
