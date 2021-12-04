<script lang="ts">

	import type { TreeLibrary } from "./parse_tree";
	import Square from "./ParseTableSquare.svelte";

	export let tree_library : TreeLibrary
	export let selected_parse : Array<string>
	export let selected_node : string

</script>

	<table style="max-width: 1000px;">
		{#each tree_library.parse_table as row}
		<tr>
			{#each row as square}
			<td>
				<Square bind:tree_library={tree_library} bind:id_list={square}
				bind:selected_parse={selected_parse} bind:selected_node={selected_node}/>
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

<style>
	td {
  		border: 1px solid black;
		vertical-align: top;
	}

	table {
  		border-collapse: collapse;
	}
</style>