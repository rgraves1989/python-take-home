<template>
	<div>
		<!-- User logged in. -->
		<template v-if="isLoggedIn">
			<h2 v-if="username !== ''">Welcome, {{username}} !</h2>
			<p><button @click="handleLogout">Logout</button></p>

			<!-- User needs to link GitHub account. -->
			<template v-if="github_access_token === ''">
				<button @click="handleLinkGithub">Link Your GitHub Account</button>
			</template>

			<!-- GitHub account is linked. -->
			<template v-else>

				<!-- User needs to select a repository. -->
				<template v-if="selected_repo_name === ''">
					<template v-if="repos.length > 0">
						<label>Select a repository: </label>
						<select v-model="selected_repo">
							<option v-for="(repo, index) in repos" :key="repo" :id="index" :value="{ name: repo.name, url: repo.url }">{{ repo.name }}</option>
						</select>
						<button @click="handleUserSaveSelectedRepo">Select</button>
					</template>

					<!-- No repositories to choose from. -->
					<template v-else>
						<i>No repositories to choose from.</i>
					</template>
				</template>

				<!-- User has already selected a repository. -->
				<template v-else>
					<p>Selected repository: <b>{{ selected_repo.name}}</b>, <a :href="selected_repo.url" target="_blank">API</a></p>
				</template>
			</template>
		</template>

		<!-- Not logged in. -->
		<template v-else>
			<button @click="handleLogin" :disabled="!Vue3GoogleOauth.isInit">Login</button>
		</template>
	</div>
</template>

<script>
	import { inject, toRefs } from 'vue';
	import axios from 'axios';
	
	export default {
		name: 'PythonTakeHome',
		props: {
			msg: String
		},

		/*********
		 *  Model
		 **/

		data() {
			return {
				isLoggedIn: false,
				uid: 0,
				username: '',
				github_access_token: '',
				repos: [],
				selected_repo: null,
				selected_repo_name: '',
				selected_repo_url: ''
			}
		},

		/**************
		 *  Reactivity
		 **/

		watch: {

			// When a GitHub access token is set, retreive the user's repos.
			github_access_token() {
				if(this.github_access_token !== '')
					this.handleGetUserRepos();
			}

		},

		/***********
		 *  Methods
		 **/

		methods: {

			// Handle login button.
			async handleLogin() {
				try {
					// Sign-in via Google.
					const googleUser = await this.$gAuth.signIn();
					if (!googleUser) {
						return null;
					}

					// Get basic user information.
					var user_profile = googleUser.getBasicProfile();
					var auth_response = googleUser.getAuthResponse();

					// Attempt to login / register the user on the backend.
					var login_response = await this.handleRestRequest('/google_login_callback', {
						'username': user_profile.getEmail(),
						'first_name': user_profile.VX,
						'last_name': user_profile.iW,
						'access_token': auth_response.access_token,
						'id_token': auth_response.id_token
					}, 'post');

					// Update the model.
					this.isLoggedIn = login_response.isLoggedIn;
					this.uid = login_response.uid;
					this.username = login_response.username;
					this.github_access_token = login_response.github_access_token;
					this.selected_repo = { 'name' : login_response.selected_repo_name, 'url': login_response.selected_repo_url };
					this.selected_repo_name = login_response.selected_repo_name;
					this.selected_repo_url = login_response.selected_repo_url;
				} catch (error) {
					console.error(error);
					return null;
				}
			},

			// Handle logout button.
			async handleLogout() {
				// Send logout request to server.
				await this.handleRestRequest('/logout', null, 'get');

				// Update the model.
				this.isLoggedIn = false;
				this.uid = 0
				this.username = '';
				this.github_access_token = '';
				this.repos = [];
				this.selected_repo = null;
				this.selected_repo_name = '';
				this.selected_repo_url = '';
			},

			// Can remove?
			/*
			async handleClickGetAuthCode(){
				try {
					this.authCode = await this.$gAuth.getAuthCode();
					console.log('authCode', this.authCode);
				} catch(error) {
					console.error(error);
					return null;
				}
			},

			// TODO
			async handleClickSignOut() {
				try {
					await this.$gAuth.signOut();
					console.log('isAuthorized', this.Vue3GoogleOauth.isAuthorized);
					this.user = '';
					this.authCode = '';
				} catch (error) {
					console.error(error);
					return null;
				}
			},

			// Can remove?
			handleClickDisconnect() {
				window.location.href = `https://www.google.com/accounts/Logout?continue=https://appengine.google.com/_ah/logout?continue=${window.location.href}`;
			},

			// Can remove?
			showAuthCode() {
				alert(this.authCode);
			},
			*/

			// Redirects the user to allow our app access to their GitHub account.
			handleLinkGithub() {
				window.location.href = 'https://github.com/login/oauth/authorize?client_id=241da044cc281f3964b0';
			},

			// Request user object & associated repos from GitHub API.
			async handleGetUserRepos() {
				var github_user_response = await this.handleAuthRequest('https://api.github.com/user', this.github_access_token);
				var github_user_repos_response = await this.handleAuthRequest(github_user_response['repos_url'], this.github_access_token);

				// Build the list of user repos from the API response.
				var user_repos = [];
				for(var i = 0; i < github_user_repos_response.length; i++) {
					user_repos.push({
						'name': github_user_repos_response[i].name,
						'url': github_user_repos_response[i].url
					});
				}

				// Update the model.
				this.repos = user_repos;
			},

			// Save the user's selected repository.
			async handleUserSaveSelectedRepo() {
				await this.handleRestRequest('/save_user_repo', {
					'name': this.selected_repo['name'],
					'url': this.selected_repo['url']
				}, 'post');

				// Update the model.
				this.selected_repo_name = this.selected_repo['name'];
				this.selected_repo_url = this.selected_repo['url'];
			},

			// Helper function for REST requests.
			async handleRestRequest(url, payload, method) {
				try {
					var response = null;
					if(method == 'get') {
						response = await axios.get(url);
					} else {
						response = await axios.post(url, payload);
					}
					return response.data;
				} catch(error) {
					console.error(error);
					return null;
				}
			},

			// Helper function for Auth token requests.
			async handleAuthRequest(url, access_token) {
				try {
					var response = await axios.get(url, {
						headers: {
							'Authorization': 'token ' + access_token
						}
					});
					return response.data;
				} catch(error) {
					console.log(error);
					return null;
				}
			}

		},

		/*********
		 *  Setup
		 **/

		setup(props) {
			const { isSignIn } = toRefs(props);
			const Vue3GoogleOauth = inject('Vue3GoogleOauth');
			const handleClickLogin = () => {};
			return {
				Vue3GoogleOauth,
				handleClickLogin,
				isSignIn,
			};
		}
	};
</script>

<style>
	button {
		display: inline-block;
		line-height: 1;
		white-space: nowrap;
		cursor: pointer;
		background: #fff;
		border: 1px solid #dcdfe6;
		color: #606266;
		-webkit-appearance: none;
		text-align: center;
		-webkit-box-sizing: border-box;
		box-sizing: border-box;
		outline: 0;
		margin: 0;
		-webkit-transition: 0.1s;
		transition: 0.1s;
		font-weight: 500;
		padding: 12px 20px;
		font-size: 14px;
		border-radius: 4px;
		margin-right: 1em;
	}
	button:disabled {
		background: #fff;
		color: #ddd;
		cursor: not-allowed;
	}

	select {
		display:  inline-block;
		line-height:  1;
		background:  #fff;
		border: 1px solid #dcdfe6;
		color: #606266;
		font-weight: 500;
		padding: 12px 20px;
		font-size: 14px;
		border-radius: 4px;
		margin-right: 1em;
	}
</style>