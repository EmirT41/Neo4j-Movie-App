# Neo4j Movie Search & Graph Exporter

Bu proje, Neo4j Movie Database üzerinde film araması yapan, detaylarını listeleyen ve filmin ilişkilerini (oyuncu/yönetmen) JSON formatında bir grafik veri yapısı olarak dışa aktaran bir Python uygulamasıdır.


## 🚀 Özellikler
* **Film Arama:** Başlık bazlı anahtar kelime ile arama.
* **Detay Görüntüleme:** Seçilen filmin vizyon yılı, yönetmenleri ve oyuncularını listeleme.
* **JSON Export:** Seçili filmin graf yapısını (node/link) D3.js gibi kütüphanelere uygun formatta kaydetme.
* **Unit Testler:** Mock kütüphanesi kullanılarak yazılmış kapsamlı testler.

## 🛠️ Kurulum
1. **Neo4j Başlatın:** Yerelinizde veya AuraDB üzerinde bir Neo4j veritabanı çalıştırın ve `Movie` örnek veri setini yükleyin.
2. **Kütüphaneleri Kurun:**
   ```bash
   pip install -r requirements.txt

🧪 Testleri Çalıştırma

python -m unittest test_project.py

📂 Kullanım

python main.py


!!Dikkat main.py'de bulunan veri tabanına bağlama kısmında kendi veri tabanı şifrenizi giriniz!!