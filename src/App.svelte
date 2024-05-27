<script lang="ts">
import { setContext } from "svelte";
import { apiLocation, knownTags } from "./common";
import Results from "./components/Results.svelte";
import ViewerContainer from "./components/Viewer/ViewerContainer.svelte";
import { Context, iconKey } from "./icons/icon-context";

window.fetch(`${apiLocation}/tags`).then(async (response) => {
  knownTags.set(JSON.parse(await response.text()));
});

setContext<Context>(iconKey, {
  width: 24,
  height: 24,
});

let selected: string | undefined = undefined;
</script>

<main class="flex">
  <Results on:select={(e) => (selected = e.detail)} />
  <ViewerContainer video={selected} />
</main>
