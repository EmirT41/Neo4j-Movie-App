from neo4j import GraphDatabase

class Database_Connection:
    def __init__(self, uri, user, password):
        try:
            self._driver = GraphDatabase.driver(uri, auth=(user, password))
            self._driver.verify_connectivity()
        except Exception:
            raise RuntimeError("Hata: Neo4j veritabanına bağlanılamadı! Lütfen bağlantı ayarlarını kontrol edin.")

    def close(self):
        if self._driver:
            self._driver.close()

class Movie_Repository:
    def __init__(self, conn: Database_Connection):
        self.__driver = conn._driver

    def search_movies(self, keyword):
        query = """
        MATCH (m:Movie)
        WHERE m.title CONTAINS $keyword
        RETURN m.title AS title, m.released AS year
        """

        try:
            with self.__driver.session(database="movie") as session:
                return list(session.run(query, keyword=keyword))
        except Exception:
            raise RuntimeError("Hata: Neo4j veritabanına bağlanılamadı! Lütfen bağlantı ayarlarını kontrol edin.")

    def get_details(self, title):
        query = """
        MATCH (m:Movie {title: $title})
        OPTIONAL MATCH (d:Person)-[:DIRECTED]->(m)
        OPTIONAL MATCH (a:Person)-[:ACTED_IN]->(m)
        RETURN m.title AS title, m.released AS year, m.tagline AS tagline,
               collect(DISTINCT d.name) AS directors,
               collect(DISTINCT a.name)[0..5] AS actors
        """
        try:
            with self.__driver.session(database="movie") as session:
                return session.run(query, title=title).single()
        except Exception:
            raise RuntimeError("Hata: Neo4j veritabanına bağlanılamadı! Lütfen bağlantı ayarlarını kontrol edin.")

    def get_graph_data(self, title):
        query = """
        MATCH (m:Movie {title: $title})
        OPTIONAL MATCH (p:Person)-[r:ACTED_IN|DIRECTED]->(m)
        RETURN m, collect(p) AS persons, collect(r) AS relationships
        """

        try:
            with self.__driver.session(database="movie") as session:
                return session.run(query, title=title).single()
        except Exception:
            raise RuntimeError("Hata: Neo4j veritabanına bağlanılamadı! Lütfen bağlantı ayarlarını kontrol edin.")