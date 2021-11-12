<script lang="ts">
import { afterUpdate, onMount } from 'svelte';
import { listen_dev } from 'svelte/internal';
import type { TreeLibrary, Node } from "./parse_tree";
import  SvgNode, { SvgMap, Line } from "./svg_utils"

    export let tree_library : TreeLibrary
	let roots = tree_library.root_list[0] 
	console.log('roots = ' + roots)

	let node_map : SvgMap = new SvgMap(tree_library, roots)
	let node_array : Array<SvgNode>
	let line_array : Array<Line>
		node_array = Array.from(node_map.values())
		line_array = node_map.lines
		onNodeClick(roots[0])

	let clicked : Node = null
	let clicked_data : Map<string, string> = null

	$: { //for new parse
		tree_library;
		console.log('tree_library')
	}

	$: {
		node_map;
		console.log('node_map')
	}

	// $: {
	// 	roots; 
		// console.log('if roots...')
		// if(roots != node_map.root_list) {
			// console.log('roots -- new node map')
			// node_map  = new SvgMap(tree_library, roots)
			// node_array = Array.from(node_map.values())
			// line_array = node_map.lines
			// console.log('roots -- done')
			//node_map = node_map
			// }
	// }

	// $:{
	// 	console.log('node_array')
	// 	node_array = Array.from(node_map.values())
	// 	line_array = node_map.lines
	// }

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
		console.log('onmount')
		updateCoordinates()
		node_map = node_map;
	})

	afterUpdate(() => {
		console.log('afterupdate')
		updateCoordinates()
		node_map = node_map;
		node_array = node_array
		line_array = node_map.lines
	})

	function onNodeClick(id : string) {
		console.log('click ' + id)
		if(id.startsWith('w')) id = id.substring(1)
			clicked = tree_library.get(id)
		// node_map = node_map //this triggers everything
		if(clicked == undefined) {
			clicked = null
			console.log('Error, unknown node id ' + id)
		}
		clicked_data = new Map<string, string>()
		for(let entry in clicked.data) {
			let key = entry
			let data_array : any = clicked.data[key]
			let data = data_array.join(',')
			if(key != 'type' && key != 'form') {
				clicked_data.set(key, data)
			}
		}
	}

	function root_to_str_rep(root : Array<string>) : string {
		let types : string = root.map(id => tree_library.get(id).type).join(',')
		return types
	}

	function onParseClick(new_roots : Array<string>) {
		console.log('roots -- new node map')
		node_map  = new SvgMap(tree_library, new_roots)
		node_array = Array.from(node_map.values())
		line_array = node_map.lines
		console.log('roots -- done')
		onNodeClick(new_roots[0])
	}


</script>

<table>
	<tr><td colspan="2">
		<!-- Table of possible parses -->
		Possible parses:
		<table><tr>
			{#each tree_library.root_list as root}
				<td on:click={()=>onParseClick(root)}>
					{root_to_str_rep(root)}
				</td>
			{/each}
		</tr></table>
	</td></tr>
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
