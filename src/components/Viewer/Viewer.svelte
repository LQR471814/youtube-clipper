<script lang="ts">
import throttle from "lodash.throttle";
import { apiLocation, knownTags } from "~/common";
import PauseLine from "~/icons/PauseLine.svelte";
import PlayLine from "~/icons/PlayLine.svelte";
import Clipper from "../Clipper/Clipper.svelte";
import { Clip, formatSeconds } from "../Clipper/common";
import RangeSlider from "svelte-range-slider-pips";
import { useKey } from "@web-std/svelte-common/src/hooks";
import { clamp } from "@web-std/common/src/general";
import { get, writable, Writable } from "svelte/store";
import ScissorsLine from "~/icons/ScissorsLine.svelte";
import { SyncedMedia } from "../viewer";
import { onMount } from "svelte";
//@ts-expect-error
import Tags from "svelte-tags-input";
import type { VideoInfo } from "./common";
import AddLine from "~/icons/AddLine.svelte";
import StopFill from "~/icons/StopFill.svelte";
import { createEventDispatcher } from "svelte";

const dispatcher = createEventDispatcher<{ complete: void }>();

export let videoInfo: VideoInfo;

let tags: string[] = [];

// clips
let clips: Writable<Clip>[] = (videoInfo.chapters ?? []).map((c) => {
  return writable({
    start: c.start_time,
    end: c.end_time,
    fromChapter: c.title,
  });
});
let recording = false;
let recordingStart = 0;
let submitting = false;

// zooming
const zoomSteps = 5;
let zoom = 3;
let min = 0;
let max: number | undefined = undefined;

$: if (!elapsedOverriden) {
  if (selectedClip === undefined) {
    min = 0;
    max = undefined;
    break $;
  }

  const marginPercentage = (zoomSteps - zoom) / zoomSteps;
  if (marginPercentage === 1) {
    min = 0;
    max = undefined;
    break $;
  }

  const margin = (selectedClip.end - selectedClip.start) * marginPercentage;
  min = clamp(selectedClip.start - margin, 0, fullDuration);
  max = clamp(selectedClip.end + margin, 0, fullDuration);
}

// control player
let videoPlayer: HTMLVideoElement;
let audioPlayer: HTMLAudioElement;
let player: SyncedMedia;
let paused = true;
let fullDuration: number;

onMount(() => {
  if (!videoPlayer || !audioPlayer) {
    return;
  }
  player = new SyncedMedia([videoPlayer, audioPlayer]);
});

let elapsed = 0;
let elapsedOverriden = false;

let selectedClipStore: Writable<Clip> | undefined;
$: selectedClip =
  selectedClipStore !== undefined ? $selectedClipStore : undefined;

$: elapsedTime = !isNaN(elapsed * 1) ? formatSeconds(elapsed) : "";

const togglePlayState = () => {
  if (!player) {
    return;
  }
  if (selectedClip && selectedClip.end - player.currentTime <= 0.01 && paused) {
    player.currentTime = selectedClip.start;
    player.play();
    return;
  }
  elapsedOverriden = false;
  if (paused) {
    player.play();
    return;
  }
  player.pause();
};

const seekTo = throttle(
  (elapsed: number) => (player.currentTime = elapsed),
  300,
  {
    leading: true,
  }
);

const seek = (delta: number) => {
  return () => {
    if (!player) {
      return;
    }

    let newTime = selectedClip
      ? clamp(elapsed + delta, selectedClip.start, selectedClip.end)
      : clamp(elapsed + delta, 0, fullDuration);

    player.currentTime = newTime;
    elapsed = newTime;

    if (paused) {
      elapsedOverriden = true;
    }
  };
};

useKey(" ", (e) => {
  togglePlayState();
  e.preventDefault();
});
useKey("ArrowRight", seek(5));
useKey("ArrowLeft", seek(-5));
</script>

{#if videoInfo !== undefined}
  <div>
    <div class="p-8 overflow-y-scroll h-full">
      <div class="flex flex-col gap-4 sticky top-0 backdrop-blur-sm pb-4">
        <div class="relative">
          <video
            class="overflow-hidden rounded-2xl"
            src={videoInfo.video}
            on:timeupdate={() => {
              if (elapsedOverriden) {
                return;
              }
              if (selectedClip && player.currentTime >= selectedClip.end) {
                player.currentTime = selectedClip.end;
                player.pause();
              }
              elapsed = player.currentTime;
            }}
            on:click={togglePlayState}
            bind:this={videoPlayer}
            bind:paused
            bind:duration={fullDuration}
          >
            <track kind="captions" src={videoInfo.captions} />
          </video>
          <div class="video-controls w-full absolute bottom-0">
            {#if selectedClip !== undefined}
              <div class="px-3">
                <RangeSlider
                  range="min"
                  values={[
                    (elapsed - selectedClip.start) /
                      (selectedClip.end - selectedClip.start),
                  ]}
                  min={0}
                  max={1}
                  step={1 / ((selectedClip.end - selectedClip.start) * 4)}
                  springValues={{
                    stiffness: 0.2,
                    damping: 0.4,
                  }}
                  on:start={() => {
                    if (player?.duration === undefined) {
                      return;
                    }
                    elapsedOverriden = true;
                  }}
                  on:change={(e) => {
                    if (
                      player?.duration === undefined ||
                      selectedClip === undefined
                    ) {
                      return;
                    }
                    const destination =
                      selectedClip.start +
                      (selectedClip.end - selectedClip.start) * e.detail.value;
                    elapsed = destination;
                    seekTo(destination);
                  }}
                  on:stop={() => {
                    elapsedOverriden = false;
                  }}
                />
              </div>
            {/if}
            <div class="flex items-center gap-2 p-2">
              {#if elapsedTime}
                <p class="text-white font-semibold">
                  {elapsedTime}
                </p>
              {/if}
              <button
                class="hover:scale-110 active:scale-90 transition-all"
                on:click={togglePlayState}
              >
                {#if paused}
                  <PlayLine className="fill-white" />
                {:else}
                  <PauseLine className="fill-white" />
                {/if}
              </button>
              <RangeSlider
                range={selectedClip !== undefined ? true : "min"}
                values={selectedClip !== undefined
                  ? [selectedClip.start, selectedClip.end]
                  : [!isNaN(elapsed) ? elapsed : 0]}
                {min}
                max={max ?? fullDuration}
                step={0.25}
                springValues={{
                  stiffness: 0.2,
                  damping: 0.4,
                }}
                on:start={() => {
                  if (player?.duration === undefined) {
                    return;
                  }
                  elapsedOverriden = true;
                }}
                on:change={(e) => {
                  if (player?.duration === undefined) {
                    return;
                  }
                  if (selectedClip !== undefined) {
                    selectedClipStore?.update((c) => {
                      c.start = e.detail.values[0];
                      c.end = e.detail.values[1];
                      return c;
                    });
                  }
                  const destination = e.detail.values[e.detail.activeHandle];
                  elapsed = destination;
                  seekTo(destination);
                }}
                on:stop={() => {
                  elapsedOverriden = false;
                }}
              />
            </div>
          </div>
        </div>
        <audio src={videoInfo.audio} bind:this={audioPlayer} />

        <div>
          <h3 class="text-2xl font-bold">{videoInfo.title}</h3>
          <h4 class="text-lg text-neutral-700">
            {videoInfo.channel}
          </h4>
        </div>

        <div on:keydown={(e) => e.stopPropagation()}>
          <Tags
            addKeys={[13, 32]}
            minChars={0}
            autoComplete={$knownTags}
            onlyAutocomplete={false}
            onlyUnique={true}
            placeholder="Insert clip tags"
            bind:tags
          />
        </div>
      </div>

      <Clipper
        selected={selectedClipStore}
        {clips}
        on:play={(e) => {
          if (e.detail.store === selectedClipStore) {
            selectedClipStore = undefined;
            return;
          }
          selectedClipStore = e.detail.store;
          player.currentTime = e.detail.value.start;
          console.log(e.detail.value.start);
          elapsed = e.detail.value.start;
          player.play();
        }}
        on:delete={(e) => {
          if (selectedClipStore === e.detail) {
            selectedClipStore = undefined;
          }
          clips = clips.filter((clip) => clip !== e.detail);
        }}
      />
    </div>
    <div class="relative">
      <div class="flex gap-2 absolute bottom-4 left-4">
        <button
          class="big-button"
          on:click={() => {
            if (recording) {
              if (player.currentTime < recordingStart) {
                alert("the end time cannot be before the start time!");
                return;
              }

              player.pause();
              const newClip = writable({
                start: recordingStart,
                end: player.currentTime,
              });
              clips = [...clips, newClip];
              selectedClipStore = newClip;
            } else {
              recordingStart = player.currentTime;
              player.play();
            }
            recording = !recording;
          }}
        >
          {#if !recording}
            <AddLine width={28} height={28} />
          {:else}
            <StopFill width={28} height={28} />
          {/if}
        </button>
        {#if selectedClip !== undefined}
          <div class="big-button px-6 w-40 items-center">
            <RangeSlider
              values={[zoom]}
              min={0}
              max={zoomSteps - 1}
              range="min"
              pips
              all="label"
              formatter={(value) => {
                if (value === 0) {
                  return "1";
                }
                return `${zoomSteps - value}/${zoomSteps}`;
              }}
              on:change={(e) => {
                zoom = e.detail.value;
              }}
            />
          </div>
        {/if}
      </div>
      <button
        class="big-button px-6 absolute bottom-4 right-4"
        disabled={submitting}
        on:click={() => {
          if (tags.length === 0) {
            alert("you must specify at least 1 tag");
            return;
          }
          submitting = true;
          window
            .fetch(`${apiLocation}/splice`, {
              method: "POST",
              headers: {
                "Content-Type": "application/json",
              },
              body: JSON.stringify({
                tags: tags,
                video: videoInfo.video,
                audio: videoInfo.audio,
                clips: clips.map((clip) => ({
                  start: get(clip).start,
                  end: get(clip).end,
                })),
              }),
            })
            .then(() => {
              submitting = false;
              dispatcher("complete");
            });
        }}
      >
        <ScissorsLine width={28} height={28} />
        {!submitting ? "Cut" : "Cutting"}
      </button>
    </div>
  </div>
{/if}

<style>
:global(.video-controls:hover .rangeSlider) {
  font-size: 14px;
}

:global(.rangePips .pipVal) {
  transform: translateX(-50%);
}

:global(.rangeSlider.pips) {
  margin-bottom: 0.5rem;
}

:global(.rangeSlider) {
  width: 100%;
  font-size: 12px;

  @apply m-0 transition-all;

  --range-slider: white;
  --range-range: rgb(239 68 68);
  --range-range-inactive: rgb(239 68 68);
  --range-range-focus: rgb(239 68 68);
  --range-handle: rgb(239 68 68);
  --range-handle-inactive: rgb(239 68 68);
  --range-handle-focus: rgb(239 68 68);
  --range-handle-border: rgb(239 68 68);
}

:global(.rangeSlider:hover) {
  cursor: pointer;
}

:global(.rangeNub) {
  border-radius: 10em !important;
}

:global(.svelte-tags-input-layout) {
  border-radius: 0.5rem !important;
  padding: 0.65rem 0.4rem !important;
  background-color: rgba(255, 255, 255, 0.2) !important;
  transition: 0.15s all ease-in-out;

  border: 2px solid #e5e7eb !important;
}

:global(.svelte-tags-input-layout.focus) {
  border-color: black !important;
}

:global(.svelte-tags-input) {
  background-color: transparent !important;
  margin: 0 !important;
}

:global(.svelte-tags-input-tag) {
  margin: 0 !important;
  border-radius: 9999px !important;
  padding: 0.25rem 0.5rem !important;
  margin: 0 0.25rem !important;
}

:global(.svelte-tags-input-matchs) {
  border-radius: 0.5rem !important;
  padding: 0.25rem !important;
}

:global(.svelte-tags-input-matchs li) {
  border-radius: 0.4rem !important;
  transition: 0.15s all ease-in-out;
}
</style>
