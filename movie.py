import json
import os

class Movie:
    def __init__(self, repo):
        self.__repo = repo
        self.last_selected_movie = None

    def search_and_list(self, keyword):
        if len(keyword.strip()) < 2:
            print("Uyarı: Lütfen geçerli bir arama terimi giriniz!")
            return None
        
        results = self.__repo.search_movies(keyword)
        if not results:
            print("Sonuç bulunamadi.Menuye dönülüyor...")
            return None
        
        print("\nBulunan Filmler:")
        for i, record in enumerate(results, 1):
            print(f"{i}) {record['title']} ({record['year']})")
        return results

    def show_details(self, movie_title):
        details = self.__repo.get_details(movie_title)
        if details:
            print(f"\nFilm: {details['title']} ({details['year']})")
            print(f"Tagline: {details['tagline'] or 'Yok'}")
            print(f"Yönetmenler: {', '.join(details['directors'])}")
            print(f"Oyuncular: {', '.join(details['actors'])}")
            self.last_selected_movie = movie_title
        else:
            print("Detaylar alınamadı. Menuye dönülüyor...")

    def export_to_json(self):
        if not self.last_selected_movie:
            print("Önce bir film seçmelisiniz! Menuye dönülüyor...")
            return
        
        data = self.__repo.get_graph_data(self.last_selected_movie)
        nodes = [{"id": data['m']['title'], "label": "Movie"}]
        links = []

        for p, r in zip(data['persons'], data['relationships']):
            nodes.append({"id": p['name'], "label": "Person"})
            links.append({"source": p['name'], "target": data['m']['title'], "type": r.type})

        if not os.path.exists('exports'): os.makedirs('exports')
        
        output = {"nodes": nodes, "links": links}
        with open("exports/graph.json", "w", encoding="utf-8") as f:
            json.dump(output, f, ensure_ascii=False, indent=4)
        print("graph.json oluşturuldu: exports/graph.json")