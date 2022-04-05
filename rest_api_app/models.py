from django.db import models

# Model for storing GitHub access tokens.
class UserGithubOauth(models.Model):
	uid = models.PositiveSmallIntegerField(unique = True)
	access_token = models.CharField(max_length=100)

# Model for storing user selected repo.
class UserSelectGithubRepo(models.Model):
	uid = models.PositiveSmallIntegerField(unique = True)
	name = models.CharField(max_length=50)
	url = models.CharField(max_length=100)