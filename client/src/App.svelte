<script lang="ts">
	
import ParseTable from "./ParseTable.svelte";
import  { TreeLibrary } from "./parse_tree";
import SvgTree from "./SvgTree.svelte";

	let sentence: string
	let message: string = ''
	let tree_library : TreeLibrary
	let parse_root : Array<string> = null
	let guess_root : string = 'VP'

	function request(text: string) :Promise<Object> {
		return fetch('./parse', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    text: sentence,
					guess : guess_root
				})
			})
		.then((response) => response.json())
		.then((data) => data as Object)
	}
	
	async function processInput() {
        //console.log(lang_value)
        if(!sentence || sentence.trim() == '')
            return
		let response
		message = 'Parse requested'
		await request(sentence)
		.then(value =>  response = value)
		.catch(reason => response = reason)
		// console.log(JSON.stringify(response))
		if(!response.error_msg) {
			tree_library = new TreeLibrary(response.data.nodes, response.data.table,
				response.data.root_list, response.data.guess_list)
			message = 'Parse OK'
		} else {
			message = response.error_msg
		}
		//console.log(tree_library)
	}

	function onDivClick() {

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
		
		<button type="submit">Parse</button><br/>
		Guess: <input type="text" bind:value={guess_root}>
		<!-- <button class="help" on:click={()=>getModal('parse_modal').open()}>?</button> -->
	</form>
	<p>{message}</p>

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