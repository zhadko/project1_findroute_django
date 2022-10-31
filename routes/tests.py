from django.core.exceptions import ValidationError
from django.test import TestCase
from cities.models import City
from django.urls import reverse

from trains.models import Train
from routes import views as routes_view
from routes.utils import dfs_paths, get_graph
from cities import views as cities_view

from src.routes.forms import RouteForm


class AllTestCase(TestCase):

    def setUp(self) -> None:
        self.city_A = City.objects.create(name='A')
        self.city_B = City.objects.create(name='B')
        self.city_C = City.objects.create(name='C')
        self.city_D = City.objects.create(name='D')
        self.city_E = City.objects.create(name='E')

        lst = [
            Train(name='t1', from_city=self.city_A, to_city=self.city_B, travel_time=9),
            Train(name='t2', from_city=self.city_B, to_city=self.city_D, travel_time=8),
            Train(name='t3', from_city=self.city_A, to_city=self.city_C, travel_time=7),
            Train(name='t4', from_city=self.city_C, to_city=self.city_B, travel_time=6),
            Train(name='t5', from_city=self.city_B, to_city=self.city_E, travel_time=3),
            Train(name='t6', from_city=self.city_B, to_city=self.city_A, travel_time=11),
            Train(name='t7', from_city=self.city_A, to_city=self.city_C, travel_time=10),
            Train(name='t8', from_city=self.city_E, to_city=self.city_D, travel_time=5),
            Train(name='t9', from_city=self.city_D, to_city=self.city_E, travel_time=4),
        ]
        Train.objects.bulk_create(lst)

    def test_model_city_duplicate(self):
        """Testing an error of duplication city"""
        city = City(name="A")
        with self.assertRaises(ValidationError):
            city.full_clean()

    def test_model_train_duplicate(self):
        """Testing an error of duplication train"""
        train = Train(name='t1', from_city=self.city_A, to_city=self.city_B, travel_time=129)
        with self.assertRaises(ValidationError):
            train.full_clean()

    def test_model_travel_time_duplicate(self):
        """Testing an error of duplication travel_time"""
        train = Train(name='t1123', from_city=self.city_A, to_city=self.city_B, travel_time=9)
        with self.assertRaises(ValidationError):
            train.full_clean()
        try:
            train.full_clean()
        except ValidationError as e:
            self.assertEqual({'__all__': ['Change the travel time']}, e.message_dict)
            self.assertIn('Change the travel time', e.messages)

    def test_home_routes_views(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(response, template_name='routes/home.html')
        self.assertEqual(response.resolver_match.func, routes_view.home)

    def test_cbv_detail_views(self):
        response = self.client.get(reverse('cities:detail', kwargs={'pk': self.city_A.id}))
        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(response, template_name='cities/detail.html')
        self.assertEqual(response.resolver_match.func.__name__, cities_view.CityDetailView.as_view().__name__)

    def test_find_all_routes(self):
        qs = Train.objects.all()
        graph = get_graph(qs)
        all_routes = list(dfs_paths(graph, self.city_A.id, self.city_E.id))
        self.assertEqual(len(all_routes), 4)

    def test_valid_route_form(self):
        data = {'from_city':self.city_A.id,
                'to_city':self.city_B.id,
                'cities': [self.city_E.id, self.city_D.id],
                'travelling_time': 9}
        form = RouteForm(data = data)
        self.assertTrue(form.is_valid())

    def test_message_error_more_time(self):
        data = {'from_city': self.city_A.id,
                'to_city': self.city_E.id,
                'cities': [self.city_C.id],
                'travelling_time': 9}
        response = self.client.post('/find_routes/', data)
        self.assertContains(response, 'Travelling time so low(', 1, 200)

    def test_message_error_from_cities(self):
        data = {'from_city': self.city_B.id,
                'to_city': self.city_E.id,
                'cities': [self.city_C.id],
                'travelling_time': 59}
        response = self.client.post('/find_routes/', data)
        self.assertContains(response, 'No route throw this cities', 1, 200)