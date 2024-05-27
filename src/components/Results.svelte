<script lang="ts">
import { createEventDispatcher } from "svelte";
import { fly } from "svelte/transition";
import { twMerge } from "tailwind-merge";
import { apiLocation } from "~/common";
import { useKey } from "@web-std/svelte-common/src/hooks";
import Search2Line from "~/icons/Search2Line.svelte";
import { stop_propagation } from "svelte/internal";

const dispatcher = createEventDispatcher<{ select: string }>();

let searchTerm = "";
let results: {
  channel: string;
  duration: string;
  id: string;
  publish_time: string;
  title: string;
  thumbnails: string[];
  views: string;
}[] = [];

let loading = false;
let inputElement: HTMLInputElement;

const updateResults = async () => {
  loading = true;

  const location = new URL(apiLocation);
  location.pathname = "/query";
  location.searchParams.append("q", searchTerm);

  const response = await window.fetch(location);
  results = JSON.parse(await response.text());

  loading = false;
};

useKey("/", (e) => {
  if (!inputElement) {
    return;
  }
  inputElement.focus();
  e.preventDefault();
});
</script>

<div class="flex-[3] overflow-y-auto h-full">
  <div class="flex flex-col items-center py-5 h-full">
    <div
      class={twMerge(
        "sticky top-0 px-10 py-4 flex gap-4 justify-center items-center w-full",
        "backdrop-blur-lg bg-opacity-50 bg-white"
      )}
    >
      <input
        type="text"
        class={twMerge(
          "max-w-sm w-full px-4 py-2 rounded-full border-2 bg-transparent outline-none transition-all",
          "border-neutral-700 placeholder:text-neutral-700",
          "focus:border-neutral-900 focus:bg-neutral-300 focus:bg-opacity-40"
        )}
        placeholder="Search"
        disabled={loading}
        bind:this={inputElement}
        bind:value={searchTerm}
        on:keydown={(e) => {
          if (e.key === "Enter") {
            updateResults();
            e.currentTarget.blur();
          }
          if (e.key === "Escape") {
            e.currentTarget.blur();
          }
          e.stopPropagation();
        }}
      />
      {#if loading}
        <div class="w-min h-min" transition:fly|local={{ y: 10 }}>
          <Search2Line />
        </div>
      {/if}
    </div>
    <div class="px-8 py-4">
      {#if results.length > 0}
        <div class="flex flex-wrap">
          {#each results as video}
            <button
              class={twMerge(
                "flex flex-col p-4 gap-3 justify-between basis-80 transition-all",
                "hover:bg-neutral-200 active:scale-90"
              )}
              on:click={() => {
                dispatcher("select", video.id);
              }}
            >
              <div class="flex flex-col gap-3">
                <img
                  class="rounded-lg overflow-hidden"
                  src={video.thumbnails[0]}
                  alt="thumbnail"
                />
                <h4 class="font-semibold text-start">{video.title}</h4>
              </div>
              <div class="flex justify-between text-neutral-700">
                <p>{video.views}</p>
                <p>{video.publish_time}</p>
              </div>
            </button>
          {/each}
        </div>
      {/if}
    </div>
    {#if results.length === 0}
      <h2 class="text-neutral-700 text-xl m-auto">
        Results will appear here...
      </h2>
    {/if}
  </div>
</div>
