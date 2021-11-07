<script lang="ts">
import { onMount } from 'svelte';
import type { TreeLibrary } from "./parse_tree";
import  SvgNode from "./svg_utils"

    export let tree_library : TreeLibrary
	export let root_id : string

	let node_map : Map<string, SvgNode> = null

	$: {
		root_id;
		node_map = SvgNode.generateTree(tree_library, root_id)
	}

	onMount(() => {
	})
	function onClick() {
	}
// 	console.log(text1.getComputedTextLength())
</script>

{#if node_map}
<svg height = "300px">
	{#each Array.from(node_map.values()) as node}
	    <text class="node" x={node.x} y={node.y}>{node.text}</text>		
	{/each}
</svg>
{/if}

<style>
	.node {
			font-family: Arial, Helvetica, sans-serif;
			font-size: 1em;
			font-style: normal;
			user-select: none;
	}
	/* .word {
		font-family: "Times New Roman", Times, serif;
		font-size: 1em;
		font-style: normal;
		user-select: none;
	} */
</style>
