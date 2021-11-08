<script lang="ts">
import { afterUpdate, onMount } from 'svelte';
import type { TreeLibrary } from "./parse_tree";
import  SvgNode, { SvgMap, Line } from "./svg_utils"

    export let tree_library : TreeLibrary
	export let root_id : string

	let node_map : SvgMap = new SvgMap(tree_library, root_id)//SvgNode.generateTree(tree_library, root_id)
	let node_array : Array<SvgNode>
	let line_array : Array<Line>

	$: {
		if(root_id != node_map.root_id) {
			node_map  = new SvgMap(tree_library, root_id)
			console.log('new node_map !')
		}
	}
	$:{
		// node_map;
		node_array = Array.from(node_map.values())
		line_array = node_map.lines
		console.log('node_map changed!')
	}

	function updateCoordinates() {
		for(let node of node_map.values()) {
			let svg_text : any = document.getElementById(node.id)
			let bbox = svg_text.getBBox()
			node.w = bbox.width
			node.h = bbox.height
		}
		node_map.updateCoordinates()
	}

	onMount(() => {
		// for(let line of line_array) {
		// 	line.x1 += 10
		// }
		console.log('doing onMount')
		updateCoordinates()
		node_map = node_map
	})

	afterUpdate(() => {
		console.log('doing afterUpdate')
		updateCoordinates()
		node_map = node_map
	})

	function onClick() {
	}
// 	console.log(text1.getComputedTextLength())

	let width : number = 300

</script>

{#if node_map}
<svg height = "300px">
	{#each node_array as node}
	    <text class="node" id={node.id} x={node.x} y={node.y}>{node.text}</text>		
	{/each}
	{#each line_array as line, i(i) }
		<line x1={line.x1} y1={line.y1} x2={line.x2} y2={line.y2} stroke="black" />
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
