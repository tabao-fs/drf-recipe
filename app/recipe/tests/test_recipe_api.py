from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Recipe



RECIPES_URL = reverse('recipe:recipe-list')


def sample_recipe(user, **params):
    '''
    Create and return a sample recipe
    '''
    defaults = {
        'title': 'Recipe',
        'time_minutes': 10,
        'price': 5.00
    }
    defaults.update(params)

    return Recipe.objects.create(user=user, **defaults)


class PublicRecipeApiTests(TestCase):
    '''
    Test unauthenticated recipe API access
    '''
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        '''
        Test that authentication is required
        '''
        res = self.client.get(RECIPES_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateRecipeApiTests(TestCase):
    '''
    Test authenticated recipe API access
    '''
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            'test@example.com',
            'password'
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)
