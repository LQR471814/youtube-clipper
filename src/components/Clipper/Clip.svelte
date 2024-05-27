<script lang="ts">
import type { Writable } from "svelte/store";
import { createEventDispatcher } from "svelte";
import { twMerge } from "tailwind-merge";
import { Clip, formatSeconds } from "./common";
import DeleteBinLine from "~/icons/DeleteBinLine.svelte";

const dispatcher = createEventDispatcher<{
  play: {
    store: Writable<Clip>;
    value: Clip;
  };
  delete: void;
}>();

export let clip: Writable<Clip>;
export let selected: Writable<Clip> | undefined;
export let index: number;
</script>

<button
  class={twMerge(
    "rounded-2xl border-2 p-4 text-left transition-all",
    "hover:shadow-lg active:scale-[98%]",
    "flex items-center justify-between",
    selected === clip ? "border-red-500" : ""
  )}
  on:click={() =>
    dispatcher("play", {
      store: clip,
      value: $clip,
    })}
>
  <div>
    <h4 class="text-lg font-semibold">
      Clip {index + 1}
    </h4>
    <h5 class="text-lg">
      {formatSeconds($clip.start)} - {formatSeconds($clip.end)}
    </h5>
    {#if $clip.fromChapter}
      <h5 class="text-lg text-neutral-700 italic">
        Taken from chapter "{$clip.fromChapter}"
      </h5>
    {/if}
  </div>
  <button
    class="rounded-full p-4 hover:bg-neutral-200 transition-all"
    on:click={(e) => {
      e.stopPropagation();
      dispatcher("delete")
    }}
  >
    <DeleteBinLine />
  </button>
</button>
