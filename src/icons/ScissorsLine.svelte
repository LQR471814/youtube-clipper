<script lang="ts">
import { getContext } from "svelte";
import { Context, iconKey } from "./icon-context";

const context = getContext<Context>(iconKey);

export let className = context.className;
export let width = context.width;
export let height = context.height;
export let x = context.x;
export let y = context.y;
</script>

<svg
  class={className}
  viewBox="0 0 24 24"
  style={`width: ${width}px; height: ${height}px;`}
  {x}
  {y}
>
  <path fill="none" d="M0 0h24v24H0z"></path><path d="M9.446 8.032L12 10.586l6.728-6.728a2 2 0 0 1 2.828 0l-12.11 12.11a4 4 0 1 1-1.414-1.414L10.586 12 8.032 9.446a4 4 0 1 1 1.414-1.414zm5.38 5.38l6.73 6.73a2 2 0 0 1-2.828 0l-5.317-5.316 1.415-1.415zm-7.412 3.174a2 2 0 1 0-2.828 2.828 2 2 0 0 0 2.828-2.828zm0-9.172a2 2 0 1 0-2.828-2.828 2 2 0 0 0 2.828 2.828z"></path>
</svg>
