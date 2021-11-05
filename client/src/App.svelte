<script lang="ts">
	
	import Square from "./Square.svelte";

	import  { TreeLibrary } from "./tree";

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
		console.log(JSON.stringify(response))
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
	<table >
		{#each tree_library.parse_table as row}
		<tr>
			{#each row as square}
			<td>
				<Square bind:tree_library={tree_library} bind:id_list={square} />
			</td>
			{/each}
		</tr>
		{/each}
		<!-- Insert bottom row with words -->
		<tr>
			{#each tree_library.parse_table[tree_library.parse_table.length-1] as word}
				<td>{tree_library.get(word[0]).form}</td>
			{/each}
		</tr>
	</table>
	{/if}

	</main>

<style>
	main {
		text-align: left;
		padding: 1em;
		max-width: 240px;
		margin: 0 auto;
	}

	table, td {
  		border: 1px solid black;
		vertical-align: top;
	}

	table {
  		border-collapse: collapse;
	}

	
	@media (min-width: 640px) {
		main {
			max-width: none;
		}
	}
</style>