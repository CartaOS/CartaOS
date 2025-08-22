<script lang="ts">
	import { invoke } from '@tauri-apps/api/core';
	import { onMount } from 'svelte';

	let apiKey = $state('');
	let baseDir = $state('');
	let statusMessage = $state('');
	let isError = $state(false);
	let isLoading = $state(false);
	let isValid = $derived(apiKey.trim().length > 0);

	interface AppSettings {
		api_key: string;
		base_dir: string;
	}

	async function loadSettings() {
		isLoading = true;
		statusMessage = 'Loading settings...';
		isError = false;
		try {
			const settings: AppSettings = await invoke('load_settings');
			apiKey = settings.api_key;
			baseDir = settings.base_dir;
			statusMessage = 'Settings loaded.';
		} catch (error) {
			console.error('Error loading settings:', error);
			statusMessage = `Error loading settings: ${error}`;
			isError = true;
		} finally {
			isLoading = false;
		}
	}

	async function saveSettings() {
		isLoading = true;
		statusMessage = 'Saving settings...';
		isError = false;
		if (!isValid) {
			isLoading = false;
			statusMessage = 'API Key is required.';
			isError = true;
			return;
		}
		try {
			await invoke('save_settings', { api_key: apiKey, base_dir: baseDir });
			statusMessage = 'Settings saved successfully!';
		} catch (error) {
			console.error('Error saving settings:', error);
			statusMessage = `Error saving settings: ${error}`;
			isError = true;
		} finally {
			isLoading = false;
		}
	}

	onMount(() => {
		loadSettings();
	});
</script>

<div class="settings-view space-y-4 rounded-lg bg-white p-4 shadow-md">
	<h2 class="text-2xl font-bold text-gray-800">Settings</h2>
	<p class="text-gray-600">Manage your API Key and Obsidian Vault Path.</p>

	<div class="space-y-2">
		<label for="apiKey" class="block text-sm font-medium text-gray-700"
			>API Key (Google Gemini):</label
		>
		<input
			type="password"
			id="apiKey"
			bind:value={apiKey}
			class="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-blue-500 focus:outline-none focus:ring-blue-500 sm:text-sm"
			placeholder="Your API Key"
			aria-invalid={!isValid}
			disabled={isLoading}
		/>
		{#if !isValid}
			<p class="text-sm text-red-600">API Key is required.</p>
		{/if}
	</div>

	<div class="space-y-2">
		<label for="baseDir" class="block text-sm font-medium text-gray-700">Obsidian Vault Path:</label
		>
		<input
			type="text"
			id="baseDir"
			bind:value={baseDir}
			class="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-blue-500 focus:outline-none focus:ring-blue-500 sm:text-sm"
			placeholder="Ex: /home/user/VaultObsidian"
			disabled={isLoading}
		/>
	</div>

	<button
		onclick={saveSettings}
		class="flex w-full justify-center rounded-md border border-transparent bg-blue-600 px-4 py-2 text-sm font-medium text-white shadow-sm hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
		disabled={isLoading || !isValid}
	>
		{#if isLoading}
			Saving...
		{:else}
			Save Settings
		{/if}
	</button>

	{#if statusMessage}
		<p
			role="status"
			aria-live="polite"
			aria-atomic="true"
			class="mt-2 text-sm {isError ? 'text-red-600' : 'text-green-600'}"
		>
			{statusMessage}
		</p>
	{/if}
</div>

<style>
</style>
