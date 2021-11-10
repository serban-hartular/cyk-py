<script lang="ts">
import { afterUpdate, onMount } from 'svelte';
import { listen_dev } from 'svelte/internal';
import type { TreeLibrary, Node } from "./parse_tree";
import  SvgNode, { SvgMap, Line } from "./svg_utils"

    export let tree_library : TreeLibrary
	export let root_id : string

	let node_map : SvgMap = new SvgMap(tree_library, root_id)//SvgNode.generateTree(tree_library, root_id)
	let node_array : Array<SvgNode>
	let line_array : Array<Line>

	let clicked : Node = null
	let clicked_data : Map<string, string> = null

	$: {
		if(root_id != node_map.root_id) {
			node_map  = new SvgMap(tree_library, root_id)
			//console.log('new node_map !')
		}
	}
	$:{
		// node_map;
		node_array = Array.from(node_map.values())
		line_array = node_map.lines
		//console.log('node_map changed!')
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

	// onMount(() => {
	// 	// for(let line of line_array) {
	// 	// 	line.x1 += 10
	// 	// }
	// 	//console.log('doing onMount')
	// 	updateCoordinates()
	// 	node_map = node_map
	// })

	afterUpdate(() => {
		//console.log('doing afterUpdate')
		updateCoordinates()
		node_map = node_map
		//console.log(line_array)
	})

	function onNodeClick(id : string) {
		if(id.startsWith('w')) id = id.substring(1)
		clicked = tree_library.get(id)
		if(clicked == undefined) {
			clicked = null
			console.log('Error, unknown node id ' + id)
		}
		clicked_data = new Map<string, string>()
		console.log(clicked.data)
		for(let entry in clicked.data) {
			console.log(entry)
			let key = entry
			let data_array : any = clicked.data[key]
			let data = data_array.join(',')
			if(key != 'type' && key != 'form') {
				clicked_data.set(key, data)
			}
		}
	}
// 	console.log(text1.getComputedTextLength())


</script>

<table>
	<tr><td>
{#if node_map}
<svg height={node_map.height} width={node_map.width}>
	{#each node_array as node}
	    <text on:click={()=>onNodeClick(node.id)} class="node" id={node.id} x={node.x} y={node.y}>{node.text}</text>		
	{/each}
	{#each line_array as line }
		<line x1={line.x1} y1={line.y1} x2={line.x2} y2={line.y2} stroke="black" />
		{#if line.deprel}
			<text class="deprel" x={line.x2} y={(line.y1 + line.y2)/2}>{line.deprel}</text>
		{/if}
	{/each}
</svg>
{/if}
</td>
<td>
{#if clicked}
<b>{clicked.type}</b>: <i>"{clicked.form}"</i><br/>
{#each Array.from(clicked_data.keys()) as key}
	{key}: {clicked_data.get(key)}<br/>
{/each}
Rule: "{clicked.rule}"
{/if}
</td></tr>
</table>

<style>
	.node {
			font-family: Arial, Helvetica, sans-serif;
			font-size: 1em;
			font-style: normal;
			user-select: none;
	}
	.deprel {
		font-family: "Times New Roman", Times, serif;
		font-size: 0.8em;
		font-style: italic;
		user-select: none;
	}
	td {
		padding: 10px;
		vertical-align: top;
	} 
</style>
