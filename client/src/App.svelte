<script lang="ts">
	
import ParseTable from "./ParseTable.svelte";
import  { TreeLibrary } from "./parse_tree";
import SvgTree from "./SvgTree.svelte";

	export let sentence: string
	let message: string = ''
	let tree_library : TreeLibrary

	function request(text: string) :Promise<Object> {
		return fetch('./parse', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    text: sentence})
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
			tree_library = new TreeLibrary(response.data.nodes, response.data.table)
			message = 'Parse OK'
		} else {
			message = response.error_msg
		}
		console.log(tree_library)
	}

	function onDivClick() {

	}
	let selected;
	$: selected = tree_library ? tree_library.selected : -1
</script>

<main>
	<h3>Enter sentence:</h3>
	<form on:submit|preventDefault={processInput}>
		<input type="text" size="50" bind:value={sentence}><br/>
		
		<button type="submit">Parse</button>
		<!-- <button class="help" on:click={()=>getModal('parse_modal').open()}>?</button> -->
	</form>
	<p>{message}</p>

	{#if tree_library}
		<ParseTable bind:tree_library={tree_library} />
	{/if}

	{#if tree_library && tree_library.selected != undefined }
		<SvgTree bind:tree_library={tree_library} bind:root_id={tree_library.selected} />
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