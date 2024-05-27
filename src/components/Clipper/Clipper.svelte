<script lang="ts">
import { createEventDispatcher } from "svelte";
import type { Writable } from "svelte/store";
import type { Clip } from "./common";
import ClipComponent from "./Clip.svelte";

const dispatcher = createEventDispatcher<{
  play: {
    store: Writable<Clip>;
    value: Clip;
  };
  delete: Writable<Clip>;
}>();

export let selected: Writable<Clip> | undefined;
export let clips: Writable<Clip>[];
</script>

<div class="flex flex-col gap-4 px-2 pb-16">
  {#each clips as clip, i}
    <ClipComponent
      {selected}
      {clip}
      index={i}
      on:play={(e) => dispatcher("play", e.detail)}
      on:delete={() => dispatcher("delete", clip)}
    />
  {/each}
</div>
