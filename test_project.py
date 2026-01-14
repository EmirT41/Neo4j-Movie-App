import unittest
from unittest.mock import Mock, patch, MagicMock
import json
import os
import sys

#Mock ile tüm dış bağımlılıkları izole etme#

sys.path.insert(0, os.path.dirname(__file__)) # Proje dosyalarını import etmek için #

from database_process import Database_Connection, Movie_Repository
from movie import Movie


class TestDatabaseConnection(unittest.TestCase): #Veritabanı bağlantısı kontrolü #

    @patch('database_process.GraphDatabase.driver')
    def test_successful_connection(self, mock_driver):

        #Başarılı bağlantı testi#
        mock_driver_instance = Mock()
        mock_driver.return_value = mock_driver_instance
        mock_driver_instance.verify_connectivity = Mock()

        conn = Database_Connection("bolt://localhost:7687", "neo4j", "password")

        self.assertIsNotNone(conn._driver)
        mock_driver.assert_called_once_with("bolt://localhost:7687", auth=("neo4j", "password"))
        mock_driver_instance.verify_connectivity.assert_called_once()

    @patch('database_process.GraphDatabase.driver')
    def test_failed_connection(self, mock_driver):
        # Bağlantıda hata fırlat
        mock_driver.side_effect = Exception("Bağlantı kurulamadı")

        with self.assertRaises(RuntimeError):
            Database_Connection("bolt://localhost:7687", "neo4j", "password")

    def test_close_connection(self):
        #Bağlantıları kapatma#
        mock_driver = Mock()
        conn = Database_Connection.__new__(Database_Connection)
        conn._driver = mock_driver

        conn.close()
        mock_driver.close.assert_called_once()

    def test_close_none_driver(self):
        conn = Database_Connection.__new__(Database_Connection)
        conn._driver = None

        # Hata atmamalı
        conn.close()


class TestMovieRepository(unittest.TestCase): #Film deposu için testler#

    def setUp(self): #Her test öncesi hazırlık#
        self.mock_conn = Mock()
        self.mock_driver = Mock()

        # database_process.py içindeki gerçek isimle uyumlu
        self.mock_conn._driver = self.mock_driver

        self.repo = Movie_Repository(self.mock_conn)

        self.mock_session = Mock() # Session context manager mock'u# 
        mock_session_cm = Mock()
        mock_session_cm.__enter__ = Mock(return_value=self.mock_session)
        mock_session_cm.__exit__ = Mock(return_value=None)

        self.mock_driver.session = Mock(return_value=mock_session_cm)

    def test_search_movies(self): #Film arama testi#
        mock_record1 = {'title': 'The Matrix', 'year': 1999}
        mock_record2 = {'title': 'The Matrix Reloaded', 'year': 2003}

        self.mock_session.run.return_value = [mock_record1, mock_record2]

        results = self.repo.search_movies("Matrix")

        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]['title'], "The Matrix")

    def test_get_details(self): #Film detayları testi#
        mock_record = {'title': 'The Matrix', 'year': 1999}

        self.mock_session.run.return_value.single.return_value = mock_record

        result = self.repo.get_details("The Matrix")

        self.assertEqual(result['title'], "The Matrix")

    def test_get_graph_data(self): #Grafik verisi testi# #Graph#

        mock_record = Mock()
        mock_movie = Mock()
        mock_movie.__getitem__ = Mock(return_value='The Matrix')
        mock_person = Mock()
        mock_person.__getitem__ = Mock(return_value='Keanu Reeves')
        mock_relationship = Mock()
        mock_relationship.type = 'ACTED_IN'

        mock_record.__getitem__ = Mock(side_effect=lambda key: {
            'm': mock_movie,
            'persons': [mock_person],
            'relationships': [mock_relationship]
        }[key])

        self.mock_session.run.return_value.single.return_value = mock_record

        result = self.repo.get_graph_data("The Matrix")

        self.assertIsNotNone(result)
        self.mock_session.run.assert_called_once()


class TestMovie(unittest.TestCase): #Movie sınıfı için testler#

    def setUp(self): #Her test öncesi hazırlık#
        self.mock_repo = Mock()
        self.movie_app = Movie(self.mock_repo)

    def test_search_and_list_success(self): #Test başarılı , listele#
        mock_results = [
            {'title': 'The Matrix', 'year': 1999},
            {'title': 'The Matrix Reloaded', 'year': 2003},
        ]

        self.mock_repo.search_movies.return_value = mock_results

        with patch('builtins.print') as mock_print:
            results = self.movie_app.search_and_list("Matrix")

        self.assertEqual(results, mock_results)

    def test_search_and_list_empty_keyword(self): #Boş anahtar kelime testi#
        with patch('builtins.print') as mock_print:
            result = self.movie_app.search_and_list("")

        self.assertIsNone(result)

    def test_search_and_list_no_results(self):
        """Sonuç bulunamama testi"""
        self.mock_repo.search_movies.return_value = []

        with patch('builtins.print') as mock_print:
            result = self.movie_app.search_and_list("NonExistentMovie")

        self.assertIsNone(result)
        mock_print.assert_called_once_with("Sonuç bulunamadi.Menuye dönülüyor...")

    def test_show_details_success(self): #Detay gösterme testi#
        mock_details = {
            'title': 'The Matrix',
            'year': 1999,
            'tagline': 'Welcome to the Real World',
            'directors': ['Wachowski Sisters'],
            'actors': ['Keanu Reeves'],
        }

        self.mock_repo.get_details.return_value = mock_details

        self.movie_app.show_details("The Matrix")

        self.assertEqual(self.movie_app.last_selected_movie, "The Matrix")

    def test_show_details_no_data(self): #"Detay verisi yok" testi#
        
        self.mock_repo.get_details.return_value = None

        with patch('builtins.print') as mock_print:
            self.movie_app.show_details("NonExistentMovie")

        self.assertIsNone(self.movie_app.last_selected_movie)
        mock_print.assert_called_once_with("Detaylar alınamadı. Menuye dönülüyor...")

    @patch('movie.os.path.exists') 
    @patch('movie.os.makedirs')
    @patch('builtins.open', new_callable=unittest.mock.mock_open)
    def test_export_to_json_success(self, mock_file, mock_makedirs, mock_exists):
        #Jsona aktarma başarılı mı testi#
        self.movie_app.last_selected_movie = "The Matrix" 

        mock_data = Mock()
        mock_movie = Mock()
        mock_movie.__getitem__ = Mock(return_value='The Matrix')
        mock_person = Mock()
        mock_person.__getitem__ = Mock(return_value='Keanu Reeves')
        mock_relationship = Mock()
        mock_relationship.type = 'ACTED_IN'

        mock_data.__getitem__ = Mock(side_effect=lambda key: {
            'm': mock_movie,
            'persons': [mock_person],
            'relationships': [mock_relationship]
        }[key])

        self.mock_repo.get_graph_data.return_value = mock_data
        mock_exists.return_value = False

        with patch('builtins.print') as mock_print:
            self.movie_app.export_to_json()

        mock_exists.assert_called_once_with('exports')
        mock_makedirs.assert_called_once_with('exports')
        mock_file.assert_called_once_with("exports/graph.json", "w", encoding="utf-8")
        mock_print.assert_called_once_with("graph.json oluşturuldu: exports/graph.json")

    def test_export_to_json_no_selection(self): #Jsona aktarma için seçim yok testi#
        
        self.movie_app.last_selected_movie = None

        with patch('builtins.print') as mock_print:
            self.movie_app.export_to_json()

        self.mock_repo.get_graph_data.assert_not_called()
        mock_print.assert_called_once_with("Önce bir film seçmelisiniz! Menuye dönülüyor...")


if __name__ == "__main__":
    unittest.main()