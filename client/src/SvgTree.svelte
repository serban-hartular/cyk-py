<script lang="ts">
import { afterUpdate, onMount } from 'svelte';
import { root_to_str_rep, score2string } from './common_utils';
import type { TreeLibrary, Node } from "./parse_tree";
import  SvgNode, { SvgMap, Line } from "./svg_utils"

    export let tree_library : TreeLibrary
	export let parse_root : Array<string>
	let parse_list : Array<Array<string>> = tree_library.root_list
	if(parse_list.length > 0 && parse_list[0].length == 1) { //complete parse
		parse_root = parse_list[parse_list.length - 1]
	} else { //fragmented parse
		parse_root = parse_list[0]
	}
	let guess_list = tree_library.guess_list
	let node_map : SvgMap = new SvgMap(tree_library, parse_root)
	let node_list : Array<SvgNode> = node_map.getNodes()
	let line_list : Array<Line> = node_map.getLines()
	let clicked_id : string = null
	let clicked_data : Map<string, string> = null
	onNodeClick(parse_root[0])

	let tree_library_ref = tree_library


	$: { 	tree_library;
			// console.log('lib changed')
			if(tree_library == tree_library_ref) {
				// console.log('dummy')
			} else {
				// console.log('not dummy')
				parse_list = tree_library.root_list
				//if(!parse_root)
					parse_root = parse_list[0]
				guess_list = tree_library.guess_list
				if(guess_list.length > 0) {
					parse_root = [guess_list[guess_list.length-1]]
				} else if(parse_list.length > 0 && parse_list[0].length == 1) { //complete parse
					parse_root = parse_list[parse_list.length - 1]
				} else { //fragmented parse
					parse_root = parse_list[0]
				}

				tree_library_ref = tree_library
		}
	}

	$: {
		if(node_map.root_list == parse_root) {
			// console.log('Dummy node map change')
		} else {
			// console.log('node_map <-  parse')
			node_map = new SvgMap(tree_library, parse_root)
			onNodeClick(parse_root[0])
		}	
	}

	$: {
//		console.log('node_map change')
		line_list = node_map.getLines()
		node_list = node_map.getNodes()

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
	// 	console.log('onmount')
	// 	updateCoordinates()
	// 	node_map = node_map;
	// })

	afterUpdate(() => {
		// console.log('afterUpdate')
		updateCoordinates()
		line_list = line_list
		node_list = node_list
	})

	function onNodeClick(id : string) {
		if(id.startsWith('w')) id = id.substring(1)
		clicked_id = id
		let clicked = tree_library.get(id)
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
			//if(key != 'type' && key != 'form') {
			clicked_data.set(key, data)
			//}
		}
	}


	function onParseClick(new_roots : Array<string>) {
		parse_root = new_roots
	}

	function rule2string(id : string) {
		let rule = tree_library.get(id).rule
		if(rule.length < 24) {
			rule = rule.replaceAll('\t', ' ')
		} else {
			rule = rule.replaceAll('\t', '\n\t')
		}
		return rule
	}

	function svgTextClass(id : string) : string {
		id = id.replaceAll('w', '')
		let n = tree_library.get(id)
		if(!n.guess) {
			return clicked_id == n.id ? "selected_node" : "node"
		} else {
			return clicked_id == n.id ? "selected_guess" : "guess"
		}
	}

</script>

{#if parse_list}
		<!-- Table of possible parses -->
		<u>Possible parses:</u>
		<table><tr>
			{#each parse_list as root}
				<td on:click={()=>onParseClick(root)}>
					{#if root == parse_root}
						<b>{root_to_str_rep(root, tree_library)}</b>	
					{:else}
					{root_to_str_rep(root, tree_library)}
					{/if}
					<br>
					({score2string(root, tree_library)})
				</td>
			{/each}
		</tr></table>
		{#if guess_list.length > 0}
		<u>Possible guesses:</u>
		{/if}
		<table><tr>
			{#each guess_list as guess}
				<td on:click={()=>onParseClick([guess])}>
					{#if parse_root.includes(guess)}
						<b>{root_to_str_rep([guess], tree_library)}</b>	
					{:else}
					{root_to_str_rep([guess], tree_library)}
					{/if}
					<br>
					({score2string([guess], tree_library)})
				</td>
			{/each}
		</tr></table>
{/if}
<table>
	<tr><td style="min-width: 250px;">
{#if node_map}
<svg height={node_map.height} width={node_map.width + 50}>
	{#each node_list as node}
	    <text on:click={()=>onNodeClick(node.id)} class={svgTextClass(node.id)} 
			id={node.id} x={node.x} y={node.y}>{node.text}</text>		
	{/each}
	{#each line_list as line }
		<line x1={line.x1} y1={line.y1} x2={line.x2} y2={line.y2} stroke="black" />
		{#if line.deprel}
			<text class="deprel" x={line.x2} y={(line.y1 + line.y2)/2}>{line.deprel}</text>
		{/if}
	{/each}
</svg>
{/if}
</td>
<td style="border-left: 1px solid;">
{#if clicked_id && clicked_id != undefined}
<p><b>{tree_library.get(clicked_id).type}</b>: <i>"{tree_library.get(clicked_id).form}"</i></p>
	{#if tree_library.get(clicked_id).guess}
		<p>guess: {tree_library.get(clicked_id).guess}</p>		
	{/if}
<p style="column-count: {clicked_data.size > 5 ? 2 : 1}; width: fit-content;">
{#each Array.from(clicked_data.keys()) as key}
	{key}: {clicked_data.get(key)}<br/>
{/each}
</p>
Rule: <pre>"{rule2string(clicked_id)}"</pre>
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
	.selected_node {
		font-family: Arial, Helvetica, sans-serif;
			font-size: 1em;
			font-style: normal;
			user-select: none;
			font-weight: bold;
	}
	.guess {
			font-family: Arial, Helvetica, sans-serif;
			font-size: 1em;
			font-style: italic;
			user-select: none;
	}
	.selected_guess {
		font-family: Arial, Helvetica, sans-serif;
			font-size: 1em;
			font-style: italic;
			user-select: none;
			font-weight: bold;
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
