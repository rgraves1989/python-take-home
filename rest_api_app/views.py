import json
import requests

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from rest_api_app.models import UserGithubOauth, UserSelectGithubRepo

# Dummy password for gAuth created users.
STATIC_PASSWORD = 'static_password'

################
# View handlers
##

# Default view handler.
def main(request):
	return render(request, 'rest_api_app/main.html')

# View handler for GitHub OAuth.
def github_oauth_callback(request):
	if request.method == "GET":
		if has_fields(request.GET, ['code']):
			# Exchange the one-time code for an access token.
			access_token = get_github_access_token(request.GET['code'])

			# Persist the access token.
			if access_token is not None:
				user_github_oauth = UserGithubOauth.objects.create(uid = request.user.id, access_token = access_token)
				user_github_oauth.save()

	return redirect('')

# View handler for Google OAuth.
@csrf_exempt
def google_login_callback(request):
	response_data = {
		'isLoggedIn': False,
		'username': '',
		'uid': 0,
		'github_access_token': '',
		'selected_repo_name': '',
		'selected_repo_url': ''
	}

	if request.method == "POST":
		data = json.loads(request.body.decode('utf-8'))

		# Make sure all fields are present.
		if has_fields(data, ['username', 'first_name', 'last_name', 'access_token', 'id_token']):

			# Verify access and ID tokens.
			if not valid_google_auth(data['access_token'], data['id_token']):
				# Google OAuth not verified, terminate.
				logout(request)
				return JsonResponse(response_data)

			# Check if our user exists or not.
			user = authenticate(username = data['username'], password = STATIC_PASSWORD)
			if user is None:
				# Register a new user.
				user = User.objects.create_user(data['username'], data['username'], STATIC_PASSWORD, first_name = data['first_name'], last_name = data['last_name'])
				user.save()

			# Login
			login(request, user)

			# Build login response.
			response_data['isLoggedIn'] = True
			response_data['username'] = user.get_username()
			response_data['uid'] = user.id
			response_data['github_access_token'] = get_user_access_token(user.id)

			selected_repo = get_user_selected_repo(user.id)
			response_data['selected_repo_name'] = selected_repo['name']
			response_data['selected_repo_url'] = selected_repo['url']
			
	return JsonResponse(response_data)

# View handler for save repo endpoint.
@csrf_exempt
def save_user_repo(request):
	if request.method == "POST":
		data = json.loads(request.body.decode('utf-8'))

		# Make sure all fields are present.
		if has_fields(data, ['name', 'url']):
			user_repo = UserSelectGithubRepo.objects.create(uid = request.user.id, name = data['name'], url = data['url'])
			user_repo.save()

	return JsonResponse({ 'success': True })

# View handler for logout.
def user_logout(request):
	logout(request)
	
	return JsonResponse({ 'success': True })

###################
# Helper functions
##

# Checks if the payload has all the keys present in fields.
def has_fields(payload, fields):
	has_fields = True
	for key in fields:
		has_fields = has_fields and (key in payload)

	return has_fields

# Google OAuth validator.
def valid_google_auth(access_token, id_token):
	# This is where we would validate the Google OAuth.
	return True

# GitHub application variables.
GITHUB_AUTH_URL = 'https://github.com/login/oauth/access_token'
GITHUB_CLIENT_ID = '241da044cc281f3964b0'
GITHUB_CLIENT_SECRET = '186fefbf8863dd44b3e57155b790670e69f3524d'

# Exchanges GitHub one-time code for an access code.
def get_github_access_token(code):
	access_token = None

	try:
		# Request an access token from the GitHub API.
		response = requests.post(GITHUB_AUTH_URL, {
			'client_id': GITHUB_CLIENT_ID,
			'client_secret': GITHUB_CLIENT_SECRET,
			'code': code
		})
		response.raise_for_status()

		# Get the access token from the GitHub API response.
		access_token = dictify(response.text)['access_token']
	except Exception as err:
		print('GitHub auth failure.')

	return access_token

# Convert response text to dictionary object.
def dictify(text):
	dict = {}

	keys_and_values = text.split('&')
	for key_value in keys_and_values:
		key_and_value = key_value.split('=')
		dict[key_and_value[0]] = key_and_value[1]
	
	return dict

###############
# Model access
##

# Access the DB to retrieve the user's GitHub access token.
def get_user_access_token(uid):
	access_token = ''

	# Search our DB.
	result = UserGithubOauth.objects.filter(uid = uid)
	if len(result) == 0:
		return access_token

	if result[0] is not None:
		access_token = result[0].access_token

	return access_token

# Access the DB to retrieve the user's selected repository.
def get_user_selected_repo(uid):
	selected_repo = {
		'name': '',
		'url': ''
	}

	# Search our DB.
	result = UserSelectGithubRepo.objects.filter(uid = uid)
	if len(result) == 0:
		return selected_repo;

	if result[0] is not None:
		selected_repo['name'] = result[0].name
		selected_repo['url'] = result[0].url

	return selected_repo