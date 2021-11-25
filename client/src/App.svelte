<script lang="ts">
import { onDestroy, onMount } from "svelte";

	
import ParseTable from "./ParseTable.svelte";
import  { TreeLibrary } from "./parse_tree";
import SvgTree from "./SvgTree.svelte";

	let client_id : number

	let sentence: string
	let message: string = ''
	let tree_library : TreeLibrary
	let parse_root : Array<string> = null
	let guess_root : string = 'VP'
	let unknown : string = ''
	let has_next_parse = true

		onMount(async () => {
			console.log('Mounting')	
			fetch('./get-client-id', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
				}
                // },
                // body: JSON.stringify({
                //     text: sentence,
				// 	guess : guess_root
				// })
			})
		.then((response) => response.json())
		.then((data) => data as Object)
		.then((data) => client_id = Number(data['client_id']))
		})

	function request_parse(text: string) :Promise<Object> {
		return fetch('./parse', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    text: sentence,
					guess : guess_root,
					client_id : client_id
				})
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
			has_next_parse = response.has_next.toLowerCase() == 'true'
		} else {
			message = 'Server error:' + response.error_msg
		}
		//console.log(tree_library)
	}

	async function nextParse() {
		let response
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
			has_next_parse = response.has_next.toLowerCase() == 'true'
			parse_root = tree_library.root_list[tree_library.root_list.length-1]//parse_list[0]
		} else {
			message = 'Server error: ' + response.error_msg
		}
	}

	async function request_next(path:string) :Promise<Object> {
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

	async function getGuess() {
		let response
		message = 'waiting for guess...'
		await request_next('./guess-parse')
		.then(value =>  response = value)
		.catch(reason => response = reason)
		// console.log(JSON.stringify(response))
		if(!response.error_msg) {
			tree_library = new TreeLibrary(response.data.nodes, response.data.table,
				response.data.root_list, response.data.guess_list)
			message = 'Guess OK'
			unknown = response.unknown
			parse_root = tree_library.root_list[tree_library.root_list.length-1]//parse_list[0]
		} else {
			message = 'Server error: ' + response.error_msg
		}
	}

</script>

<svelte:head>
	<title>CYK Parser</title>
	<html lang="en" />
</svelte:head>

<main>
	<h3>Enter sentence:</h3>
	<form on:submit|preventDefault={processInput}>
		<input type="text" size="50" bind:value={sentence}><br/>
		
		<button type="submit">Parse</button>
		<!-- <button class="help" on:click={()=>getModal('parse_modal').open()}>?</button> -->
	</form>
	<p>{message}</p>
	{#if unknown}
		<p>
		<b>Unknown words:</b> {unknown} <br/>
		<button on:click={getGuess}>Guess Parse</button>
			for root <input type="text" size="6" bind:value={guess_root}>
		</p>
		or...
	{/if}
	
	{#if tree_library}
	<button disabled={!has_next_parse} on:click={nextParse}>
		{has_next_parse ? 'Next Parse' : 'Out of parses'}</button><br/>		
	{/if}

	{#if tree_library }
		<SvgTree tree_library={tree_library} bind:parse_root={parse_root} />
	{/if}

	{#if tree_library}
		<ParseTable bind:tree_library={tree_library} bind:parse_root={parse_root} />
	{/if}


	</main>

<style>
	main {
		text-align: left;
		padding: 1em;
		max-width: 240px;
		margin: 0 auto;
	}
	
	@media (min-width: 640px) {
		main {
			max-width: none;
		}
	}
</style>