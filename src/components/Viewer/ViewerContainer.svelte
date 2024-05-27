<script lang="ts">
import debounce from "lodash.debounce";
import { apiLocation } from "~/common";
import type { VideoInfo } from "./common";
import Viewer from "./Viewer.svelte";

export let video: string | undefined;

const updateInfo = debounce(
  async (video: string) => {
    loading = true;

    const location = new URL(apiLocation);
    location.pathname = "/watch";
    location.searchParams.append("id", video);

    const response = await window.fetch(location);
    videoInfo = JSON.parse(await response.text());

    loading = false;
  },
  750,
  {
    leading: true,
  }
);

// let videoInfo: VideoInfo | undefined = {
//   audio: "http://localhost:8000/audio",
//   channel: "On Demand News",
//   chapters: [
//     { end_time: 91.0, start_time: 39.0, title: "Oranges" },
//     { end_time: 127.0, start_time: 91.0, title: "ISIS Fighters" },
//     { end_time: 136.0, start_time: 127.0, title: "No Collusion" },
//     { end_time: 157.0, start_time: 136.0, title: "No Pressure" },
//     { end_time: 192, start_time: 157.0, title: "No Responsibility" },
//   ],
//   duration: "3:12",
//   title: "Donald Trump\u2019s Most Hilarious Moments from 2019",
//   video: "http://localhost:8000/video",
// };
let videoInfo: VideoInfo | undefined
let loading = false;

$: {
  if (!video) {
    break $;
  }
  videoInfo = undefined;
  updateInfo.cancel();
  updateInfo(video);
}
</script>

{#if loading || videoInfo !== undefined}
  <div class="flex flex-[2]">
    {#if loading}
      <h4 class="text-xl font-semibold m-auto">Loading...</h4>
    {:else if !loading && videoInfo !== undefined}
      {#key videoInfo}
        <Viewer
          {videoInfo}
          on:complete={() => {
            video = undefined;
            videoInfo = undefined
          }}
        />
      {/key}
    {/if}
  </div>
{/if}
