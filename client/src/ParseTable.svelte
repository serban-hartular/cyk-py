<script lang="ts">

	import type { TreeLibrary } from "./parse_tree";
	export let tree_library : TreeLibrary
	import Square from "./ParseTableSquare.svelte";

</script>

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

<style>
	table, td {
  		border: 1px solid black;
		vertical-align: top;
	}

	table {
  		border-collapse: collapse;
	}
</style>