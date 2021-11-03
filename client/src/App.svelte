<script lang="ts">
	export let sentence: string
	let message: string = ''

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
		message = response.data.text
	}

	//$: { console.log() }
</script>

<main>
	<h3>Enter sentence:</h3>
	<form on:submit|preventDefault={processInput}>
		<input type="text" size="50" bind:value={sentence}><br/>
		
		<button type="submit">Parse</button>
		<!-- <button class="help" on:click={()=>getModal('parse_modal').open()}>?</button> -->
	</form>
	<p>{message}</p>
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