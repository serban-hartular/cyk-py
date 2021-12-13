<script lang="ts">
import { onDestroy, onMount } from "svelte";
import Grammar from "./Grammar.svelte";

	
import ParseTable from "./ParseTable.svelte";
import  { TreeLibrary } from "./parse_tree";
import SvgTree from "./SvgTree.svelte";
import { root_to_str_rep, score2string } from "./common_utils"

	let client_id : number
	let grammar : Array<string>
	let grammar_change : boolean = false

	let sentence: string
	let message: string = ''
	let tree_library : TreeLibrary
	let parse_list : Array<Array<string>> = null
	let guess_list : Array<string> = null 
	let selected_parse : Array<string> = null
	let selected_node : string = null
	let guess_root : string = 'VP'
	let unknown : string = ''
	let has_next_parse = true
	let has_next_guess = true
	let no_new_parses = false;
	let no_new_guesses = false;

	// Server-client communication

		onMount(async () => {
			console.log('Mounting')	
			fetch('./get-client-id', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
				}
			})
		.then((response) => response.json())
		.then((data) => data as Object)
		.then((data) => {
			client_id = Number(data['client_id']);
			grammar = data['grammar'].map((rule) => rule.length > 50 ? 
				rule.replaceAll(/\t+/g, '\n\t') : rule.replaceAll(/\t+/g, ' '))
				// console.log(client_id, grammar)
			return data
		})
		// grammar = data['grammar']
		// 
	})


	function request_parse(text: string) :Promise<Object> {
		let body = { 	text: sentence,
						guess : guess_root,
						client_id : client_id
		}
		if(grammar_change) {
			body['grammar'] = grammar.map((text) => text.replaceAll(/\s+/g, ' '))
		}

		return fetch('./parse', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(body)
			})
		.then((response) => response.json())
		.then((data) => data as Object)
	}
	
	async function processInput() {
        console.log(client_id)
        if(!sentence || sentence.trim() == '')
            return
		let response
		message = 'waiting for parse...'
		await request_parse(sentence)
		.then(value =>  response = value)
		.catch(reason => response = reason)
		// console.log(JSON.stringify(response))
		if(!response.error_msg) {
			tree_library = new TreeLibrary(response.data.nodes, response.data.table,
				response.data.root_list, response.data.guess_list)
			message = 'Parse OK'
			unknown = response.unknown
			has_next_parse = response.has_next_parse.toLowerCase() == 'true'
			parse_list = tree_library.root_list
			guess_list = tree_library.guess_list
		} else {
			message = 'Server error:' + response.error_msg
		}
		grammar_change = false
	}

	async function nextParse() {
		let response
		let old_list_len = parse_list.length
		message = 'waiting for parse...'
		await request_next('./next-parse')
		.then(value =>  response = value)
		.catch(reason => response = reason)
		// console.log(JSON.stringify(response))
		if(!response.error_msg) {
			tree_library = new TreeLibrary(response.data.nodes, response.data.table,
				response.data.root_list, response.data.guess_list)
			message = 'Parse OK'
			unknown = response.unknown
			has_next_parse = response.has_next_parse.toLowerCase() == 'true'
			selected_parse = tree_library.root_list[tree_library.root_list.length-1]//parse_list[0]
			parse_list = tree_library.root_list
			guess_list = tree_library.guess_list
			no_new_parses = (parse_list.length <= old_list_len)
		} else {
			message = 'Server error: ' + response.error_msg
		}
	}

	async function request_next(path:string) :Promise<Object> {
		let body = { guess : guess_root, client_id : client_id }
		return fetch(path, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
					guess : guess_root,
					client_id : client_id
				})
			})
		.then((response) => response.json())
		.then((data) => data as Object)
	}

	async function getGuess(path : string) {
		let response
		let old_list_len = guess_list.length
		message = 'waiting for guess...'
		// let path = ''
		// if(tree_library.guess_list.length == 0)
		// 	path = './guess-parse'
		// else
		// 	path = './next-guess'
		await request_next(path)
		.then(value =>  response = value)
		.catch(reason => response = reason)
		// console.log(JSON.stringify(response))
		if(!response.error_msg) {
			tree_library = new TreeLibrary(response.data.nodes, response.data.table,
				response.data.root_list, response.data.guess_list)
			message = 'Guess done'
			unknown = response.unknown
			selected_parse = tree_library.root_list[tree_library.root_list.length-1]//parse_list[0]
			has_next_guess = response.has_next_guess.toLowerCase() == 'true'
			parse_list = tree_library.root_list
			guess_list = tree_library.guess_list
			if(guess_list.length > 0) {
				selected_parse = [guess_list[guess_list.length-1]]
				selected_node = selected_parse[0]
			}
			no_new_guesses = (guess_list.length <= old_list_len)
		} else {
			message = 'Server error: ' + response.error_msg
		}
	}

	// GUI Management

	function onParseClick(new_roots : Array<string>) {
		selected_parse = new_roots
	}

</script>

<svelte:head>
	<title>CYK Parser</title>
	<html lang="en" />
</svelte:head>

<main>
	<div class="side">
		<h4 style="text-indent: 10px">CYK Parser Demo</h4>
		<ul>
			<li><a href="#top">Top of Page</a></li>
			{#if tree_library}
			<li><a href="#parse_table">Parse Table</a></li>
			<li><a href="#grammar">Grammar Editor</a></li>
			{:else}
			<li><span style="color:grey">Parse Table</span></li>
			<li><span style="color:grey">Grammar Editor</span></li>
			{/if}
			
		</ul>
	</div>
	<div class="main">
	<h3>Enter sentence:</h3>
	<!-- <form on:submit|preventDefault={processInput}> -->
		<table>
		<tr><td colspan="2">
			<input type="text" size="75" bind:value={sentence} 
				on:keypress={e => {if (e.key == "Enter") processInput()} } >
		</td></tr>
		<tr>
		<td><button on:click={processInput}>Parse</button> {message}</td>
		{#if unknown}
		<td style="text-align: right;">
		<button on:click={() => getGuess('./guess-parse')}>Guess Parse</button>
			for root <input type="text" size="6" bind:value={guess_root}>
		</td>
		{/if}
		</tr>
		</table>
		<!-- <button class="help" on:click={()=>getModal('parse_modal').open()}>?</button> -->
	<!-- </form> -->

	{#if unknown}
	<b>Unknown words:</b> {unknown} <br/>
	{/if}

	{#if parse_list}
		<!-- Table of possible parses -->
		<table><tr>
			<td class="parses">	<button disabled={!has_next_parse} style="width:min-content" on:click={nextParse}>
				{!has_next_parse ? 'Parses exhausted' : (no_new_parses ? 'Try again' : 'Next parse')}</button>	
			</td>
			{#each parse_list as root}
				<td class="parses" on:click={()=>onParseClick(root)}>
					{#if root == selected_parse}
						<b>{root_to_str_rep(root, tree_library)}</b>	
					{:else}
					{root_to_str_rep(root, tree_library)}
					{/if}
					<br>
					({score2string(root, tree_library)})
				</td>
			{/each}
		</tr></table>
	{/if}

	{#if guess_list && guess_list.length > 0}
		<table><tr>
			<td class="parses">
				<button disabled={!has_next_guess} style="width:min-content" 
					on:click={() => getGuess('./next-guess')}>
				{!has_next_guess ? 'Out of guesses' : (no_new_guesses ? 'Try again' : 'Next Guess')}
				</button>
			</td>
			{#each guess_list as guess}
				<td on:click={()=>onParseClick([guess])} class="parses">
					{#if selected_parse.includes(guess)}
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


	{#if tree_library }
		<SvgTree tree_library={tree_library} bind:selected_parse={selected_parse} 
			bind:selected_node={selected_node} />
	{/if}

	{#if tree_library}
		<a class="inactive_link" name="parse_table">
		<h3>Parse Table</h3></a>
		<ParseTable bind:tree_library={tree_library} bind:selected_parse={selected_parse}
			bind:selected_node={selected_node} />
	{/if}

	{#if tree_library && grammar && grammar != undefined}
	<a name="grammar" class="inactive_link">
	<h3>Grammar Editor</h3></a>
		<Grammar bind:grammar = {grammar} bind:grammar_change={grammar_change} />
	{/if}
	
	</div>
	</main>

<style>
	main {
		text-align: left;
		padding: 1em;
		max-width: 240px;
		margin: 0 auto;
	}

	td.parses {
		padding-left: 10px;
	}
	
	.side {
		height: 100%; /* Full-height: remove this if you want "auto" height */
		width: 160px; /* Set the width of the sidebar */
		position: fixed; /* Fixed Sidebar (stay in place on scroll) */
		z-index: 1; /* Stay on top */
		top: 0; /* Stay at the top */
		left: 0;
		background-color: #EFEFEF; 
  		overflow-x: hidden; /* Disable horizontal scroll */
  		padding-top: 20px;
	}
	.side a {
		/* padding: 6px 8px 6px 16px; */
		text-decoration: none;
		/* font-size: 25px; */
		color: black;
		display: block;
	}

	.main {
		margin-left: 160px; /* Same as the width of the sidebar */
  		/* padding: 0px 10px; */
	}

	@media (min-width: 640px) {
		main {
			max-width: none;
		}
	}
	.inactive_link {
		pointer-events: none;
		cursor: default;
		color: black;
	}
</style>